from enum import Enum
import random
import math
import pygame
from typing import List, Tuple, Optional

class EnemyType(Enum):
    SLIME = 1     # Basic enemy that hops around
    SKELETON = 2  # Ranged attacker
    GOBLIN = 3    # Fast melee attacker
    BAT = 4       # Fast-moving but weak flying enemy
    SPIDER = 5    # Lurks on walls, drops on player

class EnemyBehavior(Enum):
    IDLE = 1       # Stays in place
    PATROL = 2     # Moves back and forth in an area
    AGGRESSIVE = 3 # Actively seeks the player
    LURK = 4       # Hides until player is close
    FLEE = 5       # Runs away when hurt

class Enemy:
    def __init__(self, enemy_type: EnemyType, rect: pygame.Rect, health: int = 10):
        self.enemy_type = enemy_type
        self.rect = rect  # Position and size
        self.health = health
        self.max_health = health
        self.speed = self.get_base_speed()
        self.damage = self.get_base_damage()
        self.behavior = self.get_default_behavior()
        self.attack_cooldown = 0
        self.state_timer = 0
        self.aggro_range = 150  # Distance at which enemy notices player
        self.attack_range = 30  # Distance at which enemy can attack
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.patrol_points = None
        self.patrol_index = 0
        self.target_position = None
        self.last_position = self.rect.topleft
        self.stuck_counter = 0
        self.texture_name = self.get_texture_name()
        
        # Animation states
        self.facing_right = True
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 8  # Frames before animation updates
        self.is_attacking = False
        self.is_hit = False
        self.hit_animation_timer = 0
    
    def get_texture_name(self) -> str:
        """Get the base texture name for the enemy type"""
        if self.enemy_type == EnemyType.SLIME:
            return "slime"
        elif self.enemy_type == EnemyType.SKELETON:
            return "skeleton"
        elif self.enemy_type == EnemyType.GOBLIN:
            return "goblin"
        elif self.enemy_type == EnemyType.BAT:
            return "bat"
        elif self.enemy_type == EnemyType.SPIDER:
            return "spider"
        return "slime"  # Default
    
    def get_base_speed(self) -> int:
        """Get the base movement speed based on enemy type"""
        if self.enemy_type == EnemyType.SLIME:
            return 1
        elif self.enemy_type == EnemyType.SKELETON:
            return 2
        elif self.enemy_type == EnemyType.GOBLIN:
            return 3
        elif self.enemy_type == EnemyType.BAT:
            return 4
        elif self.enemy_type == EnemyType.SPIDER:
            return 2
        return 1  # Default
    
    def get_base_damage(self) -> int:
        """Get the base attack damage based on enemy type"""
        if self.enemy_type == EnemyType.SLIME:
            return 5
        elif self.enemy_type == EnemyType.SKELETON:
            return 8
        elif self.enemy_type == EnemyType.GOBLIN:
            return 10
        elif self.enemy_type == EnemyType.BAT:
            return 3
        elif self.enemy_type == EnemyType.SPIDER:
            return 7
        return 5  # Default
    
    def get_default_behavior(self) -> EnemyBehavior:
        """Get the default behavior based on enemy type"""
        if self.enemy_type == EnemyType.SLIME:
            return EnemyBehavior.PATROL
        elif self.enemy_type == EnemyType.SKELETON:
            return EnemyBehavior.AGGRESSIVE
        elif self.enemy_type == EnemyType.GOBLIN:
            return EnemyBehavior.AGGRESSIVE
        elif self.enemy_type == EnemyType.BAT:
            return EnemyBehavior.PATROL
        elif self.enemy_type == EnemyType.SPIDER:
            return EnemyBehavior.LURK
        return EnemyBehavior.IDLE  # Default

    def set_patrol_points(self, points: List[Tuple[int, int]]):
        """Set patrol points for the enemy to move between"""
        self.patrol_points = points
        self.patrol_index = 0
        if self.patrol_points:
            self.target_position = self.patrol_points[0]
    
    def take_damage(self, damage: int) -> bool:
        """Apply damage to the enemy and return True if it's defeated"""
        self.health -= damage
        self.is_hit = True
        self.hit_animation_timer = 10  # 10 frames of hit animation
        
        # Chance to switch to flee behavior when hurt
        if self.health < self.max_health / 2 and random.random() < 0.3:
            self.behavior = EnemyBehavior.FLEE
            self.state_timer = 60  # Flee for 60 frames
        
        return self.health <= 0
    
    def distance_to_player(self, player_rect: pygame.Rect) -> float:
        """Calculate distance to player"""
        enemy_center = self.rect.center
        player_center = player_rect.center
        dx = player_center[0] - enemy_center[0]
        dy = player_center[1] - enemy_center[1]
        return math.sqrt(dx*dx + dy*dy)

    def update_behavior(self, player_rect: pygame.Rect):
        """Update enemy behavior based on player position and other factors"""
        distance = self.distance_to_player(player_rect)

        # Check if lurking enemy should become aggressive
        if self.behavior == EnemyBehavior.LURK and distance < self.aggro_range:
            self.behavior = EnemyBehavior.AGGRESSIVE

        # Reset behavior after fleeing
        if self.behavior == EnemyBehavior.FLEE and self.state_timer <= 0:
            self.behavior = self.get_default_behavior()

        # If stuck, change behavior temporarily
        if self.stuck_counter > 10: # Increased threshold for getting stuck
            self.behavior = EnemyBehavior.PATROL # Change to patrol to try to unstick
            self.stuck_counter = 0 # Reset stuck counter

            # Create new random patrol points nearby to help unstick
            current_x, current_y = self.rect.topleft
            self.patrol_points = [
                (current_x + random.randint(-50, 50), current_y + random.randint(-50, 50)), # Shorter patrol range
                (current_x + random.randint(-50, 50), current_y + random.randint(-50, 50))
            ]
            self.patrol_index = 0
            if self.patrol_points: # Ensure patrol_points is not empty
                self.target_position = self.patrol_points[0]
    
    def update_movement(self, player_rect: pygame.Rect, wall_check_func) -> bool:
        """Update enemy movement based on behavior. Returns True if attacking."""
        # Decrement timers
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        if self.state_timer > 0:
            self.state_timer -= 1
        
        if self.hit_animation_timer > 0:
            self.hit_animation_timer -= 1
        else:
            self.is_hit = False
            
        # Update animation timer
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4  # 4 frames of animation
        
        # Check if position has changed
        current_pos = self.rect.topleft
        if current_pos == self.last_position:
            self.stuck_counter += 1
        else:
            self.stuck_counter = 0
            self.last_position = current_pos
        
        # Handle different behaviors
        if self.behavior == EnemyBehavior.IDLE:
            # Just stand around
            if random.random() < 0.01:  # 1% chance per frame to change direction
                self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)])
            
            dx, dy = self.direction
            new_rect = self.rect.move(dx * self.speed, dy * self.speed)
            if not wall_check_func(new_rect):
                self.rect = new_rect
                self.facing_right = dx >= 0
        
        elif self.behavior == EnemyBehavior.PATROL:
            if self.patrol_points and self.target_position:
                # Move toward the current patrol point
                tx, ty = self.target_position
                ex, ey = self.rect.topleft
                
                dx = tx - ex
                dy = ty - ey
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist < 10:  # Close enough to target
                    # Move to next patrol point
                    self.patrol_index = (self.patrol_index + 1) % len(self.patrol_points)
                    self.target_position = self.patrol_points[self.patrol_index]
                else:
                    # Normalize direction and move
                    if dist > 0:
                        dx = dx / dist * self.speed
                        dy = dy / dist * self.speed
                    
                    new_rect = self.rect.move(dx, dy)
                    if not wall_check_func(new_rect):
                        self.rect = new_rect
                        self.facing_right = dx >= 0
                    else:
                        # Try moving just horizontally or vertically if direct path is blocked
                        new_rect_h = self.rect.move(dx, 0)
                        if not wall_check_func(new_rect_h):
                            self.rect = new_rect_h
                            self.facing_right = dx >= 0
                        else:
                            new_rect_v = self.rect.move(0, dy)
                            if not wall_check_func(new_rect_v):
                                self.rect = new_rect_v
            else:
                # Create random patrol points
                ex, ey = self.rect.topleft
                self.patrol_points = [
                    (ex + random.randint(-100, 100), ey + random.randint(-100, 100)),
                    (ex + random.randint(-100, 100), ey + random.randint(-100, 100))
                ]
                self.patrol_index = 0
                self.target_position = self.patrol_points[0]
        
        elif self.behavior == EnemyBehavior.AGGRESSIVE:
            # Move toward the player
            player_center = player_rect.center
            enemy_center = self.rect.center
            
            dx = player_center[0] - enemy_center[0]
            dy = player_center[1] - enemy_center[1]
            dist = math.sqrt(dx*dx + dy*dy)
            
            # Check if in attack range
            if dist <= self.attack_range and self.attack_cooldown <= 0:
                self.attack_cooldown = 30  # 30 frames (0.5s at 60fps) between attacks
                self.is_attacking = True
                return True  # Signal attack
            
            # Move toward player if not in attack range
            if dist > self.attack_range:
                self.is_attacking = False
                if dist > 0:
                    dx = dx / dist * self.speed
                    dy = dy / dist * self.speed
                
                new_rect = self.rect.move(dx, dy)
                if not wall_check_func(new_rect):
                    self.rect = new_rect
                    self.facing_right = dx >= 0
                else:
                    # Try moving just horizontally or vertically if direct path is blocked
                    new_rect_h = self.rect.move(dx, 0)
                    if not wall_check_func(new_rect_h):
                        self.rect = new_rect_h
                        self.facing_right = dx >= 0
                    else:
                        new_rect_v = self.rect.move(0, dy)
                        if not wall_check_func(new_rect_v):
                            self.rect = new_rect_v
        
        elif self.behavior == EnemyBehavior.LURK:
            # Don't move, just wait for player to get close
            pass
            
        elif self.behavior == EnemyBehavior.FLEE:
            # Move away from player
            player_center = player_rect.center
            enemy_center = self.rect.center
            
            dx = enemy_center[0] - player_center[0]  # Reversed direction
            dy = enemy_center[1] - player_center[1]  # Reversed direction
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > 0:
                dx = dx / dist * self.speed
                dy = dy / dist * self.speed
            
            new_rect = self.rect.move(dx, dy)
            if not wall_check_func(new_rect):
                self.rect = new_rect
                self.facing_right = dx >= 0
        
        return False  # Not attacking
                
    def draw(self, screen, texture_getter, is_hit=False):
        """
        Draw the enemy with appropriate texture
        texture_getter: function that returns a pygame Surface when given a texture name
        is_hit: whether the enemy is currently being hit (for flash effect)
        """
        # Get base texture
        base_texture = texture_getter(self.texture_name)
        
        # Modify texture based on state
        texture = base_texture.copy()
        
        # Flash red when hit
        if self.is_hit or is_hit:
            red_overlay = pygame.Surface(texture.get_size(), pygame.SRCALPHA)
            red_overlay.fill((255, 0, 0, 128))  # Semi-transparent red
            texture.blit(red_overlay, (0, 0))
        
        # Draw health bar
        health_pct = self.health / self.max_health
        bar_width = self.rect.width
        health_width = int(bar_width * health_pct)
        bar_height = 3
        bar_y = self.rect.top - 5
        
        # Draw the red background
        pygame.draw.rect(screen, (255, 0, 0), (self.rect.left, bar_y, bar_width, bar_height))
        
        # Draw the green health
        if health_width > 0:
            pygame.draw.rect(screen, (0, 255, 0), (self.rect.left, bar_y, health_width, bar_height))
        
        # Draw enemy (flip texture if facing left)
        if self.facing_right:
            screen.blit(texture, self.rect)
        else:
            flipped = pygame.transform.flip(texture, True, False)
            screen.blit(flipped, self.rect)

    def to_dict(self):
        """Convert enemy to dictionary for saving"""
        return {
            'enemy_type': self.enemy_type.value,
            'rect': {'x': self.rect.x, 'y': self.rect.y, 'width': self.rect.width, 'height': self.rect.height},
            'health': self.health,
            'max_health': self.max_health,
            'behavior': self.behavior.value
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create enemy from dictionary data"""
        rect_data = data['rect']
        rect = pygame.Rect(rect_data['x'], rect_data['y'], rect_data['width'], rect_data['height'])
        enemy = cls(
            enemy_type=EnemyType(data['enemy_type']),
            rect=rect,
            health=data.get('health', 10)
        )
        enemy.max_health = data.get('max_health', enemy.health)
        enemy.behavior = EnemyBehavior(data.get('behavior', enemy.behavior.value))
        return enemy
