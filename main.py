import pygame
import sys
import json
import random
import os
import math
from enum import Enum
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, field, asdict
from enemies import Enemy, EnemyType, EnemyBehavior
import resources

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
    TITLE_SCREEN = 0  # Title screen with options
    NAME_INPUT = 1    # Character name input
    PLAYING = 2       # Main gameplay
    MENU = 3          # In-game menu
    INVENTORY = 4     # Inventory screen
    DIALOGUE = 5      # NPC dialogue
    GAME_OVER = 6     # Game over screen
    QUEST_LOG = 7     # Quest management
    SETTINGS = 8      # Settings menu
    SAVE_MENU = 9     # Save game menu with slots
    LOAD_MENU = 10    # Load game menu with slots
    COMBAT = 11       # Combat interaction

class ItemType(Enum):
    CONSUMABLE = 1
    KEY_ITEM = 2
    WEAPON = 3
    TREASURE = 4

class QuestStatus(Enum):
    NOT_STARTED = 1
    ACTIVE = 2
    COMPLETED = 3

class NPCPersonality(Enum):
    FRIENDLY = 1
    GRUFF = 2
    MYSTERIOUS = 3
    GREEDY = 4
    SCHOLARLY = 5
    PARANOID = 6
    CHEERFUL = 7
    MELANCHOLIC = 8

class NPCMood(Enum):
    CONTENT = 1
    EXCITED = 2
    WORRIED = 3
    ANGRY = 4
    SAD = 5
    CURIOUS = 6

# Personality color mapping for visual representation
PERSONALITY_COLORS = {
    NPCPersonality.FRIENDLY: (100, 200, 100),     # Light green
    NPCPersonality.GRUFF: (150, 100, 100),        # Brownish red
    NPCPersonality.MYSTERIOUS: (120, 100, 180),   # Purple
    NPCPersonality.GREEDY: (200, 200, 50),        # Gold
    NPCPersonality.SCHOLARLY: (100, 150, 200),    # Light blue
    NPCPersonality.PARANOID: (180, 180, 180),     # Gray
    NPCPersonality.CHEERFUL: (255, 200, 100),     # Orange
    NPCPersonality.MELANCHOLIC: (100, 100, 150),  # Dark blue
}

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
    attack_cooldown: int = 0  # Attack cooldown timer

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
            'active_quests': self.active_quests,
            'attack_cooldown': self.attack_cooldown
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
            active_quests=data.get('active_quests', []),
            attack_cooldown=data.get('attack_cooldown', 0)
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
    
    # Enhanced personality system
    personality: NPCPersonality = NPCPersonality.FRIENDLY
    current_mood: NPCMood = NPCMood.CONTENT
    interaction_count: int = 0  # How many times player has talked to this NPC
    relationship_level: int = 0  # -100 to 100, affects dialogue and prices
    last_interaction_time: int = 0  # Game ticks since last interaction
    
    # Dynamic dialogue system
    dialogue_history: List[str] = field(default_factory=list)  # Track conversation history
    contextual_responses: Dict[str, List[str]] = field(default_factory=dict)  # Context-based responses
    
    # NPC behavior
    movement_pattern: str = "stationary"  # stationary, wander, patrol
    patrol_points: List[Tuple[int, int]] = field(default_factory=list)
    movement_timer: int = 0
    home_position: Tuple[int, int] = (0, 0)  # Original spawn position
    
    # Trading and services
    gold: int = 50  # NPC's money for trading
    services: List[str] = field(default_factory=list)  # heal, repair, information, etc.
    
    def __post_init__(self):
        """Initialize derived properties after creation"""
        self.home_position = (self.rect.centerx, self.rect.centery)
        # Set color based on personality
        if self.personality in PERSONALITY_COLORS:
            self.color = PERSONALITY_COLORS[self.personality]
        # Generate contextual responses based on personality
        self.generate_personality_responses()
    
    def generate_personality_responses(self):
        """Generate personality-specific dialogue responses"""
        base_greetings = {
            NPCPersonality.FRIENDLY: [
                "Hello there, friend! How can I help you today?",
                "Welcome! It's always nice to see a new face around here.",
                "Greetings, traveler! What brings you to these parts?"
            ],
            NPCPersonality.GRUFF: [
                "What do you want?",
                "I'm busy. Make it quick.",
                "Hmph. Another wanderer, I suppose."
            ],
            NPCPersonality.MYSTERIOUS: [
                "Ah... I wondered when you would arrive...",
                "The winds whispered of your coming...",
                "Fate has many paths, yours leads here..."
            ],
            NPCPersonality.GREEDY: [
                "Got any gold to spend?",
                "Business is business, what can I sell you?",
                "Time is money, friend. What do you need?"
            ],
            NPCPersonality.SCHOLARLY: [
                "Fascinating! A traveler with an inquiring look.",
                "Knowledge is the greatest treasure. What would you learn?",
                "I have studied many things. Perhaps I can enlighten you."
            ],
            NPCPersonality.PARANOID: [
                "You're not one of THEM, are you?",
                "Keep your voice down... walls have ears.",
                "Can't be too careful these days..."
            ],
            NPCPersonality.CHEERFUL: [
                "What a wonderful day to meet someone new!",
                "Oh my, a visitor! How delightful!",
                "Hello hello! Isn't life just grand?"
            ],
            NPCPersonality.MELANCHOLIC: [
                "Oh... hello. I wasn't expecting company.",
                "Another soul wandering these lonely paths...",
                "The days grow long when you're alone..."
            ]
        }
        
        self.contextual_responses["greeting"] = base_greetings.get(
            self.personality, base_greetings[NPCPersonality.FRIENDLY]
        )
        
        # Add mood-modified responses
        self.generate_mood_responses()
    
    def generate_mood_responses(self):
        """Generate responses based on current mood"""
        mood_modifiers = {
            NPCMood.EXCITED: [
                "I have wonderful news to share!",
                "Oh, I'm so glad you're here!",
                "Everything is going so well today!"
            ],
            NPCMood.WORRIED: [
                "I'm quite concerned about recent events...",
                "Something troubling has been happening...",
                "I fear things may get worse before they get better."
            ],
            NPCMood.ANGRY: [
                "I'm not in the mood for pleasantries.",
                "Things have been going poorly lately.",
                "Don't expect me to be cheerful right now."
            ],
            NPCMood.SAD: [
                "I'm not feeling very talkative today...",
                "Life has been difficult recently...",
                "Perhaps we could speak another time."
            ],
            NPCMood.CURIOUS: [
                "You seem interesting... tell me about yourself.",
                "I'd love to hear about your adventures!",
                "What fascinating stories you must have!"
            ]
        }
        
        if self.current_mood != NPCMood.CONTENT and self.current_mood in mood_modifiers:
            self.contextual_responses["mood"] = mood_modifiers[self.current_mood]
    
    def get_dialogue_response(self, context: str = "greeting") -> str:
        """Get an appropriate response based on context and relationship"""
        # Adjust response based on relationship level
        if self.relationship_level < -50:
            negative_responses = [
                "I don't think we have anything to discuss.",
                "Perhaps you should find someone else to bother.",
                "I'm not interested in talking to you."
            ]
            return random.choice(negative_responses)
        elif self.relationship_level > 50:
            positive_responses = [
                "Always a pleasure to see you, my friend!",
                "You're one of the good ones, you know that?",
                "I'm glad our paths crossed!"
            ]
            return random.choice(positive_responses)
        
        # Use contextual responses
        if context in self.contextual_responses:
            available_responses = self.contextual_responses[context]
        else:
            available_responses = self.dialogue_options
        
        # Mix in mood responses occasionally
        if "mood" in self.contextual_responses and random.random() < 0.3:
            available_responses.extend(self.contextual_responses["mood"])
        
        if available_responses:
            response = random.choice(available_responses)
            # Avoid repeating the same response too often
            if response not in self.dialogue_history[-3:]:  # Don't repeat last 3 responses
                self.dialogue_history.append(response)
                return response
        
        # Fallback to dialogue options
        if self.dialogue_options:
            return random.choice(self.dialogue_options)
        
        return "..."  # Silent fallback
    
    def modify_relationship(self, change: int):
        """Modify relationship level with bounds checking"""
        self.relationship_level = max(-100, min(100, self.relationship_level + change))
        
        # Update mood based on relationship changes
        if change > 0:
            if self.current_mood in [NPCMood.ANGRY, NPCMood.SAD]:
                self.current_mood = NPCMood.CONTENT
            elif random.random() < 0.3:
                self.current_mood = NPCMood.EXCITED
        elif change < -10:
            if random.random() < 0.5:
                self.current_mood = NPCMood.ANGRY
    
    def update_behavior(self, game_ticks: int):
        """Update NPC behavior like movement and mood changes"""
        # Mood changes over time
        if game_ticks - self.last_interaction_time > 1000:  # About 16 seconds at 60 FPS
            if random.random() < 0.1:  # 10% chance to change mood
                self.current_mood = random.choice(list(NPCMood))
                self.generate_mood_responses()
        
        # Movement behavior
        if self.movement_pattern == "wander" and self.movement_timer <= 0:
            # Wander randomly but stay near home
            home_x, home_y = self.home_position
            max_distance = 100  # pixels
            
            new_x = home_x + random.randint(-max_distance, max_distance)
            new_y = home_y + random.randint(-max_distance, max_distance)
            
            # Constrain to screen bounds
            new_x = max(TILE_SIZE, min(SCREEN_WIDTH - TILE_SIZE, new_x))
            new_y = max(TILE_SIZE, min(SCREEN_HEIGHT - TILE_SIZE, new_y))
            
            self.rect.centerx = new_x
            self.rect.centery = new_y
            self.movement_timer = random.randint(180, 600)  # 3-10 seconds
        elif self.movement_pattern == "patrol" and self.patrol_points and self.movement_timer <= 0:
            # Move between patrol points
            if not hasattr(self, 'patrol_index'):
                self.patrol_index = 0
            
            target_x, target_y = self.patrol_points[self.patrol_index]
            self.rect.centerx = target_x
            self.rect.centery = target_y
            
            self.patrol_index = (self.patrol_index + 1) % len(self.patrol_points)
            self.movement_timer = random.randint(240, 480)  # 4-8 seconds
        
        if self.movement_timer > 0:
            self.movement_timer -= 1

    def to_dict(self):
        return {
            'name': self.name,
            'rect': {'x': self.rect.x, 'y': self.rect.y, 'width': self.rect.width, 'height': self.rect.height},
            'dialogue_options': self.dialogue_options,
            'color': self.color,
            'quest_giver': self.quest_giver,
            'quest_id': self.quest_id,
            'shop_items': [item.to_dict() for item in self.shop_items],
            # Enhanced personality system fields
            'personality': self.personality.value if isinstance(self.personality, NPCPersonality) else self.personality,
            'current_mood': self.current_mood.value if isinstance(self.current_mood, NPCMood) else self.current_mood,
            'interaction_count': self.interaction_count,
            'relationship_level': self.relationship_level,
            'last_interaction_time': self.last_interaction_time,
            'dialogue_history': self.dialogue_history,
            'contextual_responses': self.contextual_responses,
            'movement_pattern': self.movement_pattern,
            'patrol_points': self.patrol_points,
            'movement_timer': self.movement_timer,
            'home_position': self.home_position,
            'gold': self.gold,
            'services': self.services
        }
    
    @classmethod
    def from_dict(cls, data):
        rect_data = data['rect']
        rect = pygame.Rect(rect_data['x'], rect_data['y'], rect_data['width'], rect_data['height'])
        
        # Handle personality - could be string or enum value
        personality_data = data.get('personality', NPCPersonality.FRIENDLY)
        if isinstance(personality_data, str):
            try:
                personality = NPCPersonality[personality_data]
            except KeyError:
                personality = NPCPersonality.FRIENDLY
        elif isinstance(personality_data, int):
            try:
                personality = NPCPersonality(personality_data)
            except ValueError:
                personality = NPCPersonality.FRIENDLY
        else:
            personality = personality_data if personality_data else NPCPersonality.FRIENDLY
        
        # Handle mood - could be string or enum value
        mood_data = data.get('current_mood', data.get('mood', NPCMood.CONTENT))
        if isinstance(mood_data, str):
            try:
                current_mood = NPCMood[mood_data]
            except KeyError:
                current_mood = NPCMood.CONTENT
        elif isinstance(mood_data, int):
            try:
                current_mood = NPCMood(mood_data)
            except ValueError:
                current_mood = NPCMood.CONTENT
        else:
            current_mood = mood_data if mood_data else NPCMood.CONTENT
        
        npc = cls(
            name=data['name'],
            rect=rect,
            dialogue_options=data.get('dialogue_options', []),
            color=tuple(data.get('color', NPC_COLOR)),
            quest_giver=data.get('quest_giver', False),
            quest_id=data.get('quest_id'),
            shop_items=[],  # Will be populated below
            personality=personality,
            current_mood=current_mood,
            interaction_count=data.get('interaction_count', 0),
            relationship_level=data.get('relationship_level', 0),
            last_interaction_time=data.get('last_interaction_time', 0),
            dialogue_history=data.get('dialogue_history', []),
            contextual_responses=data.get('contextual_responses', {}),
            movement_pattern=data.get('movement_pattern', 'stationary'),
            patrol_points=data.get('patrol_points', []),
            movement_timer=data.get('movement_timer', 0),
            home_position=tuple(data.get('home_position', (0, 0))),
            gold=data.get('gold', 50),
            services=data.get('services', [])
        )
        
        # Populate shop items
        npc.shop_items = [Item.from_dict(item_data) for item_data in data.get('shop_items', [])]
        
        return npc


class Room:
    def __init__(self, name: str, grid_width: int, grid_height: int, room_type: str = "cave"):
        self.name = name
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.room_type = room_type  # cave, forest, dungeon, village, etc.
        self.grid: List[List[TileType]] = []
        self.items: List[Item] = []
        self.npcs: List[NPC] = []
        self.enemies: List[Enemy] = []  # List of enemies in the room
        self.exits: Dict[str, Tuple[str, int, int]] = {} # direction: (target_room_name, entry_tile_x, entry_tile_y)
        self.visited = False
        self.difficulty_level = 1  # For procedural content scaling
        self.generate_procedural_layout()
        
        # Texture names for this room
        self.floor_texture = f"{room_type}_floor"
        self.wall_texture = f"{room_type}_wall"

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
                        random.random() < 0.8):  #  80% chance per segment (gaps in fence)
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
                )[0];
                
                if obj_type == 'wall':
                    self.grid[obj_y][obj_x] = TileType.WALL
                elif obj_type == 'water':
                    self.grid[obj_y][obj_x] = TileType.WATER

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

    def add_enemy(self, enemy: Enemy):
        """Add an enemy to the room, placing it on a random floor tile"""
        possible_locations = []
        for r_idx, row in enumerate(self.grid):
            for c_idx, tile in enumerate(row):
                if tile == TileType.FLOOR:
                    occupied = False
                    # Check against items
                    for existing_item in self.items:
                        if existing_item.x == c_idx and existing_item.y == r_idx:
                            occupied = True; break
                    if occupied: continue
                    # Check against NPCs
                    for existing_npc in self.npcs:
                        if existing_npc.rect.colliderect(pygame.Rect(c_idx * TILE_SIZE, r_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE)):
                            occupied = True; break
                    if occupied: continue
                    # Check against other enemies
                    for existing_enemy in self.enemies:
                        if existing_enemy.rect.colliderect(pygame.Rect(c_idx * TILE_SIZE, r_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE)):
                            occupied = True; break
                    if not occupied:
                        possible_locations.append((c_idx, r_idx))
        
        if possible_locations:
            enemy_tile_x, enemy_tile_y = random.choice(possible_locations)
            enemy.rect.topleft = (enemy_tile_x * TILE_SIZE, enemy_tile_y * TILE_SIZE)
            self.enemies.append(enemy)

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
            'enemies': [enemy.to_dict() for enemy in self.enemies],
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
        room.enemies = [Enemy.from_dict(enemy_data) for enemy_data in data.get('enemies', [])]
        room.exits = data.get('exits', {})
        room.visited = data.get('visited', False)
        room.difficulty_level = data.get('difficulty_level', 1)
        return room

class Game:
    def __init__(self):
        pygame.init()
        
        # Try to initialize audio mixer, but don't fail if it's not available
        try:
            pygame.mixer.init()
            self.audio_available = True
        except pygame.error:
            print("Audio not available, continuing without sound...")
            self.audio_available = False
        
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
        
        self.state = GameState.TITLE_SCREEN
        self.player: Optional[Player] = None
        self.rooms: Dict[str, Room] = {}
        self.quests: Dict[str, Quest] = {}  # All available quests
        
        # Procedural room generation tracking
        self.room_id_counter = 1000  # Start procedural rooms at 1000+
        self.discovered_exits: Dict[str, Tuple[str, str]] = {}  # (room_name, direction) -> (target_room_name, target_direction)
        
        self.font_small = pygame.font.Font(FONT_NAME, FONT_SIZE_SMALL)
        self.font_medium = pygame.font.Font(FONT_NAME, FONT_SIZE_MEDIUM)
        self.font_large = pygame.font.Font(FONT_NAME, FONT_SIZE_LARGE)
        self.font_tiny = pygame.font.Font(FONT_NAME, FONT_SIZE_TINY)
        
        self.input_text = ""
        self.dialogue_target_npc: Optional[NPC] = None
        self.dialogue_text = ""
        self.dialogue_choices: List[str] = []
        self.selected_choice_idx = 0
        self.quest_log_scroll = 0  # For scrolling through quest log
        
        # Menu navigation state
        self.menu_selected_index = 0  # Currently selected menu option
        self.menu_options = ["Resume", "Settings", "Save Game", "Load Game", "Quit"]
        
        # Settings menu state
        self.settings_selection = 0
        self.settings_options = ["Master Volume", "SFX Volume", "Music Volume", "Screen Scale", "Fullscreen", "Back"]
        
        self.notification_text = ""
        self.notification_timer = 0

        # Initialize texture resources
        resources.init()

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
        if self.audio_available:
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
        
        # Add procedural enemies based on difficulty and room type
        self.add_procedural_enemies(room, room_type, difficulty)
        
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
        
        # Randomly assign personality and mood
        personality = random.choice(list(NPCPersonality))
        mood = random.choice(list(NPCMood))
        
        npc = NPC(name, pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE), dialogue, 
                  personality=personality, current_mood=mood)
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

        # Add enemies to initial rooms
        # Start room - just a few weak enemies
        slime1 = Enemy(EnemyType.SLIME, pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE), 8)
        start_room.add_enemy(slime1)
        
        # Crystal Chamber - moderate enemies
        bat1 = Enemy(EnemyType.BAT, pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE), 6)
        bat1.behavior = EnemyBehavior.PATROL
        crystal_chamber.add_enemy(bat1)
        spider1 = Enemy(EnemyType.SPIDER, pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE), 10)
        spider1.behavior = EnemyBehavior.LURK
        crystal_chamber.add_enemy(spider1)
        
        # Underground Tunnels - tougher enemies
        skeleton1 = Enemy(EnemyType.SKELETON, pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE), 15)
        underground_tunnels.add_enemy(skeleton1)
        goblin1 = Enemy(EnemyType.GOBLIN, pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE), 12)
        underground_tunnels.add_enemy(goblin1)
        
        # Lost City - stronger enemies
        skeleton2 = Enemy(EnemyType.SKELETON, pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE), 18)
        lost_city.add_enemy(skeleton2)
        spider2 = Enemy(EnemyType.SPIDER, pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE), 12)
        spider2.behavior = EnemyBehavior.LURK
        lost_city.add_enemy(spider2)
        goblin2 = Enemy(EnemyType.GOBLIN, pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE), 14)
        lost_city.add_enemy(goblin2)
        
        # Bandit Camp - aggressive enemies
        goblin3 = Enemy(EnemyType.GOBLIN, pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE), 16)
        goblin3.behavior = EnemyBehavior.AGGRESSIVE
        bandit_camp.add_enemy(goblin3)
        skeleton3 = Enemy(EnemyType.SKELETON, pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE), 20)
        bandit_camp.add_enemy(skeleton3)

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

    def transition_to_adjacent_room(self, direction: str):
        """Handle natural room transitions when player walks off screen edge"""
        if not self.player:
            return
            
        current_room_obj = self.rooms[self.player.current_room]
        
        # Check if there's already an exit in this direction
        if direction in current_room_obj.exits:
            target_room, entry_x, entry_y = current_room_obj.exits[direction]
            # If target room doesn't exist, generate it
            if target_room not in self.rooms:
                target_room = self.discover_new_room(self.player.current_room, direction)
                entry_x, entry_y = self.get_entry_position(direction)
        else:
            # Generate a new room in this direction
            target_room = self.discover_new_room(self.player.current_room, direction)
            entry_x, entry_y = self.get_entry_position(direction)
            
        # Move player to new room at opposite edge
        self.player.current_room = target_room
        self.player.rect.centerx = entry_x * TILE_SIZE + TILE_SIZE // 2
        self.player.rect.centery = entry_y * TILE_SIZE + TILE_SIZE // 2
        
        self.show_notification(f"Entered {target_room}", 2)
        self.check_quest_objectives("enter_room", target_room)
    
    def check_quest_objectives(self, action_type: str, action_target: str):
        """Check if any quest objectives are completed by this action"""
        if not self.player:
            return
            
        for quest_id in self.player.active_quests:
            if quest_id in self.quests:
                quest = self.quests[quest_id]
                if quest.status == QuestStatus.ACTIVE:
                    # Check each objective
                    for i, objective in enumerate(quest.objectives):
                        if not quest.completed_objectives[i]:
                            # Simple pattern matching for objectives
                            if action_type == "enter_room" and action_target.lower() in objective.lower():
                                quest.completed_objectives[i] = True
                                self.show_notification(f"Quest objective completed: {objective}", 3)
                            elif action_type == "collect_item" and action_target.lower() in objective.lower():
                                quest.completed_objectives[i] = True
                                self.show_notification(f"Quest objective completed: {objective}", 3)
                            elif action_type == "talk_to_npc" and action_target.lower() in objective.lower():
                                quest.completed_objectives[i] = True
                                self.show_notification(f"Quest objective completed: {objective}", 3)
                    
                    # Check if quest is complete
                    if all(quest.completed_objectives):
                        quest.status = QuestStatus.COMPLETED
                        self.show_notification(f"Quest completed: {quest.title}", 4)
                        # Give rewards
                        for reward_item in quest.reward_items:
                            self.player.inventory.append(Item(reward_item, f"Reward from {quest.title}", ItemType.TREASURE))
    
    def create_story_quests(self):
        """Create the main story quests"""
        main_quest = Quest(
            id="main_01",
            title="Ancient Mysteries",
            description="Explore the mystical caves and uncover their secrets.",
            objectives=[
                "Talk to the Cave Hermit",
                "Find the Crystal Chamber",
                "Collect the Glowing Crystal",
                "Reach the Lost City of Aethermoor"
            ],
            completed_objectives=[False, False, False, False],
            reward_items=["Ancient Tome", "Crystal Staff"],
            reward_text="You have uncovered the first mysteries of the ancient realm!"
        )
        
        side_quest = Quest(
            id="side_01", 
            title="Collector's Commission",
            description="The Mysterious Collector seeks rare treasures.",
            objectives=[
                "Talk to the Mysterious Collector",
                "Find valuable gems or artifacts",
                "Return to the collector"
            ],
            completed_objectives=[False, False, False],
            reward_items=["Collector's Reward", "Gold"],
            reward_text="The collector is pleased with your findings!"
        )
        
        self.quests = {
            "main_01": main_quest,
            "side_01": side_quest
        }
    
    def save_game(self, slot: int = 0):
        """Save the current game state"""
        if not self.player:
            self.show_notification("No game to save!", 2)
            return
            
        save_data = {
            'player': self.player.to_dict(),
            'rooms': {name: room.to_dict() for name, room in self.rooms.items()},
            'quests': {quest_id: quest.to_dict() for quest_id, quest in self.quests.items()},
            'room_id_counter': self.room_id_counter,
            'discovered_exits': self.discovered_exits
        }
        
        try:
            filename = f"savegame_slot_{slot}.json" if slot > 0 else SAVE_FILE
            with open(filename, 'w') as f:
                json.dump(save_data, f, indent=2)
            self.show_notification(f"Game saved to slot {slot}!", 3)
        except Exception as e:
            print(f"Failed to save game: {e}")
            self.show_notification(f"Save failed: {e}", 3)
    
    def load_game(self, slot: int = 0):
        """Load a saved game state"""
        try:
            filename = f"savegame_slot_{slot}.json" if slot > 0 else SAVE_FILE
            if not os.path.exists(filename):
                self.show_notification(f"No save file found in slot {slot}!", 2)
                return False
                
            with open(filename, 'r') as f:
                save_data = json.load(f)
            
            # Load player
            self.player = Player.from_dict(save_data['player'])
            
            # Load rooms
            self.rooms = {}
            for room_name, room_data in save_data['rooms'].items():
                self.rooms[room_name] = Room.from_dict(room_data, room_name)
            
            # Load quests
            self.quests = {}
            for quest_id, quest_data in save_data['quests'].items():
                self.quests[quest_id] = Quest.from_dict(quest_data)
            
            # Load other data
            self.room_id_counter = save_data.get('room_id_counter', 1000)
            self.discovered_exits = save_data.get('discovered_exits', {})
            
            self.state = GameState.PLAYING
            self.show_notification(f"Game loaded from slot {slot}!", 3)
            return True
            
        except Exception as e:
            print(f"Failed to load game: {e}")
            self.show_notification(f"Load failed: {e}", 3)
            return False
    
    def get_entry_position(self, direction: str) -> Tuple[int, int]:
        """Get the entry position when entering a room from a specific direction"""
        if direction == "north":
            return (GRID_WIDTH // 2, GRID_HEIGHT - 2)  # Enter from bottom
        elif direction == "south":
            return (GRID_WIDTH // 2, 1)  # Enter from top
        elif direction == "west":
            return (GRID_WIDTH - 2, GRID_HEIGHT // 2)  # Enter from right
        elif direction == "east":
            return (1, GRID_HEIGHT // 2)  # Enter from left
        else:
            return (GRID_WIDTH // 2, GRID_HEIGHT // 2)  # Default to center

    def get_item_texture_name(self, item_name: str) -> str:
        """Map item names to texture file names"""
        texture_map = {
            "Health Potion": "health_potion",
            "Gold Coin": "gold_coins", 
            "Gold Coins": "gold_coins",
            "Rare Gem": "rare_gem",
            "Old Map": "old_map",
            "Ancient Scroll": "old_map",
            "Scroll Fragment": "old_map",
            "Village Map": "old_map",
            "Merchant's Ledger": "old_map",
            "Rusty Key": "rusty_key",
            "City Key": "rusty_key",
            "Glowing Crystal": "glowing_crystal",
            "Crystal Shard": "glowing_crystal",
            "Jeweled Dagger": "jeweled_dagger",
            "Stone Tablet": "old_map",
            "Trade Goods": "gold_coins",
            "Bandit Treasure": "gold_coins"
        }
        return texture_map.get(item_name, "gold_coins")  # Default to gold coins

    def get_npc_texture_name(self, npc_name: str) -> str:
        """Map NPC names to texture file names"""
        texture_map = {
            "Cave Hermit": "cave_hermit",
            "Cave Dweller": "cave_hermit",
            "Lost Explorer": "cave_hermit",
            "Crystal Miner": "cave_hermit",
            "Forest Guardian": "forest_guardian",
            "Wandering Druid": "forest_guardian",
            "Lost Traveler": "forest_guardian",
            "Village Elder": "village_elder",
            "Local Merchant": "merchant",
            "Village Guard": "village_elder",
            "Mysterious Collector": "merchant",
            "Archaeologist": "village_elder",
            "Relic Hunter": "merchant",
            "Ghost of the Past": "cave_hermit"
        }
        return texture_map.get(npc_name, "village_elder")  # Default to village elder

    def check_wall_collision(self, rect: pygame.Rect) -> bool:
        """Check for wall collisions and handle edge transitions"""
        if not self.player:
            return False
            
        current_room = self.rooms[self.player.current_room]
        
        # Check screen edge transitions first
        if rect.right <= 0:
            self.transition_to_adjacent_room("west")
            return False
        elif rect.left >= SCREEN_WIDTH:
            self.transition_to_adjacent_room("east")
            return False
        elif rect.bottom <= 0:
            self.transition_to_adjacent_room("north")
            return False
        elif rect.top >= SCREEN_HEIGHT:
            self.transition_to_adjacent_room("south")
            return False
        
        # Check wall tiles within the current room
        left_tile = rect.left // TILE_SIZE
        right_tile = rect.right // TILE_SIZE
        top_tile = rect.top // TILE_SIZE
        bottom_tile = rect.bottom // TILE_SIZE
        
        for y in range(max(0, top_tile), min(current_room.grid_height, bottom_tile + 1)):
            for x in range(max(0, left_tile), min(current_room.grid_width, right_tile + 1)):
                if current_room.grid[y][x] == TileType.WALL:
                    return True
        return False

    def update_player_movement(self, keys):
        """Update player movement based on input"""
        if not self.player:
            return
            
        old_pos = self.player.rect.topleft
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.player.rect.y -= self.player.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.player.rect.y += self.player.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.player.rect.x -= self.player.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.player.rect.x += self.player.speed
        
        # Check for collisions (but don't clamp to screen edges)
        if self.check_wall_collision(self.player.rect):
            self.player.rect.topleft = old_pos

    def render_game(self):
        """Render the game world"""
        if not self.player or self.player.current_room not in self.rooms:
            return
            
        current_room = self.rooms[self.player.current_room]
        
        # Clear screen
        self.screen.fill(BLACK)
        
        # Draw room tiles
        for y in range(current_room.grid_height):
            for x in range(current_room.grid_width):
                tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                tile_type = current_room.grid[y][x]
                
                if tile_type == TileType.FLOOR:
                    texture = resources.get_texture(current_room.floor_texture)
                    if texture:
                        self.screen.blit(texture, tile_rect)
                    else:
                        self.screen.fill(FLOOR_COLOR, tile_rect)
                        
                elif tile_type == TileType.WALL:
                    texture = resources.get_texture(current_room.wall_texture)
                    if texture:
                        self.screen.blit(texture, tile_rect)
                    else:
                        self.screen.fill(WALL_COLOR, tile_rect)
                        
                elif tile_type == TileType.WATER:
                    texture = resources.get_texture("water")
                    if texture:
                        self.screen.blit(texture, tile_rect)
                    else:
                        self.screen.fill(BLUE, tile_rect)
                        
                elif tile_type == TileType.CHEST:
                    # Draw floor first
                    floor_texture = resources.get_texture(current_room.floor_texture)
                    if floor_texture:
                        self.screen.blit(floor_texture, tile_rect)
                    else:
                        self.screen.fill(FLOOR_COLOR, tile_rect)
                    # Draw chest on top
                    chest_texture = resources.get_texture("chest")
                    if chest_texture:
                        self.screen.blit(chest_texture, tile_rect)
                    else:
                        pygame.draw.rect(self.screen, ADVENTURE_BROWN, tile_rect)
                        
                elif tile_type == TileType.EXIT:
                    # Draw floor first
                    floor_texture = resources.get_texture(current_room.floor_texture)
                    if floor_texture:
                        self.screen.blit(floor_texture, tile_rect)
                    else:
                        self.screen.fill(FLOOR_COLOR, tile_rect)
                    # Draw exit indicator
                    pygame.draw.rect(self.screen, QUEST_COLOR, tile_rect, 3)
        
        # Draw items with textures
        for item in current_room.items:
            item_rect = pygame.Rect(item.x * TILE_SIZE, item.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            texture_name = self.get_item_texture_name(item.name)
            texture = resources.get_texture(texture_name)
            if texture:
                self.screen.blit(texture, item_rect)
            else:
                pygame.draw.rect(self.screen, ITEM_COLOR, item_rect)
        
        # Draw NPCs with textures and interaction indicators
        interaction_distance = TILE_SIZE + 10
        for npc in current_room.npcs:
            texture_name = self.get_npc_texture_name(npc.name)
            texture = resources.get_texture(texture_name)
            if texture:
                self.screen.blit(texture, npc.rect)
            else:
                pygame.draw.rect(self.screen, npc.color, npc.rect)
            
            # Show interaction indicator if player is nearby
            if self.player:
                distance = math.sqrt((self.player.rect.centerx - npc.rect.centerx)**2 + 
                                   (self.player.rect.centery - npc.rect.centery)**2)
                if distance <= interaction_distance:
                    # Draw "Press SPACE to talk" indicator
                    indicator_text = self.font_tiny.render("Press SPACE", True, WHITE)
                    indicator_rect = indicator_text.get_rect()
                    indicator_rect.centerx = npc.rect.centerx
                    indicator_rect.bottom = npc.rect.top - 5
                    
                    # Background for text
                    bg_rect = indicator_rect.inflate(4, 2)
                    pygame.draw.rect(self.screen, BLACK, bg_rect)
                    pygame.draw.rect(self.screen, WHITE, bg_rect, 1)
                    
                    self.screen.blit(indicator_text, indicator_rect)
        
        # Draw enemies (they have their own draw method)
        for enemy in current_room.enemies:
            enemy.draw(self.screen, resources.get_texture)
        
        # Draw player
        player_texture = resources.get_texture("player")
        if player_texture:
            self.screen.blit(player_texture, self.player.rect)
        else:
            pygame.draw.rect(self.screen, PLAYER_COLOR, self.player.rect)
        
        # Draw UI
        self.draw_ui()

    def draw_ui(self):
        """Draw the game UI"""
        if not self.player:
            return
            
        # Health bar
        health_bar_width = 200
        health_bar_height = 20
        health_x = 10
        health_y = 10
        
        # Background
        pygame.draw.rect(self.screen, DARK_GRAY, 
                        (health_x, health_y, health_bar_width, health_bar_height))
        
        # Health fill
        health_percentage = self.player.health / self.player.max_health
        health_fill_width = int(health_bar_width * health_percentage)
        health_color = GREEN if health_percentage > 0.3 else RED
        pygame.draw.rect(self.screen, health_color,
                        (health_x, health_y, health_fill_width, health_bar_height))
        
        # Health text
        health_text = self.font_small.render(f"HP: {self.player.health}/{self.player.max_health}", 
                                           True, WHITE)
        self.screen.blit(health_text, (health_x, health_y + health_bar_height + 5))
        
        # Player info
        info_y = health_y + health_bar_height + 30
        level_text = self.font_small.render(f"Level: {self.player.level}", True, WHITE)
        self.screen.blit(level_text, (health_x, info_y))
        
        gold_text = self.font_small.render(f"Gold: {self.player.gold}", True, ADVENTURE_GOLD)
        self.screen.blit(gold_text, (health_x, info_y + 25))
        
        # Current room
        room_text = self.font_small.render(f"Room: {self.player.current_room}", True, WHITE)
        self.screen.blit(room_text, (health_x, info_y + 50))
        
        # Show notification
        if self.notification_timer > 0:
            notification_surface = self.font_medium.render(self.notification_text, True, WHITE)
            notification_rect = notification_surface.get_rect()
            notification_rect.centerx = SCREEN_WIDTH // 2
            notification_rect.y = 50
            
            # Background
            bg_rect = notification_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, UI_BG_COLOR, bg_rect)
            pygame.draw.rect(self.screen, UI_BORDER_COLOR, bg_rect, 2)
            
            self.screen.blit(notification_surface, notification_rect)
            self.notification_timer -= 1

    def show_notification(self, text: str, duration_seconds: float):
        """Show a notification message"""
        self.notification_text = text
        self.notification_timer = int(duration_seconds * FPS)
    
    def handle_npc_interaction(self):
        """Handle player interaction with nearby NPCs"""
        if not self.player:
            return
            
        current_room = self.rooms[self.player.current_room]
        interaction_distance = TILE_SIZE + 10  # Allow some buffer distance
        
        # Find nearby NPCs
        for npc in current_room.npcs:
            distance = math.sqrt((self.player.rect.centerx - npc.rect.centerx)**2 + 
                               (self.player.rect.centery - npc.rect.centery)**2)
            
            if distance <= interaction_distance:
                self.start_dialogue_with_npc(npc)
                return
        
        self.show_notification("No one nearby to talk to", 1.5)
    
    def start_dialogue_with_npc(self, npc: NPC):
        """Start dialogue with an NPC"""
        self.dialogue_target_npc = npc
        self.state = GameState.DIALOGUE
        
        # Update NPC interaction data
        npc.interaction_count += 1
        npc.last_interaction_time = pygame.time.get_ticks()
        
        # Get appropriate dialogue response
        context = "greeting"
        if npc.interaction_count > 1:
            context = "return_visit"
        
        # Generate contextual response based on NPC personality and relationship
        self.dialogue_text = npc.get_dialogue_response(context)
        
        # Improve relationship slightly for friendly personalities
        if npc.personality in [NPCPersonality.FRIENDLY, NPCPersonality.CHEERFUL]:
            npc.modify_relationship(1)
        elif npc.personality == NPCPersonality.GRUFF and npc.interaction_count == 1:
            npc.modify_relationship(-1)  # Gruff NPCs are initially annoyed
        
        self.show_notification(f"Talking to {npc.name}", 0.5)
    
    def end_dialogue(self):
        """End the current dialogue"""
        self.dialogue_target_npc = None
        self.dialogue_text = ""
        self.state = GameState.PLAYING
    
    def render_dialogue(self):
        """Render the dialogue interface"""
        # Draw game background faded
        self.render_game()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        if self.dialogue_target_npc and self.dialogue_text:
            # Dialogue box
            dialogue_box_height = 200
            dialogue_box_y = SCREEN_HEIGHT - dialogue_box_height - 20
            dialogue_box = pygame.Rect(20, dialogue_box_y, SCREEN_WIDTH - 40, dialogue_box_height)
            
            # Draw dialogue box background
            pygame.draw.rect(self.screen, UI_BG_COLOR, dialogue_box)
            pygame.draw.rect(self.screen, UI_BORDER_COLOR, dialogue_box, 3)
            
            # NPC name
            name_text = self.font_medium.render(self.dialogue_target_npc.name, True, WHITE)
            self.screen.blit(name_text, (dialogue_box.x + 10, dialogue_box.y + 10))
            
            # Dialogue text (word wrapped)
            text_area = pygame.Rect(dialogue_box.x + 10, dialogue_box.y + 50, 
                                  dialogue_box.width - 20, dialogue_box.height - 100)
            self.draw_wrapped_text(self.dialogue_text, text_area, self.font_small, WHITE)
            
            # Instructions
            instruction_text = self.font_tiny.render("Press SPACE or ENTER to continue", True, LIGHT_GRAY)
            instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))
            self.screen.blit(instruction_text, instruction_rect)
            
            # Show relationship level if it's not neutral
            if hasattr(self.dialogue_target_npc, 'relationship_level') and self.dialogue_target_npc.relationship_level != 0:
                rel_level = self.dialogue_target_npc.relationship_level
                if rel_level > 0:
                    rel_text = f"Relationship: +{rel_level}"
                    rel_color = GREEN
                else:
                    rel_text = f"Relationship: {rel_level}"
                    rel_color = RED
                
                rel_surface = self.font_tiny.render(rel_text, True, rel_color)
                self.screen.blit(rel_surface, (dialogue_box.x + 10, dialogue_box.y + dialogue_box.height - 30))
    
    def draw_wrapped_text(self, text: str, rect: pygame.Rect, font: pygame.font.Font, color: tuple):
        """Draw text that wraps within a rectangle"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= rect.width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)  # Single word too long, add anyway
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw lines
        y_offset = 0
        for line in lines:
            if y_offset + font.get_height() > rect.height:
                break  # Don't draw outside the rect
            
            line_surface = font.render(line, True, color)
            self.screen.blit(line_surface, (rect.x, rect.y + y_offset))
            y_offset += font.get_height() + 2

    def render_title_screen(self):
        """Render the main title screen with quest tooltip"""
        # Create a gradient background
        self.screen.fill(UI_BG_COLOR)
        
        # Add some atmospheric particles or effects
        for i in range(20):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(1, 3)
            alpha = random.randint(50, 150)
            color = (*QUEST_COLOR, alpha)
            s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (size, size), size)
            self.screen.blit(s, (x, y))
        
        # Main title
        title_text = self.font_large.render("Procedural Adventure", True, QUEST_COLOR)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 120))
        self.screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = self.font_medium.render("Explore Infinite Dungeons & Mysteries", True, WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 70))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Quest tooltip box
        tooltip_width = 400
        tooltip_height = 150
        tooltip_x = SCREEN_WIDTH//2 - tooltip_width//2
        tooltip_y = SCREEN_HEIGHT//2 - 20
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        
        # Draw tooltip background
        pygame.draw.rect(self.screen, TOOLTIP_BG, tooltip_rect)
        pygame.draw.rect(self.screen, QUEST_COLOR, tooltip_rect, 2)
        
        # Quest tooltip title
        quest_title = self.font_medium.render("Your Quest Awaits", True, QUEST_COLOR)
        quest_title_rect = quest_title.get_rect(center=(SCREEN_WIDTH//2, tooltip_y + 25))
        self.screen.blit(quest_title, quest_title_rect)
        
        # Quest description
        quest_lines = [
            "Explore mystical caves filled with ancient secrets",
            "Battle dangerous creatures and collect treasures",
            "Uncover the mysteries of the Lost City of Aethermoor",
            "Your adventure begins in the Mystic Cave Entrance..."
        ]
        
        for i, line in enumerate(quest_lines):
            line_text = self.font_small.render(line, True, WHITE)
            line_rect = line_text.get_rect(center=(SCREEN_WIDTH//2, tooltip_y + 55 + i * 20))
            self.screen.blit(line_text, line_rect)
        
        # Start instructions
        start_text = self.font_medium.render("Press ENTER or SPACE to Begin", True, WHITE)
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 160))
        self.screen.blit(start_text, start_rect)
        
        # Exit instructions
        exit_text = self.font_small.render("Press ESC to Exit", True, LIGHT_GRAY)
        exit_rect = exit_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 190))
        self.screen.blit(exit_text, exit_rect)
