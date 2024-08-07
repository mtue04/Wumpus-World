from pysat.solvers import Glucose3
from utils import *
from program import Map, Cell
from typing import List, Tuple, Set


class AgentBrain:
    def __init__(self, map: Map):
        self.map = map
        self.knowledge_base = Glucose3()
        self.visited_cells = set()
        self.safe_cells = set()
        self.dangerous_cells = set()
        self.unknown_cells = {(x, y) for x in range(map.size) for y in range(map.size)}
        self.direction = Direction.UP
        self.initialize_knowledge_base()

    def initialize_knowledge_base(self):
        for x in range(self.map.size):
            for y in range(self.map.size):
                cell_id = self.get_cell_id(x, y)
                for obj in [Object.WUMPUS, Object.PIT, Object.POISONOUS_GAS, Object.GOLD, Object.HEALING_POTIONS]:
                    self.knowledge_base.add_clause([-cell_id[obj], -cell_id[obj]])

    def get_cell_id(self, x: int, y: int) -> dict:
        return {
            Object.WUMPUS: (x * self.map.size + y) * 6 + 1,
            Object.PIT: (x * self.map.size + y) * 6 + 2,
            Object.POISONOUS_GAS: (x * self.map.size + y) * 6 + 3,
            Object.GOLD: (x * self.map.size + y) * 6 + 4,
            Object.HEALING_POTIONS: (x * self.map.size + y) * 6 + 5,
            Object.STENCH: (x * self.map.size + y) * 6 + 6,
        }

    def update_knowledge(self, perceptions: Set[Object]):
        x, y = self.map.agent_position
        cell_id = self.get_cell_id(x, y)

        # Mark current cell as visited and safe
        self.visited_cells.add((x, y))
        self.safe_cells.add((x, y))
        self.unknown_cells.discard((x, y))
        self.dangerous_cells.discard((x, y))
        for obj in [Object.WUMPUS, Object.PIT, Object.POISONOUS_GAS]:
            self.knowledge_base.add_clause([-cell_id[obj]])

        adjacent_cells = self.get_adjacent_cells(x, y)

        # Update knowledge based on perceptions
        self.update_perception(Object.BREEZE, Object.PIT, perceptions, adjacent_cells)
        self.update_perception(Object.STENCH, Object.WUMPUS, perceptions, adjacent_cells)
        self.update_perception(Object.WHIFF, Object.POISONOUS_GAS, perceptions, adjacent_cells)
        self.update_perception(Object.GLOW, Object.HEALING_POTIONS, perceptions, adjacent_cells)

        # Mark adjacent cells as potentially dangerous based on perceptions
        if Object.BREEZE in perceptions:
            for adj in adjacent_cells:
                self.dangerous_cells.add(adj)
                self.unknown_cells.discard(adj)
                self.safe_cells.discard(adj)
        if Object.STENCH in perceptions:
            for adj in adjacent_cells:
                self.dangerous_cells.add(adj)
                self.unknown_cells.discard(adj)
                self.safe_cells.discard(adj)
        if Object.WHIFF in perceptions:
            for adj in adjacent_cells:
                self.dangerous_cells.add(adj)
                self.unknown_cells.discard(adj)
                self.safe_cells.discard(adj)

        # Mark adjacent cells as safe if no danger perceptions
        if Object.BREEZE not in perceptions:
            for adj in adjacent_cells:
                if adj not in self.visited_cells and adj not in self.dangerous_cells:
                    self.safe_cells.add(adj)
                    self.unknown_cells.discard(adj)
        if Object.STENCH not in perceptions:
            for adj in adjacent_cells:
                if adj not in self.visited_cells and adj not in self.dangerous_cells:
                    self.safe_cells.add(adj)
                    self.unknown_cells.discard(adj)
        if Object.WHIFF not in perceptions:
            for adj in adjacent_cells:
                if adj not in self.visited_cells and adj not in self.dangerous_cells:
                    self.safe_cells.add(adj)
                    self.unknown_cells.discard(adj)

    def update_perception(self, perception: Object, danger: Object, perceptions: Set[Object], adjacent_cells: List[Tuple[int, int]]):
        if perception in perceptions:
            danger_clause = [self.get_cell_id(ax, ay)[danger] for ax, ay in adjacent_cells]
            self.knowledge_base.add_clause(danger_clause)
        else:
            for ax, ay in adjacent_cells:
                self.knowledge_base.add_clause([-self.get_cell_id(ax, ay)[danger]])

    def is_safe(self, x: int, y: int) -> bool:
        cell_id = self.get_cell_id(x, y)
        return all(
            not self.knowledge_base.solve(assumptions=[cell_id[obj]])
            for obj in [Object.WUMPUS, Object.PIT, Object.POISONOUS_GAS]
        )

    def is_dangerous(self, x: int, y: int) -> bool:
        cell_id = self.get_cell_id(x, y)
        return any(
            self.knowledge_base.solve(assumptions=[cell_id[obj]])
            for obj in [Object.WUMPUS, Object.PIT, Object.POISONOUS_GAS]
        )

    def get_adjacent_cells(self, x: int, y: int) -> List[Tuple[int, int]]:
        adjacent = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        return [
            (ax, ay)
            for ax, ay in adjacent
            if 0 <= ax < self.map.size and 0 <= ay < self.map.size
        ]

    def make_decision(self, perceptions: Set[Object]) -> Action:
        self.update_knowledge(perceptions)

        if Object.GOLD in perceptions:
            return Action.GRAB_G
        if Object.HEALING_POTIONS in perceptions:
            return Action.GRAB_HP
        
        # Check for stench and shoot if Wumpus is suspected nearby
        if Object.STENCH in perceptions:
            return Action.SHOOT

        # If there are unvisited safe cells, move to one of them
        if self.safe_cells - self.visited_cells:
            target = min(
                self.safe_cells - self.visited_cells,
                key=lambda cell: self.manhattan_distance(self.map.agent_position, cell),
            )
            return self.move_towards(target)
    
        # If no unvisited safe cells, consider taking a risk
        if self.dangerous_cells:
            least_dangerous = min(
                self.dangerous_cells, key=lambda cell: self.danger_level(cell)
            )
            if self.danger_level(least_dangerous) < 0.5:
                return self.move_towards(least_dangerous)

        # If no good moves, try to backtrack
        if self.visited_cells:
            backtrack_target = max(
                self.visited_cells,
                key=lambda cell: self.manhattan_distance(self.map.agent_position, cell),
            )
            return self.move_towards(backtrack_target)

        # If all else fails, make a random move
        return Action.MOVE_FORWARD

    def manhattan_distance(self, cell1: Tuple[int, int], cell2: Tuple[int, int]) -> int:
        return abs(cell1[0] - cell2[0]) + abs(cell1[1] - cell2[1])

    def danger_level(self, cell: Tuple[int, int]) -> float:
        x, y = cell
        cell_id = self.get_cell_id(x, y)
        danger_count = sum(
            [
                self.knowledge_base.solve(assumptions=[cell_id[obj]])
                for obj in [Object.WUMPUS, Object.PIT, Object.POISONOUS_GAS]
            ]
        )
        return danger_count / 3

    def move_towards(self, target: Tuple[int, int]) -> Action:
        dx = target[0] - self.map.agent_position[0]
        dy = target[1] - self.map.agent_position[1]
        
        if dx > 0: # Move down
            if self.direction == Direction.DOWN:
                return Action.MOVE_FORWARD
            elif self.direction == Direction.UP:
                self.direction = Direction.RIGHT
                return Action.TURN_RIGHT
            elif self.direction == Direction.LEFT:
                self.direction = Direction.DOWN
                return Action.TURN_RIGHT
            elif self.direction == Direction.RIGHT:
                self.direction = Direction.DOWN
                return Action.TURN_LEFT
            
        elif dx < 0: # Move up
            if self.direction == Direction.UP:
                return Action.MOVE_FORWARD
            elif self.direction == Direction.DOWN:
                self.direction = Direction.RIGHT
                return Action.TURN_RIGHT
            elif self.direction == Direction.RIGHT:
                self.direction = Direction.UP
                return Action.TURN_LEFT
            elif self.direction == Direction.LEFT:
                self.direction = Direction.UP
                return Action.TURN_RIGHT
            
        elif dy < 0: # Move left
            if self.direction == Direction.LEFT:
                return Action.MOVE_FORWARD
            elif self.direction == Direction.RIGHT:
                self.direction = Direction.UP
                return Action.TURN_LEFT
            elif self.direction == Direction.UP:
                self.direction = Direction.LEFT
                return Action.TURN_LEFT
            elif self.direction == Direction.DOWN:
                self.direction = Direction.LEFT
                return Action.TURN_RIGHT
            
        elif dy > 0: # Move right
            if self.direction == Direction.RIGHT:
                return Action.MOVE_FORWARD
            elif self.direction == Direction.LEFT:
                self.direction = Direction.UP
                return Action.TURN_RIGHT
            elif self.direction == Direction.UP:
                self.direction = Direction.RIGHT
                return Action.TURN_RIGHT
            elif self.direction == Direction.DOWN:
                self.direction = Direction.RIGHT
                return Action.TURN_LEFT

        return Action.MOVE_FORWARD
    
    def process_successful_shot(self, wumpus_position: Tuple[int, int]):
        x, y = wumpus_position
        cell_id = self.get_cell_id(x, y)

        # Remove Wumpus from the knowledge base
        self.knowledge_base.add_clause([-cell_id[Object.WUMPUS]])

        # Mark the cell as safe
        self.safe_cells.add(wumpus_position)
        self.dangerous_cells.discard(wumpus_position)
        self.unknown_cells.discard(wumpus_position)

        # Update adjacent cells
        adjacent_cells = self.map.get_adjacent_cells(x, y)
        for ax, ay in adjacent_cells:
            adj_cell_id = self.get_cell_id(ax, ay)
            # Remove Stench from adjacent cells in the knowledge base
            self.knowledge_base.add_clause([-adj_cell_id[Object.STENCH]])

            # If the adjacent cell is not visited, mark it as safe if it's not dangerous for other reasons
            if (ax, ay) not in self.visited_cells and not self.is_dangerous(ax, ay):
                self.safe_cells.add((ax, ay))
                self.dangerous_cells.discard((ax, ay))
                self.unknown_cells.discard((ax, ay))

    # def write_output(self, output_file: str, score: int):
        # with open(output_file, "w") as f:
        #     f.write(f"Score: {score}\n\n")
        #     f.write("Safe cells:\n")
        #     for cell in sorted(self.safe_cells):
        #         f.write(f"{cell}\n")
        #     f.write("\nDangerous cells:\n")
        #     for cell in sorted(self.dangerous_cells):
        #         f.write(f"{cell}\n")
        #     f.write("\nVisited cells:\n")
        #     for cell in sorted(self.visited_cells):
        #         f.write(f"{cell}\n")