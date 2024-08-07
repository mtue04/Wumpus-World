from utils import *
from typing import List, Tuple, Optional
import pygame


class Cell:
    def __init__(self, position: Tuple[int, int]):
        self.position = position
        
        self.cell_type = CellType.UNDISCOVERED
        self.contents: set[Object] = set()
        self.is_visited = False

    def discover(self):
        if self.cell_type == CellType.UNDISCOVERED:
            self.cell_type = CellType.DISCOVERED

    def add_content(self, content: Object):
        if content in Object:
            self.contents.add(content)
        else:
            raise ValueError(f"Invalid content: {content}")

    def remove_content(self, content: Object):
        self.contents.discard(content)

    def has_content(self, content: Object) -> bool:
        return content in self.contents

    def mark_visited(self):
        self.is_visited = True

    def is_dangerous(self):
        return any(
            content in [Object.WUMPUS, Object.PIT, Object.POISONOUS_GAS]
            for content in self.contents
        )

    def is_safe(self):
        return not self.is_dangerous() and self.cell_type == CellType.DISCOVERED


class Map:
    def __init__(self):
        self.size: int = 0
        self.grid: List[List[Cell]] = []
        self.matrix: List[List[str]] = []
        self.agent_position: Optional[Tuple[int, int]] = None
        # self.gold_positions: List[Tuple[int, int]] = []
        # self.wumpus_positions: List[Tuple[int, int]] = []

    def load_map(self, filepath: str):
        with open(filepath, "r") as f:
            self.size = int(f.readline().strip())

            self.grid = [[Cell((x, y)) for y in range(self.size)] for x in range(self.size)]
            self.matrix = [[] for _ in range(self.size)]
            for x in range(self.size):
                line = f.readline().strip().split(".")
                for y, char in enumerate(line):
                    self.matrix[x].append(char)
                    self._process_cell(x, y, char)

        self._add_perceptions() 

    def _process_cell(self, x: int, y: int, char: str):
        cell = self.grid[x][y]

        if char == "-":
            cell.add_content(Object.EMPTY)
        elif char == "W":
            # self.wumpus_positions.append((x, y))
            cell.add_content(Object.WUMPUS)
        elif char == "P":
            cell.add_content(Object.PIT)
        elif char == "A":
            self.agent_position = (x, y)
            cell.add_content(Object.AGENT)
        elif char == "G":
            # self.gold_positions.append((x, y))
            cell.add_content(Object.GOLD)
        elif char == "P_G":
            cell.add_content(Object.POISONOUS_GAS)
        elif char == "H_P":
            cell.add_content(Object.HEALING_POTIONS)
        else:
            raise ValueError(f"Invalid character: {char}")

    def _add_perceptions(self):
        for x in range(self.size):
            for y in range(self.size):
                cell = self.grid[x][y]
                if cell.has_content(Object.WUMPUS):
                    self._add_perception_around(x, y, Object.STENCH)
                if cell.has_content(Object.PIT):
                    self._add_perception_around(x, y, Object.BREEZE)
                if cell.has_content(Object.POISONOUS_GAS):
                    self._add_perception_around(x, y, Object.WHIFF)
                if cell.has_content(Object.HEALING_POTIONS):
                    self._add_perception_around(x, y, Object.GLOW)

    def _add_perception_around(self, x: int, y: int, perception: Object):
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < self.size and 0 <= new_y < self.size:
                self.grid[new_x][new_y].add_content(perception)

    def get_cell(self, x: int, y: int) -> Cell:
        return self.grid[x][y]
    
    def get_cell_by_map_pos(self, x: int, y: int) -> Cell:
        return self.grid[self.size - x][y + 1]

    def matrix_to_map_pos(self, matrix_pos) -> Tuple[int, int]:
        x, y = matrix_pos
        return self.size - x, y + 1
    
    def map_to_matrix_pos(self, map_pos) -> Tuple[int, int]:
        x, y = map_pos
        return self.size - x, y - 1
    
    def is_valid_position(self, x: int, y: int) -> bool:
        return 0 <= x < self.size and 0 <= y < self.size

    def get_adjacent_cells(self, x: int, y: int) -> List[Tuple[int, int]]:
        adjacent = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
        return [(ax, ay) for ax, ay in adjacent if self.is_valid_position(ax, ay)]