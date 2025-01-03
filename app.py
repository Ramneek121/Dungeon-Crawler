import pygame
import random
import sys 
from pygame.locals import *
import math
import pygame.mixer


# Pygame setup
pygame.init()


###############################
# CONFIGURATION PARAMETERS
###############################
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32

MAP_WIDTH = 25
MAP_HEIGHT = 18
ROOM_COUNT = 8
MIN_ROOM_SIZE = 3
MAX_ROOM_SIZE = 6

FOG_RADIUS = 5  # How far the player can see
PLAYER_COLOR = (0, 255, 0)
ENEMY_COLOR = (255, 0, 0)
TREASURE_COLOR = (255, 215, 0)
TRAP_COLOR = (139, 0, 0)
DOOR_COLOR = (100, 100, 255)
EXIT_COLOR = (0, 255, 255)
FOG_COLOR = (30, 30, 30)
POTION_COLOR = (0, 128, 255) 

particles = []

# Symbols for map tiles
WALL = "#"
FLOOR = "."
PLAYER = "@"
TRAP = "^"
TREASURE = "T"
KEY = "K"
ENEMY = "E"
EXIT = "X"
POTION = "P"

FOG_RADIUS = 3
AMBIENT_LIGHT_COLOR = (50, 50, 50, 128)
LIGHT_RADIUS = 3

# Fonts and Sounds
FONT = pygame.font.Font(None, 24)
FONT_LARGE = pygame.font.Font(None, 48)

def create_light_surface(radius, color):
    light_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    center = radius

    for y in range(radius * 2):
        for x in range(radius * 2):
            # Calculate distance from the center
            distance = math.sqrt((x - center) ** 2 + (y - center) ** 2)

            # Gradual transparency for the light effect
            if distance <= radius:
                alpha = max(0, int(255 * (1 - distance / radius)))  # Gradual fade
                light_surface.set_at((x, y), (*color[:3], alpha))  # RGBA
            else:
                light_surface.set_at((x, y), (0, 0, 0, 0))  # Fully transparent outside the radius

    return light_surface


light_cache = {}

def get_light_surface(radius, color):
    if radius not in light_cache:
        light_cache[radius] = create_light_surface(radius, color)
    return light_cache[radius]

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Advanced Dungeon Crawler")

###############################
# GAME STATE CLASSES
###############################

class Player:
    def __init__(self, x, y):
            self.x = x        
            self.y = y        
            self.hp = 100
            self.keys = 0
            self.score = 0
            self.inventory = []
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill(PLAYER_COLOR)
            self.animation_offset = [0, 0]  # For smooth movement
            
    def move(self, dx, dy):
        self.x += dx        
        self.y += dy

    def damage(self, amount):
        self.hp -= amount        
        
        if self.hp <= 0:
            self.hp = 0
            print("Player died.")  # Debugging
            game.game_over()

        for _ in range(20):  # Adjust number of particles
            velocity = (random.uniform(-5, 5), random.uniform(-5, 5))
        particles.append(Particle(self.x * TILE_SIZE, self.y * TILE_SIZE, (255, 0, 0), 60, velocity))
                                           
    def heal(self, amount):
        self.hp = min(self.hp + amount, 100)

    def add_key(self):
        self.keys += 1
        print(f"Keys collected: {self.keys}")


    def pick_item(self, item):
        self.inventory.append(item)

    def __str__(self):
        return f"HP: {self.hp} | Keys: {self.keys} | Score: {self.score}"
    

    
class Particle:
    def __init__(self, x, y, color, lifetime, velocity):
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = lifetime
        self.velocity = velocity

    def update(self):
        self.lifetime -= 1
        self.x += random.uniform(-1, 1)
        self.y += random.uniform(-1, 1)

    def draw(self, screen):
        if self.lifetime > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 2)


                                                                                           

class Enemy:
        def __init__(self, x, y):
            self.x = x        
            self.y = y        
            self.hp = 30
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill(ENEMY_COLOR)
                                                                                                                       
        def move_towards(self, target_x, target_y, dungeon_map):
            dx, dy = 0, 0
            if self.x < target_x:
                dx = 1
            elif self.x > target_x:
                dx = -1
                                                                                                                                                           
            if self.y < target_y:
                dy = 1
            elif self.y > target_y:
                dy = -1
                                                                                                                                                                               
            new_x, new_y = self.x + dx, self.y + dy        
            
            if dungeon_map[new_y][new_x] == FLOOR:
                                                                                                                                                                                           
                self.x = new_x            
                self.y = new_y
                                                                                                                                                                               
class DungeonGame:
            def __init__(self):
                self.map = [[WALL for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
                self.rooms = []
                self.player = None        
                self.enemies = []
                self.traps = []
                self.treasures = []
                self.exit_position = None
                self.camera = Camera(MAP_WIDTH, MAP_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE)
                self.key_sound = pygame.mixer.Sound("door_open.mp3")

            def update_particles(self):
                for particle in particles[:]:
                    particle.update()
                    if particle.lifetime <= 0:
                        particles.remove(particle)
                                                                                                                                                                                                               
            def generate_dungeon(self):
                self.rooms = []  # Clear existing rooms
                self.map = [[WALL for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]

    # Step 1: Generate non-overlapping rooms
                for _ in range(ROOM_COUNT):
                    w = random.randint(MIN_ROOM_SIZE, MAX_ROOM_SIZE)
                    h = random.randint(MIN_ROOM_SIZE, MAX_ROOM_SIZE)
                    x = random.randint(1, MAP_WIDTH - w - 2)
                    y = random.randint(1, MAP_HEIGHT - h - 2)

        # Ensure rooms don't overlap
                    overlap = False
                    for room in self.rooms:
                        rx, ry, rw, rh = room
                        if x < rx + rw and x + w > rx and y < ry + rh and y + h > ry:
                            overlap = True
                            break

                    if not overlap:
                        self.rooms.append((x, y, w, h))
                        for i in range(y, y + h):
                            for j in range(x, x + w):
                                self.map[i][j] = FLOOR

    # Step 2: Connect rooms using a graph-based approach
                self.connect_rooms()

            def generate_new_rooms(self, key_x, key_y):
                
                NEW_MIN_ROOM_SIZE = 30  # Bigger minimum size for new rooms
                NEW_MAX_ROOM_SIZE = 60  # Bigger maximum size for new rooms

                max_attempts = 50  # Safety limit for room placement
                placed_rooms = 0
        # Generate new rooms in the expanded map
                for _ in range(ROOM_COUNT // 2):  # Generate fewer rooms during expansion
                    attempts = 0
                    while attempts < max_attempts:
                     w = random.randint(MIN_ROOM_SIZE, MAX_ROOM_SIZE)
                     h = random.randint(MIN_ROOM_SIZE, MAX_ROOM_SIZE)
                     x = key_x + random.choice([-1, 1]) * random.randint(3, 10)
                     y = key_y + random.choice([-1, 1]) * random.randint(3, 10) 
                     x = max(1, min(x, MAP_WIDTH - w - 2))
                     y = max(1, min(y, MAP_HEIGHT - h - 2))



                     overlap = False
                     for room in self.rooms:
                        rx, ry, rw, rh = room
                        if x < rx + rw and x + w > rx and y < ry + rh and y + h > ry:
                            overlap = True
                            break

                     if not overlap:
                # Room is valid; add to map
                        self.rooms.append((x, y, w, h))

                        for i in range(y, y + h):
                            for j in range(x, x + w):
                        # Add random cut-outs for odd shapes
                                if random.random() > 0.2:  # 80% chance to mark as FLOOR
                                    self.map[i][j] = FLOOR

                        placed_rooms += 1
                        break

                     if attempts >= max_attempts:
                        print("Warning: Room placement exceeded maximum attempts.")
                        break  # Exit the function to avoid freezing
                
                self.connect_rooms()
                


            def connect_rooms(self):
    # Get room centers
                room_centers = [(x + w // 2, y + h // 2) for x, y, w, h in self.rooms]

    # Track already connected rooms
                connected_rooms = set()
                connected_rooms.add(0)  # Assume the first room is always connected

                for i in range(1, len(room_centers)):
                    x1, y1 = room_centers[i]

        # Find the nearest connected room
                    nearest_index = min(
                    connected_rooms, key=lambda idx: (room_centers[idx][0] - x1) ** 2 + (room_centers[idx][1] - y1) ** 2
                    )
                    x2, y2 = room_centers[nearest_index]

        # Connect the current room to the nearest connected room
                    self.create_corridor(x1, y1, x2, y2)
                    connected_rooms.add(i)
                
            def create_corridor(self, x1, y1, x2, y2):
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    self.map[y1][x] = FLOOR

                for y in range(min(y1, y2), max(y1, y2) + 1):
                       self.map[y][x2] = FLOOR
                                                                                                                                                                                                                                                                                                           # 
            def place_entities(self):
                                                                                                                                                                                                                
                px, py = self.rooms[0][0] + self.rooms[0][2] // 2, self.rooms[0][1] + self.rooms[0][3] // 2
                self.player = Player(px, py)
                                                                                                                                                                                                                                                                                                            
                for _ in range(6):
                    tx, ty = self.find_random_floor()
                    self.traps.append((tx, ty))
                    self.map[ty][tx] = TRAP
                                                                                                                                                                                                                                                                                                            
                for _ in range(5):
                    tx, ty = self.find_random_floor()
                    self.treasures.append((tx, ty))
                    self.map[ty][tx] = TREASURE

                for _ in range(3):
                    px, py = self.find_random_floor()
                    self.map[py][px] = POTION

                for _ in range(3):
                    ex, ey = self.find_random_floor()
                    self.enemies.append(Enemy(ex, ey))
                    self.map[ey][ex] = ENEMY
                
                key_x, key_y = self.find_random_floor()
                self.map[key_y][key_x] = KEY
                self.key_position = (key_x, key_y)
                                                                                                                                                                                                                                                                                                           # 
            def find_random_floor(self):
                while True:
                    x = random.randint(1, MAP_WIDTH - 2)
                    y = random.randint(1, MAP_HEIGHT - 2)
                    if self.map[y][x] == FLOOR:
                        return x, y
                                                                                                                                                                                                                                                                                                           # 
            def handle_interaction(self):
                                                                                                                                                                                                                                                                                                                   
                tile = self.map[self.player.y][self.player.x]
                                                                                                                                                                                                                                                                                                           # 
                if tile == TRAP:
                    
                    self.player.damage(15)
                    print(f"You stepped on a trap! HP: {self.player.hp}")
                                                                                                                                                                                                                                                                                                           # 
                elif tile == TREASURE:
                    
                    self.player.score += 20
                    self.map[self.player.y][self.player.x] = FLOOR
                    print(f"You found a treasure! Score: {self.player.score}")
                                                                                                                                                                                                                                                                                                            
                elif tile == ENEMY:
                    
                    self.player.damage(25)
                    print(f"An enemy attacked you! HP: {self.player.hp}")

                elif tile == POTION:
                    self.player.heal(20)
                    self.map[self.player.y][self.player.x] = FLOOR
                    print(f"You drank a health potion! HP: {self.player.hp}")


                elif tile == KEY:
                    self.map[self.player.y][self.player.x] = FLOOR  # Remove the key from the map
                    self.key_sound.play()
                    self.player.add_key()
                    self.expand_map() 

                    print("You found a key! The dungeon expands!")
                                                                                                                                                                                                                                                                                                           # 
                elif tile == EXIT:
                    if self.player.keys >= 3:
                       
                        print("You escaped the dungeon!")
                        sys.exit(0)
                    else:
                        print("You need more keys to unlock the exit.")
                                                                                                                                                                                                                                                                                                           # 
            def game_loop(self):
                                                                                                                                                                                                                                
                running = True
                while running:
                    for event in pygame.event.get():
                        if event.type == QUIT:
                            running = False
                        elif event.type == KEYDOWN:
                            if event.key == K_w:
                                self.move_player(0, -1)
                            elif event.key == K_s:
                                self.move_player(0, 1)
                            elif event.key == K_a:
                                self.move_player(-1, 0)
                            elif event.key == K_d:
                                self.move_player(1, 0)
                           
                                                                                                                                             
                    self.update_particles()
                    self.render()
                    pygame.display.flip()
                                                                                                                                                                                                                                                                                                           # 
            def move_player(self, dx, dy):
                                                                                                                                                                               
                new_x = self.player.x + dx
                new_y = self.player.y + dy
                                                                                                                                                                                                                                                                                                           # 
                if self.map[new_y][new_x] != WALL:
                    self.player.move(dx, dy)
                    self.handle_interaction()

                    self.camera.update(self.player.x, self.player.y)
                                                                                                                                                                                                                                                                                                           
            def render(self):
                darkness_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                darkness_surface.fill((0, 0, 0, 255))                                                                                                                                
                screen.fill((0, 0, 0))
                camera = Camera(MAP_WIDTH, MAP_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE)
                camera.update(self.player.x, self.player.y)

    # Draw only visible tiles based on the camera
                for y in range(MAP_HEIGHT):
                    for x in range(MAP_WIDTH):
                        screen_x, screen_y = camera.apply(x, y)

            # Skip rendering tiles outside the screen
                        if screen_x < -TILE_SIZE or screen_x >= SCREEN_WIDTH or screen_y < -TILE_SIZE or screen_y >= SCREEN_HEIGHT:
                            continue

                        if self.map[y][x] == WALL:
                            pygame.draw.rect(screen, (100, 100, 100), (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                        elif self.map[y][x] == FLOOR:
                            pygame.draw.rect(screen, (50, 50, 50), (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                        elif self.map[y][x] == POTION:
                            pygame.draw.rect(screen, POTION_COLOR, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))

    # Draw the player at the correct position relative to the camera
                player_screen_x, player_screen_y = camera.apply(self.player.x, self.player.y)
                screen.blit(self.player.image, (player_screen_x, player_screen_y))

                

                player_screen_x, player_screen_y = camera.apply(self.player.x, self.player.y)
                light_radius = LIGHT_RADIUS * TILE_SIZE
                light_surface = get_light_surface(light_radius, (255, 255, 0, 255))  # Yellow light

    # Position the light surface over the player
                light_x = player_screen_x - light_radius
                light_y = player_screen_y - light_radius

    # Subtract the light from the darkness to reveal the visible area
                darkness_surface.blit(light_surface, (light_x, light_y), special_flags=pygame.BLEND_RGBA_SUB)

    # Apply the darkness mask over the entire screen
                screen.blit(darkness_surface, (0, 0))

                for particle in particles:
                    particle.draw(screen)

                max_hp = 100
                bar_width = 200
                bar_height = 20
                health_ratio = self.player.hp / max_hp
                pygame.draw.rect(screen, (255, 0, 0), (10, 10, bar_width, bar_height))  # Background (full bar)
                pygame.draw.rect(screen, (0, 255, 0), (10, 10, bar_width * health_ratio, bar_height))  # Current HP

                health_text = FONT.render(f"{self.player.hp} / {max_hp}", True, (255, 255, 255))
                health_text_rect = health_text.get_rect(center=(10 + bar_width // 2, 10 + bar_height // 2))
                screen.blit(health_text, health_text_rect)

                score_text = FONT.render(f"SCORE: {self.player.score}", True, (255,255,0))
                screen.blit(score_text, (10,40))

                pygame.display.flip()

            def game_over(self):
                
                running = True
                while running:
                    screen.fill((0, 0, 0))
                    pygame.draw.rect(screen, (50, 50, 50), (200, 150, 400, 300))  # Pop-up background

        # Display Game Over text
                    text = FONT_LARGE.render("GAME OVER", True, (255, 0, 0))
                    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
                    screen.blit(text, text_rect)

                    score_text = FONT.render(f"Final Score: {self.player.score}", True, (255, 255, 0))
                    score_text_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.5))
                    screen.blit(score_text, score_text_rect)


        # Display Restart button
                    button_rect = pygame.Rect(300, 300, 200, 50)  # Position and size of button
                    pygame.draw.rect(screen, (0, 255, 0), button_rect)
                    button_text = FONT.render("Restart", True, (0, 0, 0))
                    button_text_rect = button_text.get_rect(center=button_rect.center)
                    screen.blit(button_text, button_text_rect)

                    pygame.display.flip()

        # Handle events
                    for event in pygame.event.get():
                        if event.type == QUIT:
                            pygame.quit()
                            sys.exit()
                        elif event.type == MOUSEBUTTONDOWN:
                            if button_rect.collidepoint(event.pos):  # Check if restart button is clicked
                                self.restart_game()
                                running = False
                                pygame.mixer.music.stop()
                                pygame.mixer.music.load("background_music1.mp3")
                                pygame.mixer.music.set_volume(0.1)
                                pygame.mixer.music.play(-1)
                    

            def restart_game(self):
                pygame.mixer.music.stop()
                pygame.mixer.music.load("background_music1.mp3")
                pygame.mixer.music.set_volume(0.1)
                pygame.mixer.music.play(-1)
                self.__init__()
                self.generate_dungeon()
                self.place_entities()
                self.game_loop()
               
            
            def expand_map(self):
                global MAP_WIDTH, MAP_HEIGHT  # Ensure we modify the global variables

                old_width = MAP_WIDTH
                old_height = MAP_HEIGHT

                MAP_WIDTH += 10
                MAP_HEIGHT += 10

    # Resize the map and fill it with walls
                new_map = [[WALL for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]

    # Copy the existing map into the new larger map
                for y in range(old_height):  # Preserve previous dungeon
                    for x in range(old_width):
                        new_map[y][x] = self.map[y][x]

                self.map = new_map  # Replace the old map with the new expanded map
                self.generate_new_rooms(self.key_position[0], self.key_position[1])

    # Regenerate rooms and corridors for the expanded map
                  # Clear previous room data

    # Re-add entities to the expanded map
                self.generate_new_traps(old_width, old_height)
                self.generate_new_key(old_width, old_height)
                self.generate_new_potions(old_width, old_height)
                self.generate_new_treasures(old_width, old_height)


    # Ensure the player remains at their current position
                self.map[self.player.y][self.player.x] = PLAYER

            def generate_new_potions(self, old_width, old_height):
                new_potions = []
                for _ in range(3):  # Adjust the number of potions as needed
                    while True:
                        x = random.randint(0, MAP_WIDTH - 1)
                        y = random.randint(0, MAP_HEIGHT - 1)
                                             
                        if (x >= old_width or y >= old_height) and self.map[y][x] == FLOOR:
                            self.map[y][x] = POTION                
                            new_potions.append((x, y))
                            break
            def generate_new_treasures(self, old_width, old_height):
                    new_treasures = []
                    for _ in range(5):  # Adjust the number of treasures as needed
                        while True:
                            x = random.randint(0, MAP_WIDTH - 1)
                            y = random.randint(0, MAP_HEIGHT - 1)
                                                
                                                            # Ensure the treasure is placed in the new expanded area and on a floor tile
                            if (x >= old_width or y >= old_height) and self.map[y][x] == FLOOR:
                                self.map[y][x] = TREASURE        
                                new_treasures.append((x, y))
                                break

            def generate_new_traps(self, old_width, old_height):
                new_traps = []
                for _ in range(6):  # Adjust the number of traps as needed
                    while True:
                        x = random.randint(0, MAP_WIDTH - 1)
                        y = random.randint(0, MAP_HEIGHT - 1)

            # Ensure the trap is placed in the new expanded area and on a floor tile
                        if (x >= old_width or y >= old_height) and self.map[y][x] == FLOOR:
                            self.map[y][x] = TRAP
                            new_traps.append((x, y))
                            break

            def generate_new_key(self, old_width, old_height):
                while True:
                    x = random.randint(0, MAP_WIDTH - 1)
                    y = random.randint(0, MAP_HEIGHT - 1)

                    if (x >= old_width or y >= old_height) and self.map[y][x] == FLOOR:
                        self.map[y][x] = KEY
                        self.key_position = (x, y)
                        print(f"New key placed at: {self.key_position}")  # Debugging
                        break


class Camera:
    def __init__(self, map_width, map_height, screen_width, screen_height, tile_size):
        self.map_width = map_width
        self.map_height = map_height
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.tile_size = tile_size
        self.x_offset = 0
        self.y_offset = 0

    def update(self, player_x, player_y):
        # Center the camera on the player
        self.x_offset = player_x * self.tile_size - self.screen_width // 2
        self.y_offset = player_y * self.tile_size - self.screen_height // 2

        # Clamp the camera to map bounds
        self.x_offset = max(0, min(self.x_offset, (self.map_width * self.tile_size) - self.screen_width))
        self.y_offset = max(0, min(self.y_offset, (self.map_height * self.tile_size) - self.screen_height))

    def apply(self, x, y):
        # Adjust map coordinates to screen coordinates
        return x * self.tile_size - self.x_offset, y * self.tile_size - self.y_offset

def show_start_menu(): 
 
    menu_font = pygame.font.Font(None, 64)
    button_font = pygame.font.Font(None, 36)
    pygame.mixer.music.stop()
    pygame.mixer.music.load("background_music.mp3")
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play(-1)

    # Colors
    bg_color = (30, 30, 30)    # Dark background
    title_color = (200, 200, 200)
    button_color = (100, 100, 100)
    hover_color = (150, 150, 150)
    text_color = (255, 255, 255)


    # Button positions and sizes
    start_button_rect = pygame.Rect(0, 0, 200, 50)
    exit_button_rect = pygame.Rect(0, 0, 200, 50)

    # Center the buttons on screen
    start_button_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    exit_button_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70)

    title_text = menu_font.render("Dungeon Crawler", True, title_color)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))

    clock = pygame.time.Clock()

    while True:
            screen.fill(bg_color)

            screen.blit(title_text, title_rect)
            
                    # Get mouse position
            mx, my = pygame.mouse.get_pos()
            
                    # Check if mouse is over the buttons (for hover effect)
            if start_button_rect.collidepoint(mx, my):
                pygame.draw.rect(screen, hover_color, start_button_rect)
            else:
                pygame.draw.rect(screen, button_color, start_button_rect)

            if exit_button_rect.collidepoint(mx, my):
                                pygame.draw.rect(screen, hover_color, exit_button_rect)
            else:
                                pygame.draw.rect(screen, button_color, exit_button_rect)

                                        # Render button text
            start_text = button_font.render("Start Game", True, text_color)
            exit_text = button_font.render("Exit", True, text_color)
                                
                                        # Center text on the button
            start_text_rect = start_text.get_rect(center=start_button_rect.center)
            exit_text_rect = exit_text.get_rect(center=exit_button_rect.center)
                                
                                        # Draw button text
            screen.blit(start_text, start_text_rect)
            screen.blit(exit_text, exit_text_rect)
                                
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse click
                        if start_button_rect.collidepoint(event.pos):
                            pygame.mixer.music.stop()
                            return True
                        elif exit_button_rect.collidepoint(event.pos):
                            return False        
                                        
            pygame.display.flip()
            clock.tick(60)



def main():

    global game

    pygame.mixer.init()

    start_chosen = show_start_menu()
    if not start_chosen:
        # If the user chose Exit, quit the game
        pygame.quit()
        sys.exit()

    pygame.mixer.music.load("background_music1.mp3")
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play(-1)  # Loop indefinitely

    

# Play sounds on events

    game = DungeonGame()
    game.generate_dungeon()
    game.place_entities()
    game.game_loop()
                                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                            
if __name__ == "__main__":
    main()
                                                                                                                                                                                                                                                                                                         