from utils import *
from typing import List, Tuple, Optional
import pygame

class Cell:
    def __init__(self, matrix_pos, map_size):
        self.matrix_pos = matrix_pos                                            # (0, 0) (0, 1) ... (9, 9)   (TL -> BR)
        self.map_pos = matrix_pos[1] + 1, map_size - matrix_pos[0]              # (1, 1) (1, 2) ... (10, 10) (BL -> TR)
        self.index_pos = map_size * (self.map_pos[1] - 1) + self.map_pos[0]     # 1 2 3 ... 99 100           (BL -> TR)
        self.map_size = map_size

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
        return any(content in [Object.WUMPUS, Object.PIT, Object.POISONOUS_GAS] for content in self.contents)

    def is_safe(self):
        return not self.is_dangerous() and self.cell_type == CellType.DISCOVERED
    
class Map:
    def __init__(self):
        self.size: int = 0
        self.grid: List[List[Cell]] = []
        self.agent_position: Optional[Tuple[int, int]] = None
        self.gold_positions: List[Tuple[int, int]] = []
        self.wumpus_positions: List[Tuple[int, int]] = []
    
    def load_map(self, filepath: str):
        with open(filepath, "r") as f:
            self.size = int(f.readline().strip())
        
            self.grid = [[Cell((i, j), self.size) for j in range(self.size)] for i in range(self.size)]
            for y in range(self.size):
                line = f.readline().strip().split('.')
                for x, char in enumerate(line):
                    self._process_cell(x, y, char)
        
        self._add_perceptions()
    
    def _process_cell(self, x: int, y: int, char: str):
        cell = self.grid[y][x]

        if char == '-':
            cell.add_content(Object.EMPTY)
        elif char == 'W':
            self.wumpus_positions.append((x, y))
            cell.add_content(Object.WUMPUS)
        elif char == 'P':
            cell.add_content(Object.PIT)
        elif char == 'A':
            self.agent_position = (x, y)
            cell.add_content(Object.AGENT)
        elif char == 'G':
            self.gold_positions.append((x, y))
            cell.add_content(Object.GOLD)
        elif char == 'P_G':
            cell.add_content(Object.POISONOUS_GAS)
        elif char == 'H_P':
            cell.add_content(Object.HEALING_POTIONS)
        else:
            raise ValueError(f"Invalid character: {char}")
    
    def _add_perceptions(self):
        for y in range(self.size):
            for x in range(self.size):
                cell = self.grid[y][x]
                if cell.has_content(Object.WUMPUS):
                    self._add_perception_around(x, y, Object.STENCH)
                if cell.has_content(Object.PIT):
                    self._add_perception_around(x, y, Object.BREEZE)
                if cell.has_content(Object.POISONOUS_GAS):
                    self._add_perception_around(x, y, Object.WHIFF)
                if cell.has_content(Object.HEALING_POTIONS):
                    self._add_perception_around(x, y, Object.GLOW)
    
    def _add_perception_around(self, x: int, y: int, perception: Object):
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < self.size and 0 <= new_y < self.size:
                self.grid[new_y][new_x].add_content(perception)
    
    def get_cell(self, x: int, y: int) -> Cell:
        return self.grid[y][x]
    
    def is_valid_position(self, x: int, y: int) -> bool:
        return 0 <= x < self.size and 0 <= y < self.size