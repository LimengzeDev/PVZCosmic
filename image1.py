import pygame
import sys
import os
import screen

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Path handling
current_dir = os.getcwd()
images_path = os.path.join(current_dir, "images")
music_path = os.path.join(current_dir, "music")

# Load music with error handling
try:
    pygame.mixer.music.load(os.path.join(music_path, 'Faster.mp3'))
    pygame.mixer.music.play(-1)
except pygame.error as e:
    print(f"Could not load music: {e}")


def load_image(path):
    """Helper function to load images with error handling"""
    try:
        return pygame.image.load(path).convert_alpha()
    except pygame.error as e:
        print(f"Could not load image {path}: {e}")
        return pygame.Surface((100, 100))  # Return blank surface if image fails to load


# Load images
surface = load_image(os.path.join(images_path, "interface", "Surface.png"))

# Adventure images
adventure = load_image(os.path.join(images_path, 'SelectorScreenAdventure.png'))
adventure_start = load_image(os.path.join(images_path, 'SelectorScreenStartAdventure.png'))
adventure_on = load_image(os.path.join(images_path, 'SelectorScreenAdventure1.png'))
adventure_start_on = load_image(os.path.join(images_path, 'SelectorScreenStartAdventure1.png'))

# Other UI elements
challenges = load_image(os.path.join(images_path, 'SelectorScreenChallenges.png'))
survival = load_image(os.path.join(images_path, 'SelectorScreenSurvival.png'))

# Wood signs
WoodSign1 = load_image(os.path.join(images_path, 'SelectorScreen_WoodSign1_32.png'))
WoodSign2_on = load_image(os.path.join(images_path, 'SelectorScreen_WoodSign2_32_1.png'))
WoodSign2 = load_image(os.path.join(images_path, 'SelectorScreen_WoodSign2_32.png'))
WoodSign3 = load_image(os.path.join(images_path, 'SelectorScreen_WoodSign3_32.png'))

# Shadows
survival_shadow = load_image(os.path.join(images_path, 'SelectorScreen_Shadow_Survival.png'))
adventure_shadow = load_image(os.path.join(images_path, 'SelectorScreen_Shadow_Adventure.png'))
challenges_shadow = load_image(os.path.join(images_path, 'SelectorScreen_Shadow_Challenge.png'))

# Set up WoodSign2 rectangle
WoodSign2_rect = WoodSign2.get_rect()
WoodSign2_rect.left, WoodSign2_rect.top = 20, 140
WoodSign2_rect.width, WoodSign2_rect.height = WoodSign2_rect.width - 20, WoodSign2_rect.height - 20


def interface():
    """Main interface function"""
    counter = 1  # Level counter

    # Set up adventure button based on counter
    if counter == 1:
        adv = adventure_start
        adv_on = adventure_start_on
    else:
        adv = adventure
        adv_on = adventure_on

    # Set up adventure button rectangles
    adv_rect1 = adv.get_rect()
    adv_rect1.left, adv_rect1.top = 478, 85
    adv_rect1.width, adv_rect1.height = adv_rect1.width - 9, adv_rect1.height - 70

    adv_rect2 = adv.get_rect()
    adv_rect2.left, adv_rect2.top = 478 + 205, 85 + 74
    adv_rect2.width, adv_rect2.height = 117, 23

    # Create buttons - ensure we're passing proper Rect objects
    adv_button = screen.GameButton(adv, adv_on, (adv_rect1, adv_rect2))

    # For WoodSign2 button, make sure we're passing a single Rect
    wood2_button = screen.GameButton(WoodSign2, WoodSign2_on, WoodSign2_rect)

    # Main game loop
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Handle mouse events
            if event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONDOWN:
                adv_button.is_on(event)
                wood2_button.is_on(event)

        # Rest of your drawing code...
        # Draw everything
        screen.screen1.blit(surface, (0, 0))
        screen.screen1.blit(WoodSign1, (10, 0))
        screen.screen1.blit(wood2_button.image, (10, 140))
        screen.screen1.blit(WoodSign3, (10, 200))
        screen.screen1.blit(adventure_shadow, (466, 54))
        screen.screen1.blit(survival_shadow, (476, 166))
        screen.screen1.blit(challenges_shadow, (481, 255))
        screen.screen1.blit(adv_button.image, (475, 53))
        screen.screen1.blit(survival, (475, 161))
        screen.screen1.blit(challenges, (480, 251))

        pygame.display.flip()
        clock.tick(60)  # Limit to 60 FPS

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    interface()