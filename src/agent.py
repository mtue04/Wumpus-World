from utils import *
from program import Map
from algorithm import AgentBrain

class Agent:
    def __init__(self, map):
        self.map = map
        self.brain = AgentBrain(self.map)

        self.image = pygame.image.load(IMG_AGENT_UP).convert_alpha()
        self.image_list = self.load_images()
        
        self.is_alive = True
        self.score = 0
        self.health = 100
    
    def load_images(self):
        return {
            Direction.UP: pygame.image.load(IMG_AGENT_UP).convert_alpha(),
            Direction.DOWN: pygame.image.load(IMG_AGENT_DOWN).convert_alpha(),
            Direction.LEFT: pygame.image.load(IMG_AGENT_LEFT).convert_alpha(),
            Direction.RIGHT: pygame.image.load(IMG_AGENT_RIGHT).convert_alpha()
        }

    def perceive(self, cell):
        perceptions = set()
        for content in cell.contents:
            if content in [Object.STENCH, Object.BREEZE, Object.GLOW, Object.WHIFF]:
                perceptions.add(content)

        return perceptions

    def act(self, perceptions):
        if not self.is_alive:
            return None

        action = self.brain.make_decision(perceptions)

        if action == Action.MOVE_FORWARD:
            print("Moving forward")
            self.score -= 10
            self.move_forward()
        elif action == Action.TURN_LEFT:
            print("Turning left")
            self.score -= 10
            self.turn_left()
        elif action == Action.TURN_RIGHT:
            print("Turning right")
            self.score -= 10
            self.turn_right()
        elif action == Action.SHOOT:
            print("Shooting")
            self.score -= 100
            self.shoot()
        elif action == Action.GRAB_G:
            print("Grabbing gold")
            self.score += 5000
            self.grab()
        elif action == Action.GRAB_HP:
            print("Grabbing health potion")
            self.grab()
        elif action == Action.CLIMB:
            print("Climbing")
            self.score += 10
            self.climb()
        
        return action

    def move_forward(self):
        new_position = self.get_forward_position()
        if self.is_valid_position(new_position):
            self.map.agent_position = new_position
            new_cell = self.map.get_cell(*new_position)
            new_cell.discover()
            new_cell.mark_visited()

    def turn_left(self):
        pass
    
    def turn_right(self):
        pass
    
    def shoot(self):
        target_position = self.get_forward_position()
        if self.map.is_valid_position(*target_position):
            target_cell = self.map.get_cell(*target_position)
            if Object.WUMPUS in target_cell.contents:
                # Remove Wumpus from the cell
                target_cell.contents.remove(Object.WUMPUS)
                
                # Remove Stench from adjacent cells
                adjacent_positions = self.map.get_adjacent_cells(*target_position)
                for adj_x, adj_y in adjacent_positions:
                    adj_cell = self.map.get_cell(adj_x, adj_y)
                    if Object.STENCH in adj_cell.contents:
                        adj_cell.contents.remove(Object.STENCH)
                
                # Update brain's knowledge
                self.brain.process_successful_shot(target_position)
                
                print("Wumpus killed!")
            else:
                print("Missed! Try again!")
                self.rotate_and_shoot()

    def rotate_and_shoot(self):
        # Rotate to the right
        if self.brain.direction == Direction.UP:
            self.brain.direction = Direction.RIGHT
        elif self.brain.direction == Direction.RIGHT:
            self.brain.direction = Direction.DOWN
        elif self.brain.direction == Direction.DOWN:
            self.brain.direction = Direction.LEFT
        else:  # LEFT
            self.brain.direction = Direction.UP
        
        # Shoot
        target_position = self.get_forward_position()
        if self.map.is_valid_position(*target_position):
            target_cell = self.map.get_cell(*target_position)
            if Object.WUMPUS in target_cell.contents:
                # Remove Wumpus from the cell
                target_cell.contents.remove(Object.WUMPUS)
                
                # Remove Stench from adjacent cells
                adjacent_positions = self.map.get_adjacent_cells(*target_position)
                for adj_x, adj_y in adjacent_positions:
                    adj_cell = self.map.get_cell(adj_x, adj_y)
                    if Object.STENCH in adj_cell.contents:
                        adj_cell.contents.remove(Object.STENCH)
                
                # Update brain's knowledge
                self.brain.process_successful_shot(target_position)
                
                print("Re-shooting! Wumpus killed!")
            else:
                print("Missed again!")
        
                # Rotate to the left
                if self.brain.direction == Direction.UP:
                    self.brain.direction = Direction.DOWN
                elif self.brain.direction == Direction.RIGHT:
                    self.brain.direction = Direction.LEFT
                elif self.brain.direction == Direction.DOWN:
                    self.brain.direction = Direction.UP
                else:  # LEFT
                    self.brain.direction = Direction.RIGHT
                
                # Shoot
                target_position = self.get_forward_position()
                if self.map.is_valid_position(*target_position):
                    target_cell = self.map.get_cell(*target_position)
                    if Object.WUMPUS in target_cell.contents:
                        # Remove Wumpus from the cell
                        target_cell.contents.remove(Object.WUMPUS)
                        
                        # Remove Stench from adjacent cells
                        adjacent_positions = self.map.get_adjacent_cells(*target_position)
                        for adj_x, adj_y in adjacent_positions:
                            adj_cell = self.map.get_cell(adj_x, adj_y)
                            if Object.STENCH in adj_cell.contents:
                                adj_cell.contents.remove(Object.STENCH)
                        
                        # Update brain's knowledge
                        self.brain.process_successful_shot(target_position)
                        
                        print("Re-shooting! Wumpus killed!")
        
        else:
            # Rotate to the left
            if self.brain.direction == Direction.UP:
                self.brain.direction = Direction.DOWN
            elif self.brain.direction == Direction.RIGHT:
                self.brain.direction = Direction.LEFT
            elif self.brain.direction == Direction.DOWN:
                self.brain.direction = Direction.UP
            else:  # LEFT
                self.brain.direction = Direction.RIGHT
                
            # Shoot
            target_position = self.get_forward_position()
            if self.map.is_valid_position(*target_position):
                target_cell = self.map.get_cell(*target_position)
                if Object.WUMPUS in target_cell.contents:
                    # Remove Wumpus from the cell
                    target_cell.contents.remove(Object.WUMPUS)
                    
                    # Remove Stench from adjacent cells
                    adjacent_positions = self.map.get_adjacent_cells(*target_position)
                    for adj_x, adj_y in adjacent_positions:
                        adj_cell = self.map.get_cell(adj_x, adj_y)
                        if Object.STENCH in adj_cell.contents:
                            adj_cell.contents.remove(Object.STENCH)
                    
                    # Update brain's knowledge
                    self.brain.process_successful_shot(target_position)
                    
                    print("Re-shooting! Wumpus killed!")

    def grab(self):
        x, y = self.map.agent_position
        cell = self.map.get_cell(x, y)

        if self.map.agent_position in self.map.gold_positions:
            self.brain.has_gold = True
            cell.remove_content(Object.GOLD)
            self.map.gold_positions.remove((x, y))
            self.brain.update_knowledge_after_grab(Object.GOLD, (x, y))
        
        elif self.map.agent_position in self.map.healing_positions:
            cell.remove_content(Object.HEALING_POTIONS)
            self.map.healing_positions.remove((x, y))
            self.brain.update_knowledge_after_grab(Object.HEALING_POTIONS, (x, y))

            # Remove GLOW from adjacent cells
            for adj_x, adj_y in self.map.get_adjacent_cells(x, y):
                adj_cell = self.map.get_cell(adj_x, adj_y)
                if Object.GLOW in adj_cell.contents:
                    adj_cell.remove_content(Object.GLOW)

    def get_forward_position(self):
        x, y = self.map.agent_position
        if self.brain.direction == Direction.UP:
            return (x - 1, y)
        elif self.brain.direction == Direction.RIGHT:
            return (x, y + 1)
        elif self.brain.direction == Direction.DOWN:
            return (x + 1, y)
        else:  # LEFT
            return (x, y - 1)
    
    def is_valid_position(self, position):
        x, y = position
        return 0 <= x < self.map.size and 0 <= y < self.map.size
    
    def die(self):
        self.is_alive = False
        self.score -= 10000

    def climb(self):
        if self.map.agent_position == (9, 0):
            return True
        return False

    def update_score(self, points):
        self.score += points

    def update_position(self, action):
        self.image = self.image_list[self.brain.direction]