import json
import os
import pygame
import sys
from pathlib import Path
from pygame.locals import *
from PIL import Image, ImageSequence  # For GIF animation support

class AnimatedSprite:
    def __init__(self, gif_path, position=(0, 0)):
        self.frames = []
        self.current_frame = 0
        self.animation_speed = 0.1
        self.time_since_last_frame = 0
        self.position = position
        self.load_gif(gif_path)
        
    def load_gif(self, gif_path):
        """Load GIF animation using PIL and convert to pygame surfaces"""
        try:
            with Image.open(gif_path) as img:
                for frame in ImageSequence.Iterator(img):
                    # Convert PIL image to pygame surface
                    frame = frame.convert("RGBA")
                    pygame_frame = pygame.image.fromstring(
                        frame.tobytes(), frame.size, frame.mode
                    )
                    self.frames.append(pygame_frame)
        except Exception as e:
            print(f"Failed to load GIF {gif_path}: {str(e)}")
            # Create a placeholder surface if loading fails
            placeholder = pygame.Surface((50, 50), pygame.SRCALPHA)
            placeholder.fill((255, 0, 255, 128))  # Magenta with alpha
            self.frames = [placeholder]
    
    def update(self, dt):
        """Update animation frame based on time"""
        self.time_since_last_frame += dt
        if self.time_since_last_frame >= self.animation_speed:
            self.time_since_last_frame = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
    
    def get_current_frame(self):
        """Get current animation frame"""
        return self.frames[self.current_frame]



class GameEngine:
    def __init__(self, levels_folder="levels", data_folder="data"):
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((880, 600))
        pygame.display.set_caption("Plants vs Zombies")
        self.clock = pygame.time.Clock()
        
        # Path setup
        self.base_dir = Path(__file__).parent
        self.levels_folder = self.base_dir / levels_folder
        self.data_folder = self.base_dir / data_folder
        
        # Load game data
        self.plants_data = self.load_data_file("plants.json")
        self.zombies_data = self.load_data_file("zombies.json")
        self.loaded_levels = self.load_all_levels()
        
        # Game state variables
        self.current_level = None
        self.W = 880
        self.H = 600
        self.C = 9
        self.LawnMowerX = 70
        self.SunNum = 50
        self.Chose = 0
        self.ChoseCard = ""
        self.MPID = ""
        self.ArCard = []
        self.ArPCard = {}
        self.ArSun = []
        self.Plants = {}
        self.Zombies = {}
        self.DraggingCard = None
        self.DraggingPos = (0, 0)
        self.Grid = [[None for _ in range(9)] for _ in range(5)]
        
        # UI elements
        self.font = pygame.font.SysFont('Arial', 16)
        self.big_font = pygame.font.SysFont('Arial', 24)
        self.last_time = pygame.time.get_ticks()
        self.card_gray_images = {}  # Store grayed-out card images
        self.last_update_time = pygame.time.get_ticks()
    def load_data_file(self, filename):
        """Load a JSON data file from the data folder"""
        file_path = self.data_folder / filename
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load {filename}: {str(e)}")
            return {}
    
    def load_all_levels(self):
        """Load all level JSON files from the levels folder"""
        levels = {}
        for level_file in self.levels_folder.glob("*.json"):
            level_id = level_file.stem.split("_")[-1]
            try:
                with open(level_file, "r") as f:
                    levels[level_id] = json.load(f)
            except Exception as e:
                print(f"Failed to load level {level_file}: {str(e)}")
        return levels
    
    def load_level(self, level_id):
        """Load a specific level by ID"""
        self.current_level = self.loaded_levels.get(str(level_id))
        if self.current_level:
            self.init_level()
            return True
        return False
    
    def init_level(self):
        """Initialize level based on loaded data"""
        # Set up level properties from JSON
        self.PName = self.current_level.get("PName", [])
        self.ZName = self.current_level.get("ZName", [])
        self.LevelName = self.current_level.get("LevelName", "Level")
        self.SunNum = self.current_level.get("SunNum", 50)
        
        # Initialize plant cards
        self.init_plant_cards()
        
        # Load card images
        self.load_card_images()
        
        # Set background
        bg_path = self.current_level.get("backgroundImage", "images/interface/background1.jpg")
        try:
            self.background = pygame.image.load(str(self.base_dir / bg_path))
        except Exception as e:
            print(f"Failed to load background {bg_path}: {str(e)}")
            self.background = pygame.Surface((880, 600))
            self.background.fill((100, 200, 100))
    
    def init_plant_cards(self):
        """Initialize plant cards for selection with cooldown states"""
        self.ArCard = []
        self.ArPCard = {}
        
        for i, plant_type in enumerate(self.PName):
            plant_data = self.plants_data.get(plant_type, {})
            card_data = {
                "DID": f"Card{plant_type}",
                "PName": plant_type,
                "Index": i,
                "Rect": pygame.Rect(80 + i * 70, 10, 70, 90),
                "Cost": plant_data.get("cost", 100),
                "MaxCooldown": plant_data.get("cooldown", 7.5),
                "Cooldown": 0,
                "CDReady": 1,
                "SunReady": 1,
                "Cooling": False,
                "ImgPath": plant_data.get("card_image", "")
            }
            self.ArCard.append(card_data)
            self.ArPCard[plant_type] = card_data
    
    def load_card_images(self):
        """Load card images and create grayed-out versions for cooldown state"""
        self.card_images = {}
        self.card_gray_images = {}
        
        for plant_type, plant_data in self.plants_data.items():
            if plant_type in self.PName:
                try:
                    img_path = self.base_dir / plant_data["card_image"]
                    # Load normal card image
                    normal_img = pygame.image.load(str(img_path)).convert_alpha()
                    self.card_images[plant_type] = normal_img
                    
                    # Create grayed-out version for cooldown
                    gray_img = self.convert_to_grayscale(normal_img.copy())
                    self.card_gray_images[plant_type] = gray_img
                    
                except Exception as e:
                    print(f"Failed to load card image for {plant_type}: {str(e)}")
                    # Create placeholders
                    placeholder = pygame.Surface((70, 90), pygame.SRCALPHA)
                    placeholder.fill((200, 100, 100, 128))
                    self.card_images[plant_type] = placeholder
                    self.card_gray_images[plant_type] = self.convert_to_grayscale(placeholder.copy())

    def convert_to_grayscale(self, surface):
        """Convert a surface to grayscale while preserving alpha"""
        gray_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        for x in range(surface.get_width()):
            for y in range(surface.get_height()):
                r, g, b, a = surface.get_at((x, y))
                # Calculate grayscale value (luminosity method)
                gray = int(0.21 * r + 0.72 * g + 0.07 * b)
                gray_surface.set_at((x, y), (gray, gray, gray, a))
        return gray_surface

    
        
        # Update cooldowns for all cards
        for card in self.ArCard:
            if card["Cooldown"] > 0:
                card["Cooldown"] = max(0, card["Cooldown"] - delta)
                card["CDReady"] = 1 if card["Cooldown"] <= 0 else 0
            
            card["SunReady"] = 1 if self.SunNum >= card["Cost"] else 0


    
    def create_plant(self, plant_type, position):
        """Create a new plant using data from plants.json"""
        plant_data = self.plants_data.get(plant_type, {})
        if not plant_data:
            print(f"Plant type {plant_type} not found in plants.json")
            return None
            
        try:
            anim_path = self.base_dir / plant_data["animation"]
            anim = AnimatedSprite(str(anim_path))
            return {
                "type": plant_type,
                "position": position,
                "anim": anim,
                "health": plant_data.get("health", 100),
                "cooldown": 0
            }
        except Exception as e:
            print(f"Failed to create plant {plant_type}: {str(e)}")
            return None
    
    def create_zombie(self, zombie_type, position):
        """Create a new zombie using data from zombies.json"""
        zombie_data = self.zombies_data.get(zombie_type, {})
        if not zombie_data:
            print(f"Zombie type {zombie_type} not found in zombies.json")
            return None
            
        try:
            anim_path = self.base_dir / zombie_data["animation"]
            anim = AnimatedSprite(str(anim_path))
            return {
                "type": zombie_type,
                "position": position,
                "anim": anim,
                "health": zombie_data.get("health", 100),
                "speed": zombie_data.get("speed", 0.5),
                "damage": zombie_data.get("damage", 1)
            }
        except Exception as e:
            print(f"Failed to create zombie {zombie_type}: {str(e)}")
            return None


    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            current_time = pygame.time.get_ticks()
            dt = (current_time - self.last_time) / 1000.0  # Delta time in seconds
            self.last_time = current_time
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == MOUSEBUTTONDOWN:
                    self.handle_mouse_down(event)
                elif event.type == MOUSEBUTTONUP:
                    self.handle_mouse_up(event)
                elif event.type == MOUSEMOTION and self.DraggingCard:
                    self.handle_mouse_motion(event)
            
            # Update game state
            self.update(dt)
            
            # Render
            self.render()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()
    
    def handle_mouse_down(self, event):
        """Handle mouse click events"""
        if event.button == 1:  # Left click
            # Check plant cards
            for card in self.ArCard:
                if card["Rect"].collidepoint(event.pos):
                    self.DraggingCard = card
                    self.DraggingPos = event.pos
                    break
            
            # Check battlefield grid
            if not self.DraggingCard and self.ChoseCard:
                row, col = self.get_grid_position(event.pos)
                if 0 <= row < 5 and 0 <= col < 9:
                    self.plant_selected(row, col)
    
    def handle_mouse_up(self, event):
        """Handle mouse release events"""
        if self.DraggingCard:
            # Check if dropped on battlefield
            row, col = self.get_grid_position(event.pos)
            if 0 <= row < 5 and 0 <= col < 9:
                self.plant_selected(row, col)
            
            self.DraggingCard = None
    
    def handle_mouse_motion(self, event):
        """Handle mouse movement while dragging"""
        if self.DraggingCard:
            self.DraggingPos = event.pos
    
    def get_grid_position(self, pos):
        """Convert screen position to grid coordinates"""
        x, y = pos
        col = (x - 220) // 80 if x > 220 else -1
        row = (y - 120) // 100 if y > 120 else -1
        return row, col
    
    def plant_selected(self, row, col):
        """Plant a card at specified grid position and trigger cooldown"""
        if self.DraggingCard and not self.Grid[row][col]:
            plant_type = self.DraggingCard["PName"]
            plant_cost = self.DraggingCard["Cost"]
            
            if self.SunNum >= plant_cost:
                self.SunNum -= plant_cost
                plant = self.create_plant(plant_type, (220 + col * 80, 120 + row * 100))
                if plant:
                    # Trigger cooldown for this card
                    self.DraggingCard["Cooldown"] = self.DraggingCard["MaxCooldown"]
                    self.DraggingCard["CDReady"] = 0
                    plant_id = f"plant_{row}_{col}"
                    self.Plants[plant_id] = plant
                    self.Grid[row][col] = plant_id
                    print(f"Planted {plant_type} at {row},{col}")
    
    def update(self, dt):
        """Update game logic with delta time including card cooldowns"""
        current_time = pygame.time.get_ticks()
        delta = (current_time - self.last_update_time) / 1000.0
        self.last_update_time = current_time
        
        # Update cooldowns for all cards
        for card in self.ArCard:
            if card["Cooldown"] > 0:
                card["Cooldown"] = max(0, card["Cooldown"] - delta)
                card["CDReady"] = 1 if card["Cooldown"] <= 0 else 0
            
            card["SunReady"] = 1 if self.SunNum >= card["Cost"] else 0
        """Update game logic with delta time"""
        # Update plant animations
        for plant_id, plant in self.Plants.items():
            plant["anim"].update(dt)
        
        # Update zombie animations
        for zombie_id, zombie in self.Zombies.items():
            zombie["anim"].update(dt)
        
        # Spawn zombies based on level configuration
        self.spawn_zombies()
    
    def spawn_zombies(self):
        """Spawn zombies based on level configuration"""
        if not hasattr(self, "last_spawn_time"):
            self.last_spawn_time = pygame.time.get_ticks()
        
        current_time = pygame.time.get_ticks()
        if current_time - self.last_spawn_time > 5000:  # Spawn every 5 seconds
            self.last_spawn_time = current_time
            
            if self.current_level and "AZ" in self.current_level:
                for zombie_data in self.current_level["AZ"]:
                    zombie_type, count, row = zombie_data
                    for _ in range(count):
                        zombie = self.create_zombie(zombie_type, (850, 120 + row * 100))
                        if zombie:
                            zombie_id = f"zombie_{len(self.Zombies)}"
                            self.Zombies[zombie_id] = zombie
    
    def render(self):
        """Render game elements with card state awareness"""
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw plant cards with state awareness
        for card in self.ArCard:
            plant_type = card["PName"]
            if plant_type in self.card_images:
                # Select image based on card state
                if card["CDReady"] and card["SunReady"]:
                    img = self.card_images[plant_type]  # Normal colored
                else:
                    img = self.card_gray_images[plant_type]  # Grayed out
                    
                self.screen.blit(img, card["Rect"])
                
                # Draw cost text
                cost_text = self.font.render(str(card["Cost"]), True, 
                    (255, 255, 0) if card["SunReady"] else (150, 150, 150))
                self.screen.blit(cost_text, (card["Rect"].x + 5, card["Rect"].y + 70))
        
        # Draw dragging card
        if self.DraggingCard and self.DraggingCard["PName"] in self.card_images:
            self.screen.blit(
                self.card_images[self.DraggingCard["PName"]],
                (self.DraggingPos[0] - 35, self.DraggingPos[1] - 45)
            )
        
        # Draw plants with animations
        for plant_id, plant in self.Plants.items():
            frame = plant["anim"].get_current_frame()
            self.screen.blit(frame, plant["position"])
        
        # Draw zombies with animations
        for zombie_id, zombie in self.Zombies.items():
            frame = zombie["anim"].get_current_frame()
            self.screen.blit(frame, zombie["position"])


if __name__ == "__main__":
    # Check for required packages
    try:
        import PIL
    except ImportError:
        print("Please install Pillow for GIF support: pip install pillow")
        sys.exit(1)
    
    # Ensure the levels folder exists
    if not os.path.exists("levels"):
        os.makedirs("levels")
        print("Created 'levels' directory - please add your level JSON files here")
    
    game = GameEngine()
    if game.load_level("1"):  # Load level 1
        game.run()
    else:
        print(f"Failed to load level 1. Please ensure levels/level_1.json exists")