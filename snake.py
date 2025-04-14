import pygame
import random
import sqlite3

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 400
CELL_SIZE = 10
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Database setup
def setup_database():
    conn = sqlite3.connect("snake_game.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS user_scores (user_id INTEGER, score INTEGER, level INTEGER, FOREIGN KEY(user_id) REFERENCES users(id))""")
    conn.commit()
    conn.close()

setup_database()

# Fetch leaderboard and display as a table
def display_leaderboard():
    conn = sqlite3.connect("snake_game.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT username, score, level
        FROM user_scores
        JOIN users ON user_scores.user_id = users.id
        ORDER BY score DESC, level DESC
    """)
    leaderboard = cursor.fetchall()
    conn.close()

    font = pygame.font.Font(None, 30)
    screen.fill(BLACK)

    # Table Header
    header_font = pygame.font.Font(None, 35)
    header_text = header_font.render("Leaderboard", True, WHITE)
    screen.blit(header_text, (WIDTH // 2 - header_text.get_width() // 2, 20))

    # Table Column Names
    col_width = WIDTH // 4
    screen.blit(font.render("Rank", True, WHITE), (10, 80))
    screen.blit(font.render("Username", True, WHITE), (col_width, 80))
    screen.blit(font.render("Score", True, WHITE), (2 * col_width, 80))
    screen.blit(font.render("Level", True, WHITE), (3 * col_width, 80))

    # Draw a horizontal line under the header
    pygame.draw.line(screen, WHITE, (0, 110), (WIDTH, 110), 2)

    # Draw Leaderboard Entries
    y_offset = 120
    for idx, (username, score, level) in enumerate(leaderboard[:10]):  # Show top 10
        rank_text = font.render(f"{idx + 1}", True, WHITE)
        username_text = font.render(username, True, WHITE)
        score_text = font.render(str(score), True, WHITE)
        level_text = font.render(str(level), True, WHITE)

        # Display each column in its respective position
        screen.blit(rank_text, (10, y_offset))
        screen.blit(username_text, (col_width, y_offset))
        screen.blit(score_text, (2 * col_width, y_offset))
        screen.blit(level_text, (3 * col_width, y_offset))

        y_offset += 40

    pygame.display.flip()

# Get username, user id, and progress (same as before)
def get_username():
    font = pygame.font.Font(None, 40)
    username = ""
    input_active = True
    while input_active:
        screen.fill(BLACK)
        prompt_text = font.render("Enter Username: " + username, True, WHITE)
        screen.blit(prompt_text, (WIDTH // 6, HEIGHT // 3))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and username:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif event.unicode.isalnum():
                    username += event.unicode
    return username

def get_or_create_user(username):
    conn = sqlite3.connect("snake_game.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
        conn.commit()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
    conn.close()
    return user[0]

def get_user_progress(user_id):
    conn = sqlite3.connect("snake_game.db")
    cursor = conn.cursor()
    cursor.execute("SELECT score, level FROM user_scores WHERE user_id = ? ORDER BY score DESC LIMIT 1", (user_id,))
    progress = cursor.fetchone()
    conn.close()
    return progress if progress else (0, 1)

def save_progress(user_id, score, level):
    conn = sqlite3.connect("snake_game.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_scores (user_id, score, level) VALUES (?, ?, ?)", (user_id, score, level))
    conn.commit()
    conn.close()

def generate_walls(level):
    walls = []

    # Add border walls
    for i in range(0, HEIGHT, CELL_SIZE):
        walls.append((0, i))
        walls.append((WIDTH - CELL_SIZE, i))
    for i in range(0, WIDTH, CELL_SIZE):
        walls.append((i, 0))
        walls.append((i, HEIGHT - CELL_SIZE))

    # Add new random obstacles every 5 levels
    if level >= 5:
        multiplier = (level // 5)
        obstacle_blocks = min(3 * multiplier, 30)  # Multiples of 3, max 30

        safe_zone = pygame.Rect(40, 40, 140, 140)  # Starting area safety zone

        placed = 0
        attempts = 0
        while placed < obstacle_blocks and attempts < 300:
            x = random.randint(1, (WIDTH // CELL_SIZE) - 2) * CELL_SIZE
            y = random.randint(1, (HEIGHT // CELL_SIZE) - 2) * CELL_SIZE
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            if not safe_zone.colliderect(rect) and (x, y) not in walls:
                walls.append((x, y))
                placed += 1
            attempts += 1

    return walls



def generate_food():
    while True:
        x = random.randint(1, (WIDTH // CELL_SIZE) - 2) * CELL_SIZE
        y = random.randint(1, (HEIGHT // CELL_SIZE) - 2) * CELL_SIZE
        if (x, y) not in snake and (x, y) not in walls:
            return (x, y), random.randint(1, 3)

# Main Game Logic
username = get_username()
user_id = get_or_create_user(username)
score, level = get_user_progress(user_id)

snake = [(100, 100), (90, 100), (80, 100)]
snake_dir = (CELL_SIZE, 0)
speed = 10 + (level - 1) 

walls = generate_walls(level)

food, food_weight = generate_food()

running = True
paused = False
show_leaderboard = False

while running:
    screen.fill(BLACK)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_progress(user_id, score, level)
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and snake_dir != (0, CELL_SIZE):
                snake_dir = (0, -CELL_SIZE)
            elif event.key == pygame.K_DOWN and snake_dir != (0, -CELL_SIZE):
                snake_dir = (0, CELL_SIZE)
            elif event.key == pygame.K_LEFT and snake_dir != (CELL_SIZE, 0):
                snake_dir = (-CELL_SIZE, 0)
            elif event.key == pygame.K_RIGHT and snake_dir != (-CELL_SIZE, 0):
                snake_dir = (CELL_SIZE, 0)
            elif event.key == pygame.K_p:
                paused = not paused
            elif event.key == pygame.K_l:  # Press 'L' to show leaderboard
                show_leaderboard = not show_leaderboard
    
    if show_leaderboard:
        display_leaderboard()
        continue
    
    if paused:
        pygame.display.flip()
        continue
    
    new_head = (snake[0][0] + snake_dir[0], snake[0][1] + snake_dir[1])
    
    if new_head in walls or new_head in snake:
        save_progress(user_id, score, level)
        running = False
        continue
    
    snake.insert(0, new_head)
    
    if new_head == food:
        score += food_weight
        food, food_weight = generate_food()
        if score % 3 == 0:
            level += 1
            speed += 2
            walls = generate_walls(level)
    else:
        snake.pop()
    
    for segment in snake:
        pygame.draw.rect(screen, GREEN, (segment[0], segment[1], CELL_SIZE, CELL_SIZE))
    
    food_color = RED if food_weight == 1 else (YELLOW if food_weight == 2 else ORANGE)
    pygame.draw.rect(screen, food_color, (food[0], food[1], CELL_SIZE, CELL_SIZE))
    
    for wall in walls:
        pygame.draw.rect(screen, WHITE, (wall[0], wall[1], CELL_SIZE, CELL_SIZE))
    
    font = pygame.font.Font(None, 30)
    screen.blit(font.render(f"User: {username}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 40))
    screen.blit(font.render(f"Level: {level}", True, WHITE), (10, 70))
    
    pygame.display.flip()
    clock.tick(speed)

pygame.quit()
