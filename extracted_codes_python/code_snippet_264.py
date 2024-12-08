import pygame
from player import Player
from food import Food
from trap import Trap

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (169, 169, 169)
RED = (255, 0, 0)

class Game:
    def __init__(self, width, height, screen):
        self.width = width
        self.height = height
        self.screen = screen
        self.player = Player(width, height)
        self.font = pygame.font.Font(None, 36)
        self.selected_difficulty_text = None
        self.selected_difficulty_text = self.font.render("", True, BLACK)
        self.game_over = False

        button_width = 150
        button_height = 50
        spacing = 20 
        total_width = button_width * 2 + spacing
        keyboard_button_x = (width - total_width) // 2
        mouse_button_x = keyboard_button_x + button_width + spacing

        self.keyboard_button = pygame.Rect(keyboard_button_x, height // 3 - 25, button_width, button_height)
        self.mouse_button = pygame.Rect(mouse_button_x, height // 3 - 25, button_width, button_height)
        self.keyboard_button_text = self.font.render('Keyboard', True, (255, 255, 255))
        self.mouse_button_text = self.font.render('Mouse', True, (255, 255, 255))

        self.keyboard_button_text_rect = self.keyboard_button_text.get_rect(center=self.keyboard_button.center)
        self.mouse_button_text_rect = self.mouse_button_text.get_rect(center=self.mouse_button.center)
        self.control_mode = 'keyboard'
        
        self.easy_button = pygame.Rect(width // 4 - 75, height // 2 - 25, 150, 50)
        self.medium_button = pygame.Rect(width // 2 - 75, height // 2 - 25, 150, 50)
        self.hard_button = pygame.Rect(3 * width // 4 - 75, height // 2 - 25, 150, 50)

        self.easy_button_text = self.font.render('Easy', True, (255, 255, 255))
        self.medium_button_text = self.font.render('Medium', True, (255, 255, 255))
        self.hard_button_text = self.font.render('Hard', True, (255, 255, 255))

        self.easy_button_text_rect = self.easy_button_text.get_rect(center=self.easy_button.center)
        self.medium_button_text_rect = self.medium_button_text.get_rect(center=self.medium_button.center)
        self.hard_button_text_rect = self.hard_button_text.get_rect(center=self.hard_button.center)

        self.selected_difficulty = None
        
        self.EASY_COLOR = GRAY
        self.MEDIUM_COLOR = GRAY
        self.HARD_COLOR = GRAY
        
        self.timer = 60
        self.timer_text = self.font.render(str(self.timer), True, BLACK)
        self.timer_text_rect = self.timer_text.get_rect(midtop=(self.width // 2, 90))
        
        self.food = None
        self.trap = None

    def run(self):
        clock = pygame.time.Clock()
        game_run = False
        
        selecting_difficulty = True
        self.player_moved = False

        while selecting_difficulty:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                self.select_difficulty(event)
                
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                pygame.quit()
                quit()
            
            pygame.draw.rect(self.screen, self.EASY_COLOR, self.easy_button)
            self.screen.blit(self.easy_button_text, self.easy_button_text_rect)
            pygame.draw.rect(self.screen, self.MEDIUM_COLOR, self.medium_button)
            self.screen.blit(self.medium_button_text, self.medium_button_text_rect)
            pygame.draw.rect(self.screen, self.HARD_COLOR, self.hard_button)
            self.screen.blit(self.hard_button_text, self.hard_button_text_rect)
            pygame.display.flip()
            
            if self.selected_difficulty:
                self.food = Food(self.width, self.height, self.selected_difficulty)
                self.trap = Trap(self.width, self.height, self.selected_difficulty)
                selecting_difficulty = False

        while not game_run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                
                keys = pygame.key.get_pressed()
                if keys[pygame.K_a]:
                    pygame.quit()
                    quit()
                
                elif event.type == pygame.MOUSEBUTTONDOWN and self.keyboard_button.collidepoint(event.pos):
                    game_run = True
                elif event.type == pygame.MOUSEBUTTONDOWN and self.mouse_button.collidepoint(event.pos):
                    if self.control_mode == 'keyboard':
                        self.control_mode = 'mouse'
                    else:
                        self.control_mode = 'keyboard'
                    game_run = not game_run

            pygame.draw.rect(self.screen, (0, 128, 255), self.keyboard_button)
            self.screen.blit(self.keyboard_button_text, self.keyboard_button_text_rect)
            pygame.draw.rect(self.screen, (0, 128, 255), self.mouse_button)
            self.screen.blit(self.mouse_button_text, self.mouse_button_text_rect)
            pygame.display.flip()

        while game_run:
            elapsed_time = clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_run = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_run = False
                        self.reset_game(self.width, self.height)
                        self.run()
                        
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                game_run = False
                
            if self.control_mode == 'keyboard':
                self.player.handle_key_event()
            elif self.control_mode == 'mouse':
                self.player.handle_mouse_event()
                
            if self.check_collision(self.player, self.food):
                self.food.respawn(self.width, self.height)
                
            if self.check_trap_collision(self.player, self.trap):
                self.trap.respawn(self.width, self.height)
            
            self.player.move(elapsed_time)
            self.update_timer(elapsed_time)
            self.player.teleport(self.width, self.height)

            self.screen.fill(WHITE)
            self.player.render(self.screen)
            self.food.render(self.screen)
            self.trap.render(self.screen)
            self.update_game_info()
            self.screen.blit(self.timer_text, self.timer_text_rect)
            pygame.display.flip()
            
            if self.game_over:
                self.game_over_screen()

        pygame.quit()
        quit()
        
    def select_difficulty(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.easy_button.collidepoint(event.pos):
                self.selected_difficulty = 'easy'
                self.EASY_COLOR = RED
                self.MEDIUM_COLOR = GRAY
                self.HARD_COLOR = GRAY
            elif self.medium_button.collidepoint(event.pos):
                self.selected_difficulty = 'medium'
                self.EASY_COLOR = GRAY
                self.MEDIUM_COLOR = RED
                self.HARD_COLOR = GRAY
            elif self.hard_button.collidepoint(event.pos):
                self.selected_difficulty = 'hard'
                self.EASY_COLOR = GRAY
                self.MEDIUM_COLOR = GRAY
                self.HARD_COLOR = RED
    
    def update_game_info(self):
        info_text = f"Score: {self.player.score}   Speed: {self.player.speed}   Size: {self.player.size}   Difficulty: {self.selected_difficulty}"
        info_surface = self.font.render(info_text, True, BLACK)
        info_rect = info_surface.get_rect(midtop=(self.width // 2, 10))
        self.screen.blit(info_surface, info_rect)
        self.screen.blit(self.selected_difficulty_text, self.selected_difficulty_text.get_rect(midtop=(self.width // 2, 50)))
    
    def update_timer(self, elapsed_time):
        self.timer -= elapsed_time
        if self.timer <= 0:
            self.end_game()

        self.timer_text = self.font.render(str(round(self.timer)), True, BLACK)
        
    def end_game(self):
        self.game_over = True

    def reset_game(self, width, height):
        self.timer = 60
        self.timer_text = self.font.render(str(self.timer), True, BLACK)
        self.player.reset(width, height)
        self.selected_difficulty = None
        self.game_over = False
        self.screen.fill(WHITE)
        self.EASY_COLOR = GRAY
        self.MEDIUM_COLOR = GRAY
        self.HARD_COLOR = GRAY
        pygame.display.flip()
        
    def game_over_screen(self):
        while self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.menu_button.collidepoint(event.pos):
                        self.reset_game(self.width, self.height)
                        self.run()

            self.screen.fill(WHITE)
            game_over_text = self.font.render("Game Over", True, BLACK)
            game_over_rect = game_over_text.get_rect(center=(self.width // 2, self.height // 3))
            self.screen.blit(game_over_text, game_over_rect)

            score_text = self.font.render(f"Score: {self.player.score}", True, BLACK)
            score_rect = score_text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(score_text, score_rect)

            self.menu_button = pygame.Rect(self.width // 4, 2 * self.height // 3, self.width // 2, 50)
            pygame.draw.rect(self.screen, (0, 128, 255), self.menu_button)
            menu_text = self.font.render('Retour au menu principal', True, WHITE)
            menu_rect = menu_text.get_rect(center=self.menu_button.center)
            self.screen.blit(menu_text, menu_rect)

            pygame.display.flip()
            
    def check_collision(self, player, food):
        if self.check_trap_collision(player, self.trap):
            return True
        for food_position in food.positions:
            if (
                self.player.position[0] < food_position[0] + self.food.size and
                self.player.position[0] + self.player.size > food_position[0] and
                self.player.position[1] < food_position[1] + self.food.size and
                self.player.position[1] + self.player.size > food_position[1]
            ):
                self.player.score += 1
                self.player.speed += 5
                self.player.speed = min(player.speed, 500)
                self.player.size += 2
                self.player.size = min(player.size, 200)
                return True
        return False
    
    def get_difficulty_multiplier(self):
        if self.selected_difficulty == 'easy':
            return 2
        elif self.selected_difficulty == 'medium':
            return 3
        elif self.selected_difficulty == 'hard':
            return 4
        else:
            return 1
    
    def check_trap_collision(self, player, trap):
        for trap_position in trap.positions:
            if (
                self.player.position[0] < trap_position[0] + self.trap.radius and
                self.player.position[0] + self.player.size > trap_position[0] and
                self.player.position[1] < trap_position[1] + self.trap.radius and
                self.player.position[1] + self.player.size > trap_position[1]
            ):
                if self.player.size <= self.trap.radius:
                    return False
                else:
                    self.player.size /= self.get_difficulty_multiplier()
                    self.player.speed /= self.get_difficulty_multiplier()
                    self.trap.respawn(self.width, self.height)
                    return True
        return False
