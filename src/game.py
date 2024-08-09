import pygame
from program import *
from agent import Agent
from algorithm import AgentBrain

class Button:
    def __init__(self, x, y, width, height, text, color, text_color, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = font

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(CAPTION)
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.Font(FONT_TITLE, TITLE_SIZE)
        self.button_font = pygame.font.Font(FONT_TEXT, BUTTON_SIZE)
        self.text_font = pygame.font.Font(FONT_TEXT, TEXT_SIZE)
        self.reset_game()

    def reset_game(self):
        self.map_type = 0
        self.map = None
        self.agent = None
        self.agent_brain = None

    def main_menu(self):
        title = self.title_font.render(CAPTION, True, BLUE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 75))

        play_button = Button(
            SCREEN_WIDTH// 2 - 150,
            175,
            300,
            100,
            "PLAY",
            BLUE,
            WHITE,
            self.button_font,
        )

        settings_button = Button(
            SCREEN_WIDTH // 2 - 150,
            325,
            300,
            100,
            "SETTINGS",
            BLUE,
            WHITE,
            self.button_font,
        )

        quit_button = Button(
            SCREEN_WIDTH // 2 - 150,
            475,
            300,
            100,
            "QUIT",
            RED,
            WHITE,
            self.button_font,
        )

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "QUIT"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_button.is_clicked(event.pos):
                        return "PLAY"
                    if settings_button.is_clicked(event.pos):
                        return "SETTINGS"
                    if quit_button.is_clicked(event.pos):
                        return "QUIT"
            
            self.screen.fill(WHITE)
            self.screen.blit(title, title_rect)
            play_button.draw(self.screen)
            settings_button.draw(self.screen)
            quit_button.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(FPS)
    
    def settings_menu(self):
        title = self.title_font.render("- SETTINGS -", True, BLUE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 75))

        map_button = Button(
            SCREEN_WIDTH // 2 - 150,
            200,
            300,
            100,
            "MAP",
            BLUE,
            WHITE,
            self.button_font,
        )

        back_button = Button(
            SCREEN_WIDTH // 2 - 150,
            350,
            300,
            100,
            "BACK",
            RED,
            WHITE,
            self.button_font,
        )

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "QUIT"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if map_button.is_clicked(event.pos):
                        self.map_type = (self.map_type + 1) % len(MAP_LIST)
                    if back_button.is_clicked(event.pos):
                        return "BACK"
        
            map_button.text = f"MAP: {self.map_type + 1}"   
            
            self.screen.fill(WHITE)
            self.screen.blit(title, title_rect)
            map_button.draw(self.screen)
            back_button.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(FPS)

    def play_game(self):
        # Initialize map and agent
        self.map = Map()
        self.map.load_map(MAP_LIST[self.map_type])
        self.agent = Agent(self.map)
        self.agent_brain = AgentBrain(self.map)
        
        first_cell = self.map.get_cell(*self.map.agent_position)
        first_cell.discover()
        first_cell.mark_visited()

        # Calculate cell size
        cell_size = SCREEN_HEIGHT // self.map.size
        
        # Load images
        images = self.load_images(cell_size)
        
        game_over = False
        while not game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    return "QUIT"

            if not game_over:
                # Get agent's perceptions
                last_position = self.map.agent_position
                current_cell = self.map.get_cell(*self.map.agent_position)
                perceptions = self.agent.perceive(current_cell)
                
                # Agent makes a decision
                action = self.agent.act(perceptions)
                self.write_output(f"output/output{self.map_type + 1}.txt", action, last_position, self.agent)

                # Update game state based on action
                if action == Action.MOVE_FORWARD:
                    new_cell = self.map.get_cell(*self.map.agent_position)
                        
                    # Check for game over conditions
                    if Object.WUMPUS in new_cell.contents or Object.PIT in new_cell.contents:
                        self.agent.die()
                        game_over = True
                    elif Object.GOLD in new_cell.contents:
                        self.agent.brain.has_gold = True
                        new_cell.remove_content(Object.GOLD)
                    elif Object.POISONOUS_GAS in new_cell.contents:
                        self.agent.health = max(0, self.agent.health - 25)
                        if self.agent.health == 0:
                            self.agent.die()
                            game_over = True
                    elif Object.HEALING_POTIONS in new_cell.contents:
                        pass

                elif action in [Action.TURN_LEFT, Action.TURN_RIGHT]:
                    self.agent.update_position(action)

                elif action == Action.SHOOT:
                    pass
                
                elif action == Action.GRAB_G:
                    current_cell.remove_content(Object.GOLD)
                    self.agent.brain.has_gold = True

                elif action == Action.GRAB_HP:
                    self.agent.health = min(100, self.agent.health + 25)

                # Check if agent wants to climb out
                if self.map.agent_position == (9, 0) and self.agent.brain.has_gold:
                    action = Action.CLIMB
                    game_over = True

            self.draw_game(images, cell_size, self.agent, self.map)
            pygame.display.flip()
            self.clock.tick(FPS)

        # Game over, display final score
        self.write_output(f"output/output{self.map_type + 1}.txt", action, self.map.agent_position, self.agent, game_over=True)
        self.display_game_over()

    def load_images(self, cell_size):
        images = {
            'undiscovered': pygame.image.load(IMG_UNDISCOVERED_CELL).convert_alpha(),
            'discovered': pygame.image.load(IMG_DISCOVERED_CELL).convert_alpha(),
            'pit': pygame.image.load(IMG_PIT).convert_alpha(),
            'gold': pygame.image.load(IMG_GOLD).convert_alpha(),
            'wumpus': pygame.image.load(IMG_WUMPUS).convert_alpha(),
            'poisonous_gas': pygame.image.load(IMG_POISONOUS_GAS).convert_alpha(),
            'healing_potions': pygame.image.load(IMG_HEALING_POTIONS).convert_alpha(),
            'breeze': pygame.image.load(IMG_BREEZE).convert_alpha(),
            'glow': pygame.image.load(IMG_GLOW).convert_alpha(),
            'stench': pygame.image.load(IMG_STENCH).convert_alpha(),
            'whiff': pygame.image.load(IMG_WHIFF).convert_alpha(),
            'scream': pygame.image.load(IMG_SCREAM).convert_alpha()
        }
        
        # Resize images
        for key in images:
            images[key] = pygame.transform.scale(images[key], (cell_size, cell_size))
        
        return images

    def draw_game(self, images, cell_size, agent, map):
        self.screen.fill(WHITE)

        # Draw grid
        for row in range(self.map.size):
            for col in range(self.map.size):
                cell = self.map.grid[row][col]
                x = col * cell_size
                y = row * cell_size

                # Draw base cell
                if cell.cell_type == CellType.UNDISCOVERED:
                    self.screen.blit(images['undiscovered'], (x, y))
                else:
                    self.screen.blit(images['discovered'], (x, y))
                
                    # Draw cell contents
                    if Object.PIT in cell.contents:
                        self.screen.blit(images['pit'], (x, y))
                    elif Object.GOLD in cell.contents:
                        self.screen.blit(images['gold'], (x, y))
                    elif Object.WUMPUS in cell.contents:
                        self.screen.blit(images['wumpus'], (x, y))
                    elif Object.POISONOUS_GAS in cell.contents:
                        self.screen.blit(images['poisonous_gas'], (x, y))
                    elif Object.HEALING_POTIONS in cell.contents:
                        self.screen.blit(images['healing_potions'], (x, y))
                    
                    # Draw perceptions
                    else:
                        if Object.BREEZE in cell.contents:
                            self.screen.blit(images['breeze'], (x, y))
                        if Object.GLOW in cell.contents:
                            self.screen.blit(images['glow'], (x, y))
                        if Object.STENCH in cell.contents:
                            self.screen.blit(images['stench'], (x, y))
                        if Object.WHIFF in cell.contents:
                            self.screen.blit(images['whiff'], (x, y))
                        if Object.SCREAM in cell.contents:
                            self.screen.blit(images['scream'], (x, y))
                
                # Draw agent
                if map.agent_position == (row, col):
                    self.screen.blit(agent.image, (x, y))

        # Draw grid lines
        for i in range(self.map.size):
            pygame.draw.line(self.screen, BLACK, (0, i * cell_size), (SCREEN_HEIGHT, i * cell_size))
            pygame.draw.line(self.screen, BLACK, (i * cell_size, 0), (i * cell_size, SCREEN_HEIGHT))
        
        # Draw information board
        self.draw_info_board()

    def draw_info_board(self):
        info_surface = pygame.Surface((SCREEN_WIDTH - SCREEN_HEIGHT, SCREEN_HEIGHT))
        info_surface.fill(LIGHT_GRAY)
        
        # Add game information
        title = self.text_font.render("GAME INFO", True, BLACK)
        info_surface.blit(title, ((SCREEN_WIDTH - SCREEN_HEIGHT - title.get_width()) // 2, 50))
        map_info = self.text_font.render(f"MAP: {self.map_type + 1}", True, BLACK)
        info_surface.blit(map_info, ((SCREEN_WIDTH - SCREEN_HEIGHT - map_info.get_width()) // 2, 150))
        score_info = self.text_font.render(f"SCORE: {self.agent.score}", True, BLACK)
        info_surface.blit(score_info, ((SCREEN_WIDTH - SCREEN_HEIGHT - score_info.get_width()) // 2, 200))
        health_info = self.text_font.render(f"HEALTH: {self.agent.health}", True, BLACK)
        info_surface.blit(health_info, ((SCREEN_WIDTH - SCREEN_HEIGHT - health_info.get_width()) // 2, 250))
        
        self.screen.blit(info_surface, (SCREEN_HEIGHT, 0))

    def write_output(self, output_file: str, action: Action, position: Tuple[int, int], agent: Agent, game_over: bool = False):
        x, y = position
        transformed_position = (self.map.size - x, y + 1)
        
        action_str = {
            Action.MOVE_FORWARD: "Move forward",
            Action.TURN_LEFT: "Turn left",
            Action.TURN_RIGHT: "Turn right",
            Action.SHOOT: "Shoot",
            Action.GRAB_G: "Grab gold",
            Action.GRAB_HP: "Grab health potion",
            Action.CLIMB: "Climb"
        }.get(action, "Unknown action")

        with open(output_file, "a") as f:
            f.write(f"{transformed_position}: {action_str}\n")

        # If the action is CLIMB, we assume the game has ended and we write the final score and health
        if game_over and action == Action.CLIMB:
            with open(output_file, "a") as f:
                f.write("------------------------------\n")
                f.write(f"SCORE: {agent.score}\n")
                f.write(f"HEALTH: {agent.health}\n")
        elif game_over:
            with open(output_file, "a") as f:
                f.write(f"Agent die in Wumpus World\n")
                f.write("------------------------------\n")
                f.write(f"SCORE: {agent.score}\n")
                f.write(f"HEALTH: {agent.health}\n")

    def display_game_over(self):
        game_over_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        game_over_surface.set_alpha(200)
        game_over_surface.fill(BLACK)
        self.screen.blit(game_over_surface, (0, 0))

        game_over_text = self.title_font.render("FINISH!", True, WHITE)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, game_over_rect)

        score_text = self.text_font.render(f"Final Score: {self.agent.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(score_text, score_rect)

        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    return "QUIT"
                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                    waiting = False

    def run(self):
        while True:
            action = self.main_menu()
            if action == "QUIT":
                break
            elif action == "PLAY":
                self.play_game()
            elif action == "SETTINGS":
                self.settings_menu()

        pygame.quit()