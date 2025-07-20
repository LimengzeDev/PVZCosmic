import json
import os
import pygame
import sys
from pathlib import Path

class GameEngine:
    def __init__(self, levels_folder="levels"):
        pygame.init()
        self.screen = pygame.display.set_mode((880, 600))
        self.clock = pygame.time.Clock()
        self.levels_folder = Path(levels_folder)
        self.current_level = None
        self.loaded_levels = {}
        self.load_all_levels()
        
        # Game state variables similar to 1000013378.js
        self.W = 880
        self.H = 600
        self.C = 9
        self.LawnMowerX = 70
        self.SunNum = 50
        self.Chose = 0
        self.ChoseCard = ""
        
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
        
        # Load assets
        self.load_assets()
        
    def load_assets(self):
        """Load images and audio for current level"""
        # Load images from PicArr paths
        self.images = {}
        for img_path in self.PicArr:
            try:
                self.images[img_path] = pygame.image.load(img_path)
            except:
                print(f"Failed to load image: {img_path}")
                
        # Set background
        bg_path = self.current_level.get("backgroundImage", "images/interface/background1.jpg")
        self.background = pygame.image.load(bg_path)
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            # Update game state
            self.update()
            
            # Render
            self.render()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()
    
    def update(self):
        """Update game logic"""
        # Placeholder for game logic
        pass
    
    def render(self):
        """Render game elements"""
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw other game elements here
        # (Would implement plant, zombie rendering based on 1000013378.js logic)

if __name__ == "__main__":
    game = GameEngine()
    if game.load_level("1"):  # Load level 1
        game.run()