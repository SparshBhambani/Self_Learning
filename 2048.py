import pygame
import sys
import random

pygame.init()
pygame.mixer.init()  # Initialize the mixer module

# Constants
SIZE = 4
WIDTH = 400
HEIGHT = 400
TILE_SIZE = WIDTH // SIZE
BACKGROUND_COLOR = (187, 173, 160)
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
}

# Initialize display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048")
font = pygame.font.Font(None, 40)
game_over_font = pygame.font.Font(None, 80)  # Font for Game Over text

# Load and play background music
pygame.mixer.music.load("background.mp3")  # Ensure you have a file named background.mp3 in your project directory
pygame.mixer.music.play(-1)  # Play the music in a loop

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
    for i in range(SIZE - 1):
        if row[i] == row[i + 1] and row[i] != 0:
            row[i] *= 2
            row[i + 1] = 0
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
    for r in range(SIZE):
        for c in range(SIZE):
            value = grid[r][c]
            color = TILE_COLORS.get(value, (60, 58, 50))
            pygame.draw.rect(screen, color, (c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            if value != 0:
                text = font.render(str(value), True, (0, 0, 0))
                text_rect = text.get_rect(center=(c * TILE_SIZE + TILE_SIZE / 2, r * TILE_SIZE + TILE_SIZE / 2))
                screen.blit(text, text_rect)

def show_game_over(screen):
    game_over_text = game_over_font.render("Game Over", True, (255, 0, 0))
    text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(game_over_text, text_rect)
    pygame.display.flip()

    # Wait for user to quit
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

def main():
    global grid
    grid = init_grid()
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                original_grid = [row[:] for row in grid]  # Create a copy of the grid for comparison
                if event.key == pygame.K_LEFT:
                    grid = move(grid, 'left')
                elif event.key == pygame.K_RIGHT:
                    grid = move(grid, 'right')
                elif event.key == pygame.K_UP:
                    grid = move(grid, 'up')
                elif event.key == pygame.K_DOWN:
                    grid = move(grid, 'down')
                
                if grid != original_grid:  # Add a new tile only if the grid changed
                    add_random_tile(grid)

        screen.fill(BACKGROUND_COLOR)
        draw_grid(screen, grid)
        pygame.display.flip()

        if is_game_over(grid):
            show_game_over(screen)

        clock.tick(30)

if __name__ == "__main__":
    main()
