from pysat.solvers import Glucose3
from utils import *
from program import Map, Cell
from typing import List, Tuple, Set
from collections import deque

class AgentBrain:
    def __init__(self, map: Map):
        self.map = map
        self.knowledge_base = Glucose3()
        self.visited_cells = set()
        self.safe_cells = set()
        self.dangerous_cells = set()
        self.unknown_cells = {(x, y) for x in range(map.size) for y in range(map.size)}
        self.direction = Direction.UP
        self.has_gold = False
        self.last_positions = deque(maxlen=3)  # Store last 3 positions to detect loops
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
            Object.BREEZE: (x * self.map.size + y) * 6 + 7,
            Object.WHIFF: (x * self.map.size + y) * 6 + 8,
            Object.GLOW: (x * self.map.size + y) * 6 + 9,
        }

    def update_knowledge(self, perceptions: Set[Object]):
        x, y = self.map.agent_position
        cell_id = self.get_cell_id(x, y)

        self.visited_cells.add((x, y))
        self.safe_cells.add((x, y))
        self.unknown_cells.discard((x, y))
        self.dangerous_cells.discard((x, y))
        for obj in [Object.WUMPUS, Object.PIT, Object.POISONOUS_GAS]:
            self.knowledge_base.add_clause([-cell_id[obj]])

        adjacent_cells = self.get_adjacent_cells(x, y)

        self.update_perception(Object.BREEZE, Object.PIT, perceptions, adjacent_cells)
        self.update_perception(Object.STENCH, Object.WUMPUS, perceptions, adjacent_cells)
        self.update_perception(Object.WHIFF, Object.POISONOUS_GAS, perceptions, adjacent_cells)
        self.update_perception(Object.GLOW, Object.HEALING_POTIONS, perceptions, adjacent_cells)

        for perception, danger in [(Object.BREEZE, Object.PIT), (Object.STENCH, Object.WUMPUS), (Object.WHIFF, Object.POISONOUS_GAS)]:
            if perception in perceptions:
                for adj in adjacent_cells:
                    if adj not in self.visited_cells:
                        self.dangerous_cells.add(adj)
                        self.unknown_cells.discard(adj)
                        self.safe_cells.discard(adj)
            else:
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
        self.last_positions.append(self.map.agent_position)

        if self.map.agent_position in self.map.gold_positions:
            return Action.GRAB_G
        if self.map.agent_position in self.map.healing_positions:
            return Action.GRAB_HP
        
        if Object.STENCH in perceptions:
            return Action.SHOOT

        safe_unvisited = self.safe_cells - self.visited_cells
        if safe_unvisited:
            return self.move_towards_safe(safe_unvisited)

        if self.unknown_cells and self.has_gold == False:
            return self.explore_unknown()
        elif self.has_gold:
            return self.return_to_start()

        # Back to start
        if self.has_gold and self.map.agent_position == (self.map.size - 1, 0):
            return Action.CLIMB

        return self.backtrack()

    def move_towards_safe(self, safe_cells: Set[Tuple[int, int]]) -> Action:
        current_x, current_y = self.map.agent_position
        for dx, dy in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
            target = (current_x + dx, current_y + dy)
            if target in safe_cells and target not in self.last_positions:
                return self.move_towards(target)

        # If there is no safe cell around, move to the next safe cell
        unvisited_safe = safe_cells - self.visited_cells
        if unvisited_safe:
            nearest_safe = min(unvisited_safe, key=lambda cell: self.manhattan_distance(self.map.agent_position, cell))
            path = self.find_safe_path(self.map.agent_position, nearest_safe)
            if path:
                return self.move_towards(path[1])
        
        return self.move_towards(next(iter(safe_cells)))

    def move_towards_safe(self, safe_cells: Set[Tuple[int, int]]) -> Action:
        current_x, current_y = self.map.agent_position
        for dx, dy in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
            target = (current_x + dx, current_y + dy)
            if target in safe_cells and target not in self.last_positions:
                return self.move_towards(target)

        # If there is no safe cell around, move to the next safe cell
        unvisited_safe = safe_cells - self.visited_cells
        if unvisited_safe:
            nearest_safe = min(unvisited_safe, key=lambda cell: self.manhattan_distance(self.map.agent_position, cell))
            path = self.find_safe_path(self.map.agent_position, nearest_safe)
            if path:
                return self.move_towards(path[1])
        
        return self.move_towards(next(iter(safe_cells)))

    def find_safe_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        queue = deque([(start, [start])])
        visited = set()

        while queue:
            (x, y), path = queue.popleft()
            if (x, y) == goal:
                return path

            if (x, y) not in visited:
                visited.add((x, y))
                for dx, dy in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
                    next_cell = (x + dx, y + dy)
                    if (next_cell in self.safe_cells and 
                        next_cell not in visited and 
                        0 <= next_cell[0] < self.map.size and 
                        0 <= next_cell[1] < self.map.size):
                        queue.append((next_cell, path + [next_cell]))

        return []  # No path found

    def explore_unknown(self) -> Action:
        current_x, current_y = self.map.agent_position
        for dx, dy in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
            target = (current_x + dx, current_y + dy)
            if target in self.unknown_cells and target not in self.dangerous_cells and target not in self.last_positions:
                return self.move_towards(target)
        
        safe_unknown = self.unknown_cells - self.dangerous_cells
        if safe_unknown:
            nearest_unknown = min(safe_unknown, key=lambda cell: self.manhattan_distance(self.map.agent_position, cell))
            return self.move_towards(nearest_unknown)
        
        return self.backtrack()

    def backtrack(self) -> Action:
        if not self.visited_cells:
            return Action.MOVE_FORWARD

        target = min(self.visited_cells - set(self.last_positions), 
                     key=lambda cell: self.manhattan_distance(self.map.agent_position, cell), 
                     default=None)

        if target is None:
            target = max(self.visited_cells, 
                         key=lambda cell: self.manhattan_distance(self.map.agent_position, cell))
            
        return self.move_towards(target)
    
    def return_to_start(self) -> Action:
        # Find path to start position
        start_position = (self.map.size - 1, 0)  # Pos (9, 0)
        path = self.find_safe_path(self.map.agent_position, start_position)
        if path:
            return self.move_towards(path[1])
    
    def move_towards(self, target: Tuple[int, int]) -> Action:
        dx = target[0] - self.map.agent_position[0]
        dy = target[1] - self.map.agent_position[1]
        
        target_direction = None
        if dx > 0:
            target_direction = Direction.DOWN
        elif dx < 0:
            target_direction = Direction.UP
        elif dy < 0:
            target_direction = Direction.LEFT
        elif dy > 0:
            target_direction = Direction.RIGHT

        if target_direction is None:
            return Action.MOVE_FORWARD

        return self.turn_to_direction(target_direction)

    def turn_to_direction(self, target_direction: Direction) -> Action:
        if self.direction == target_direction:
            return Action.MOVE_FORWARD
        
        turns = {
            (Direction.UP, Direction.RIGHT): Action.TURN_RIGHT,
            (Direction.UP, Direction.DOWN): Action.TURN_RIGHT,
            (Direction.UP, Direction.LEFT): Action.TURN_LEFT,
            (Direction.RIGHT, Direction.DOWN): Action.TURN_RIGHT,
            (Direction.RIGHT, Direction.LEFT): Action.TURN_RIGHT,
            (Direction.RIGHT, Direction.UP): Action.TURN_LEFT,
            (Direction.DOWN, Direction.LEFT): Action.TURN_RIGHT,
            (Direction.DOWN, Direction.UP): Action.TURN_RIGHT,
            (Direction.DOWN, Direction.RIGHT): Action.TURN_LEFT,
            (Direction.LEFT, Direction.UP): Action.TURN_RIGHT,
            (Direction.LEFT, Direction.RIGHT): Action.TURN_RIGHT,
            (Direction.LEFT, Direction.DOWN): Action.TURN_LEFT,
        }
        
        turn_action = turns.get((self.direction, target_direction), Action.MOVE_FORWARD)
        if turn_action != Action.MOVE_FORWARD:
            self.direction = target_direction
        return turn_action

    def process_successful_shot(self, wumpus_position: Tuple[int, int]):
        x, y = wumpus_position
        cell_id = self.get_cell_id(x, y)

        self.knowledge_base.add_clause([-cell_id[Object.WUMPUS]])
        self.safe_cells.add(wumpus_position)
        self.dangerous_cells.discard(wumpus_position)
        self.unknown_cells.discard(wumpus_position)

        adjacent_cells = self.map.get_adjacent_cells(x, y)
        for ax, ay in adjacent_cells:
            adj_cell_id = self.get_cell_id(ax, ay)
            self.knowledge_base.add_clause([-adj_cell_id[Object.STENCH]])

            if (ax, ay) not in self.visited_cells and not self.is_dangerous(ax, ay):
                self.safe_cells.add((ax, ay))
                self.dangerous_cells.discard((ax, ay))
                self.unknown_cells.discard((ax, ay))

    def update_knowledge_after_grab(self, grabbed_object: Object, position: Tuple[int, int]):
        x, y = position
        cell_id = self.get_cell_id(x, y)

        if grabbed_object == Object.GOLD:
            self.knowledge_base.add_clause([-cell_id[Object.GOLD]])
            self.has_gold = True
        elif grabbed_object == Object.HEALING_POTIONS:
            self.knowledge_base.add_clause([-cell_id[Object.HEALING_POTIONS]])
            
            # Remove GLOW from adjacent cells in the knowledge base
            adjacent_cells = self.get_adjacent_cells(x, y)
            for ax, ay in adjacent_cells:
                adj_cell_id = self.get_cell_id(ax, ay)
                self.knowledge_base.add_clause([-adj_cell_id[Object.GLOW]])

        # Update safe cells and remove from unknown cells
        self.safe_cells.add(position)
        self.unknown_cells.discard(position)
    
    def manhattan_distance(self, cell1: Tuple[int, int], cell2: Tuple[int, int]) -> int:
        return abs(cell1[0] - cell2[0]) + abs(cell1[1] - cell2[1])