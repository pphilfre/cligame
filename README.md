# Adventure Quest - Pokémon-Style 2D Game

A 2D adventure game built with Pygame, inspired by Pokémon Red. Players explore multiple rooms, make choices, collect items, and save their progress.

## Features

### Core Gameplay
- **Personalized Experience**: Enter your name at the start and see it used throughout dialogues and story
- **Multiple Rooms**: Explore 6 different locations, each with unique descriptions and items
- **Interactive Choices**: At least 2 meaningful choices per room that affect your experience
- **Movement System**: Use WASD or arrow keys to navigate between connected rooms

### Advanced Features
- **Procedural Generation**: Random item spawning (30% chance per room) makes each playthrough unique
- **Inventory System**: Collect, store, and manage items across all rooms
- **Save/Load System**: Complete game state persistence including name, location, choices, and inventory
- **Room Memory**: Rooms remember if they've been visited and their current state

### Rooms Available
1. **Professor's Lab** (Starting room) - Tutorial area with basic supplies
2. **Mysterious Forest** - Dense woodland with strange sounds and glowing mushrooms
3. **Peaceful Village** - Friendly town with NPCs and shops
4. **Dark Cave** - Crystal-filled cavern with magical items
5. **Sunny Clearing** - Peaceful area with wildflowers
6. **General Store** - Shop with various items and a helpful shopkeeper

## Installation

1. Install Python 3.7 or higher
2. Install Pygame:
   ```bash
   pip install -r requirements.txt
   ```

## How to Play

### Starting the Game
1. Run the game: `python main.py`
2. Enter your name when prompted
3. Press ENTER to begin your adventure

### Controls
- **Movement**: WASD or Arrow Keys to move between rooms
- **SPACE**: Interact with the current room
- **I**: Open/close inventory
- **S**: Save game
- **L**: Load saved game
- **ESC**: Close dialogue or menus

### Gameplay
- Explore different rooms by moving in cardinal directions
- Each room has unique items, NPCs, and interaction opportunities
- Make choices during dialogues that can affect your experience
- Collect items to build your inventory
- Save your progress at any time and resume later

### Room Navigation
- **North/South/East/West**: Different rooms are connected via these directions
- Available exits are displayed in each room
- Your character (blue circle) represents your position

### Dialogue System
- Use UP/DOWN arrow keys to select dialogue choices
- Press ENTER to confirm your selection
- Your name will appear in conversations for personalization

## Technical Details

### Procedural Generation
- Items spawn randomly in rooms with a 30% chance
- Possible random items include potions, keys, coins, berries, and map fragments
- This ensures different experiences across playthroughs

### Save System
- Game state is saved to `savegame.json`
- Includes player data, room states, and inventory
- Complete state persistence allows seamless continuation

### Architecture
- Object-oriented design with separate classes for Game, Player, Room, and Item
- Modular room system allows easy expansion
- State machine handles different game phases (name input, playing, dialogue, inventory)

## Customization

### Adding New Rooms
1. Create a new Room instance in the `create_rooms()` method
2. Define connections to existing rooms via the exits dictionary
3. Add unique items and NPCs as desired

### Adding New Items
1. Create Item instances with name and description
2. Add to room item lists or random generation pool
3. Items automatically integrate with the inventory system

### Expanding Dialogue
1. Modify the `handle_dialogue_choice()` method
2. Add room-specific interactions in `handle_room_interaction()`
3. Personalize with the player's name using `self.player.name`

## Game Design Philosophy

This game captures the essence of classic RPGs like Pokémon Red while adding modern procedural elements:

- **Exploration**: Multiple interconnected rooms encourage discovery
- **Personalization**: Player name integration creates emotional connection
- **Choice & Consequence**: Dialogue options provide agency
- **Collection**: Inventory system rewards thorough exploration
- **Persistence**: Save/load ensures progress isn't lost

The procedural generation keeps the experience fresh while maintaining the carefully crafted room designs and story elements.