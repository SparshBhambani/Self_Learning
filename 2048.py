import os
import pygame
import sys
import random

pygame.init()
pygame.mixer.init() 

SIZE = 4
WIDTH = 500  
HEIGHT = 600 
TILE_SIZE = 110 
GRID_PADDING = 10  
BACKGROUND_COLOR = (187, 173, 160)
GRID_COLOR = (205, 193, 180)
TEXT_COLOR = (119, 110, 101)
TILE_COLORS = {
    0: (205, 193, 180),
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
    4096: (60, 58, 50)
}

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048")
font = pygame.font.Font(None, 40)

def load_tile_image(value):
    try:
        return pygame.transform.scale(
            pygame.image.load(f"/Users/sparsh/Desktop/2048/{value}.png"), (TILE_SIZE - GRID_PADDING, TILE_SIZE - GRID_PADDING)
        )
    except pygame.error as e:
        print(f"Error loading image for tile {value}: {e}")
        return None

tile_images = {value: load_tile_image(value) for value in [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]}

game_over_image = pygame.image.load("/Users/sparsh/Desktop/2048/game_over.png")
rematch_image = pygame.image.load("/Users/sparsh/Desktop/2048/rematch.png")

game_over_image = pygame.transform.scale(game_over_image, (300, 100))
rematch_image = pygame.transform.scale(rematch_image, (150, 50))

player_sprite_image = pygame.image.load("/Users/sparsh/Desktop/2048/player_sprite.png")
player_sprite_image = pygame.transform.scale(player_sprite_image, (50, 50))

game_over_music = "/Users/sparsh/Desktop/2048/pokemon.mp3"

class RematchSprite(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = rematch_image
        self.rect = self.image.get_rect()
        self.rect.topleft = (175, 500)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

rematch_sprite = RematchSprite()

class PlayerSprite(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_sprite_image
        self.rect = self.image.get_rect()
        self.rect.topleft = (WIDTH // 2 - self.rect.width // 2, HEIGHT // 2)

    def update(self, keys):
        if keys[pygame.K_w] and self.rect.top > 0:
            self.rect.y -= 5
        if keys[pygame.K_s] and self.rect.bottom < HEIGHT:
            self.rect.y += 5
        if keys[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= 5
        if keys[pygame.K_d] and self.rect.right < WIDTH:
            self.rect.x += 5

player_sprite = PlayerSprite()

score = 0

def init_grid():
    grid = [[0] * SIZE for _ in range(SIZE)]
    add_random_tile(grid)
    add_random_tile(grid)
    return grid

def add_random_tile(grid):
    empty_tiles = [(r, c) for r in range(SIZE) for c in range(SIZE) if grid[r][c] == 0]
    if empty_tiles:
        r, c = random.choice(empty_tiles)
        grid[r][c] = 2 if random.random() < 0.9 else 4

def compress(row):
    new_row = [tile for tile in row if tile != 0]
    new_row += [0] * (SIZE - len(new_row))
    return new_row

def merge(row):
    global score
    for i in range(SIZE - 1):
        if row[i] == row[i + 1] and row[i] != 0:
            row[i] *= 2
            row[i + 1] = 0
            score += row[i]
    return row

def move_left(grid):
    new_grid = []
    for row in grid:
        compressed_row = compress(row)
        merged_row = merge(compressed_row)
        final_row = compress(merged_row)
        new_grid.append(final_row)
    return new_grid

def rotate_grid_clockwise(grid):
    return [list(row) for row in zip(*grid[::-1])]

def rotate_grid_counterclockwise(grid):
    return [list(row) for row in zip(*grid)][::-1]

def move(grid, direction):
    if direction == 'left':
        return move_left(grid)
    elif direction == 'right':
        return rotate_grid_clockwise(rotate_grid_clockwise(move_left(rotate_grid_clockwise(rotate_grid_clockwise(grid)))))
    elif direction == 'up':
        return rotate_grid_clockwise(move_left(rotate_grid_counterclockwise(grid)))
    elif direction == 'down':
        return rotate_grid_counterclockwise(move_left(rotate_grid_clockwise(grid)))

def is_game_over(grid):
    if any(0 in row for row in grid):
        return False
    for row in grid:
        for i in range(SIZE - 1):
            if row[i] == row[i + 1]:
                return False
    for col in range(SIZE):
        for row in range(SIZE - 1):
            if grid[row][col] == grid[row + 1][col]:
                return False
    return True

def draw_grid(screen, grid):
    screen.fill(BACKGROUND_COLOR)
    for r in range(SIZE):
        for c in range(SIZE):
            rect = pygame.Rect(c * TILE_SIZE + GRID_PADDING, r * TILE_SIZE + GRID_PADDING, TILE_SIZE - GRID_PADDING, TILE_SIZE - GRID_PADDING)
            pygame.draw.rect(screen, GRID_COLOR, rect)
            value = grid[r][c]
            if value in tile_images and tile_images[value] is not None:
                screen.blit(tile_images[value], (c * TILE_SIZE + GRID_PADDING, r * TILE_SIZE + GRID_PADDING))
            else:
                pygame.draw.rect(screen, TILE_COLORS.get(value, TILE_COLORS[0]), rect)

def draw_score(screen, score):
    score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
    screen.blit(score_text, (10, HEIGHT - 70))

def show_game_over(screen):
    pygame.mixer.music.load(game_over_music)
    pygame.mixer.music.play(-1)  # Play the game over music in a loop
    
    game_over_text_rect = game_over_image.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
    screen.blit(game_over_image, game_over_text_rect)

    rematch_sprite.draw(screen)
    player_sprite.rect.topleft = (WIDTH // 2 - player_sprite.rect.width // 2, HEIGHT // 2)
    screen.blit(player_sprite.image, player_sprite.rect)
    
    pygame.display.flip()

    while True:
        keys = pygame.key.get_pressed()
        player_sprite.update(keys)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if rematch_sprite.is_clicked(event.pos):
                    pygame.mixer.music.stop()
                    return

        screen.fill(BACKGROUND_COLOR)
        draw_grid(screen, grid)
        screen.blit(game_over_image, game_over_text_rect)
        rematch_sprite.draw(screen)
        screen.blit(player_sprite.image, player_sprite.rect)
        pygame.display.flip()

def show_intro_screen(screen):
    intro_font = pygame.font.Font(None, 36)
    intro_text = [
        "Welcome to 2048!",
        "Combine the tiles to get the 2048 tile!",
        "Use arrow keys to move tiles:",
        "Tiles with the same number merge into one!",
        "2 + 2 = 4",
        "4 + 4 = 8",
        "Press ENTER to start the game."
    ]
    screen.fill(BACKGROUND_COLOR)

    for i, line in enumerate(intro_text):
        text_surface = intro_font.render(line, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 4 - 100 + i * 40))
        screen.blit(text_surface, text_rect)

    example_tiles = [
        (2, 2, 4),
        (4, 4, 8)
    ]

    for i, (tile1, tile2, result) in enumerate(example_tiles):
        x_offset = 70
        y_offset = HEIGHT // 2 + 50 + i * 70

        if tile1 in tile_images:
            screen.blit(tile_images[tile1], (WIDTH // 2 - x_offset - TILE_SIZE, y_offset))
        if tile2 in tile_images:
            screen.blit(tile_images[tile2], (WIDTH // 2 - TILE_SIZE // 2, y_offset))
        if result in tile_images:
            screen.blit(tile_images[result], (WIDTH // 2 + x_offset, y_offset))

        plus_text = intro_font.render("+", True, TEXT_COLOR)
        equal_text = intro_font.render("=", True, TEXT_COLOR)
        screen.blit(plus_text, (WIDTH // 2 - TILE_SIZE // 2 - 20, y_offset + TILE_SIZE // 2 - 20))
        screen.blit(equal_text, (WIDTH // 2 + TILE_SIZE // 2, y_offset + TILE_SIZE // 2 - 20))

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return

def main():
    global grid, score
    grid = init_grid()
    clock = pygame.time.Clock()
    game_over = False

    show_intro_screen(screen)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if not game_over:
                    original_grid = [row[:] for row in grid] 
                    if event.key == pygame.K_LEFT:
                        grid = move(grid, 'left')
                    elif event.key == pygame.K_RIGHT:
                        grid = move(grid, 'right')
                    elif event.key == pygame.K_UP:
                        grid = move(grid, 'up')
                    elif event.key == pygame.K_DOWN:
                        grid = move(grid, 'down')
                    
                    if grid != original_grid:  
                        add_random_tile(grid)

        if not game_over and is_game_over(grid):
            game_over = True
            show_game_over(screen)
            grid = init_grid()
            score = 0 
            game_over = False

        screen.fill(BACKGROUND_COLOR)
        draw_grid(screen, grid)
        draw_score(screen, score)
        pygame.display.flip()

        clock.tick(30)

if __name__ == "__main__":
    main()
