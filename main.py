import pygame
import sys
import json
import random
import os
import math
from enum import Enum
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, field, asdict

# --- Constants ---
BASE_SCREEN_WIDTH = 1200
BASE_SCREEN_HEIGHT = 800
SCREEN_WIDTH = BASE_SCREEN_WIDTH
SCREEN_HEIGHT = BASE_SCREEN_HEIGHT
FPS = 60

# Enhanced color palette for adventure feel
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 150, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)

# Adventure theme colors
FLOOR_COLOR = (85, 107, 47)  # Dark olive green (default)
WALL_COLOR = (139, 69, 19)   # Saddle brown (default)

# Biome-specific colors
# Cave biome
CAVE_FLOOR_COLOR = (100, 100, 100)  # Gray floor
CAVE_WALL_COLOR = (70, 70, 80)      # Dark gray walls

# Forest biome
FOREST_FLOOR_COLOR = (85, 120, 40)  # Rich green floor
FOREST_WALL_COLOR = (60, 90, 30)    # Dark green walls (trees)

# Dungeon biome
DUNGEON_FLOOR_COLOR = (80, 70, 60)  # Stone floor
DUNGEON_WALL_COLOR = (50, 45, 40)   # Dark stone walls

# Village biome
VILLAGE_FLOOR_COLOR = (160, 140, 100)  # Dirt/path
VILLAGE_WALL_COLOR = (120, 80, 50)     # Wooden structure

# Mountain biome
MOUNTAIN_FLOOR_COLOR = (130, 130, 130)  # Rocky surface
MOUNTAIN_WALL_COLOR = (90, 90, 100)     # Cliff face

# Swamp biome
SWAMP_FLOOR_COLOR = (70, 80, 50)     # Muddy floor
SWAMP_WALL_COLOR = (50, 70, 40)      # Swamp vegetation

# Ruins biome
RUINS_FLOOR_COLOR = (150, 140, 120)   # Sandy ruins floor
RUINS_WALL_COLOR = (120, 110, 90)     # Weathered stone

# Clearing biome
CLEARING_FLOOR_COLOR = (130, 180, 70)  # Vibrant grass
CLEARING_WALL_COLOR = (90, 140, 40)    # Dense foliage

# Other theme colors
PLAYER_COLOR = (255, 215, 0) # Gold
ITEM_COLOR = (255, 215, 0)   # Gold
NPC_COLOR = (150, 0, 150)    # Purple
TEXT_COLOR = WHITE
UI_BG_COLOR = (25, 25, 25)   # Very dark gray
UI_BORDER_COLOR = (139, 69, 19) # Brown border
QUEST_COLOR = (255, 165, 0)  # Orange
SPECIAL_ITEM_COLOR = (255, 105, 180) # Hot pink
ADVENTURE_GOLD = (218, 165, 32)
ADVENTURE_BROWN = (160, 82, 45)
TOOLTIP_BG = (40, 40, 40)

FONT_NAME = None
FONT_SIZE_LARGE = 42
FONT_SIZE_MEDIUM = 28
FONT_SIZE_SMALL = 20
FONT_SIZE_TINY = 16
SAVE_FILE = "savegame.json"
SETTINGS_FILE = "settings.json"

TILE_SIZE = 32
GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // TILE_SIZE

# Audio settings
DEFAULT_MASTER_VOLUME = 0.7
DEFAULT_SFX_VOLUME = 0.8
DEFAULT_MUSIC_VOLUME = 0.6

class TileType(Enum):
    FLOOR = 0
    WALL = 1
    EXIT = 2
    WATER = 3  # New tile type
    CHEST = 4  # Treasure chests

class GameState(Enum):
    TITLE_SCREEN = 0  # New title screen state
    NAME_INPUT = 1
    PLAYING = 2
    MENU = 3
    INVENTORY = 4
    DIALOGUE = 5
    GAME_OVER = 6
    QUEST_LOG = 7  # Quest management
    SETTINGS = 8   # Settings menu
    SAVE_MENU = 9  # Save game menu with slots
    LOAD_MENU = 10 # Load game menu with slots

class ItemType(Enum):
    CONSUMABLE = 1
    KEY_ITEM = 2
    WEAPON = 3
    TREASURE = 4

class QuestStatus(Enum):
    NOT_STARTED = 1
    ACTIVE = 2
    COMPLETED = 3

@dataclass
class GameSettings:
    master_volume: float = DEFAULT_MASTER_VOLUME
    sfx_volume: float = DEFAULT_SFX_VOLUME
    music_volume: float = DEFAULT_MUSIC_VOLUME
    screen_scale: float = 1.0
    fullscreen: bool = False
    
    def to_dict(self):
        return {
            'master_volume': self.master_volume,
            'sfx_volume': self.sfx_volume,
            'music_volume': self.music_volume,
            'screen_scale': self.screen_scale,
            'fullscreen': self.fullscreen
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            master_volume=data.get('master_volume', DEFAULT_MASTER_VOLUME),
            sfx_volume=data.get('sfx_volume', DEFAULT_SFX_VOLUME),
            music_volume=data.get('music_volume', DEFAULT_MUSIC_VOLUME),
            screen_scale=data.get('screen_scale', 1.0),
            fullscreen=data.get('fullscreen', False)
        )

@dataclass
class Quest:
    id: str
    title: str
    description: str
    status: QuestStatus = QuestStatus.NOT_STARTED
    objectives: List[str] = field(default_factory=list)
    completed_objectives: List[bool] = field(default_factory=list)
    reward_items: List[str] = field(default_factory=list)
    reward_text: str = ""
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status.value,
            'objectives': self.objectives,
            'completed_objectives': self.completed_objectives,
            'reward_items': self.reward_items,
            'reward_text': self.reward_text
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data['id'],
            title=data['title'],
            description=data['description'],
            status=QuestStatus(data['status']),
            objectives=data.get('objectives', []),
            completed_objectives=data.get('completed_objectives', []),
            reward_items=data.get('reward_items', []),
            reward_text=data.get('reward_text', '')
        )

@dataclass
class Item:
    name: str
    description: str
    item_type: ItemType = ItemType.CONSUMABLE
    quantity: int = 1
    value: int = 0  # For trading/selling
    # For 2D placement
    x: Optional[int] = None # Tile X
    y: Optional[int] = None # Tile Y
    
    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'item_type': self.item_type.value,
            'quantity': self.quantity,
            'value': self.value,
            'x': self.x,
            'y': self.y
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data['name'],
            description=data['description'],
            item_type=ItemType(data.get('item_type', 1)),
            quantity=data.get('quantity', 1),
            value=data.get('value', 0),
            x=data.get('x'),
            y=data.get('y')
        )

@dataclass
class Player:
    name: str
    rect: pygame.Rect # Player's position and size
    current_room: str
    inventory: List[Item] = field(default_factory=list)
    health: int = 100
    max_health: int = 100
    speed: int = 5 # Pixels per frame
    level: int = 1
    experience: int = 0
    gold: int = 50  # Starting gold
    active_quests: List[str] = field(default_factory=list)  # Quest IDs

    def to_dict(self):
        return {
            'name': self.name,
            'rect': {'x': self.rect.x, 'y': self.rect.y, 'width': self.rect.width, 'height': self.rect.height},
            'current_room': self.current_room,
            'inventory': [item.to_dict() for item in self.inventory],
            'health': self.health,
            'max_health': self.max_health,
            'speed': self.speed,
            'level': self.level,
            'experience': self.experience,
            'gold': self.gold,
            'active_quests': self.active_quests
        }
    
    @classmethod
    def from_dict(cls, data):
        inventory = [Item.from_dict(item) for item in data.get('inventory', [])]
        rect_data = data['rect']
        rect = pygame.Rect(rect_data['x'], rect_data['y'], rect_data['width'], rect_data['height'])
        return cls(
            name=data['name'],
            rect=rect,
            current_room=data['current_room'],
            inventory=inventory,
            health=data.get('health', 100),
            max_health=data.get('max_health', 100),
            speed=data.get('speed', 5),
            level=data.get('level', 1),
            experience=data.get('experience', 0),
            gold=data.get('gold', 50),
            active_quests=data.get('active_quests', [])
        )

    def has_item(self, item_name: str) -> bool:
        return any(item.name == item_name for item in self.inventory)
    
    def get_item(self, item_name: str) -> Optional[Item]:
        for item in self.inventory:
            if item.name == item_name:
                return item
        return None
    
    def remove_item(self, item_name: str, quantity: int = 1) -> bool:
        for item in self.inventory:
            if item.name == item_name:
                if item.quantity >= quantity:
                    item.quantity -= quantity
                    if item.quantity <= 0:
                        self.inventory.remove(item)
                    return True
        return False

@dataclass
class NPC:
    name: str
    rect: pygame.Rect # NPC's position and size
    dialogue_options: List[str] # Different lines or choices
    color: Tuple[int,int,int] = NPC_COLOR
    quest_giver: bool = False
    quest_id: Optional[str] = None
    shop_items: List[Item] = field(default_factory=list)  # For merchant NPCs

    def to_dict(self):
        return {
            'name': self.name,
            'rect': {'x': self.rect.x, 'y': self.rect.y, 'width': self.rect.width, 'height': self.rect.height},
            'dialogue_options': self.dialogue_options,
            'color': self.color,
            'quest_giver': self.quest_giver,
            'quest_id': self.quest_id,
            'shop_items': [item.to_dict() for item in self.shop_items]
        }
    
    @classmethod
    def from_dict(cls, data):
        rect_data = data['rect']
        rect = pygame.Rect(rect_data['x'], rect_data['y'], rect_data['width'], rect_data['height'])
        shop_items = [Item.from_dict(item_data) for item_data in data.get('shop_items', [])]
        return cls(
            name=data['name'],
            rect=rect,
            dialogue_options=data['dialogue_options'],
            color=tuple(data.get('color', NPC_COLOR)),
            quest_giver=data.get('quest_giver', False),
            quest_id=data.get('quest_id'),
            shop_items=shop_items
        )


class Room:
    def __init__(self, name: str, grid_width: int, grid_height: int, room_type: str = "cave"):
        self.name = name
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.room_type = room_type  # cave, forest, dungeon, village, etc.
        self.grid: List[List[TileType]] = []
        self.items: List[Item] = []
        self.npcs: List[NPC] = []
        self.exits: Dict[str, Tuple[str, int, int]] = {} # direction: (target_room_name, entry_tile_x, entry_tile_y)
        self.visited = False
        self.difficulty_level = 1  # For procedural content scaling
        self.generate_procedural_layout()

    def generate_procedural_layout(self):
        # Initialize grid with floors instead of walls
        self.grid = [[TileType.FLOOR for _ in range(self.grid_width)] for _ in range(self.grid_height)]

        # No more wall margins - the entire room is open
        room_x = 0
        room_y = 0
        room_w = self.grid_width
        room_h = self.grid_height
        
        # Add scattered walls and features in the room interior for more interesting layouts
        # This will be primarily done by the biome-specific generation functions
        
        # Add potential exit tiles on all edges for infinite generation
        self.add_potential_exits()
        
        # Generate room-specific features based on type
        if self.room_type == "cave":
            self.generate_cave_features()
        elif self.room_type == "forest":
            self.generate_forest_features()
        elif self.room_type == "dungeon":
            self.generate_dungeon_features()
        elif self.room_type == "village":
            self.generate_village_features()
        elif self.room_type == "clearing":
            self.generate_clearing_features()
        elif self.room_type == "ruins":
            self.generate_ruins_features()
        elif self.room_type == "swamp":
            self.generate_swamp_features()
        elif self.room_type == "mountain":
            self.generate_mountain_features()
        else:
            self.generate_generic_features()
    
    def generate_clearing_features(self):
        """Generate clearing-specific features like flowers and peaceful elements with natural patterns"""
        room_x, room_y = 2, 2
        room_w, room_h = self.grid_width - 4, self.grid_height - 4
        
        # Create a central clearing area
        clearing_center_x = room_x + room_w // 2
        clearing_center_y = room_y + room_h // 2
        clearing_radius = min(room_w, room_h) // 3
        
        # Add a ring of trees/rocks around the outer edges of the clearing
        edge_features = []
        num_edge_features = random.randint(15, 25)  # More features for natural look
        
        # Distribute edge features evenly around the perimeter
        for i in range(num_edge_features):
            angle = 2 * math.pi * i / num_edge_features
            
            # Get position on an elliptical perimeter
            perimeter_x = clearing_center_x + int((room_w / 2 - 3) * math.cos(angle))
            perimeter_y = clearing_center_y + int((room_h / 2 - 3) * math.sin(angle))
            
            # Add small variation
            perimeter_x += random.randint(-2, 2)
            perimeter_y += random.randint(-2, 2)
            
            # Ensure within bounds
            perimeter_x = max(room_x + 1, min(room_x + room_w - 2, perimeter_x))
            perimeter_y = max(room_y + 1, min(room_y + room_h - 2, perimeter_y))
            
            edge_features.append((perimeter_x, perimeter_y))
        
        # Place trees/rocks (wall tiles) at the edge of the clearing
        for feature_x, feature_y in edge_features:
            # Create small clusters for each feature point
            feature_size = random.randint(1, 2)
            for dy in range(-feature_size, feature_size + 1):
                for dx in range(-feature_size, feature_size + 1):
                    if random.random() < 0.7 / (abs(dx) + abs(dy) + 0.5):  # More concentrated near center
                        nx, ny = feature_x + dx, feature_y + dy
                        if (room_x <= nx < room_x + room_w and 
                            room_y <= ny < room_y + room_h):
                            self.grid[ny][nx] = TileType.WALL
        
        # Add flower patches (represented with alternative floor patterns)
        num_patches = random.randint(4, 8)
        for _ in range(num_patches):
            # Flower patches more likely in the central area
            dist = random.random() * clearing_radius
            angle = random.uniform(0, 2 * math.pi)
            patch_x = int(clearing_center_x + dist * math.cos(angle))
            patch_y = int(clearing_center_y + dist * math.sin(angle))
            
            # Vary patch size
            patch_size = random.randint(2, 4)
            
            # Create natural-looking flower patch shape
            for dy in range(-patch_size, patch_size + 1):
                for dx in range(-patch_size, patch_size + 1):
                    dist_from_center = math.sqrt(dx**2 + dy**2)
                    if (dist_from_center <= patch_size * random.uniform(0.5, 0.8) and
                        patch_y + dy < room_y + room_h - 1 and 
                        patch_x + dx < room_x + room_w - 1 and
                        patch_y + dy >= room_y and 
                        patch_x + dx >= room_x):
                        # Keep as floor but add visual elements
                        # In the future this could be a special tile type
                        pass  # Flowers would be represented visually
        
        # Add a small water feature in the center
        if random.random() < 0.7:  # 70% chance for central water feature
            water_size = random.randint(2, 3)
            for dy in range(-water_size, water_size + 1):
                for dx in range(-water_size, water_size + 1):
                    dist_from_center = math.sqrt(dx**2 + dy**2)
                    if (dist_from_center < water_size * 0.8 and  # Oval shape
                        clearing_center_y + dy < room_y + room_h - 1 and 
                        clearing_center_x + dx < room_x + room_w - 1 and
                        clearing_center_y + dy >= room_y and
                        clearing_center_x + dx >= room_x):
                        self.grid[clearing_center_y + dy][clearing_center_x + dx] = TileType.WATER
        
        # Add a few scattered standalone trees/rocks inside the clearing
        num_standalone = random.randint(3, 6)
        for _ in range(num_standalone):
            # Position away from center
            dist = random.random() * clearing_radius * 0.7
            angle = random.uniform(0, 2 * math.pi)
            feature_x = int(clearing_center_x + dist * math.cos(angle))
            feature_y = int(clearing_center_y + dist * math.sin(angle))
            
            if (room_x < feature_x < room_x + room_w - 1 and 
                room_y < feature_y < room_y + room_h - 1):
                self.grid[feature_y][feature_x] = TileType.WALL
    
    def generate_ruins_features(self):
        """Generate ruins-specific features like broken walls and debris with natural patterns"""
        room_x, room_y = 2, 2
        room_w, room_h = self.grid_width - 4, self.grid_height - 4
        
        # Create different types of ruins with distinct architectural patterns
        ruin_types = ["temple", "building", "wall", "monument"]
        num_ruins = random.randint(2, 4)
        
        for _ in range(num_ruins):
            ruin_type = random.choice(ruin_types)
            
            if ruin_type == "temple":
                # Create temple ruins (rectangular structure with columns)
                temple_w = random.randint(6, 9)
                temple_h = random.randint(5, 8)
                temple_x = random.randint(room_x + 2, room_x + room_w - temple_w - 2)
                temple_y = random.randint(room_y + 2, room_y + room_h - temple_h - 2)
                
                # Create temple outline (with gaps for broken walls)
                for dy in range(temple_h):
                    for dx in range(temple_w):
                        # Only draw perimeter
                        if dy == 0 or dy == temple_h - 1 or dx == 0 or dx == temple_w - 1:
                            # Add gaps for ruins effect
                            if random.random() < 0.7:  # 70% chance for wall piece
                                if temple_y + dy < self.grid_height and temple_x + dx < self.grid_width:
                                    self.grid[temple_y + dy][temple_x + dx] = TileType.WALL
                
                # Add columns (regularly spaced but some missing)
                col_spacing = 2
                for col_x in range(temple_x + 2, temple_x + temple_w - 2, col_spacing):
                    # Front row columns
                    if random.random() < 0.7:  # 70% chance for column
                        if temple_y + 1 < self.grid_height and col_x < self.grid_width:
                            self.grid[temple_y + 1][col_x] = TileType.WALL
                    
                    # Back row columns
                    if random.random() < 0.7:  # 70% chance for column
                        if temple_y + temple_h - 2 < self.grid_height and col_x < self.grid_width:
                            self.grid[temple_y + temple_h - 2][col_x] = TileType.WALL
                
            elif ruin_type == "building":
                # Create building ruins (rooms with corridors)
                building_w = random.randint(5, 8)
                building_h = random.randint(5, 7)
                building_x = random.randint(room_x + 1, room_x + room_w - building_w - 1)
                building_y = random.randint(room_y + 1, room_y + room_h - building_h - 1)
                
                # Create room divisions (partial walls inside)
                num_divisions = random.randint(1, 3)
                for _ in range(num_divisions):
                    is_horizontal = random.choice([True, False])
                    
                    if is_horizontal:
                        div_y = building_y + random.randint(2, building_h - 2)
                        for dx in range(building_w):
                            # Create gaps in the division wall
                            if random.random() < 0.8 and building_x + dx < self.grid_width and div_y < self.grid_height:  # 80% chance
                                self.grid[div_y][building_x + dx] = TileType.WALL
                    else:
                        div_x = building_x + random.randint(2, building_w - 2)
                        for dy in range(building_h):
                            # Create gaps in the division wall
                            if random.random() < 0.8 and div_x < self.grid_width and building_y + dy < self.grid_height:  # 80% chance
                                self.grid[building_y + dy][div_x] = TileType.WALL
                
                # Create the outer walls with larger gaps (more broken)
                for dy in range(building_h):
                    for dx in range(building_w):
                        if dy == 0 or dy == building_h - 1 or dx == 0 or dx == building_w - 1:
                            if random.random() < 0.65:  # 65% chance for wall
                                if building_y + dy < self.grid_height and building_x + dx < self.grid_width:
                                    self.grid[building_y + dy][building_x + dx] = TileType.WALL
            
            elif ruin_type == "wall":
                # Create a linear wall ruin
                wall_length = random.randint(8, 15)
                is_horizontal = random.choice([True, False])
                
                if is_horizontal:
                    wall_y = random.randint(room_y + 2, room_y + room_h - 3)
                    wall_x = random.randint(room_x + 2, room_x + room_w - wall_length - 2)
                    
                    # Draw the wall with gaps and occasional thickness
                    for dx in range(wall_length):
                        if random.random() < 0.85:  # 85% chance for wall segment
                            if wall_y < self.grid_height and wall_x + dx < self.grid_width:
                                self.grid[wall_y][wall_x + dx] = TileType.WALL
                                
                                # Sometimes make the wall thicker
                                if random.random() < 0.4:  # 40% chance
                                    thickness = random.choice([-1, 1])
                                    if 0 <= wall_y + thickness < self.grid_height:
                                        self.grid[wall_y + thickness][wall_x + dx] = TileType.WALL
                else:
                    wall_x = random.randint(room_x + 2, room_x + room_w - 3)
                    wall_y = random.randint(room_y + 2, room_y + room_h - wall_length - 2)
                    
                    # Draw the wall with gaps
                    for dy in range(wall_length):
                        if random.random() < 0.85:  # 85% chance for wall segment
                            if wall_y + dy < self.grid_height and wall_x < self.grid_width:
                                self.grid[wall_y + dy][wall_x] = TileType.WALL
                                
                                # Sometimes make the wall thicker
                                if random.random() < 0.4:  # 40% chance
                                    thickness = random.choice([-1, 1])
                                    if 0 <= wall_x + thickness < self.grid_width:
                                        self.grid[wall_y + dy][wall_x + thickness] = TileType.WALL
            
            elif ruin_type == "monument":
                # Create a monument ruin (circular or special pattern)
                monument_x = random.randint(room_x + 5, room_x + room_w - 6)
                monument_y = random.randint(room_y + 5, room_y + room_h - 6)
                monument_size = random.randint(3, 5)
                
                # Draw circular monument
                for dy in range(-monument_size, monument_size + 1):
                    for dx in range(-monument_size, monument_size + 1):
                        distance = math.sqrt(dx*dx + dy*dy)
                        if monument_size - 0.8 <= distance <= monument_size and random.random() < 0.75:
                            if (monument_y + dy < self.grid_height and monument_x + dx < self.grid_width and
                                monument_y + dy >= room_y and monument_x + dx >= room_x):
                                self.grid[monument_y + dy][monument_x + dx] = TileType.WALL
                
                # Add some internal structure
                if random.random() < 0.7:  # 70% chance
                    for dy in range(-1, 2):
                        for dx in range(-1, 2):
                            if abs(dx) + abs(dy) <= 1:  # Cross pattern
                                if (monument_y + dy < self.grid_height and monument_x + dx < self.grid_width and
                                    monument_y + dy >= room_y and monument_x + dx >= room_x):
                                    self.grid[monument_y + dy][monument_x + dx] = TileType.WALL
        
        # Add scattered debris (small rubble piles)
        num_debris = random.randint(6, 12)
        for _ in range(num_debris):
            debris_x = random.randint(room_x + 1, room_x + room_w - 3)
            debris_y = random.randint(room_y + 1, room_y + room_h - 3)
            debris_size = random.randint(1, 2)
            
            # Create small debris cluster
            for dy in range(-debris_size, debris_size + 1):
                for dx in range(-debris_size, debris_size + 1):
                    if random.random() < 0.4 / (abs(dx) + abs(dy) + 0.5):  # More likely near center
                        if (room_y <= debris_y + dy < room_y + room_h and
                            room_x <= debris_x + dx < room_x + room_w):
                            self.grid[debris_y + dy][debris_x + dx] = TileType.WALL
    
    def generate_swamp_features(self):
        """Generate swamp-specific features like water and muddy areas with natural patterns"""
        room_x, room_y = 2, 2
        room_w, room_h = self.grid_width - 4, self.grid_height - 4
        
        # Create interconnected water pools with organically shaped edges
        num_pools = random.randint(3, 5)
        pool_centers = []
        
        # Place pool centers
        for _ in range(num_pools):
            pool_x = random.randint(room_x + 4, room_x + room_w - 5)
            pool_y = random.randint(room_y + 4, room_y + room_h - 5)
            pool_size = random.randint(4, 7)
            pool_centers.append((pool_x, pool_y, pool_size))
        
        # Create organic water pools
        for center_x, center_y, size in pool_centers:
            # Draw irregular pool shape
            for dy in range(-size, size + 1):
                for dx in range(-size, size + 1):
                    # Create oval-like shape with noise
                    dist = math.sqrt((dx/1.5)**2 + (dy/1.8)**2) + random.uniform(-0.8, 0.8)
                    
                    # More likely to place water near center
                    if (center_y + dy < room_y + room_h - 1 and 
                        center_x + dx < room_x + room_w - 1 and
                        center_y + dy >= room_y and center_x + dx >= room_x and
                        dist <= size * random.uniform(0.5, 0.9)):
                        self.grid[center_y + dy][center_x + dx] = TileType.WATER
        
        # Connect some pools with water channels
        if len(pool_centers) >= 2:
            for i in range(len(pool_centers) - 1):
                start_x, start_y, _ = pool_centers[i]
                end_x, end_y, _ = pool_centers[i+1]
                
                # Create a meandering water channel
                points = []
                steps = max(abs(end_x - start_x), abs(end_y - start_y))
                steps = max(5, steps)  # Ensure minimum number of steps
                
                for step in range(steps + 1):
                    # Linear interpolation with random deviation
                    t = step / steps
                    deviation = random.randint(-3, 3)
                    point_x = int(start_x * (1-t) + end_x * t) + deviation
                    point_y = int(start_y * (1-t) + end_y * t) + deviation
                    points.append((point_x, point_y))
                
                # Draw the water channel
                for point_x, point_y in points:
                    if (room_x < point_x < room_x + room_w - 1 and
                        room_y < point_y < room_y + room_h - 1):
                        self.grid[point_y][point_x] = TileType.WATER
                        
                        # Add width to the channel
                        for dy in range(-1, 2):
                            for dx in range(-1, 2):
                                if random.random() < 0.4:  # 40% chance
                                    nx, ny = point_x + dx, point_y + dy
                                    if (room_x < nx < room_x + room_w - 1 and
                                        room_y < ny < room_y + room_h - 1):
                                        self.grid[ny][nx] = TileType.WATER
        
        # Add vegetation (wall tiles) around water
        for r_idx in range(room_y, room_y + room_h):
            for c_idx in range(room_x, room_x + room_w):
                if self.grid[r_idx][c_idx] == TileType.FLOOR:
                    # Check if near water
                    near_water = False
                    for dy in range(-1, 2):
                        for dx in range(-1, 2):
                            ny, nx = r_idx + dy, c_idx + dx
                            if (0 <= ny < self.grid_height and 0 <= nx < self.grid_width and
                                self.grid[ny][nx] == TileType.WATER):
                                near_water = True
                                break
                        if near_water:
                            break
                    
                    # Place vegetation near water with higher probability
                    if near_water and random.random() < 0.3:  # 30% chance
                        self.grid[r_idx][c_idx] = TileType.WALL
    
    def generate_mountain_features(self):
        """Generate mountain-specific features like rocky outcrops in natural patterns"""
        room_x, room_y = 2, 2
        room_w, room_h = self.grid_width - 4, self.grid_height - 4
        
        # Create mountain ridge formations with natural clustering
        num_formations = random.randint(3, 5)
        for _ in range(num_formations):
            # Choose starting points for ridge lines
            ridge_start_x = random.randint(room_x + 2, room_x + room_w - 3)
            ridge_start_y = random.randint(room_y + 2, room_y + room_h - 3)
            
            # Ridge length and direction
            ridge_length = random.randint(5, 10)
            angle = random.uniform(0, 2 * 3.14159)  # Random angle in radians
            
            # Draw ridge line
            for i in range(ridge_length):
                # Calculate position along the ridge with some natural variation
                dx = int(i * math.cos(angle) + random.uniform(-0.5, 0.5))
                dy = int(i * math.sin(angle) + random.uniform(-0.5, 0.5))
                rock_x = ridge_start_x + dx
                rock_y = ridge_start_y + dy
                
                # Ensure within room bounds
                if (room_x < rock_x < room_x + room_w - 1 and
                    room_y < rock_y < room_y + room_h - 1):
                    self.grid[rock_y][rock_x] = TileType.WALL
                    
                    # Add some smaller rocks around the main ridge
                    for _ in range(2):
                        scatter_dx = random.randint(-2, 2)
                        scatter_dy = random.randint(-2, 2)
                        scatter_x = rock_x + scatter_dx
                        scatter_y = rock_y + scatter_dy
                        
                        # More rocks closer to ridge, fewer further away
                        if (room_x < scatter_x < room_x + room_w - 1 and
                            room_y < scatter_y < room_y + room_h - 1 and
                            random.random() < 0.7 / (abs(scatter_dx) + abs(scatter_dy) + 0.1)):
                            self.grid[scatter_y][scatter_x] = TileType.WALL
        
        # Add boulders (small clusters of rocks)
        num_boulders = random.randint(4, 8)
        for _ in range(num_boulders):
            boulder_x = random.randint(room_x + 1, room_x + room_w - 3)
            boulder_y = random.randint(room_y + 1, room_y + room_h - 3)
            boulder_size = random.randint(2, 4)
            
            for dy in range(-boulder_size, boulder_size + 1):
                for dx in range(-boulder_size, boulder_size + 1):
                    # Create boulder with circular pattern
                    distance = math.sqrt(dx**2 + dy**2)
                    if distance <= boulder_size and random.random() < (boulder_size - distance) / boulder_size:
                        rock_x = boulder_x + dx
                        rock_y = boulder_y + dy
                        if (room_x < rock_x < room_x + room_w - 1 and
                            room_y < rock_y < room_y + room_h - 1):
                            self.grid[rock_y][rock_x] = TileType.WALL
    
    def add_potential_exits(self):
        """Add potential exit tiles on room edges for infinite generation"""
        # Add exit tiles at multiple positions along each edge for more options
        
        # North edge - add 2-3 exits spaced out
        num_n_exits = random.randint(2, 3)
        n_exit_positions = [int(self.grid_width * (i+1)/(num_n_exits+1)) for i in range(num_n_exits)]
        for pos in n_exit_positions:
            self.grid[0][pos] = TileType.EXIT
        
        # South edge - add 2-3 exits spaced out  
        num_s_exits = random.randint(2, 3)
        s_exit_positions = [int(self.grid_width * (i+1)/(num_s_exits+1)) for i in range(num_s_exits)]
        for pos in s_exit_positions:
            self.grid[self.grid_height - 1][pos] = TileType.EXIT
        
        # West edge - add 2-3 exits spaced out
        num_w_exits = random.randint(2, 3)
        w_exit_positions = [int(self.grid_height * (i+1)/(num_w_exits+1)) for i in range(num_w_exits)]
        for pos in w_exit_positions:
            self.grid[pos][0] = TileType.EXIT
        
        # East edge - add 2-3 exits spaced out
        num_e_exits = random.randint(2, 3)
        e_exit_positions = [int(self.grid_height * (i+1)/(num_e_exits+1)) for i in range(num_e_exits)]
        for pos in e_exit_positions:
            self.grid[pos][self.grid_width - 1] = TileType.EXIT
            
        # Mark the edge with a special indicator
        # This creates a subtle visual edge without walls
        for x in range(self.grid_width):
            # Only mark if it's not already an exit
            if self.grid[0][x] != TileType.EXIT:
                self.grid[0][x] = TileType.FLOOR
            if self.grid[self.grid_height - 1][x] != TileType.EXIT:
                self.grid[self.grid_height - 1][x] = TileType.FLOOR
                
        for y in range(self.grid_height):
            # Only mark if it's not already an exit
            if self.grid[y][0] != TileType.EXIT:
                self.grid[y][0] = TileType.FLOOR
            if self.grid[y][self.grid_width - 1] != TileType.EXIT:
                self.grid[y][self.grid_width - 1] = TileType.FLOOR

    def generate_cave_features(self):
        """Generate cave-specific features like stalactites, water pools"""
        room_x, room_y = 2, 2
        room_w, room_h = self.grid_width - 4, self.grid_height - 4
        
        # Add rock formations in natural-looking clumps
        num_formations = random.randint(3, 6)
        for _ in range(num_formations):
            if room_w > 6 and room_h > 6:
                # Choose a central point for the formation
                center_x = random.randint(room_x + 2, room_x + room_w - 3)
                center_y = random.randint(room_y + 2, room_y + room_h - 3)
                
                # Create a randomized cluster of rocks around the center
                formation_size = random.randint(3, 7)
                for i in range(formation_size * 2):
                    # Calculate position with proximity to center (more likely closer)
                    dx = int(random.gauss(0, formation_size / 3))
                    dy = int(random.gauss(0, formation_size / 3))
                    rock_x = center_x + dx
                    rock_y = center_y + dy
                    
                    # Ensure within room bounds
                    if (room_x < rock_x < room_x + room_w - 1 and 
                        room_y < rock_y < room_y + room_h - 1):
                        self.grid[rock_y][rock_x] = TileType.WALL
        
        # Add stalactite pillars in corners and edges more naturally
        num_pillars = random.randint(3, 7)
        for _ in range(num_pillars):
            # Pick a position biased toward edges
            edge_bias = random.choice([0, 1])  # 0 = close to edge, 1 = anywhere
            if edge_bias == 0:
                # Close to edge
                if random.choice([True, False]):  # horizontal edge
                    pillar_x = random.randint(room_x + 1, room_x + room_w - 2)
                    pillar_y = random.choice([room_y + random.randint(0, 3), 
                                             room_y + room_h - random.randint(1, 4)])
                else:  # vertical edge
                    pillar_x = random.choice([room_x + random.randint(0, 3), 
                                             room_x + room_w - random.randint(1, 4)])
                    pillar_y = random.randint(room_y + 1, room_y + room_h - 2)
            else:
                # Anywhere in room
                pillar_x = random.randint(room_x + 1, room_x + room_w - 2)
                pillar_y = random.randint(room_y + 1, room_y + room_h - 2)
                
            if 0 <= pillar_y < self.grid_height and 0 <= pillar_x < self.grid_width:
                self.grid[pillar_y][pillar_x] = TileType.WALL
                
                # Add some smaller rocks around the pillar
                for i in range(random.randint(1, 3)):
                    dx = random.randint(-1, 1)
                    dy = random.randint(-1, 1)
                    nx, ny = pillar_x + dx, pillar_y + dy
                    if (room_x < nx < room_x + room_w - 1 and 
                        room_y < ny < room_y + room_h - 1 and
                        random.random() < 0.6):  # 60% chance
                        self.grid[ny][nx] = TileType.WALL
        
        # Add water pools with more natural, irregular shapes
        num_pools = random.randint(1, 3)
        for _ in range(num_pools):
            pool_x = random.randint(room_x + 1, room_x + room_w - 6)
            pool_y = random.randint(room_y + 1, room_y + room_h - 6)
            pool_size = random.randint(3, 5)
            
            # Generate organic-looking water pool
            for dy in range(-1, pool_size + 1):
                for dx in range(-1, pool_size + 1):
                    # Calculate distance from center (for oval shape)
                    dist_from_center = ((dx - pool_size/2)**2 / (pool_size/1.5)**2 + 
                                       (dy - pool_size/2)**2 / (pool_size/1.8)**2)
                    
                    # More likely to place water near center
                    if (pool_y + dy < room_y + room_h - 1 and 
                        pool_x + dx < room_x + room_w - 1 and
                        pool_y + dy >= room_y and pool_x + dx >= room_x and
                        dist_from_center <= random.uniform(0.3, 0.7)):
                        self.grid[pool_y + dy][pool_x + dx] = TileType.WATER

    def generate_forest_features(self):
        """Generate forest-specific features like tree groves with natural clustering"""
        room_x, room_y = 2, 2
        room_w, room_h = self.grid_width - 4, self.grid_height - 4
        
        # Create forest tree clusters with natural patterns
        num_groves = random.randint(3, 6)  # More tree groves
        for _ in range(num_groves):
            # Choose a central point for the grove
            center_x = random.randint(room_x + 3, room_x + room_w - 4)
            center_y = random.randint(room_y + 3, room_y + room_h - 4)
            
            # Use Gaussian distribution for natural-looking clusters
            grove_size = random.randint(3, 6)  # Larger groves
            num_trees = grove_size * 3  # More trees per grove
            
            for _ in range(num_trees):
                # Trees are more likely to be near the center of the grove
                dx = int(random.gauss(0, grove_size / 2.5))
                dy = int(random.gauss(0, grove_size / 2.5))
                tree_x = center_x + dx
                tree_y = center_y + dy
                
                # Ensure within room bounds
                if (room_x < tree_x < room_x + room_w - 1 and
                    room_y < tree_y < room_y + room_h - 1):
                    self.grid[tree_y][tree_x] = TileType.WALL
                    
                    # Occasionally add smaller bushes around trees
                    if random.random() < 0.3:  # 30% chance for bushes
                        bush_dx = random.choice([-1, 0, 1])
                        bush_dy = random.choice([-1, 0, 1])
                        bush_x = tree_x + bush_dx
                        bush_y = tree_y + bush_dy
                        if (room_x < bush_x < room_x + room_w - 1 and
                            room_y < bush_y < room_y + room_h - 1):
                            self.grid[bush_y][bush_x] = TileType.WALL

    def generate_dungeon_features(self):
        """Generate dungeon-specific features like chambers and corridors with realistic wall patterns"""
        room_x, room_y = 2, 2
        room_w, room_h = self.grid_width - 4, self.grid_height - 4
        
        # Create small chambers with varying architectural styles
        num_chambers = random.randint(2, 3)
        chambers = []
        
        for _ in range(num_chambers):
            chamber_w = random.randint(5, 8)
            chamber_h = random.randint(5, 8)
            chamber_x = random.randint(room_x + 2, room_x + room_w - chamber_w - 2)
            chamber_y = random.randint(room_y + 2, room_y + room_h - chamber_h - 2)
            
            # Create chamber walls with occasional crumbling sections
            for dy in range(chamber_h):
                for dx in range(chamber_w):
                    if (dy == 0 or dy == chamber_h - 1 or dx == 0 or dx == chamber_w - 1):
                        # Add wall with occasional gaps for "crumbling" effect
                        if chamber_y + dy < self.grid_height and chamber_x + dx < self.grid_width:
                            # Corners are always walls
                            if (dy == 0 and dx == 0) or (dy == 0 and dx == chamber_w - 1) or \
                               (dy == chamber_h - 1 and dx == 0) or (dy == chamber_h - 1 and dx == chamber_w - 1):
                                self.grid[chamber_y + dy][chamber_x + dx] = TileType.WALL
                            # Other edge tiles have a small chance to be floor (crumbling effect)
                            elif random.random() < 0.9:  # 90% chance to be wall
                                self.grid[chamber_y + dy][chamber_x + dx] = TileType.WALL
                                
                                # Occasionally add rubble next to walls
                                if random.random() < 0.2:
                                    rubble_dx = -1 if dx == 0 else (1 if dx == chamber_w - 1 else 0)
                                    rubble_dy = -1 if dy == 0 else (1 if dy == chamber_h - 1 else 0)
                                    rubble_x = chamber_x + dx + rubble_dx
                                    rubble_y = chamber_y + dy + rubble_dy
                                    if (room_x < rubble_x < room_x + room_w - 1 and
                                        room_y < rubble_y < room_y + room_h - 1):
                                        self.grid[rubble_y][rubble_x] = TileType.WALL
            
            # Add entrance to chamber
            entrance_side = random.choice(['top', 'bottom', 'left', 'right'])
            if entrance_side == 'top' and chamber_y > room_y:
                self.grid[chamber_y][chamber_x + chamber_w // 2] = TileType.FLOOR
                self.grid[chamber_y][chamber_x + chamber_w // 2 - 1] = TileType.FLOOR  # Wider entrance
            elif entrance_side == 'bottom' and chamber_y + chamber_h < room_y + room_h:
                self.grid[chamber_y + chamber_h - 1][chamber_x + chamber_w // 2] = TileType.FLOOR
                self.grid[chamber_y + chamber_h - 1][chamber_x + chamber_w // 2 + 1] = TileType.FLOOR  # Wider entrance
            elif entrance_side == 'left' and chamber_x > room_x:
                self.grid[chamber_y + chamber_h // 2][chamber_x] = TileType.FLOOR
                self.grid[chamber_y + chamber_h // 2 + 1][chamber_x] = TileType.FLOOR  # Taller entrance
            elif entrance_side == 'right' and chamber_x + chamber_w < room_x + room_w:
                self.grid[chamber_y + chamber_h // 2][chamber_x + chamber_w - 1] = TileType.FLOOR
                self.grid[chamber_y + chamber_h // 2 - 1][chamber_x + chamber_w - 1] = TileType.FLOOR  # Taller entrance
                
            chambers.append((chamber_x, chamber_y, chamber_w, chamber_h, entrance_side))
        
        # Add connecting corridors between chambers
        if len(chambers) >= 2:
            for i in range(len(chambers) - 1):
                start_chamber = chambers[i]
                end_chamber = chambers[i + 1]
                
                # Find corridor path (simple implementation)
                start_x = start_chamber[0] + start_chamber[2] // 2
                start_y = start_chamber[1] + start_chamber[3] // 2
                end_x = end_chamber[0] + end_chamber[2] // 2
                end_y = end_chamber[1] + end_chamber[3] // 2
                
                # Create horizontal then vertical corridor
                current_x = start_x
                while current_x != end_x:
                    step = 1 if current_x < end_x else -1
                    current_x += step
                    if room_x < current_x < room_x + room_w and room_y < start_y < room_y + room_h:
                        self.grid[start_y][current_x] = TileType.FLOOR
                
                current_y = start_y
                while current_y != end_y:
                    step = 1 if current_y < end_y else -1
                    current_y += step
                    if room_x < end_x < room_x + room_w and room_y < current_y < room_y + room_h:
                        self.grid[current_y][end_x] = TileType.FLOOR

    def generate_village_features(self):
        """Generate village-specific features like building foundations with natural layouts"""
        room_x, room_y = 2, 2
        room_w, room_h = self.grid_width - 4, self.grid_height - 4
        
        # Create a central path through the village
        path_width = 3
        path_direction = random.choice(["horizontal", "vertical", "cross"])
        
        if path_direction == "horizontal":
            path_y = room_y + room_h // 2
            for x in range(room_x, room_x + room_w):
                for dy in range(-path_width // 2, path_width // 2 + 1):
                    if 0 <= path_y + dy < self.grid_height:
                        # Make sure path is floor (road through village)
                        self.grid[path_y + dy][x] = TileType.FLOOR
        elif path_direction == "vertical":
            path_x = room_x + room_w // 2
            for y in range(room_y, room_y + room_h):
                for dx in range(-path_width // 2, path_width // 2 + 1):
                    if 0 <= path_x + dx < self.grid_width:
                        self.grid[y][path_x + dx] = TileType.FLOOR
        else:  # Cross pattern
            path_x = room_x + room_w // 2
            path_y = room_y + room_h // 2
            for y in range(room_y, room_y + room_h):
                for dx in range(-path_width // 2, path_width // 2 + 1):
                    if 0 <= path_x + dx < self.grid_width:
                        self.grid[y][path_x + dx] = TileType.FLOOR
            for x in range(room_x, room_x + room_w):
                for dy in range(-path_width // 2, path_width // 2 + 1):
                    if 0 <= path_y + dy < self.grid_height:
                        self.grid[path_y + dy][x] = TileType.FLOOR
        
        # Create buildings in a more natural village layout with different sizes
        building_zones = []
        
        # Determine zones for buildings
        if path_direction == "horizontal":
            building_zones.append((room_x, room_y, room_w, path_y - room_y - 1))  # North zone
            building_zones.append((room_x, path_y + path_width, room_w, room_y + room_h - path_y - path_width))  # South zone
        elif path_direction == "vertical":
            building_zones.append((room_x, room_y, path_x - room_x - 1, room_h))  # West zone
            building_zones.append((path_x + path_width, room_y, room_x + room_w - path_x - path_width, room_h))  # East zone
        else:  # Cross
            building_zones.append((room_x, room_y, path_x - room_x - 1, path_y - room_y - 1))  # NW zone
            building_zones.append((path_x + path_width, room_y, room_x + room_w - path_x - path_width, path_y - room_y - 1))  # NE zone
            building_zones.append((room_x, path_y + path_width, path_x - room_x - 1, room_y + room_h - path_y - path_width))  # SW zone
            building_zones.append((path_x + path_width, path_y + path_width, 
                                 room_x + room_w - path_x - path_width, room_y + room_h - path_y - path_width))  # SE zone
        
        # Place buildings in zones
        for zone_x, zone_y, zone_w, zone_h in building_zones:
            if zone_w < 7 or zone_h < 7:
                continue  # Skip small zones
            
            num_buildings = random.randint(1, max(1, min(zone_w, zone_h) // 6))
            
            for _ in range(num_buildings):
                # Vary building sizes
                building_w = random.randint(4, min(7, zone_w - 2))
                building_h = random.randint(3, min(6, zone_h - 2))
                
                # Position within zone
                building_x = random.randint(zone_x + 1, zone_x + zone_w - building_w - 1)
                building_y = random.randint(zone_y + 1, zone_y + zone_h - building_h - 1)
                
                # Create building outline with variations
                for dy in range(building_h):
                    for dx in range(building_w):
                        if (dy == 0 or dy == building_h - 1 or dx == 0 or dx == building_w - 1):
                            if building_y + dy < self.grid_height and building_x + dx < self.grid_width:
                                self.grid[building_y + dy][building_x + dx] = TileType.WALL
                
                # Add door facing path or in random position
                door_side = random.choice(["north", "south", "east", "west"])
                
                if door_side == "north" and building_y > zone_y + 1:
                    door_x = building_x + building_w // 2
                    door_y = building_y
                elif door_side == "south" and building_y + building_h < zone_y + zone_h - 1:
                    door_x = building_x + building_w // 2
                    door_y = building_y + building_h - 1
                elif door_side == "west" and building_x > zone_x + 1:
                    door_x = building_x
                    door_y = building_y + building_h // 2
                elif door_side == "east" and building_x + building_w < zone_x + zone_w - 1:
                    door_x = building_x + building_w - 1
                    door_y = building_y + building_h // 2
                else:
                    # Default to south door
                    door_x = building_x + building_w // 2
                    door_y = building_y + building_h - 1
                
                if door_y < self.grid_height and door_x < self.grid_width:
                    self.grid[door_y][door_x] = TileType.FLOOR
                
                # Internal features
                if random.random() < 0.4 and building_w > 5 and building_h > 4:  # 40% chance for internal walls
                    # Add an internal wall
                    wall_x = building_x + building_w // 2
                    for internal_y in range(building_y + 1, building_y + building_h - 1):
                        if internal_y < self.grid_height and wall_x < self.grid_width:
                            if random.random() < 0.7:  # 70% chance for wall segment
                                self.grid[internal_y][wall_x] = TileType.WALL
                    
                    # Add door in internal wall
                    door_y = building_y + 1 + random.randint(1, building_h - 3)
                    if door_y < self.grid_height and wall_x < self.grid_width:
                        self.grid[door_y][wall_x] = TileType.FLOOR
        
        # Add small decoration elements (fences, wells, gardens)
        num_decorations = random.randint(3, 8)
        for _ in range(num_decorations):
            decor_x = random.randint(room_x + 1, room_x + room_w - 3)
            decor_y = random.randint(room_y + 1, room_y + room_h - 3)
            decor_type = random.choice(["well", "garden", "fence"])
            
            if decor_type == "well" and self.grid[decor_y][decor_x] == TileType.FLOOR:
                # Well (small water surrounded by wall)
                self.grid[decor_y][decor_x] = TileType.WATER
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        if abs(dx) + abs(dy) == 2:  # Diagonal corners
                            nx, ny = decor_x + dx, decor_y + dy
                            if (room_x < nx < room_x + room_w - 1 and
                                room_y < ny < room_y + room_h - 1 and
                                self.grid[ny][nx] == TileType.FLOOR):
                                self.grid[ny][nx] = TileType.WALL
            
            elif decor_type == "garden" and self.grid[decor_y][decor_x] == TileType.FLOOR:
                # Small garden plot (2x2 or 3x2)
                garden_w = random.randint(2, 3)
                garden_h = 2
                for dy in range(garden_h):
                    for dx in range(garden_w):
                        nx, ny = decor_x + dx, decor_y + dy
                        if (room_x < nx < room_x + room_w - 1 and
                            room_y < ny < room_y + room_h - 1 and
                            self.grid[ny][nx] == TileType.FLOOR):
                            # 50% chance for wall (representing crops/plants)
                            if random.random() < 0.5:
                                self.grid[ny][nx] = TileType.WALL
            
            elif decor_type == "fence" and self.grid[decor_y][decor_x] == TileType.FLOOR:
                # Small fence line
                fence_length = random.randint(3, 5)
                direction = random.choice([(0, 1), (1, 0)])  # Vertical or horizontal
                dx, dy = direction
                
                for i in range(fence_length):
                    nx, ny = decor_x + dx * i, decor_y + dy * i
                    if (room_x < nx < room_x + room_w - 1 and
                        room_y < ny < room_y + room_h - 1 and
                        self.grid[ny][nx] == TileType.FLOOR and
                        random.random() < 0.8):  # 80% chance per segment (gaps in fence)
                        self.grid[ny][nx] = TileType.WALL

    def generate_generic_features(self):
        """Generate more interesting generic room features"""
        room_x, room_y = 1, 1  # Reduced margin now that we don't have wall borders
        room_w, room_h = self.grid_width - 2, self.grid_height - 2
        
        # Determine a dominant feature type for this room to give it character
        dominant_feature = random.choice(['pillars', 'maze', 'chambers', 'asymmetric', 'island'])
        
        if dominant_feature == 'pillars':
            # Create a pattern of pillars throughout the room
            pillar_spacing = random.randint(4, 7)
            for x in range(room_x + pillar_spacing, room_x + room_w - 1, pillar_spacing):
                for y in range(room_y + pillar_spacing, room_y + room_h - 1, pillar_spacing):
                    # Add some randomization to pillar placement
                    if random.random() < 0.8:  # 80% chance to place a pillar
                        offset_x = random.randint(-1, 1)
                        offset_y = random.randint(-1, 1)
                        pillar_x = x + offset_x
                        pillar_y = y + offset_y
                        
                        # Ensure we're not placing pillars on the edge
                        if (1 < pillar_x < self.grid_width - 2 and 
                            1 < pillar_y < self.grid_height - 2):
                            self.grid[pillar_y][pillar_x] = TileType.WALL
                            
                            # Sometimes create pillar clusters
                            if random.random() < 0.3:  # 30% chance for a cluster
                                for dx, dy in [(1, 0), (0, 1), (1, 1), (-1, 0), (0, -1)]:
                                    if random.random() < 0.5 and 1 < pillar_x + dx < self.grid_width - 2 and 1 < pillar_y + dy < self.grid_height - 2:
                                        self.grid[pillar_y + dy][pillar_x + dx] = TileType.WALL
        
        elif dominant_feature == 'maze':
            # Create partial maze-like features
            start_x = room_x + random.randint(3, 8)
            start_y = room_y + random.randint(3, 8)
            
            # Generate a small maze section
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            for _ in range(20):  # Create 20 wall segments
                wall_length = random.randint(3, 8)
                dx, dy = random.choice(directions)
                
                for i in range(wall_length):
                    wall_x = start_x + dx * i
                    wall_y = start_y + dy * i
                    
                    # Ensure we don't place walls at room edges
                    if (2 < wall_x < self.grid_width - 3 and 
                        2 < wall_y < self.grid_height - 3):
                        self.grid[wall_y][wall_x] = TileType.WALL
                
                # Update starting position for next wall segment
                start_x += dx * wall_length
                start_y += dy * wall_length
                
                # Ensure we stay within room bounds
                start_x = max(3, min(self.grid_width - 4, start_x))
                start_y = max(3, min(self.grid_height - 4, start_y))
        
        elif dominant_feature == 'chambers':
            # Create multiple small chambers/rooms within the room
            num_chambers = random.randint(2, 4)
            for _ in range(num_chambers):
                chamber_w = random.randint(5, 10)
                chamber_h = random.randint(5, 8)
                chamber_x = random.randint(room_x + 2, room_x + room_w - chamber_w - 2)
                chamber_y = random.randint(room_y + 2, room_y + room_h - chamber_h - 2)
                
                # Create chamber walls
                for dy in range(chamber_h):
                    for dx in range(chamber_w):
                        if (dx == 0 or dx == chamber_w - 1 or dy == 0 or dy == chamber_h - 1):
                            # Add some gaps for doorways
                            if not (dx == chamber_w // 2 and dy == 0) and not (dx == chamber_w // 2 and dy == chamber_h - 1):
                                if chamber_y + dy < self.grid_height and chamber_x + dx < self.grid_width:
                                    self.grid[chamber_y + dy][chamber_x + dx] = TileType.WALL
                
                # Add some interesting features inside chambers
                feature = random.choice(['water', 'chest', 'pillar'])
                if feature == 'water' and chamber_w > 4 and chamber_h > 4:
                    water_x = chamber_x + chamber_w // 2
                    water_y = chamber_y + chamber_h // 2
                    self.grid[water_y][water_x] = TileType.WATER
                elif feature == 'chest' and chamber_w > 4 and chamber_h > 4:
                    chest_x = chamber_x + chamber_w // 2
                    chest_y = chamber_y + chamber_h // 2
                    self.grid[chest_y][chest_x] = TileType.CHEST
                elif feature == 'pillar' and chamber_w > 5 and chamber_h > 5:
                    for i in range(2):
                        pillar_x = chamber_x + random.randint(2, chamber_w - 3)
                        pillar_y = chamber_y + random.randint(2, chamber_h - 3)
                        self.grid[pillar_y][pillar_x] = TileType.WALL
        
        elif dominant_feature == 'asymmetric':
            # Create an asymmetric layout with a large feature to one side
            side = random.choice(['north', 'south', 'east', 'west'])
            
            if side == 'north':
                feature_y = room_y + random.randint(2, 5)
                feature_h = random.randint(4, 8)
                feature_x = room_x + random.randint(5, room_w - 20)
                feature_w = random.randint(15, room_w - feature_x - 5)
                
                # Create a large wall section
                for dy in range(feature_h):
                    for dx in range(feature_w):
                        if (dx == 0 or dx == feature_w - 1 or dy == 0 or dy == feature_h - 1):
                            # Add doorways
                            if not (dx == feature_w // 2 and dy == feature_h - 1):
                                self.grid[feature_y + dy][feature_x + dx] = TileType.WALL
                
            elif side == 'south':
                feature_h = random.randint(4, 8)
                feature_y = room_y + room_h - feature_h - random.randint(2, 5)
                feature_x = room_x + random.randint(5, room_w - 20)
                feature_w = random.randint(15, room_w - feature_x - 5)
                
                # Create a large wall section
                for dy in range(feature_h):
                    for dx in range(feature_w):
                        if (dx == 0 or dx == feature_w - 1 or dy == 0 or dy == feature_h - 1):
                            # Add doorways
                            if not (dx == feature_w // 2 and dy == 0):
                                self.grid[feature_y + dy][feature_x + dx] = TileType.WALL
            
            # Add some random natural features in the remaining space
            num_features = random.randint(8, 15)
            for _ in range(num_features):
                feature_x = random.randint(room_x + 2, room_x + room_w - 3)
                feature_y = random.randint(room_y + 2, room_y + room_h - 3)
                
                # Check if this position is away from our main feature
                if self.grid[feature_y][feature_x] == TileType.FLOOR:
                    feature_type = random.choice(['wall', 'water', 'chest'])
                    
                    if feature_type == 'wall':
                        self.grid[feature_y][feature_x] = TileType.WALL
                    elif feature_type == 'water':
                        self.grid[feature_y][feature_x] = TileType.WATER
                    elif feature_type == 'chest':
                        self.grid[feature_y][feature_x] = TileType.CHEST
        
        elif dominant_feature == 'island':
            # Create one or more island features in a sea of water
            center_x = self.grid_width // 2
            center_y = self.grid_height // 2
            
            # Create the water around the edges
            water_margin = random.randint(3, 6)
            for y in range(room_y, room_y + room_h):
                for x in range(room_x, room_x + room_w):
                    # Calculate distance from center
                    dist_x = abs(x - center_x)
                    dist_y = abs(y - center_y)
                    
                    # Create water in a ring pattern
                    if max(dist_x, dist_y) > min(room_w, room_h) // 2 - water_margin:
                        self.grid[y][x] = TileType.WATER
            
            # Create bridges across the water in the cardinal directions
            bridges = random.sample(['north', 'south', 'east', 'west'], k=random.randint(2, 4))
            bridge_width = random.randint(2, 3)
            
            for direction in bridges:
                if direction == 'north':
                    for x in range(center_x - bridge_width // 2, center_x + bridge_width // 2 + 1):
                        for y in range(0, center_y):
                            if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
                                self.grid[y][x] = TileType.FLOOR
                
                elif direction == 'south':
                    for x in range(center_x - bridge_width // 2, center_x + bridge_width // 2 + 1):
                        for y in range(center_y, self.grid_height):
                            if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
                                self.grid[y][x] = TileType.FLOOR
                
                elif direction == 'west':
                    for y in range(center_y - bridge_width // 2, center_y + bridge_width // 2 + 1):
                        for x in range(0, center_x):
                            if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
                                self.grid[y][x] = TileType.FLOOR
                
                elif direction == 'east':
                    for y in range(center_y - bridge_width // 2, center_y + bridge_width // 2 + 1):
                        for x in range(center_x, self.grid_width):
                            if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
                                self.grid[y][x] = TileType.FLOOR
            
            # Add some decorative elements on the central island
            island_radius = min(room_w, room_h) // 2 - water_margin - 1
            num_decorations = random.randint(3, 7)
            
            for _ in range(num_decorations):
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(0, island_radius * 0.7)
                
                dec_x = int(center_x + distance * math.cos(angle))
                dec_y = int(center_y + distance * math.sin(angle))
                
                if 1 <= dec_x < self.grid_width - 1 and 1 <= dec_y < self.grid_height - 1:
                    decoration_type = random.choice(['wall', 'chest', 'wall_cluster'])
                    
                    if decoration_type == 'wall':
                        self.grid[dec_y][dec_x] = TileType.WALL
                    elif decoration_type == 'chest':
                        self.grid[dec_y][dec_x] = TileType.CHEST
                    elif decoration_type == 'wall_cluster':
                        self.grid[dec_y][dec_x] = TileType.WALL
                        for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                            if random.random() < 0.7:
                                nx, ny = dec_x + dx, dec_y + dy
                                if 1 <= nx < self.grid_width - 1 and 1 <= ny < self.grid_height - 1:
                                    self.grid[ny][nx] = TileType.WALL
            
        # Add some random objects regardless of dominant feature
        num_objects = random.randint(5, 10)
        for _ in range(num_objects):
            obj_x = random.randint(room_x + 3, room_x + room_w - 4)
            obj_y = random.randint(room_y + 3, room_y + room_h - 4)
            
            # Only place on floor tiles
            if self.grid[obj_y][obj_x] == TileType.FLOOR:
                obj_type = random.choices(
                    ['wall', 'water', 'chest', 'wall_cluster'], 
                    weights=[0.5, 0.3, 0.1, 0.1], 
                    k=1
                )[0]
                
                if obj_type == 'wall':
                    self.grid[obj_y][obj_x] = TileType.WALL
                elif obj_type == 'water':
                    self.grid[obj_y][obj_x] = TileType.WATER
                    # Sometimes create a small pond
                    if random.random() < 0.5:
                        for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                            if random.random() < 0.7:
                                nx, ny = obj_x + dx, obj_y + dy
                                if 1 <= nx < self.grid_width - 1 and 1 <= ny < self.grid_height - 1:
                                    self.grid[ny][nx] = TileType.WATER
                elif obj_type == 'chest':
                    self.grid[obj_y][obj_x] = TileType.CHEST
                elif obj_type == 'wall_cluster':
                    self.grid[obj_y][obj_x] = TileType.WALL
                    for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                        if random.random() < 0.7:
                            nx, ny = obj_x + dx, obj_y + dy
                            if 1 <= nx < self.grid_width - 1 and 1 <= ny < self.grid_height - 1:
                                self.grid[ny][nx] = TileType.WALL


    def add_item(self, item: Item):
        # Find a random floor tile to place the item
        possible_locations = []
        for r_idx, row in enumerate(self.grid):
            for c_idx, tile in enumerate(row):
                if tile == TileType.FLOOR:
                    # Check if location is already occupied by another item
                    occupied = False
                    for existing_item in self.items:
                        if existing_item.x == c_idx and existing_item.y == r_idx:
                            occupied = True
                            break
                    if not occupied:
                        possible_locations.append((c_idx, r_idx))
        
        if possible_locations:
            item.x, item.y = random.choice(possible_locations)
            self.items.append(item)

    def add_npc(self, npc: NPC):
        # Find a random floor tile for NPC, similar to items
        possible_locations = []
        for r_idx, row in enumerate(self.grid):
            for c_idx, tile in enumerate(row):
                if tile == TileType.FLOOR:
                    occupied = False
                    for existing_item in self.items: # Check against items
                        if existing_item.x == c_idx and existing_item.y == r_idx:
                            occupied = True; break
                    if occupied: continue
                    for existing_npc in self.npcs: # Check against other NPCs
                        if existing_npc.rect.colliderect(pygame.Rect(c_idx * TILE_SIZE, r_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE)):
                            occupied = True; break
                    if not occupied:
                        possible_locations.append((c_idx, r_idx))
        
        if possible_locations:
            npc_tile_x, npc_tile_y = random.choice(possible_locations)
            npc.rect.topleft = (npc_tile_x * TILE_SIZE, npc_tile_y * TILE_SIZE)
            self.npcs.append(npc)

    def to_dict(self):
        return {
            'name': self.name,
            'grid_width': self.grid_width,
            'grid_height': self.grid_height,
            'room_type': self.room_type,
            'difficulty_level': self.difficulty_level,
            'grid': [[tile.value for tile in row] for row in self.grid],
            'items': [item.to_dict() for item in self.items],
            'npcs': [npc.to_dict() for npc in self.npcs],
            'exits': self.exits,
            'visited': self.visited
        }

    @classmethod
    def from_dict(cls, data, name_override=None): # name_override for dynamic room creation
        room_name = name_override if name_override else data['name']
        room_type = data.get('room_type', 'cave')
        room = cls(room_name, data['grid_width'], data['grid_height'], room_type)
        room.grid = [[TileType(tile_val) for tile_val in row] for row in data['grid']]
        room.items = [Item.from_dict(item_data) for item_data in data.get('items', [])]
        room.npcs = [NPC.from_dict(npc_data) for npc_data in data.get('npcs', [])]
        room.exits = data.get('exits', {})
        room.visited = data.get('visited', False)
        room.difficulty_level = data.get('difficulty_level', 1)
        return room

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Load settings first
        self.settings = self.load_settings()
        
        # Calculate screen size based on settings
        self.actual_screen_width = int(BASE_SCREEN_WIDTH * self.settings.screen_scale)
        self.actual_screen_height = int(BASE_SCREEN_HEIGHT * self.settings.screen_scale)
        
        if self.settings.fullscreen:
            self.screen = pygame.display.set_mode((self.actual_screen_width, self.actual_screen_height), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.actual_screen_width, self.actual_screen_height))
        
        pygame.display.set_caption("Procedural Adventure")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.state = GameState.NAME_INPUT
        self.player: Optional[Player] = None
        self.rooms: Dict[str, Room] = {}
        self.quests: Dict[str, Quest] = {}  # All available quests
        
        # Procedural room generation tracking
        self.room_id_counter = 1000  # Start procedural rooms at 1000+
        self.discovered_exits: Dict[str, Tuple[str, str]] = {}  # (room_name, direction) -> (target_room_name, target_direction)
        
        self.font_small = pygame.font.Font(FONT_NAME, FONT_SIZE_SMALL)
        self.font_medium = pygame.font.Font(FONT_NAME, FONT_SIZE_MEDIUM)
        self.font_large = pygame.font.Font(FONT_NAME, FONT_SIZE_LARGE)
        
        self.input_text = ""
        self.dialogue_target_npc: Optional[NPC] = None
        self.dialogue_text = ""
        self.dialogue_choices: List[str] = []
        self.selected_choice_idx = 0
        self.quest_log_scroll = 0  # For scrolling through quest log
        
        # Settings menu state
        self.settings_selection = 0
        self.settings_options = ["Master Volume", "SFX Volume", "Music Volume", "Screen Scale", "Fullscreen", "Back"]
        
        self.notification_text = ""
        self.notification_timer = 0

        self.create_initial_rooms()
        self.create_story_quests()
        # self.load_game_on_startup() # Option to auto-load

    def load_settings(self) -> GameSettings:
        """Load settings from file or return defaults"""
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    settings_data = json.load(f)
                return GameSettings.from_dict(settings_data)
            except:
                return GameSettings()
        return GameSettings()
    
    def save_settings(self):
        """Save current settings to file"""
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(self.settings.to_dict(), f, indent=2)
            self.show_notification("Settings saved!", 2)
        except Exception as e:
            print(f"Failed to save settings: {e}")
            self.show_notification(f"Settings save failed: {e}", 3)
    
    def apply_settings(self):
        """Apply current settings to the game"""
        # Calculate new screen size
        new_width = int(BASE_SCREEN_WIDTH * self.settings.screen_scale)
        new_height = int(BASE_SCREEN_HEIGHT * self.settings.screen_scale)
        
        # Check if screen size or fullscreen changed
        if (new_width != self.actual_screen_width or 
            new_height != self.actual_screen_height or
            self.settings.fullscreen != pygame.display.get_surface().get_flags() & pygame.FULLSCREEN):
            
            self.actual_screen_width = new_width
            self.actual_screen_height = new_height
            
            if self.settings.fullscreen:
                self.screen = pygame.display.set_mode((new_width, new_height), pygame.FULLSCREEN)
            else:
                self.screen = pygame.display.set_mode((new_width, new_height))
            
            # Update global screen dimensions
            global SCREEN_WIDTH, SCREEN_HEIGHT
            SCREEN_WIDTH = new_width
            SCREEN_HEIGHT = new_height
        
        # Apply audio settings (if pygame.mixer supports it)
        try:
            pygame.mixer.music.set_volume(self.settings.master_volume * self.settings.music_volume)
        except:
            pass  # Audio might not be available
    
    def generate_procedural_room(self, suggested_type: str = None) -> Room:
        """Generate a completely new procedural room"""
        room_types = ["cave", "forest", "dungeon", "village", "clearing", "ruins", "swamp", "mountain"]
        room_type = suggested_type if suggested_type else random.choice(room_types)
        
        # Generate unique room name
        room_id = f"procedural_{self.room_id_counter}"
        self.room_id_counter += 1
        
        # Create descriptive names based on type
        type_names = {
            "cave": ["Echoing Cavern", "Crystal Grotto", "Deep Chamber", "Limestone Cave", "Hidden Hollow"],
            "forest": ["Dense Woodland", "Mystic Grove", "Ancient Forest", "Enchanted Thicket", "Twilight Woods"],
            "dungeon": ["Forgotten Crypt", "Stone Corridors", "Ancient Dungeon", "Dark Passages", "Lost Tomb"],
            "village": ["Abandoned Village", "Rural Settlement", "Ghost Town", "Old Hamlet", "Desert Outpost"],
            "clearing": ["Sunny Meadow", "Peaceful Glade", "Flower Field", "Open Plains", "Tranquil Grove"],
            "ruins": ["Ancient Ruins", "Crumbling Temple", "Lost City", "Weathered Stones", "Forgotten Monument"],
            "swamp": ["Murky Swamp", "Fetid Marsh", "Misty Bog", "Dark Wetlands", "Stagnant Pool"],
            "mountain": ["Rocky Summit", "Windswept Peak", "Stone Plateau", "Alpine Pass", "Cliff Face"]
        }
        
        room_name = f"{random.choice(type_names.get(room_type, ['Unknown Place']))} {room_id[-3:]}"
        
        # Create room with enhanced difficulty based on distance from start
        difficulty = min(10, 1 + (self.room_id_counter - 1000) // 5)
        room = Room(room_name, GRID_WIDTH, GRID_HEIGHT, room_type)
        room.difficulty_level = difficulty
        
        # Add procedural items based on room type and difficulty
        self.add_procedural_items(room, room_type, difficulty)
        
        # Add procedural NPCs occasionally
        if random.random() < 0.3:  # 30% chance for NPC
            self.add_procedural_npc(room, room_type)
        
        return room
    
    def add_procedural_items(self, room: Room, room_type: str, difficulty: int):
        """Add procedural items to a room based on type and difficulty"""
        num_items = random.randint(1, min(5, 2 + difficulty // 2))
        
        type_items = {
            "cave": [
                ("Crystal Shard", "A glowing crystal fragment", ItemType.TREASURE, 50),
                ("Cave Mushroom", "Edible fungus that restores health", ItemType.CONSUMABLE, 0),
                ("Stone Tablet", "Ancient writings on stone", ItemType.KEY_ITEM, 0),
                ("Rare Mineral", "Valuable ore deposit", ItemType.TREASURE, 100)
            ],
            "forest": [
                ("Healing Herb", "Natural medicine", ItemType.CONSUMABLE, 0),
                ("Ancient Seed", "Mysterious plant seed", ItemType.KEY_ITEM, 0),
                ("Wild Berry", "Sweet fruit that restores energy", ItemType.CONSUMABLE, 0),
                ("Wooden Amulet", "Carved forest charm", ItemType.TREASURE, 75)
            ],
            "dungeon": [
                ("Rusty Key", "Opens ancient locks", ItemType.KEY_ITEM, 0),
                ("Gold Coin", "Old currency", ItemType.TREASURE, 25),
                ("Scroll Fragment", "Piece of ancient knowledge", ItemType.KEY_ITEM, 0),
                ("Jeweled Dagger", "Ornate weapon", ItemType.TREASURE, 200)
            ],
            "village": [
                ("Trade Goods", "Valuable merchandise", ItemType.TREASURE, 150),
                ("Village Map", "Shows local area", ItemType.KEY_ITEM, 0),
                ("Rations", "Preserved food", ItemType.CONSUMABLE, 0),
                ("Merchant's Ledger", "Trading records", ItemType.KEY_ITEM, 0)
            ],
            "ruins": [
                ("Ancient Relic", "Mysterious artifact", ItemType.KEY_ITEM, 0),
                ("Precious Gemstone", "Valuable jewel", ItemType.TREASURE, 300),
                ("Runed Stone", "Magical inscription", ItemType.KEY_ITEM, 0),
                ("Golden Idol", "Religious artifact", ItemType.TREASURE, 500)
            ]
        }
        
        available_items = type_items.get(room_type, type_items["cave"])
        
        for _ in range(num_items):
            item_data = random.choice(available_items)
            name, description, item_type, base_value = item_data
            
            # Scale value with difficulty
            value = base_value + (difficulty * 10)
            quantity = random.randint(1, 3) if item_type == ItemType.CONSUMABLE else 1
            
            item = Item(name, description, item_type, quantity, value)
            room.add_item(item)
    
    def add_procedural_npc(self, room: Room, room_type: str):
        """Add a procedural NPC to a room"""
        type_npcs = {
            "cave": [
                ("Cave Dweller", ["I've lived in these caves for years...", "The crystals sing at night.", "Beware the deeper chambers."]),
                ("Lost Explorer", ["I've been lost for days!", "Do you know the way out?", "I found some interesting things here."]),
                ("Crystal Miner", ["These crystals are valuable.", "I can trade for rare gems.", "Mining is dangerous work."])
            ],
            "forest": [
                ("Forest Guardian", ["The trees whisper ancient secrets.", "Nature must be protected.", "You seem worthy of passage."]),
                ("Wandering Druid", ["The forest spirits are restless.", "I can teach you about herbs.", "Balance must be maintained."]),
                ("Lost Traveler", ["I've been walking for hours!", "These woods all look the same.", "Have you seen the main road?"])
            ],
            "village": [
                ("Village Elder", ["Welcome to our humble settlement.", "We don't get many visitors.", "Times have been hard lately."]),
                ("Local Merchant", ["I have goods for trade.", "Coin for quality items.", "Business has been slow."]),
                ("Village Guard", ["Stay out of trouble here.", "We keep the peace.", "Move along, traveler."])
            ],
            "ruins": [
                ("Archaeologist", ["These ruins are fascinating!", "I study ancient civilizations.", "Some artifacts are quite valuable."]),
                ("Relic Hunter", ["I seek ancient treasures.", "Knowledge has its price.", "Some secrets are dangerous."]),
                ("Ghost of the Past", ["I remember when this place lived...", "Long ago, this was magnificent.", "The past echoes in these stones."])
            ]
        }
        
        available_npcs = type_npcs.get(room_type, type_npcs["cave"])
        npc_data = random.choice(available_npcs)
        name, dialogue = npc_data
        
        npc = NPC(name, pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE), dialogue)
        room.add_npc(npc)
    
    def discover_new_room(self, from_room: str, direction: str) -> str:
        """Discover or generate a new room in the given direction"""
        # Check if we already have a room connection for this direction
        connection_key = (from_room, direction)
        if connection_key in self.discovered_exits:
            target_room, _ = self.discovered_exits[connection_key]
            return target_room
        
        # Generate new room
        current_room = self.rooms[from_room]
        room_type = current_room.room_type if random.random() < 0.4 else None  # 40% chance to keep same type
        new_room = self.generate_procedural_room(room_type)
        
        # Add to rooms dictionary
        self.rooms[new_room.name] = new_room
        
        # Set up bidirectional connections
        opposite_directions = {"north": "south", "south": "north", "east": "west", "west": "east"}
        opposite_dir = opposite_directions[direction]
        
        # Connect from current room to new room
        if direction == "north":
            entry_x, entry_y = GRID_WIDTH // 2, GRID_HEIGHT - 2
            exit_x, exit_y = GRID_WIDTH // 2, 0
        elif direction == "south":
            entry_x, entry_y = GRID_WIDTH // 2, 1
            exit_x, exit_y = GRID_WIDTH // 2, GRID_HEIGHT - 1
        elif direction == "east":
            entry_x, entry_y = 1, GRID_HEIGHT // 2
            exit_x, exit_y = GRID_WIDTH - 1, GRID_HEIGHT // 2
        elif direction == "west":
            entry_x, entry_y = GRID_WIDTH - 2, GRID_HEIGHT // 2
            exit_x, exit_y = 0, GRID_HEIGHT // 2
        
        # Set up exits
        current_room.exits[direction] = (new_room.name, entry_x, entry_y)
        new_room.exits[opposite_dir] = (from_room, exit_x, exit_y)
        
        # Place exit tiles
        self.place_exit_tile(current_room, direction, exit_y if direction in ["north", "south"] else GRID_HEIGHT // 2, 
                           exit_x if direction in ["east", "west"] else GRID_WIDTH // 2)
        self.place_exit_tile(new_room, opposite_dir, entry_y, entry_x)
        
        # Store the connection for future reference
        self.discovered_exits[connection_key] = (new_room.name, opposite_dir)
        self.discovered_exits[(new_room.name, opposite_dir)] = (from_room, direction)
        
        return new_room.name

    def create_initial_rooms(self):
        # Create expanded interconnected world
        start_room = Room("Mystic Cave Entrance", GRID_WIDTH, GRID_HEIGHT)
        start_room.add_item(Item("Old Map", "A dusty map fragment showing underground passages.", ItemType.KEY_ITEM, quantity=1))
        start_room.add_item(Item("Health Potion", "Restores 50 HP when consumed.", ItemType.CONSUMABLE, quantity=2))
        
        # Create quest-giving NPC
        hermit = NPC("Cave Hermit", pygame.Rect(0,0,TILE_SIZE, TILE_SIZE), 
                    ["Welcome, brave seeker...", "These caves hold ancient secrets.", "I sense great potential in you."],
                    quest_giver=True, quest_id="main_01")
        start_room.add_npc(hermit)
        
        crystal_chamber = Room("Crystal Chamber", GRID_WIDTH, GRID_HEIGHT)
        crystal_chamber.add_item(Item("Glowing Crystal", "Pulses with mysterious energy.", ItemType.KEY_ITEM, quantity=1))
        crystal_chamber.add_item(Item("Rare Gem", "A valuable crystal formation.", ItemType.TREASURE, quantity=1, value=100))
        
        # Add water tiles for environmental variety
        for i in range(3):
            x, y = random.randint(2, GRID_WIDTH-3), random.randint(2, GRID_HEIGHT-3)
            if crystal_chamber.grid[y][x] == TileType.FLOOR:
                crystal_chamber.grid[y][x] = TileType.WATER
        
        # Create underground tunnels
        underground_tunnels = Room("Underground Tunnels", GRID_WIDTH, GRID_HEIGHT)
        underground_tunnels.add_item(Item("Ancient Scroll", "Contains cryptic writings.", ItemType.KEY_ITEM, quantity=1))
        
        # Create the Lost City
        lost_city = Room("Lost City of Aethermoor", GRID_WIDTH, GRID_HEIGHT)
        lost_city.add_item(Item("City Key", "Opens the gates to the inner sanctum.", ItemType.KEY_ITEM, quantity=1))
        
        # Add treasure chests
        for i in range(2):
            x, y = random.randint(1, GRID_WIDTH-2), random.randint(1, GRID_HEIGHT-2)
            if lost_city.grid[y][x] == TileType.FLOOR:
                lost_city.grid[y][x] = TileType.CHEST
        
        # Create merchant area
        merchant_quarter = Room("Merchant Quarter", GRID_WIDTH, GRID_HEIGHT)
        merchant = NPC("Mysterious Collector", pygame.Rect(0,0,TILE_SIZE, TILE_SIZE),
                      ["I collect rare gems...", "Bring me treasures and I'll reward you well."],
                      quest_giver=True, quest_id="side_01")
        merchant_quarter.add_npc(merchant)
        
        # Create bandit camp for side quest
        bandit_camp = Room("Bandit Camp", GRID_WIDTH, GRID_HEIGHT)
        bandit_camp.add_item(Item("Stolen Goods", "Valuable items taken from merchants.", ItemType.KEY_ITEM, quantity=1))
        bandit_camp.add_item(Item("Bandit Treasure", "Ill-gotten gains.", ItemType.TREASURE, quantity=1, value=200))

        # Connect rooms with exits
        start_room.exits["north"] = ("Crystal Chamber", GRID_WIDTH // 2, GRID_HEIGHT - 2)
        start_room.exits["east"] = ("Merchant Quarter", 1, GRID_HEIGHT // 2)
        self.place_exit_tile(start_room, "north", 0, GRID_WIDTH // 2)
        self.place_exit_tile(start_room, "east", GRID_HEIGHT // 2, GRID_WIDTH - 1)

        crystal_chamber.exits["south"] = ("Mystic Cave Entrance", GRID_WIDTH // 2, 1)
        crystal_chamber.exits["west"] = ("Underground Tunnels", GRID_WIDTH - 2, GRID_HEIGHT // 2)
        self.place_exit_tile(crystal_chamber, "south", GRID_HEIGHT - 1, GRID_WIDTH // 2)
        self.place_exit_tile(crystal_chamber, "west", GRID_HEIGHT // 2, 0)

        underground_tunnels.exits["east"] = ("Crystal Chamber", 1, GRID_HEIGHT // 2)
        underground_tunnels.exits["north"] = ("Lost City of Aethermoor", GRID_WIDTH // 2, GRID_HEIGHT - 2)
        self.place_exit_tile(underground_tunnels, "east", GRID_HEIGHT // 2, GRID_WIDTH - 1)
        self.place_exit_tile(underground_tunnels, "north", 0, GRID_WIDTH // 2)

        lost_city.exits["south"] = ("Underground Tunnels", GRID_WIDTH // 2, 1)
        self.place_exit_tile(lost_city, "south", GRID_HEIGHT - 1, GRID_WIDTH // 2)

        merchant_quarter.exits["west"] = ("Mystic Cave Entrance", GRID_WIDTH - 2, GRID_HEIGHT // 2)
        merchant_quarter.exits["north"] = ("Bandit Camp", GRID_WIDTH // 2, GRID_HEIGHT - 2)
        self.place_exit_tile(merchant_quarter, "west", GRID_HEIGHT // 2, 0)
        self.place_exit_tile(merchant_quarter, "north", 0, GRID_WIDTH // 2)

        bandit_camp.exits["south"] = ("Merchant Quarter", GRID_WIDTH // 2, 1)
        self.place_exit_tile(bandit_camp, "south", GRID_HEIGHT - 1, GRID_WIDTH // 2)

        self.rooms = {
            "Mystic Cave Entrance": start_room,
            "Crystal Chamber": crystal_chamber,
            "Underground Tunnels": underground_tunnels,
            "Lost City of Aethermoor": lost_city,
            "Merchant Quarter": merchant_quarter,
            "Bandit Camp": bandit_camp
        }

    def place_exit_tile(self, room: Room, direction: str, tile_y: int, tile_x: int):
        """Place an exit tile at the specified coordinates in the room"""
        if (0 <= tile_x < room.grid_width and 0 <= tile_y < room.grid_height):
            # Force the tile to be an exit regardless of current type
            room.grid[tile_y][tile_x] = TileType.EXIT
            # Also ensure the area around the exit is clear
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    check_x, check_y = tile_x + dx, tile_y + dy
                    if (0 <= check_x < room.grid_width and 0 <= check_y < room.grid_height and
                        room.grid[check_y][check_x] != TileType.EXIT):
                        room.grid[check_y][check_x] = TileType.FLOOR

    def create_story_quests(self):
        """Create the main storyline quests and side quests"""
        # Main storyline quests
        self.quests["main_01"] = Quest(
            id="main_01",
            title="The Ancient Map",
            description="Find the Cave Hermit and learn about the ancient mysteries.",
            objectives=["Talk to the Cave Hermit", "Find the Old Map"],
            completed_objectives=[False, False],
            reward_items=["Mystic Compass"],
            reward_text="You've begun your journey into the ancient mysteries!"
        )
        
        self.quests["main_02"] = Quest(
            id="main_02",
            title="The Crystal Power",
            description="Explore the Crystal Chamber and harness its power.",
            objectives=["Enter the Crystal Chamber", "Collect the Glowing Crystal"],
            completed_objectives=[False, False],
            reward_items=["Crystal Amulet"],
            reward_text="The crystal's energy flows through you!"
        )
        
        self.quests["main_03"] = Quest(
            id="main_03",
            title="The Lost City",
            description="Find the legendary lost city of Aethermoor.",
            objectives=["Navigate through the Underground Tunnels", "Discover the Lost City"],
            completed_objectives=[False, False],
            reward_items=["Ancient Medallion"],
            reward_text="You've made a discovery of historical significance!"
        )
        
        # Side quests
        self.quests["side_01"] = Quest(
            id="side_01",
            title="The Gem Collector",
            description="Collect rare gems for the Mysterious Collector.",
            objectives=["Find 3 Rare Gems"],
            completed_objectives=[False],
            reward_items=["Gem Pouch", "Gold Coins"],
            reward_text="The collector is pleased with your finds!"
        )
        
        self.quests["side_02"] = Quest(
            id="side_02",
            title="Bandit Trouble",
            description="Help the merchants deal with bandits stealing their goods.",
            objectives=["Find the Bandit Camp", "Recover the Stolen Goods"],
            completed_objectives=[False, False],
            reward_items=["Merchant's Gratitude", "Trading License"],
            reward_text="The merchants thank you for your help!"
        )

    def get_next_room_name(self) -> str:
        """Generate the name for the next room based on existing rooms"""
        base_name = "Room"
        counter = 1
        while True:
            new_name = f"{base_name} {counter}"
            if new_name not in self.rooms:
                return new_name
            counter += 1

    def update_room_visits(self, room_name: str):
        """Update room visit status and difficulty based on player progress"""
        if room_name in self.rooms:
            room = self.rooms[room_name]
            room.visited = True
            
            # Increase difficulty slightly for revisited rooms
            room.difficulty_level = min(10, room.difficulty_level + 1)
            
    def start_quest(self, quest_id: str):
        """Start a new quest"""
        if quest_id in self.quests:
            quest = self.quests[quest_id]
            if quest.status == QuestStatus.NOT_STARTED:
                quest.status = QuestStatus.ACTIVE
                self.player.active_quests.append(quest_id)
                self.show_notification(f"New Quest: {quest.title}", 3)
            return True
        return False

    def complete_quest(self, quest: Quest):
        """Complete a quest and give rewards"""
        if quest.status == QuestStatus.ACTIVE:
            quest.status = QuestStatus.COMPLETED
            
            # Add reward items to inventory
            for item_name in quest.reward_items:
                new_item = Item(item_name, f"Quest reward from {quest.title}", ItemType.KEY_ITEM)
                self.player.inventory.append(new_item)
            
            # Other rewards could be added here (gold, exp, etc.)
            self.player.gold += 50  # Basic gold reward
            self.player.experience += 100  # Basic exp reward
            
            # Show completion message
            self.show_notification(quest.reward_text, 4)
            return True
        return False
    
    def check_quest_objectives(self, action_type: str, target: str):
        """Check if an action completes any quest objectives"""
        if not self.player:
            return
            
        for quest_id in self.player.active_quests:
            if quest_id not in self.quests:
                continue
                
            quest = self.quests[quest_id]
            if quest.status != QuestStatus.ACTIVE:
                continue
                
            # Check objectives based on action type
            if action_type == "talk_npc":
                for i, objective in enumerate(quest.objectives):
                    if not quest.completed_objectives[i] and f"Talk to {target}" in objective:
                        quest.completed_objectives[i] = True
                        self.show_notification(f"Objective completed: {objective}", 3)
                        
            elif action_type == "enter_room":
                for i, objective in enumerate(quest.objectives):
                    if not quest.completed_objectives[i] and (
                        f"Enter {target}" in objective or 
                        f"Find {target}" in objective or
                        f"Discover {target}" in objective
                    ):
                        quest.completed_objectives[i] = True
                        self.show_notification(f"Objective completed: {objective}", 3)
                        
            elif action_type == "pickup_item":
                for i, objective in enumerate(quest.objectives):
                    if not quest.completed_objectives[i] and (
                        f"Find {target}" in objective or
                        f"Collect {target}" in objective or
                        f"Obtain {target}" in objective
                    ):
                        quest.completed_objectives[i] = True
                        self.show_notification(f"Objective completed: {objective}", 3)
            
            # Check if all objectives are completed
            if all(quest.completed_objectives):
                self.show_notification(f"Quest complete: {quest.title}! Return to quest giver for reward.", 4)
                
    def use_item(self, item_name: str):
        """Use an item from the player's inventory"""
        if not self.player:
            return False
            
        item = self.player.get_item(item_name)
        if not item:
            self.show_notification(f"You don't have a {item_name}.", 2)
            return False
            
        # Handle different item types
        if item_name == "Health Potion":
            # Heal the player
            if self.player.health >= self.player.max_health:
                self.show_notification("You are already at full health.", 2)
                return False
                
            heal_amount = 50  # Standard health potion healing
            self.player.health = min(self.player.max_health, self.player.health + heal_amount)
            self.player.remove_item(item_name, 1)
            self.show_notification(f"Used {item_name}. +{heal_amount} HP!", 2)
            return True
            
        # Add more item types as needed
        
        return False

    def load_game(self):
        if not os.path.exists(SAVE_FILE):
            self.show_notification("No save file found.", 2)
            return False
        try:
            with open(SAVE_FILE, 'r') as f:
                save_data = json.load(f)
            
            self.player = Player.from_dict(save_data['player'])
            
            self.rooms = {}
            for room_name, room_data in save_data['rooms'].items():
                self.rooms[room_name] = Room.from_dict(room_data, name_override=room_name)
            
            # Load quest data if available
            if 'quests' in save_data:
                self.quests = {}
                for quest_id, quest_data in save_data['quests'].items():
                    self.quests[quest_id] = Quest.from_dict(quest_data)
            else:
                # Fallback to default quests if save doesn't have quest data
                self.create_story_quests()
            
            # Load procedural generation data
            self.room_id_counter = save_data.get('room_id_counter', 1000)
            
            # Deserialize discovered exits
            self.discovered_exits = {}
            if 'discovered_exits' in save_data:
                for key_str, value in save_data['discovered_exits'].items():
                    room_name, direction = key_str.split('_', 1)
                    self.discovered_exits[(room_name, direction)] = tuple(value)
            
            # Load settings if available
            if 'settings' in save_data:
                self.settings = GameSettings.from_dict(save_data['settings'])
                self.apply_settings()
            
            self.state = GameState.PLAYING
            self.show_notification("Game Loaded!", 2)
            return True
        except Exception as e:
            print(f"Failed to load game: {e}")
            self.show_notification(f"Load Failed: {e}", 3)
            # Reset to a safe state
            self.player = None
            self.state = GameState.NAME_INPUT
            self.create_initial_rooms()
            self.create_story_quests()
            return False

    def show_notification(self, text: str, duration_seconds: int):
        self.notification_text = text
        self.notification_timer = FPS * duration_seconds

    def handle_name_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and self.input_text.strip():
                start_pos_x = SCREEN_WIDTH // 2
                start_pos_y = SCREEN_HEIGHT // 2
                # Try to place player on a floor tile in the starting room
                start_room_obj = self.rooms.get("Mystic Cave Entrance")
                if start_room_obj:
                    placed = False
                    for r in range(start_room_obj.grid_height):
                        for c in range(start_room_obj.grid_width):
                            if start_room_obj.grid[r][c] == TileType.FLOOR:
                                start_pos_x = c * TILE_SIZE + TILE_SIZE // 2
                                start_pos_y = r * TILE_SIZE + TILE_SIZE // 2
                                placed = True
                                break
                        if placed: break
                
                self.player = Player(
                    name=self.input_text.strip(),
                    rect=pygame.Rect(start_pos_x - TILE_SIZE//4, start_pos_y - TILE_SIZE//4, TILE_SIZE//2, TILE_SIZE//2),
                    current_room="Mystic Cave Entrance"
                )
                
                # Start the first quest automatically
                self.start_quest("main_01")
                
                self.state = GameState.PLAYING
                self.show_notification(f"Welcome, {self.player.name}! Your adventure begins...", 3)
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif len(self.input_text) < 20: # Max name length
                self.input_text += event.unicode
    
    def handle_playing_input(self, event):
        if not self.player: return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:
                self.state = GameState.INVENTORY
            elif event.key == pygame.K_q:
                self.state = GameState.QUEST_LOG
            elif event.key == pygame.K_e: # Interact key
                self.try_interaction()
            elif event.key == pygame.K_h: # Use health potion
                self.use_item("Health Potion")
            elif event.key == pygame.K_TAB:  # Settings menu - Fixed to ensure it opens settings, not quest menu
                self.state = GameState.SETTINGS
                self.settings_selection = 0
            elif event.key == pygame.K_ESCAPE:
                 # Simple pause/main menu functionality can be added here
                self.show_notification("Controls: WASD=Move, E=Interact, I=Inventory, Q=Quests, H=Health Potion, TAB=Settings", 4)
            elif event.key == pygame.K_F5: # Quick Save
                self.save_game()
            elif event.key == pygame.K_F9: # Quick Load
                self.load_game()
    
    def handle_settings_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.settings_selection = (self.settings_selection - 1) % len(self.settings_options)
            elif event.key == pygame.K_DOWN:
                self.settings_selection = (self.settings_selection + 1) % len(self.settings_options)
            elif event.key == pygame.K_LEFT:
                self.adjust_setting(-1)
            elif event.key == pygame.K_RIGHT:
                self.adjust_setting(1)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_e:
                if self.settings_options[self.settings_selection] == "Back":
                    self.apply_settings()
                    self.save_settings()
                    self.state = GameState.PLAYING
                elif self.settings_options[self.settings_selection] == "Fullscreen":
                    self.settings.fullscreen = not self.settings.fullscreen
                    self.apply_settings()
            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_TAB:
                self.apply_settings()
                self.save_settings()
                self.state = GameState.PLAYING
    
    def adjust_setting(self, direction: int):
        """Adjust the currently selected setting"""
        setting_name = self.settings_options[self.settings_selection]
        
        if setting_name == "Master Volume":
            self.settings.master_volume = max(0.0, min(1.0, self.settings.master_volume + direction * 0.1))
        elif setting_name == "SFX Volume":
            self.settings.sfx_volume = max(0.0, min(1.0, self.settings.sfx_volume + direction * 0.1))
        elif setting_name == "Music Volume":
            self.settings.music_volume = max(0.0, min(1.0, self.settings.music_volume + direction * 0.1))
        elif setting_name == "Screen Scale":
            self.settings.screen_scale = max(0.5, min(2.0, self.settings.screen_scale + direction * 0.1))


    def try_interaction(self):
        if not self.player: return
        current_room_obj = self.rooms[self.player.current_room]
        interaction_rect = self.player.rect.inflate(TILE_SIZE // 2, TILE_SIZE // 2) # Slightly larger interaction radius

        # Check for NPC interaction
        for npc in current_room_obj.npcs:
            if interaction_rect.colliderect(npc.rect):
                self.dialogue_target_npc = npc
                
                # Check for quest interactions
                if npc.quest_giver and npc.quest_id:
                    quest = self.quests.get(npc.quest_id)
                    if quest:
                        if quest.status == QuestStatus.NOT_STARTED:
                            # Offer quest
                            self.dialogue_text = f"I have a task for you: {quest.description}"
                            self.dialogue_choices = ["Accept Quest", "Ask more", "Decline"]
                        elif quest.status == QuestStatus.ACTIVE:
                            # Check quest progress
                            if all(quest.completed_objectives):
                                self.dialogue_text = "Excellent work! You've completed the task."
                                self.dialogue_choices = ["Claim Reward", "Ask more", "Goodbye"]
                            else:
                                completed = sum(quest.completed_objectives)
                                total = len(quest.objectives)
                                self.dialogue_text = f"Progress: {completed}/{total} objectives completed."
                                self.dialogue_choices = ["Check Objectives", "Ask more", "Goodbye"]
                        elif quest.status == QuestStatus.COMPLETED:
                            self.dialogue_text = "Thank you for your help with that task!"
                            self.dialogue_choices = ["Ask more", "Goodbye"]
                        else:
                            self.dialogue_text = random.choice(npc.dialogue_options)
                            self.dialogue_choices = ["Ask more", "Goodbye"]
                    else:
                        self.dialogue_text = random.choice(npc.dialogue_options)
                        self.dialogue_choices = ["Ask more", "Goodbye"]
                else:
                    self.dialogue_text = random.choice(npc.dialogue_options)
                    self.dialogue_choices = ["Ask more", "Goodbye"]
                
                self.selected_choice_idx = 0
                self.state = GameState.DIALOGUE
                
                # Track talking to NPCs for quest objectives
                self.check_quest_objectives("talk_npc", npc.name)
                return

        # Check for item pickup
        for item in current_room_obj.items[:]: # Iterate copy for safe removal
            item_rect = pygame.Rect(item.x * TILE_SIZE, item.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if interaction_rect.colliderect(item_rect):
                self.player.inventory.append(item)
                current_room_obj.items.remove(item)
                self.show_notification(f"Picked up {item.name}", 2)
                
                # Track item pickup for quest objectives
                self.check_quest_objectives("pickup_item", item.name)
                return
        
        # Check for chest interactions
        player_tile_x = self.player.rect.centerx // TILE_SIZE
        player_tile_y = self.player.rect.centery // TILE_SIZE
        
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                check_x, check_y = player_tile_x + dx, player_tile_y + dy
                if (0 <= check_x < current_room_obj.grid_width and 
                    0 <= check_y < current_room_obj.grid_height):
                    if current_room_obj.grid[check_y][check_x] == TileType.CHEST:
                        # Open chest
                        current_room_obj.grid[check_y][check_x] = TileType.FLOOR
                        treasure_items = [
                            Item("Gold Coins", "Shiny gold coins", ItemType.TREASURE, quantity=random.randint(20, 50), value=1),
                            Item("Rare Gem", "A valuable crystal", ItemType.TREASURE, quantity=1, value=100),
                            Item("Health Potion", "Restores HP", ItemType.CONSUMABLE, quantity=random.randint(1, 3))
                        ]
                        found_item = random.choice(treasure_items)
                        self.player.inventory.append(found_item)
                        self.show_notification(f"Found {found_item.name} in chest!", 3)
                        return
        
        # Check for room transitions
        self.check_room_transitions()

    def check_room_transitions(self):
        """Check if player is on an exit tile and handle room transitions"""
        current_room_obj = self.rooms[self.player.current_room]
        player_tile_x = self.player.rect.centerx // TILE_SIZE
        player_tile_y = self.player.rect.centery // TILE_SIZE
        
        # Check if current tile is an exit
        if (0 <= player_tile_x < current_room_obj.grid_width and 
            0 <= player_tile_y < current_room_obj.grid_height):
            if current_room_obj.grid[player_tile_y][player_tile_x] == TileType.EXIT:
                # Find which exit this is
                for direction, (target_room, entry_x, entry_y) in current_room_obj.exits.items():
                    # Check if player is on the correct exit tile for this direction
                    if self.is_player_on_exit_tile(current_room_obj, player_tile_x, player_tile_y, direction):
                        # If target room doesn't exist, it might be a procedural exit
                        if target_room not in self.rooms:
                            target_room = self.discover_new_room(self.player.current_room, direction)
                        
                        self.player.current_room = target_room
                        self.player.rect.centerx = entry_x * TILE_SIZE + TILE_SIZE // 2
                        self.player.rect.centery = entry_y * TILE_SIZE + TILE_SIZE // 2
                        self.show_notification(f"Entered {target_room}", 2)
                        
                        # Track room entry for quest objectives
                        self.check_quest_objectives("enter_room", target_room)
                        return
                
                # If no existing exit found, generate a new room in the direction player is moving
                direction = self.get_direction_from_exit_position(current_room_obj, player_tile_x, player_tile_y)
                if direction and direction not in current_room_obj.exits:
                    target_room = self.discover_new_room(self.player.current_room, direction)
                    # Get the entry position for the new room
                    _, entry_x, entry_y = current_room_obj.exits[direction]
                    self.player.current_room = target_room
                    self.player.rect.centerx = entry_x * TILE_SIZE + TILE_SIZE // 2
                    self.player.rect.centery = entry_y * TILE_SIZE + TILE_SIZE // 2
                    self.show_notification(f"Discovered {target_room}!", 3)
                    self.check_quest_objectives("enter_room", target_room)
    
    def get_direction_from_exit_position(self, room: Room, tile_x: int, tile_y: int) -> Optional[str]:
        """Determine direction based on exit tile position"""
        if tile_y == 0:
            return "north"
        elif tile_y == room.grid_height - 1:
            return "south"
        elif tile_x == 0:
            return "west"
        elif tile_x == room.grid_width - 1:
            return "east"
        return None


    def is_player_on_exit_tile(self, room: Room, player_tile_x: int, player_tile_y: int, direction: str) -> bool:
        """Checks if the player is on a tile that is an exit for the given direction."""
        if direction in room.exits:
            target_room, entry_x, entry_y = room.exits[direction]
            
            # Check if player is on the specific exit tile for this direction
            # The exit tiles are placed at specific coordinates based on direction
            if direction == "north":
                return player_tile_y == 0 and abs(player_tile_x - (GRID_WIDTH // 2)) <= 1
            elif direction == "south":
                return player_tile_y == room.grid_height - 1 and abs(player_tile_x - (GRID_WIDTH // 2)) <= 1
            elif direction == "west":
                return player_tile_x == 0 and abs(player_tile_y - (GRID_HEIGHT // 2)) <= 1
            elif direction == "east":
                return player_tile_x == room.grid_width - 1 and abs(player_tile_y - (GRID_HEIGHT // 2)) <= 1
        return False


    def handle_dialogue_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_choice_idx = (self.selected_choice_idx - 1) % len(self.dialogue_choices)
            elif event.key == pygame.K_DOWN:
                self.selected_choice_idx = (self.selected_choice_idx + 1) % len(self.dialogue_choices)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_e:
                chosen_option = self.dialogue_choices[self.selected_choice_idx]
                
                if chosen_option == "Goodbye" or chosen_option == "Goodbye.":
                    self.state = GameState.PLAYING
                    self.dialogue_target_npc = None
                elif chosen_option == "Accept Quest":
                    # Start the quest
                    if self.dialogue_target_npc and self.dialogue_target_npc.quest_id:
                        self.start_quest(self.dialogue_target_npc.quest_id)
                        self.dialogue_text = "Excellent! I knew I could count on you."
                        self.dialogue_choices = ["Check Objectives", "Goodbye"]
                elif chosen_option == "Claim Reward":
                    # Complete the quest
                    if self.dialogue_target_npc and self.dialogue_target_npc.quest_id:
                        quest = self.quests.get(self.dialogue_target_npc.quest_id)
                        if quest and quest.status == QuestStatus.ACTIVE:
                            self.complete_quest(quest)
                            self.dialogue_text = "Here is your reward! Well earned."
                            self.dialogue_choices = ["Thank you", "Goodbye"]
                elif chosen_option == "Check Objectives":
                    # Show quest objectives
                    if self.dialogue_target_npc and self.dialogue_target_npc.quest_id:
                        quest = self.quests.get(self.dialogue_target_npc.quest_id)
                        if quest:
                            obj_text = "Your tasks:\n"
                            for i, obj in enumerate(quest.objectives):
                                status = "✓" if quest.completed_objectives[i] else "○"
                                obj_text += f"{status} {obj}\n"
                            self.dialogue_text = obj_text.strip()
                            self.dialogue_choices = ["Continue Quest", "Goodbye"]
                elif chosen_option == "Decline":
                    self.dialogue_text = "Perhaps another time then."
                    self.dialogue_choices = ["Ask more", "Goodbye"]
                else: # "Ask more" or other options
                    # Show another random line or contextual information
                    if self.dialogue_target_npc and self.dialogue_target_npc.dialogue_options:
                        self.dialogue_text = random.choice(self.dialogue_target_npc.dialogue_options)
                    else:
                        self.dialogue_text = "They have nothing more to say."
                    self.dialogue_choices = ["Ask more", "Goodbye"]
                
                self.selected_choice_idx = 0

            elif event.key == pygame.K_ESCAPE:
                self.state = GameState.PLAYING
                self.dialogue_target_npc = None

    def handle_inventory_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_i:
                self.state = GameState.PLAYING
            elif event.key == pygame.K_h:  # Use health potion from inventory
                self.use_item("Health Potion")

    def handle_quest_log_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                self.state = GameState.PLAYING
            elif event.key == pygame.K_UP:
                self.quest_log_scroll = max(0, self.quest_log_scroll - 1)
            elif event.key == pygame.K_DOWN:
                max_scroll = max(0, len(self.player.active_quests) - 3) if self.player else 0
                self.quest_log_scroll = min(max_scroll, self.quest_log_scroll + 1)
    
    def update_player_movement(self):
        if not self.player: return
        
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]: dy -= self.player.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy += self.player.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx -= self.player.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += self.player.speed

        if dx != 0 or dy != 0:
            new_rect = self.player.rect.move(dx, 0)
            if not self.check_wall_collision(new_rect):
                self.player.rect = new_rect
            
            new_rect = self.player.rect.move(0, dy)
            if not self.check_wall_collision(new_rect):
                self.player.rect = new_rect

            # Boundary checks for screen (though ideally rooms handle this with walls)
            self.player.rect.clamp_ip(self.screen.get_rect())


    def check_wall_collision(self, rect: pygame.Rect) -> bool:
        if not self.player: return True # No player, no movement
        current_room_obj = self.rooms[self.player.current_room]
        
        # Check collision with screen boundaries first (acting as outer walls)
        if rect.left < 0 or rect.right > SCREEN_WIDTH or rect.top < 0 or rect.bottom > SCREEN_HEIGHT:
            return True

        # Check collision with tiles
        for r_idx, row in enumerate(current_room_obj.grid):
            for c_idx, tile_type in enumerate(row):
                if tile_type == TileType.WALL:
                    wall_rect = pygame.Rect(c_idx * TILE_SIZE, r_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if rect.colliderect(wall_rect):
                        return True
        return False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False # Consider save prompt here
            
            if self.state == GameState.NAME_INPUT:
                self.handle_name_input(event)
            elif self.state == GameState.PLAYING:
                self.handle_playing_input(event)
            elif self.state == GameState.DIALOGUE:
                self.handle_dialogue_input(event)
            elif self.state == GameState.INVENTORY:
                self.handle_inventory_input(event)
            elif self.state == GameState.QUEST_LOG:
                self.handle_quest_log_input(event)
            elif self.state == GameState.SETTINGS:
                self.handle_settings_input(event)
    
    def update(self):
        if self.state == GameState.PLAYING:
            self.update_player_movement()
        
        if self.notification_timer > 0:
            self.notification_timer -=1
            if self.notification_timer == 0:
                self.notification_text = ""


    def draw_name_input(self):
        self.screen.fill(UI_BG_COLOR)
        self.draw_text("Enter Your Name:", self.font_large, TEXT_COLOR, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, align="center")
        
        input_box_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 20, 300, 40)
        pygame.draw.rect(self.screen, UI_BORDER_COLOR, input_box_rect, 2, border_radius=5)
        pygame.draw.rect(self.screen, FLOOR_COLOR, input_box_rect.inflate(-4,-4), border_radius=5)

        self.draw_text(self.input_text, self.font_medium, TEXT_COLOR, input_box_rect.centerx, input_box_rect.centery, align="center")
        self.draw_text("Press ENTER to begin", self.font_small, LIGHT_GRAY, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3, align="center")

    def draw_game(self):
        if not self.player: 
            self.screen.fill(BLACK) # Should not happen if state is PLAYING
            self.draw_text("Error: Player not initialized.", self.font_medium, RED, SCREEN_WIDTH//2, SCREEN_HEIGHT//2, align="center")
            return

        # Set room-specific colors based on biome
        floor_color = FLOOR_COLOR
        wall_color = WALL_COLOR
        current_room_obj = self.rooms[self.player.current_room]
        
        # Select biome-specific colors
        if current_room_obj.room_type == "cave":
            floor_color = CAVE_FLOOR_COLOR
            wall_color = CAVE_WALL_COLOR
        elif current_room_obj.room_type == "forest":
            floor_color = FOREST_FLOOR_COLOR
            wall_color = FOREST_WALL_COLOR
        elif current_room_obj.room_type == "dungeon":
            floor_color = DUNGEON_FLOOR_COLOR
            wall_color = DUNGEON_WALL_COLOR
        elif current_room_obj.room_type == "village":
            floor_color = VILLAGE_FLOOR_COLOR
            wall_color = VILLAGE_WALL_COLOR
        elif current_room_obj.room_type == "mountain":
            floor_color = MOUNTAIN_FLOOR_COLOR
            wall_color = MOUNTAIN_WALL_COLOR
        elif current_room_obj.room_type == "swamp":
            floor_color = SWAMP_FLOOR_COLOR
            wall_color = SWAMP_WALL_COLOR
        elif current_room_obj.room_type == "ruins":
            floor_color = RUINS_FLOOR_COLOR
            wall_color = RUINS_WALL_COLOR
        elif current_room_obj.room_type == "clearing":
            floor_color = CLEARING_FLOOR_COLOR
            wall_color = CLEARING_WALL_COLOR
            
        self.screen.fill(floor_color)  # Background color based on biome

        # Draw tiles
        for r_idx, row in enumerate(current_room_obj.grid):
            for c_idx, tile_type in enumerate(row):
                tile_rect = pygame.Rect(c_idx * TILE_SIZE, r_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if tile_type == TileType.WALL:
                    pygame.draw.rect(self.screen, wall_color, tile_rect)
                    pygame.draw.rect(self.screen, GRAY, tile_rect, 1) # Outline walls
                elif tile_type == TileType.EXIT:
                    pygame.draw.rect(self.screen, (0, 255, 0), tile_rect)  # Bright green for exits
                    pygame.draw.rect(self.screen, WHITE, tile_rect, 3)
                    # Add arrow indicators for exits
                    center_x, center_y = tile_rect.center
                    if r_idx == 0:  # North exit
                        arrow_points = [(center_x, center_y - 8), (center_x - 6, center_y + 2), (center_x + 6, center_y + 2)]
                        pygame.draw.polygon(self.screen, WHITE, arrow_points)
                    elif r_idx == current_room_obj.grid_height - 1:  # South exit
                        arrow_points = [(center_x, center_y + 8), (center_x - 6, center_y - 2), (center_x + 6, center_y - 2)]
                        pygame.draw.polygon(self.screen, WHITE, arrow_points)
                    elif c_idx == 0:  # West exit
                        arrow_points = [(center_x - 8, center_y), (center_x + 2, center_y - 6), (center_x + 2, center_y + 6)]
                        pygame.draw.polygon(self.screen, WHITE, arrow_points)
                    elif c_idx == current_room_obj.grid_width - 1:  # East exit
                        arrow_points = [(center_x + 8, center_y), (center_x - 2, center_y - 6), (center_x - 2, center_y + 6)]
                        pygame.draw.polygon(self.screen, WHITE, arrow_points)
                elif tile_type == TileType.WATER:
                    pygame.draw.rect(self.screen, (0, 100, 255), tile_rect)  # Blue for water
                    pygame.draw.rect(self.screen, (0, 150, 255), tile_rect, 1)
                elif tile_type == TileType.CHEST:
                    pygame.draw.rect(self.screen, (139, 69, 19), tile_rect)  # Brown for chest
                    pygame.draw.rect(self.screen, (255, 215, 0), tile_rect, 2)  # Gold outline

        # Draw items with more detailed visuals
        for item in current_room_obj.items:
            if item.x is not None and item.y is not None:
                item_center_x = item.x * TILE_SIZE + TILE_SIZE // 2
                item_center_y = item.y * TILE_SIZE + TILE_SIZE // 2
                
                if item.item_type == ItemType.KEY_ITEM:
                    # Draw key items as scrolls or special symbols
                    if "Map" in item.name:
                        # Draw as a scroll
                        scroll_rect = pygame.Rect(item_center_x - 12, item_center_y - 8, 24, 16)
                        pygame.draw.rect(self.screen, (240, 230, 140), scroll_rect)  # Khaki color
                        pygame.draw.rect(self.screen, (139, 69, 19), scroll_rect, 2)  # Brown border
                        # Add scroll details
                        pygame.draw.line(self.screen, (139, 69, 19), (scroll_rect.left + 4, scroll_rect.top + 4), 
                                       (scroll_rect.right - 4, scroll_rect.top + 4), 1)
                        pygame.draw.line(self.screen, (139, 69, 19), (scroll_rect.left + 4, scroll_rect.top + 8), 
                                       (scroll_rect.right - 4, scroll_rect.top + 8), 1)
                    elif "Crystal" in item.name:
                        # Draw as a glowing crystal
                        crystal_points = [
                            (item_center_x, item_center_y - 10),
                            (item_center_x - 8, item_center_y - 2),
                            (item_center_x - 5, item_center_y + 8),
                            (item_center_x + 5, item_center_y + 8),
                            (item_center_x + 8, item_center_y - 2)
                        ]
                        pygame.draw.polygon(self.screen, (173, 216, 230), crystal_points)  # Light blue
                        pygame.draw.polygon(self.screen, (0, 191, 255), crystal_points, 2)  # Blue border
                    else:
                        # Default key item appearance
                        pygame.draw.ellipse(self.screen, SPECIAL_ITEM_COLOR, 
                                          pygame.Rect(item_center_x - 10, item_center_y - 10, 20, 20))
                        pygame.draw.ellipse(self.screen, WHITE, 
                                          pygame.Rect(item_center_x - 10, item_center_y - 10, 20, 20), 2)
                        
                elif item.item_type == ItemType.TREASURE:
                    if "Gem" in item.name:
                        # Draw as a diamond
                        gem_points = [
                            (item_center_x, item_center_y - 8),
                            (item_center_x - 6, item_center_y),
                            (item_center_x, item_center_y + 8),
                            (item_center_x + 6, item_center_y)
                        ]
                        pygame.draw.polygon(self.screen, (255, 20, 147), gem_points)  # Deep pink
                        pygame.draw.polygon(self.screen, (255, 255, 255), gem_points, 2)  # White border
                    elif "Gold" in item.name or "Treasure" in item.name:
                        # Draw as a treasure bag
                        bag_rect = pygame.Rect(item_center_x - 8, item_center_y - 6, 16, 12)
                        pygame.draw.ellipse(self.screen, (255, 215, 0), bag_rect)  # Gold
                        pygame.draw.ellipse(self.screen, (184, 134, 11), bag_rect, 2)  # Dark gold border
                        # Add string on top
                        pygame.draw.line(self.screen, (139, 69, 19), (item_center_x - 3, item_center_y - 6), 
                                       (item_center_x + 3, item_center_y - 6), 3)
                    else:
                        # Default treasure appearance
                        pygame.draw.ellipse(self.screen, (255, 215, 0), 
                                          pygame.Rect(item_center_x - 8, item_center_y - 8, 16, 16))
                        
                elif item.item_type == ItemType.CONSUMABLE:
                    if "Potion" in item.name:
                        # Draw as a potion bottle
                        bottle_rect = pygame.Rect(item_center_x - 5, item_center_y - 6, 10, 12)
                        pygame.draw.rect(self.screen, (0, 255, 0), bottle_rect)  # Green liquid
                        pygame.draw.rect(self.screen, (50, 50, 50), bottle_rect, 2)  # Dark border
                        # Bottle neck
                        neck_rect = pygame.Rect(item_center_x - 2, item_center_y - 8, 4, 3)
                        pygame.draw.rect(self.screen, (139, 69, 19), neck_rect)  # Brown cork
                    else:
                        # Default consumable appearance
                        pygame.draw.ellipse(self.screen, ITEM_COLOR, 
                                          pygame.Rect(item_center_x - 8, item_center_y - 8, 16, 16))

        # Draw NPCs with more detailed visuals
        for npc in current_room_obj.npcs:
            npc_center_x = npc.rect.centerx
            npc_center_y = npc.rect.centery
            
            # Draw NPC based on their name/type
            if "Hermit" in npc.name:
                # Draw as an old wizard-like figure
                # Body (robe)
                pygame.draw.ellipse(self.screen, (75, 0, 130), npc.rect)  # Purple robe
                pygame.draw.ellipse(self.screen, (148, 0, 211), npc.rect, 2)  # Violet border
                # Head
                head_rect = pygame.Rect(npc_center_x - 8, npc_center_y - 12, 16, 16)
                pygame.draw.ellipse(self.screen, (255, 220, 177), head_rect)  # Skin tone
                # Beard
                beard_rect = pygame.Rect(npc_center_x - 6, npc_center_y - 2, 12, 8)
                pygame.draw.ellipse(self.screen, (192, 192, 192), beard_rect)  # Gray beard
                # Hat
                hat_points = [
                    (npc_center_x, npc_center_y - 20),
                    (npc_center_x - 8, npc_center_y - 8),
                    (npc_center_x + 8, npc_center_y - 8)
                ]
                pygame.draw.polygon(self.screen, (25, 25, 112), hat_points)  # Dark blue hat
                
            elif "Collector" in npc.name or "Merchant" in npc.name:
                # Draw as a merchant figure
                # Body
                pygame.draw.ellipse(self.screen, (139, 69, 19), npc.rect)  # Brown clothes
                pygame.draw.ellipse(self.screen, (160, 82, 45), npc.rect, 2)  # Saddle brown border
                # Head
                head_rect = pygame.Rect(npc_center_x - 6, npc_center_y - 10, 12, 12)
                pygame.draw.ellipse(self.screen, (255, 220, 177), head_rect)  # Skin tone
                # Hat (merchant cap)
                hat_rect = pygame.Rect(npc_center_x - 8, npc_center_y - 14, 16, 8)
                pygame.draw.ellipse(self.screen, (34, 139, 34), hat_rect)  # Forest green hat
                # Money bag accessory
                bag_rect = pygame.Rect(npc_center_x + 10, npc_center_y + 5, 8, 8)
                pygame.draw.ellipse(self.screen, (255, 215, 0), bag_rect)  # Gold bag
                
            else:
                # Default NPC appearance with more detail
                # Body
                pygame.draw.ellipse(self.screen, npc.color, npc.rect)
                pygame.draw.ellipse(self.screen, WHITE, npc.rect, 2)
                # Head
                head_rect = pygame.Rect(npc_center_x - 6, npc_center_y - 8, 12, 12)
                pygame.draw.ellipse(self.screen, (255, 220, 177), head_rect)  # Skin tone
            
            # Draw name initial on the NPC
            self.draw_text(npc.name[0], self.font_small, WHITE, npc_center_x, npc_center_y + 2, align="center")
            
            # Draw quest indicator
            if npc.quest_giver and npc.quest_id:
                quest = self.quests.get(npc.quest_id)
                if quest:
                    indicator_y = npc.rect.top - 15
                    if quest.status == QuestStatus.NOT_STARTED:
                        # Yellow exclamation mark for new quest
                        pygame.draw.circle(self.screen, (255, 255, 0), (npc_center_x, indicator_y), 10)
                        pygame.draw.circle(self.screen, (255, 140, 0), (npc_center_x, indicator_y), 10, 2)
                        self.draw_text("!", self.font_medium, BLACK, npc_center_x, indicator_y, align="center")
                    elif quest.status == QuestStatus.ACTIVE and not all(quest.completed_objectives):
                        # Blue question mark for active quest
                        pygame.draw.circle(self.screen, (0, 150, 255), (npc_center_x, indicator_y), 10)
                        pygame.draw.circle(self.screen, (0, 100, 200), (npc_center_x, indicator_y), 10, 2)
                        self.draw_text("?", self.font_medium, WHITE, npc_center_x, indicator_y, align="center")
                    elif quest.status == QuestStatus.ACTIVE and all(quest.completed_objectives):
                        # Green checkmark for completed quest ready to turn in
                        pygame.draw.circle(self.screen, (0, 255, 0), (npc_center_x, indicator_y), 10)
                        pygame.draw.circle(self.screen, (0, 200, 0), (npc_center_x, indicator_y), 10, 2)
                        self.draw_text("✓", self.font_medium, BLACK, npc_center_x, indicator_y, align="center")

        # Draw Player with more detail
        player_center_x = self.player.rect.centerx
        player_center_y = self.player.rect.centery
        
        # Player body
        pygame.draw.ellipse(self.screen, PLAYER_COLOR, self.player.rect)
        pygame.draw.ellipse(self.screen, WHITE, self.player.rect, 2)
        
        # Player head
        head_rect = pygame.Rect(player_center_x - 6, player_center_y - 8, 12, 12)
        pygame.draw.ellipse(self.screen, (255, 220, 177), head_rect)  # Skin tone
        pygame.draw.ellipse(self.screen, (200, 180, 140), head_rect, 1)  # Head outline
        
        # Simple hair
        hair_rect = pygame.Rect(player_center_x - 7, player_center_y - 10, 14, 6)
        pygame.draw.ellipse(self.screen, (139, 69, 19), hair_rect)  # Brown hair
        
        # Player name initial
        self.draw_text(self.player.name[0], self.font_small, WHITE, player_center_x, player_center_y + 2, align="center")

        # Draw UI and quest tips
        self.draw_ui_bar()
        self.draw_quest_tips()

    def draw_quest_tips(self):
        """Draw quest tips in the top right corner"""
        if not self.player or not self.player.active_quests:
            return
        
        # Get the most recent active quest
        current_quest_id = self.player.active_quests[-1]
        if current_quest_id not in self.quests:
            return
        
        quest = self.quests[current_quest_id]
        
        # Calculate position (top right corner)
        tip_width = 300
        tip_height = 120
        tip_x = SCREEN_WIDTH - tip_width - 10
        tip_y = 10
        
        # Draw background
        tip_rect = pygame.Rect(tip_x, tip_y, tip_width, tip_height)
        pygame.draw.rect(self.screen, TOOLTIP_BG, tip_rect, border_radius=8)
        pygame.draw.rect(self.screen, QUEST_COLOR, tip_rect, 2, border_radius=8)
        
        # Draw quest title
        title_y = tip_y + 10
        self.draw_text("Current Quest:", self.font_small, QUEST_COLOR, tip_x + 10, title_y)
        self.draw_text(quest.title, self.font_small, WHITE, tip_x + 10, title_y + 15)
        
        # Draw current objective
        objectives_y = title_y + 40
        self.draw_text("Objective:", self.font_small, LIGHT_GRAY, tip_x + 10, objectives_y)
        
        # Find current incomplete objective
        current_objective = None
        for i, completed in enumerate(quest.completed_objectives):
            if not completed and i < len(quest.objectives):
                current_objective = quest.objectives[i]
                break
        
        if current_objective:
            # Wrap objective text if too long
            objective_rect = pygame.Rect(tip_x + 10, objectives_y + 15, tip_width - 20, 40)
            self.draw_wrapped_text(current_objective, self.font_small, WHITE, objective_rect)
        else:
            self.draw_text("All objectives complete!", self.font_small, GREEN, tip_x + 10, objectives_y + 15)
        
        # Draw progress
        completed_count = sum(quest.completed_objectives)
        total_count = len(quest.objectives)
        progress_text = f"Progress: {completed_count}/{total_count}"
        self.draw_text(progress_text, self.font_small, ADVENTURE_GOLD, tip_x + 10, tip_y + tip_height - 25)

    def draw_ui_bar(self):
        """Draw the UI information bar at the top"""
        current_room_obj = self.rooms[self.player.current_room]
        
        # Room name
        self.draw_text(current_room_obj.name, self.font_medium, TEXT_COLOR, SCREEN_WIDTH // 2, 20, align="center")
        
        # Player stats
        self.draw_text(f"HP: {self.player.health}/{self.player.max_health}", self.font_small, GREEN, 10, 10)
        self.draw_text(f"Level: {self.player.level}", self.font_small, TEXT_COLOR, 10, 30)
        self.draw_text(f"Gold: {self.player.gold}", self.font_small, (255, 215, 0), 10, 50)
        
        # Available exits
        if current_room_obj.exits:
            exits_text = "Exits: " + ", ".join(current_room_obj.exits.keys())
            self.draw_text(exits_text, self.font_small, (0, 255, 255), 10, 70)  # Cyan for exits
        
        # Show potential exits (edges of the map that could lead to new rooms)
        potential_exits = []
        if not any(direction == "north" for direction in current_room_obj.exits.keys()):
            potential_exits.append("north")
        if not any(direction == "south" for direction in current_room_obj.exits.keys()):
            potential_exits.append("south")
        if not any(direction == "east" for direction in current_room_obj.exits.keys()):
            potential_exits.append("east")
        if not any(direction == "west" for direction in current_room_obj.exits.keys()):
            potential_exits.append("west")
        
        if potential_exits:
            potential_text = "Unexplored: " + ", ".join(potential_exits)
            self.draw_text(potential_text, self.font_small, (255, 255, 0), 10, 90)  # Yellow for unexplored
        
        # Controls hint
        self.draw_text("WASD=Move, E=Interact, I=Inventory, Q=Quests, H=Health, TAB=Settings", self.font_small, LIGHT_GRAY, SCREEN_WIDTH - 10, SCREEN_HEIGHT - 20, align="topright")


    def draw_dialogue(self):
        self.draw_game() # Draw game world underneath

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,180)) # Semi-transparent black
        self.screen.blit(overlay, (0,0))

        box_width = SCREEN_WIDTH * 0.8
        box_height = SCREEN_HEIGHT * 0.4
        box_x = (SCREEN_WIDTH - box_width) / 2
        box_y = SCREEN_HEIGHT - box_height - 20 # At the bottom

        dialogue_box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(self.screen, UI_BG_COLOR, dialogue_box_rect, border_radius=10)
        pygame.draw.rect(self.screen, UI_BORDER_COLOR, dialogue_box_rect, 2, border_radius=10)

        # Speaker Name
        if self.dialogue_target_npc:
            self.draw_text(self.dialogue_target_npc.name + ":", self.font_medium, ITEM_COLOR, box_x + 20, box_y + 15)
        
        # Dialogue Text (wrapped)
        text_y_offset = box_y + 50
        self.draw_wrapped_text(self.dialogue_text, self.font_small, TEXT_COLOR, 
                               pygame.Rect(box_x + 20, text_y_offset, box_width - 40, box_height - 100))


        # Choices
        choice_start_y = box_y + box_height - (len(self.dialogue_choices) * 30) - 15
        for i, choice_text in enumerate(self.dialogue_choices):
            color = PLAYER_COLOR if i == self.selected_choice_idx else TEXT_COLOR
            prefix = "> " if i == self.selected_choice_idx else "  "
            self.draw_text(prefix + choice_text, self.font_small, color, box_x + 30, choice_start_y + i * 30)


    def draw_inventory(self):
        self.draw_game() # Draw game world underneath

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,180)) 
        self.screen.blit(overlay, (0,0))

        box_width = SCREEN_WIDTH * 0.7
        box_height = SCREEN_HEIGHT * 0.7
        box_x = (SCREEN_WIDTH - box_width) / 2
        box_y = (SCREEN_HEIGHT - box_height) / 2

        inv_box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(self.screen, UI_BG_COLOR, inv_box_rect, border_radius=10)
        pygame.draw.rect(self.screen, UI_BORDER_COLOR, inv_box_rect, 2, border_radius=10)

        self.draw_text("Inventory", self.font_large, ITEM_COLOR, inv_box_rect.centerx, box_y + 30, align="center")

        if not self.player or not self.player.inventory:
            self.draw_text("Empty", self.font_medium, TEXT_COLOR, inv_box_rect.centerx, inv_box_rect.centery, align="center")
        else:
            item_y_start = box_y + 80
            
            # Group items by type
            consumables = [item for item in self.player.inventory if item.item_type == ItemType.CONSUMABLE]
            key_items = [item for item in self.player.inventory if item.item_type == ItemType.KEY_ITEM]
            treasures = [item for item in self.player.inventory if item.item_type == ItemType.TREASURE]
            
            y_offset = 0
            
            if key_items:
                self.draw_text("Key Items:", self.font_medium, SPECIAL_ITEM_COLOR, box_x + 30, item_y_start + y_offset)
                y_offset += 25
                for item in key_items:
                    self.draw_text(f"• {item.name}: {item.description}", self.font_small, TEXT_COLOR, box_x + 50, item_y_start + y_offset)
                    y_offset += 20
                y_offset += 10
            
            if consumables:
                self.draw_text("Consumables:", self.font_medium, GREEN, box_x + 30, item_y_start + y_offset)
                y_offset += 25
                for item in consumables:
                    self.draw_text(f"• {item.name} (x{item.quantity}): {item.description}", self.font_small, TEXT_COLOR, box_x + 50, item_y_start + y_offset)
                    y_offset += 20
                y_offset += 10
            
            if treasures:
                self.draw_text("Treasures:", self.font_medium, (255, 215, 0), box_x + 30, item_y_start + y_offset)
                y_offset += 25
                for item in treasures:
                    value_text = f" (Value: {item.value})" if item.value > 0 else ""
                    self.draw_text(f"• {item.name} (x{item.quantity}){value_text}", self.font_small, TEXT_COLOR, box_x + 50, item_y_start + y_offset)
                    y_offset += 20
        
        self.draw_text("Press H to use Health Potion | I or ESC to close", self.font_small, LIGHT_GRAY, inv_box_rect.centerx, box_y + box_height - 30, align="center")

    def draw_settings(self):
        self.draw_game()  # Draw game world underneath

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))

        box_width = SCREEN_WIDTH * 0.6
        box_height = SCREEN_HEIGHT * 0.7
        box_x = (SCREEN_WIDTH - box_width) / 2
        box_y = (SCREEN_HEIGHT - box_height) / 2

        settings_box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(self.screen, UI_BG_COLOR, settings_box_rect, border_radius=10)
        pygame.draw.rect(self.screen, UI_BORDER_COLOR, settings_box_rect, 2, border_radius=10)

        self.draw_text("Settings", self.font_large, TEXT_COLOR, settings_box_rect.centerx, box_y + 30, align="center")

        # Draw settings options
        option_start_y = box_y + 80
        option_spacing = 50

        for i, option in enumerate(self.settings_options):
            y_pos = option_start_y + i * option_spacing
            
            # Highlight selected option
            if i == self.settings_selection:
                highlight_rect = pygame.Rect(box_x + 20, y_pos - 5, box_width - 40, 30)
                pygame.draw.rect(self.screen, ADVENTURE_BROWN, highlight_rect, border_radius=5)
            
            # Draw option name
            color = ADVENTURE_GOLD if i == self.settings_selection else TEXT_COLOR
            self.draw_text(option, self.font_medium, color, box_x + 40, y_pos)
            
            # Draw option value
            value_x = box_x + box_width - 200
            if option == "Master Volume":
                volume_percent = int(self.settings.master_volume * 100)
                self.draw_text(f"{volume_percent}%", self.font_medium, color, value_x, y_pos)
                # Draw volume bar
                bar_width = 100
                bar_height = 10
                bar_x = value_x + 50
                bar_y = y_pos + 5
                bar_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
                pygame.draw.rect(self.screen, DARK_GRAY, bar_rect)
                fill_width = int(bar_width * self.settings.master_volume)
                if fill_width > 0:
                    fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
                    pygame.draw.rect(self.screen, GREEN, fill_rect)
                
            elif option == "SFX Volume":
                volume_percent = int(self.settings.sfx_volume * 100)
                self.draw_text(f"{volume_percent}%", self.font_medium, color, value_x, y_pos)
                # Draw volume bar
                bar_width = 100
                bar_height = 10
                bar_x = value_x + 50
                bar_y = y_pos + 5
                bar_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
                pygame.draw.rect(self.screen, DARK_GRAY, bar_rect)
                fill_width = int(bar_width * self.settings.sfx_volume)
                if fill_width > 0:
                    fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
                    pygame.draw.rect(self.screen, BLUE, fill_rect)
                    
            elif option == "Music Volume":
                volume_percent = int(self.settings.music_volume * 100)
                self.draw_text(f"{volume_percent}%", self.font_medium, color, value_x, y_pos)
                # Draw volume bar
                bar_width = 100
                bar_height = 10
                bar_x = value_x + 50
                bar_y = y_pos + 5
                bar_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
                pygame.draw.rect(self.screen, DARK_GRAY, bar_rect)
                fill_width = int(bar_width * self.settings.music_volume)
                if fill_width > 0:
                    fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
                    pygame.draw.rect(self.screen, RED, fill_rect)
                    
            elif option == "Screen Scale":
                scale_percent = int(self.settings.screen_scale * 100)
                self.draw_text(f"{scale_percent}%", self.font_medium, color, value_x, y_pos)
                
            elif option == "Fullscreen":
                fullscreen_text = "ON" if self.settings.fullscreen else "OFF"
                self.draw_text(fullscreen_text, self.font_medium, color, value_x, y_pos)
                
            elif option == "Back":
                pass  # No value to display

        # Draw instructions
        instructions = [
            "↑↓ Navigate options",
            "←→ Adjust values",
            "ENTER Toggle/Select",
            "TAB/ESC Return to game"
        ]
        
        instr_start_y = box_y + box_height - 100
        for i, instruction in enumerate(instructions):
            self.draw_text(instruction, self.font_small, LIGHT_GRAY, box_x + 40, instr_start_y + i * 18)

    def draw_quest_log(self):
        self.draw_game() # Draw game world underneath

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,180)) 
        self.screen.blit(overlay, (0,0))

        box_width = SCREEN_WIDTH * 0.8
        box_height = SCREEN_HEIGHT * 0.8
        box_x = (SCREEN_WIDTH - box_width) / 2
        box_y = (SCREEN_HEIGHT - box_height) / 2

        quest_box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(self.screen, UI_BG_COLOR, quest_box_rect, border_radius=10)
        pygame.draw.rect(self.screen, UI_BORDER_COLOR, quest_box_rect, 2, border_radius=10)

        self.draw_text("Quest Log", self.font_large, QUEST_COLOR, quest_box_rect.centerx, box_y + 30, align="center")

        if not self.player or not self.player.active_quests:
            self.draw_text("No active quests", self.font_medium, TEXT_COLOR, quest_box_rect.centerx, quest_box_rect.centery, align="center")
        else:
            quest_y_start = box_y + 80
            y_offset = 0
            
            for quest_id in self.player.active_quests:
                if quest_id in self.quests:
                    quest = self.quests[quest_id]
                    
                    # Quest title
                    self.draw_text(quest.title, self.font_medium, QUEST_COLOR, box_x + 30, quest_y_start + y_offset)
                    y_offset += 25
                    
                    # Quest description
                    self.draw_wrapped_text(quest.description, self.font_small, TEXT_COLOR, 
                                         pygame.Rect(box_x + 50, quest_y_start + y_offset, box_width - 100, 40))
                    y_offset += 45
                    
                    # Objectives
                    self.draw_text("Objectives:", self.font_small, LIGHT_GRAY, box_x + 50, quest_y_start + y_offset)
                    y_offset += 20
                    
                    for i, objective in enumerate(quest.objectives):
                        status = "✓" if quest.completed_objectives[i] else "○"
                        color = GREEN if quest.completed_objectives[i] else TEXT_COLOR
                        self.draw_text(f"  {status} {objective}", self.font_small, color, box_x + 70, quest_y_start + y_offset)
                        y_offset += 18
                    
                    y_offset += 20  # Space between quests
        
        self.draw_text("Press Q or ESC to close", self.font_small, LIGHT_GRAY, quest_box_rect.centerx, box_y + box_height - 30, align="center")


    def draw_notifications(self):
        if self.notification_text and self.notification_timer > 0:
            text_surface = self.font_small.render(self.notification_text, True, TEXT_COLOR)
            text_rect = text_surface.get_rect(centerx=SCREEN_WIDTH // 2, bottom=SCREEN_HEIGHT - 20)
            
            bg_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, UI_BG_COLOR, bg_rect, border_radius=5)
            pygame.draw.rect(self.screen, UI_BORDER_COLOR, bg_rect, 1, border_radius=5)
            self.screen.blit(text_surface, text_rect)

    def draw_text(self, text: str, font: pygame.font.Font, color: Tuple[int,int,int], x: int, y: int, align="topleft"):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "center": text_rect.center = (x,y)
        elif align == "topleft": text_rect.topleft = (x,y)
        elif align == "topright": text_rect.topright = (x,y)
        elif align == "midbottom": text_rect.midbottom = (x,y)
        elif align == "midleft": text_rect.midleft = (x,y)
        elif align == "midright": text_rect.midright = (x,y)
        self.screen.blit(text_surface, text_rect)

    def draw_wrapped_text(self, text: str, font: pygame.font.Font, color: Tuple[int,int,int], rect: pygame.Rect):
        words = text.split(' ')
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] <= rect.width:
                current_line = test_line
            else:
                lines.append(current_line.strip())
                current_line = word + " "
        lines.append(current_line.strip())

        y_offset = 0
        for line in lines:
            if y_offset + font.get_linesize() > rect.height: break # Don't overflow box
            self.draw_text(line, font, color, rect.x, rect.y + y_offset)
            y_offset += font.get_linesize()


    def draw(self):
        if self.state == GameState.NAME_INPUT:
            self.draw_name_input()
        elif self.state == GameState.PLAYING:
            self.draw_game()
        elif self.state == GameState.DIALOGUE:
            self.draw_dialogue()
        elif self.state == GameState.INVENTORY:
            self.draw_inventory()
        elif self.state == GameState.QUEST_LOG:
            self.draw_quest_log()
        elif self.state == GameState.SETTINGS:
            self.draw_settings()
        
        self.draw_notifications() # Draw notifications on top of everything
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        # Prompt to save before quitting?
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
