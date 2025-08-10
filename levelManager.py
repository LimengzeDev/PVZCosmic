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
    def __init__(self, levels_folder="levels"):
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((880, 600))
        pygame.display.set_caption("Plants vs Zombies")
        self.clock = pygame.time.Clock()
        self.levels_folder = Path(levels_folder)
        self.current_level = None
        self.loaded_levels = {}
        self.load_all_levels()
        
        # Game state variables
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
        self.Plants = {}  # {plant_id: {"type": str, "position": tuple, "anim": AnimatedSprite}}
        self.Zombies = {}  # {zombie_id: {"type": str, "position": tuple, "anim": AnimatedSprite}}
        self.DraggingCard = None
        self.DraggingPos = (0, 0)
        self.Grid = [[None for _ in range(9)] for _ in range(5)]  # 5 rows, 9 columns
        
        # UI elements
        self.font = pygame.font.SysFont('Arial', 16)
        self.big_font = pygame.font.SysFont('Arial', 24)
        
        # Base directory for assets (relative to script location)
        self.base_dir = Path(__file__).parent
        
        # For tracking animation time
        self.last_time = pygame.time.get_ticks()
    
    def load_all_levels(self):
        """Load all level JSON files from the levels folder"""
        for level_file in self.levels_folder.glob("*.json"):
            level_id = level_file.stem.split("_")[-1]
            with open(level_file, "r") as f:
                self.loaded_levels[level_id] = json.load(f)
    
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
        self.PicArr = self.current_level.get("PicArr", [])
        self.LF = self.current_level.get("LF", [0, 1, 1, 1, 1, 1])
        self.CanSelectCard = self.current_level.get("CanSelectCard", 1)
        self.LevelName = self.current_level.get("LevelName", "Level")
        self.AudioArr = self.current_level.get("AudioArr", [])
        self.SunNum = self.current_level.get("SunNum", 50)
        
        # Initialize plant cards
        self.init_plant_cards()
        
        # Load assets
        self.load_assets()
        
    def init_plant_cards(self):
        """Initialize plant cards for selection"""
        self.ArCard = []
        self.ArPCard = {}
        
        for i, plant in enumerate(self.PName):
            # Card images are PNGs, plant animations are GIFs
            card_img_path = f"images/Card/Plants/{plant}.png"
            plant_data = {
                "DID": f"Card{plant}",
                "CDReady": 0,
                "SunReady": 1,
                "PName": plant,
                "Index": i,
                "Rect": pygame.Rect(80 + i * 70, 10, 70, 90),
                "Cost": self.get_plant_cost(plant),
                "ImgPath": card_img_path
            }
            self.ArCard.append(plant_data)
            self.ArPCard[plant] = plant_data
    
    def get_plant_cost(self, plant_type):
        """Return sun cost for different plant types"""
        costs = {
            "Peashooter": 100,
            "SunFlower": 50,
            "WallNut": 50,
            "CherryBomb": 150,
            "PotatoMine": 25
        }
        return costs.get(plant_type, 100)
    
    def load_assets(self):
        """Load images and audio for current level"""
        # Load static images from PicArr paths
        self.images = {}
        for img_path in self.PicArr:
            try:
                full_path = self.base_dir / img_path
                if img_path.endswith(".gif"):
                    # We'll load GIFs as animated sprites when needed
                    continue
                self.images[img_path] = pygame.image.load(str(full_path))
            except Exception as e:
                print(f"Failed to load image {img_path}: {str(e)}")
                
        # Set background
        bg_path = self.current_level.get("backgroundImage", "images/interface/background1.jpg")
        try:
            full_bg_path = self.base_dir / bg_path
            self.background = pygame.image.load(str(full_bg_path))
        except Exception as e:
            print(f"Failed to load background {bg_path}: {str(e)}")
            self.background = pygame.Surface((880, 600))
            self.background.fill((100, 200, 100))
        
        # Load card images (static PNGs)
        self.card_images = {}
        for plant in self.PName:
            card_path = f"images/Card/Plants/{plant}.png"
            try:
                full_card_path = self.base_dir / card_path
                self.card_images[plant] = pygame.image.load(str(full_card_path))
            except Exception as e:
                print(f"Failed to load card image {card_path}: {str(e)}")
                self.card_images[plant] = pygame.Surface((70, 90))
                self.card_images[plant].fill((200, 100, 100))
    
    def create_plant(self, plant_type, position):
        """Create a new plant with animation"""
        plant_gif_path = f"images/Plants/{plant_type}/{plant_type}.gif"
        full_path = self.base_dir / plant_gif_path
        
        if not full_path.exists():
            print(f"Plant animation not found: {plant_gif_path}")
            return None
            
        anim = AnimatedSprite(str(full_path))
        return {
            "type": plant_type,
            "position": position,
            "anim": anim,
            "cooldown": 0,
            "health": 100
        }
    
    def create_zombie(self, zombie_type, position):
        """Create a new zombie with animation"""
        zombie_gif_path = f"images/Zombies/{zombie_type}/{zombie_type}.gif"
        full_path = self.base_dir / zombie_gif_path
        
        if not full_path.exists():
            print(f"Zombie animation not found: {zombie_gif_path}")
            return None
            
        anim = AnimatedSprite(str(full_path))
        return {
            "type": zombie_type,
            "position": position,
            "anim": anim,
            "speed": 0.5,
            "health": 100
        }
    
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
        """Plant a card at the specified grid position"""
        if self.DraggingCard and not self.Grid[row][col]:
            plant_type = self.DraggingCard["PName"]
            plant_cost = self.DraggingCard["Cost"]
            
            if self.SunNum >= plant_cost:
                self.SunNum -= plant_cost
                plant = self.create_plant(plant_type, (220 + col * 80, 120 + row * 100))
                if plant:
                    plant_id = f"plant_{row}_{col}"
                    self.Plants[plant_id] = plant
                    self.Grid[row][col] = plant_id
                    print(f"Planted {plant_type} at {row},{col}")
    
    def update(self, dt):
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
        """Render game elements"""
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw sun counter
        sun_text = self.big_font.render(str(self.SunNum), True, (0, 0, 0))
        self.screen.blit(sun_text, (70, 30))
        
        # Draw plant cards
        for card in self.ArCard:
            if card["PName"] in self.card_images:
                self.screen.blit(self.card_images[card["PName"]], card["Rect"])
                cost_text = self.font.render(str(card["Cost"]), True, (255, 255, 0))
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