from program import *


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
        self.map_size = None
        self.map = None

    def main_menu(self):
        title = self.title_font.render(CAPTION, True, BLUE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 75))

        show_button = Button(
            SCREEN_WIDTH// 2 - 150,
            175,
            300,
            100,
            "SHOW",
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
                    if show_button.is_clicked(event.pos):
                        return "SHOW"
                    if settings_button.is_clicked(event.pos):
                        return "SETTINGS"
                    if quit_button.is_clicked(event.pos):
                        return "QUIT"
            
            self.screen.fill(WHITE)
            self.screen.blit(title, title_rect)
            show_button.draw(self.screen)
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

    def show_game(self):
        # Initialize map
        self.map = Map()
        self.map.load_map(MAP_LIST[self.map_type])
        
        # Calculate cell size
        cell_size = SCREEN_HEIGHT // self.map.size
        
        # Load images
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
            'scream': pygame.image.load(IMG_SCREAM).convert_alpha(),
            'agent': pygame.image.load(IMG_AGENT_UP).convert_alpha()
        }
        
        # Resize images
        for key in images:
            images[key] = pygame.transform.scale(images[key], (cell_size, cell_size))
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    return "QUIT"

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
                                self.screen.blit(pygame.transform.scale(images['breeze'], (cell_size, cell_size)), (x, y))
                            if Object.GLOW in cell.contents:
                                self.screen.blit(pygame.transform.scale(images['glow'], (cell_size, cell_size)), (x, y))
                            if Object.STENCH in cell.contents:
                                self.screen.blit(pygame.transform.scale(images['stench'], (cell_size, cell_size)), (x, y))
                            if Object.WHIFF in cell.contents:
                                self.screen.blit(pygame.transform.scale(images['whiff'], (cell_size, cell_size)), (x, y))
                            if Object.SCREAM in cell.contents:
                                self.screen.blit(images['scream'], (x, y))
                    
                    # Draw agent
                    if (col, row) == self.map.agent_position:
                        self.screen.blit(images['agent'], (x, y))

            # Draw grid line
            for i in range(self.map.size):
                pygame.draw.line(self.screen, BLACK, (0, i * cell_size), (SCREEN_HEIGHT, i * cell_size))
                pygame.draw.line(self.screen, BLACK, (i * cell_size, 0), (i * cell_size, SCREEN_HEIGHT))
            
            # Draw information board
            info_surface = pygame.Surface((SCREEN_WIDTH - SCREEN_HEIGHT, SCREEN_HEIGHT))
            info_surface.fill(LIGHT_GRAY)
            
            # Add game information
            title = self.text_font.render("GAME INFO", True, BLACK)
            info_surface.blit(title, ((SCREEN_WIDTH - SCREEN_HEIGHT - title.get_width()) // 2, 50))
            map_info = self.text_font.render(f"MAP: {self.map_type + 1}", True, BLACK)
            info_surface.blit(map_info, ((SCREEN_WIDTH - SCREEN_HEIGHT - map_info.get_width()) // 2, 150))
            # score_info = self.text_font.render(f"SCORE: {self.map.score}", True, BLACK)
            # info_surface.blit(score_info, ((SCREEN_WIDTH - SCREEN_HEIGHT - score_info.get_width()) // 2, 200))
            
            self.screen.blit(info_surface, (SCREEN_HEIGHT, 0))

            pygame.display.flip()
            self.clock.tick(FPS)    
    
    def run(self):
        while True:
            action = self.main_menu()
            if action == "QUIT":
                break
            elif action == "SHOW":
                self.show_game()
            elif action == "SETTINGS":
                self.settings_menu()