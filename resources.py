import pygame
import os

# Create resources directory if it doesn't exist
os.makedirs('resources/textures', exist_ok=True)

# Dictionary to hold loaded textures
textures = {}

def load_texture(name, filename):
    """Load a texture from file and store it in the textures dictionary"""
    try:
        full_path = os.path.join('resources/textures', filename)
        if not os.path.exists(full_path):
            # Create a default colored surface if the texture doesn't exist
            if "wall" in name:
                color = (100, 80, 60)  # Brown for walls
            elif "floor" in name:
                color = (150, 140, 120)  # Tan for floors
            elif "water" in name:
                color = (30, 144, 255)  # Blue for water
            elif "player" in name:
                color = (255, 215, 0)  # Gold for player
            elif "enemy" in name:
                color = (220, 20, 60)  # Crimson for enemies
            else:
                color = (200, 200, 200)  # Light gray default
            
            # Create a surface with the default color
            surface = pygame.Surface((32, 32))
            surface.fill(color)
            
            # Add some texture/pattern
            if "wall" in name:
                # Add brick pattern
                for i in range(4):
                    for j in range(8):
                        if (i + j) % 2 == 0:
                            pygame.draw.rect(surface, (80, 60, 40), (i*8, j*4, 8, 4))
            elif "floor" in name:
                # Add tiny dots for texture
                for i in range(8):
                    for j in range(8):
                        pygame.draw.rect(surface, (140, 130, 110), (i*4+1, j*4+1, 2, 2))
            elif "water" in name:
                # Add wave pattern
                for i in range(4):
                    pygame.draw.rect(surface, (70, 180, 255), (0, i*8, 32, 3))
            
            textures[name] = surface
            return surface
        
        texture = pygame.image.load(full_path).convert_alpha()
        textures[name] = texture
        return texture
    except pygame.error as e:
        print(f"Error loading texture {name}: {e}")
        # Create an error texture (purple/black checkerboard pattern)
        surface = pygame.Surface((32, 32))
        for i in range(4):
            for j in range(4):
                color = (255, 0, 255) if (i + j) % 2 == 0 else (0, 0, 0)
                pygame.draw.rect(surface, color, (i*8, j*8, 8, 8))
        textures[name] = surface
        return surface

def get_texture(name):
    """Get a texture from the dictionary, loading it if necessary"""
    if name not in textures:
        # Try to load the texture with a default filename based on the name
        filename = f"{name}.png"
        return load_texture(name, filename)
    return textures[name]

# Load all default textures
def load_default_textures():
    textures_to_load = {
        # Biomes
        "cave_wall": "cave_wall.png",
        "cave_floor": "cave_floor.png",
        "forest_wall": "forest_wall.png",
        "forest_floor": "forest_floor.png",
        "dungeon_wall": "dungeon_wall.png", 
        "dungeon_floor": "dungeon_floor.png",
        "village_wall": "village_wall.png",
        "village_floor": "village_floor.png",
        "mountain_wall": "mountain_wall.png",
        "mountain_floor": "mountain_floor.png",
        "ruins_wall": "ruins_wall.png",
        "ruins_floor": "ruins_floor.png",
        "swamp_wall": "swamp_wall.png",
        "swamp_floor": "swamp_floor.png",
        "clearing_wall": "clearing_wall.png",
        "clearing_floor": "clearing_floor.png",
        
        # Features
        "water": "water.png",
        "chest": "chest.png",
        "exit": "exit.png",
        
        # Entities
        "player": "player.png",
        
        # Enemy types
        "slime": "slime.png",
        "skeleton": "skeleton.png",
        "goblin": "goblin.png",
        "bat": "bat.png",
        "spider": "spider.png",
        
        # UI elements
        "heart_full": "heart_full.png",
        "heart_empty": "heart_empty.png",
        "title_background": "title_background.png",
        "logo": "logo.png"
    }
    
    for name, filename in textures_to_load.items():
        load_texture(name, filename)

# Initialize all textures
def init():
    load_default_textures()
