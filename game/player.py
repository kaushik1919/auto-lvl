"""Player character with Sonic-style physics implementation.
Features smooth acceleration, momentum-based movement, and responsive controls.
"""

import math
import pygame
from config.settings import (
    AIR_FRICTION,
    CHARACTER_SPRITE,
    GRAVITY,
    GROUND_FRICTION,
    MAX_FALL_SPEED,
    PARTICLE_LIFETIME,
    PLAYER_ACCELERATION,
    PLAYER_JUMP_POWER,
    PLAYER_MAX_SPEED,
    PLAYER_SIZE,
)

COIN_SCORE_VALUE = 10
ENEMY_SCORE_VALUE = 25


class Player:
    """
    Player character with advanced Sonic-inspired physics.
    Implements acceleration, momentum, smooth jumping, and collision detection.
    """

    def __init__(self, x, y):
        """Initialize player at starting position."""
        self.x = x
        self.y = y
        self.width, self.height = PLAYER_SIZE
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.set_spawn_point(x, y)

        # Physics properties
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True

        # Gameplay state
        self.score = 0

        # Animation state
        self.animation_frame = 0
        self.animation_timer = 0
        self.state = 'idle'  # idle, running, jumping, falling

        # Particle trail for high-speed movement
        self.particles = []
        self.particle_color = (140, 0, 0)

        # Create player surface (placeholder - will be sprite later)
        self.create_sprite()

    def add_score(self, points):
        """Increase player score by the given amount."""
        if points > 0:
            self.score += points

    def collect_coin(self, count=1):
        """Handle coin collection and score update."""
        if count > 0:
            self.add_score(COIN_SCORE_VALUE * count)

    def defeat_enemy(self, count=1):
        """Handle enemy defeat and corresponding score update."""
        if count > 0:
            self.add_score(ENEMY_SCORE_VALUE * count)

    def reset_score(self):
        """Reset the player's score."""
        self.score = 0

    def set_spawn_point(self, x, y):
        """Store the spawn point used for future respawns."""
        self.spawn_point = (x, y)

    def reset_to_spawn(self):
        """Respawn the player at the stored spawn point."""
        self.reset(*self.spawn_point)

    def create_sprite(self):
        """Create character sprites based on configuration."""
        if CHARACTER_SPRITE == "optimus_prime":
            self.sprites = {
                'idle': self._create_optimus_pose(),
                'run': [
                    self._create_optimus_pose(arm_swing=-4, leg_swing=4, vertical_shift=0),
                    self._create_optimus_pose(arm_swing=-2, leg_swing=-2, vertical_shift=-1),
                    self._create_optimus_pose(arm_swing=4, leg_swing=-4, vertical_shift=0),
                    self._create_optimus_pose(arm_swing=2, leg_swing=2, vertical_shift=-1)
                ],
                'jump': self._create_optimus_pose(airborne=True, vertical_shift=-4),
                'fall': self._create_optimus_pose(airborne=True, falling=True, vertical_shift=2)
            }
            self.particle_color = (90, 150, 255)
        else:
            self.sprites = {
                'idle': self._create_shadow_idle(),
                'run': [self._create_shadow_run(i) for i in range(4)],
                'jump': self._create_shadow_jump(),
                'fall': self._create_shadow_fall()
            }
            self.particle_color = (140, 0, 0)

    def _create_optimus_pose(self, arm_swing=0, leg_swing=0, vertical_shift=0, airborne=False, falling=False):
        """Create an Optimus Prime sprite pose with simple pixel art."""
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Color palette inspired by classic Optimus Prime scheme
        red = (205, 30, 35)
        dark_red = (160, 20, 25)
        blue = (45, 90, 200)
        dark_blue = (30, 60, 140)
        silver = (205, 205, 215)
        steel = (150, 150, 160)
        yellow = (250, 200, 60)
        black = (20, 20, 25)

        center_x = self.width // 2
        torso_top = self.height // 2 - 24 + vertical_shift
        torso_height = 28
        torso_width = 24

        # Torso and chest details
        torso_rect = pygame.Rect(center_x - torso_width // 2, torso_top, torso_width, torso_height)
        pygame.draw.rect(surf, red, torso_rect)
        pygame.draw.rect(surf, dark_red, torso_rect.inflate(-6, -torso_height + 10))

        window_height = 8
        window_width = 8
        left_window = pygame.Rect(center_x - 9, torso_top + 4, window_width, window_height)
        right_window = pygame.Rect(center_x + 1, torso_top + 4, window_width, window_height)
        pygame.draw.rect(surf, blue, left_window)
        pygame.draw.rect(surf, blue, right_window)
        pygame.draw.rect(surf, yellow, left_window.inflate(-4, -4))
        pygame.draw.rect(surf, yellow, right_window.inflate(-4, -4))

        grille_rect = pygame.Rect(center_x - 10, torso_top + 16, 20, 6)
        pygame.draw.rect(surf, silver, grille_rect)
        pygame.draw.rect(surf, steel, grille_rect.inflate(-6, -2))

        belt_rect = pygame.Rect(center_x - 12, torso_top + torso_height - 6, 24, 6)
        pygame.draw.rect(surf, silver, belt_rect)

        # Smokestacks on shoulders
        left_stack = pygame.Rect(center_x - torso_width // 2 - 3, torso_top - 6, 3, 16)
        right_stack = pygame.Rect(center_x + torso_width // 2, torso_top - 6, 3, 16)
        pygame.draw.rect(surf, silver, left_stack)
        pygame.draw.rect(surf, silver, right_stack)

        # Head and crest
        head_width = 18
        head_height = 16
        head_rect = pygame.Rect(center_x - head_width // 2, torso_top - head_height + 4, head_width, head_height)
        pygame.draw.rect(surf, blue, head_rect)

        mask_rect = pygame.Rect(center_x - 8, head_rect.bottom - 6, 16, 6)
        pygame.draw.rect(surf, silver, mask_rect)
        pygame.draw.rect(surf, steel, mask_rect.inflate(-6, -2))

        visor_rect = pygame.Rect(center_x - 7, head_rect.top + 4, 14, 4)
        pygame.draw.rect(surf, yellow, visor_rect)
        pygame.draw.rect(surf, black, visor_rect.inflate(-6, -2))

        crest_rect = pygame.Rect(center_x - 2, head_rect.top - 4, 4, 6)
        pygame.draw.rect(surf, red, crest_rect)

        # Arms with swing offsets to simulate motion
        arm_width = 6
        arm_height = 18
        arm_top = torso_top + 6
        left_arm_offset = -arm_swing
        right_arm_offset = arm_swing
        left_arm = pygame.Rect(center_x - torso_width // 2 - arm_width + left_arm_offset, arm_top, arm_width, arm_height)
        right_arm = pygame.Rect(center_x + torso_width // 2 + right_arm_offset - arm_width, arm_top, arm_width, arm_height)

        if airborne:
            left_arm.move_ip(0, -4)
            right_arm.move_ip(0, -4 if not falling else -1)

        pygame.draw.rect(surf, red, left_arm)
        pygame.draw.rect(surf, red, right_arm)

        left_fist = pygame.Rect(left_arm.left, left_arm.bottom - 4, arm_width, 4)
        right_fist = pygame.Rect(right_arm.left, right_arm.bottom - 4, arm_width, 4)
        pygame.draw.rect(surf, silver, left_fist)
        pygame.draw.rect(surf, silver, right_fist)

        # Legs with swing offsets and airborne adjustments
        leg_width = 8
        leg_height = 20
        leg_top = torso_top + torso_height
        left_leg_offset = -leg_swing
        right_leg_offset = leg_swing
        left_leg = pygame.Rect(center_x - leg_width - 2 + left_leg_offset, leg_top, leg_width, leg_height)
        right_leg = pygame.Rect(center_x + 2 + right_leg_offset, leg_top, leg_width, leg_height)

        if airborne:
            left_leg.move_ip(1, -2)
            right_leg.move_ip(-1, -2)
            if falling:
                left_leg.move_ip(-1, 4)
                right_leg.move_ip(1, 4)

        pygame.draw.rect(surf, dark_blue, left_leg)
        pygame.draw.rect(surf, dark_blue, right_leg)

        left_boot = pygame.Rect(left_leg.left, left_leg.bottom - 6, leg_width, 6)
        right_boot = pygame.Rect(right_leg.left, right_leg.bottom - 6, leg_width, 6)
        pygame.draw.rect(surf, silver, left_boot)
        pygame.draw.rect(surf, silver, right_boot)

        # Add small highlights for depth
        pygame.draw.rect(surf, black, torso_rect, 1)
        pygame.draw.rect(surf, black, head_rect, 1)
        pygame.draw.line(surf, black, (left_leg.left, left_leg.bottom), (left_leg.right - 1, left_leg.bottom))
        pygame.draw.line(surf, black, (right_leg.left, right_leg.bottom), (right_leg.right - 1, right_leg.bottom))

        return surf

    def _create_shadow_idle(self):
        """Create Shadow idle sprite - pixel art style."""
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Shadow's color palette
        black = (20, 20, 20)
        dark_red = (140, 0, 0)
        bright_red = (220, 0, 0)
        tan = (210, 170, 130)
        white = (255, 255, 255)

        # Body - black with red stripes
        center_x, center_y = self.width // 2, self.height // 2 + 2

        # Draw black body
        for y in range(-8, 9):
            for x in range(-8, 9):
                if x * x + y * y <= 64:  # Circle radius 8
                    surf.set_at((center_x + x, center_y + y), black)

        # Red stripes on quills (top spikes)
        spike_positions = [
            (-10, -4), (-8, -8), (-6, -10),  # Left spikes
            (0, -11), (6, -10), (8, -8), (10, -4)  # Top and right spikes
        ]

        for sx, sy in spike_positions:
            # Draw spike
            for i in range(5):
                px = center_x + sx + (1 if sx > 0 else -1 if sx < 0 else 0) * i // 2
                py = center_y + sy - i // 3
                if 0 <= px < self.width and 0 <= py < self.height:
                    surf.set_at((px, py), black)
                    # Red stripe on spike
                    if i > 1:
                        surf.set_at((px + 1, py), dark_red)

        # Muzzle/mouth area (tan)
        for y in range(3):
            for x in range(-3, 4):
                if abs(x) + y < 5:
                    surf.set_at((center_x + x, center_y + 3 + y), tan)

        # Eyes (red with white pupils)
        eye_y = center_y - 2
        surf.set_at((center_x - 4, eye_y - 1), white)
        surf.set_at((center_x - 4, eye_y), bright_red)
        surf.set_at((center_x - 4, eye_y + 1), bright_red)
        surf.set_at((center_x - 3, eye_y), bright_red)
        surf.set_at((center_x - 5, eye_y), bright_red)

        surf.set_at((center_x + 4, eye_y - 1), white)
        surf.set_at((center_x + 4, eye_y), bright_red)
        surf.set_at((center_x + 4, eye_y + 1), bright_red)
        surf.set_at((center_x + 3, eye_y), bright_red)
        surf.set_at((center_x + 5, eye_y), bright_red)

        # Air shoes
        shoe_y = center_y + 10
        for x in range(-6, -2):
            surf.set_at((center_x + x, shoe_y), bright_red)
            surf.set_at((center_x + x, shoe_y + 1), dark_red)
            surf.set_at((center_x + x, shoe_y - 1), white)
        for x in range(3, 7):
            surf.set_at((center_x + x, shoe_y), bright_red)
            surf.set_at((center_x + x, shoe_y + 1), dark_red)
            surf.set_at((center_x + x, shoe_y - 1), white)

        return surf

    def _create_shadow_run(self, frame):
        """Create Shadow running animation sprite."""
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        black = (20, 20, 20)
        dark_red = (140, 0, 0)
        bright_red = (220, 0, 0)
        tan = (210, 170, 130)
        white = (255, 255, 255)

        offset_y = 2 if frame % 2 == 0 else -2
        center_x, center_y = self.width // 2, self.height // 2 + offset_y

        for i in range(3):
            trail_x = center_x - i * 6
            trail_alpha = 120 - i * 40
            if trail_x > 0:
                for y in range(-6, 7):
                    for x in range(-2, 2):
                        if x * x + y * y <= 25 and trail_x + x < self.width:
                            color = pygame.Color(*bright_red, trail_alpha)
                            surf.set_at((trail_x + x, center_y + y), color)

        for y in range(-7, 8):
            for x in range(-7, 8):
                if x * x + y * y <= 49:
                    surf.set_at((center_x + x, center_y + y), black)

        spike_angle = -30 if frame < 2 else -40
        for base_angle in [-60, -30, 0, 30, 60]:
            angle = base_angle + spike_angle
            rad = math.radians(angle)
            for dist in range(3, 10):
                sx = int(center_x + math.cos(rad) * dist)
                sy = int(center_y - 8 + math.sin(rad) * dist)
                if 0 <= sx < self.width and 0 <= sy < self.height:
                    surf.set_at((sx, sy), black)
                    if dist > 5:
                        surf.set_at((sx + 1, sy), dark_red)

        eye_y = center_y - 2
        surf.set_at((center_x - 3, eye_y), bright_red)
        surf.set_at((center_x + 3, eye_y), bright_red)

        for x in range(-2, 3):
            surf.set_at((center_x + x, center_y + 3), tan)

        shoe_y = center_y + 9
        leg_offset = 2 if frame % 2 == 0 else -2
        for x in range(2, 6):
            surf.set_at((center_x + x, shoe_y + leg_offset), bright_red)
            surf.set_at((center_x + x, shoe_y + leg_offset - 1), white)
        for x in range(-6, -2):
            surf.set_at((center_x + x, shoe_y - leg_offset), bright_red)
            surf.set_at((center_x + x, shoe_y - leg_offset - 1), white)

        return surf

    def _create_shadow_jump(self):
        """Create Shadow jumping/spin attack sprite."""
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        black = (20, 20, 20)
        dark_red = (140, 0, 0)
        bright_red = (220, 0, 0)

        center_x, center_y = self.width // 2, self.height // 2

        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            for dist in range(3, 10):
                x = int(center_x + math.cos(rad) * dist)
                y = int(center_y + math.sin(rad) * dist)
                if 0 <= x < self.width and 0 <= y < self.height:
                    surf.set_at((x, y), black)
                    if angle % 90 == 0 and dist > 6:
                        surf.set_at((x, y), bright_red)

        for y in range(-6, 7):
            for x in range(-6, 7):
                if x * x + y * y <= 36:
                    surf.set_at((center_x + x, center_y + y), black)

        for i in range(3):
            blur_alpha = 100 - i * 30
            for y in range(-4, 5):
                for x in range(-4, 5):
                    if x * x + y * y <= 16:
                        blur_y = center_y + y + i * 3
                        if 0 <= blur_y < self.height:
                            surf.set_at((center_x + x, blur_y), pygame.Color(*dark_red, blur_alpha))

        return surf

    def _create_shadow_fall(self):
        """Create Shadow falling sprite."""
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        black = (20, 20, 20)
        dark_red = (140, 0, 0)
        bright_red = (220, 0, 0)
        tan = (210, 170, 130)

        center_x, center_y = self.width // 2, self.height // 2 + 3

        for y in range(-7, 8):
            for x in range(-7, 8):
                if x * x + y * y <= 49:
                    surf.set_at((center_x + x, center_y + y), black)

        for base_angle in [-60, -30, 0, 30, 60]:
            rad = math.radians(base_angle - 90)
            for dist in range(3, 9):
                sx = int(center_x + math.cos(rad) * dist)
                sy = int(center_y + math.sin(rad) * dist)
                if 0 <= sx < self.width and 0 <= sy < self.height:
                    surf.set_at((sx, sy), black)
                    if dist > 5:
                        surf.set_at((sx, sy + 1), dark_red)

        eye_y = center_y - 1
        surf.set_at((center_x - 3, eye_y), bright_red)
        surf.set_at((center_x + 3, eye_y), bright_red)

        for x in range(-2, 3):
            surf.set_at((center_x + x, center_y + 3), tan)

        for i in range(2):
            trail_y = center_y - 10 - i * 3
            if trail_y > 0:
                for x in range(-3, 4):
                    surf.set_at((center_x + x, trail_y), pygame.Color(*dark_red, 80 - i * 30))

        return surf

    def handle_input(self, keys):
        """
        Process player input for movement.
        Implements smooth acceleration and deceleration.
        """
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x -= PLAYER_ACCELERATION
            self.facing_right = False
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x += PLAYER_ACCELERATION
            self.facing_right = True
        else:
            if self.on_ground:
                self.vel_x *= GROUND_FRICTION
            else:
                self.vel_x *= AIR_FRICTION

        self.vel_x = max(-PLAYER_MAX_SPEED, min(PLAYER_MAX_SPEED, self.vel_x))

        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vel_y = -PLAYER_JUMP_POWER
            self.on_ground = False

    def update(self, dt, platforms):
        """Update player physics and animation."""
        if not self.on_ground:
            self.vel_y += GRAVITY
            self.vel_y = min(self.vel_y, MAX_FALL_SPEED)

        self.x += self.vel_x
        self.y += self.vel_y

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        self.handle_collisions(platforms)
        self.update_animation(dt)

        self.update_particles()
        if abs(self.vel_x) > PLAYER_MAX_SPEED * 0.7:
            self.spawn_particle()

    def handle_collisions(self, platforms):
        """Handle collision detection and response with platforms."""
        self.on_ground = False

        for platform in platforms:
            if self.rect.colliderect(platform):
                # Vertical collision
                if self.vel_y > 0:  # Falling
                    if self.rect.bottom > platform.top and self.rect.bottom < platform.top + 20:
                        self.rect.bottom = platform.top
                        self.y = self.rect.y
                        self.vel_y = 0
                        self.on_ground = True
                elif self.vel_y < 0:  # Jumping up
                    if self.rect.top < platform.bottom and self.rect.top > platform.bottom - 20:
                        self.rect.top = platform.bottom
                        self.y = self.rect.y
                        self.vel_y = 0

                # Horizontal collision
                if self.vel_x > 0:  # Moving right
                    if self.rect.right > platform.left and self.rect.right < platform.left + abs(self.vel_x) + 5:
                        self.rect.right = platform.left
                        self.x = self.rect.x
                        self.vel_x = 0
                elif self.vel_x < 0:  # Moving left
                    if self.rect.left < platform.right and self.rect.left > platform.right - abs(self.vel_x) - 5:
                        self.rect.left = platform.right
                        self.x = self.rect.x
                        self.vel_x = 0

    def update_animation(self, dt):
        """Update animation state and frame."""
        if not self.on_ground:
            self.state = 'jump' if self.vel_y < 0 else 'fall'
        elif abs(self.vel_x) > 0.5:
            self.state = 'run'
        else:
            self.state = 'idle'

        if self.state == 'run':
            self.animation_timer += dt * abs(self.vel_x)
            if self.animation_timer > 0.1:
                self.animation_timer = 0
                self.animation_frame = (self.animation_frame + 1) % 4

    def spawn_particle(self):
        """Create particle for Shadow's speed trail effect."""
        particle = {
            'x': self.x + self.width // 2,
            'y': self.y + self.height // 2,
            'vel_x': -self.vel_x * 0.2,
            'vel_y': 0,
            'lifetime': PARTICLE_LIFETIME,
            'color': self.particle_color
        }
        self.particles.append(particle)

        if len(self.particles) > 50:
            self.particles.pop(0)

    def update_particles(self):
        """Update particle positions and lifetimes."""
        for particle in self.particles[:]:
            particle['x'] += particle['vel_x']
            particle['y'] += particle['vel_y']
            particle['lifetime'] -= 1

            if particle['lifetime'] <= 0:
                self.particles.remove(particle)

    def render(self, screen, camera_offset):
        """Render player and particles."""
        for particle in self.particles:
            alpha = int((particle['lifetime'] / PARTICLE_LIFETIME) * 255)
            color = (*particle['color'], alpha)
            size = int((particle['lifetime'] / PARTICLE_LIFETIME) * 6) + 2
            pos_x = int(particle['x'] - camera_offset[0])
            pos_y = int(particle['y'] - camera_offset[1])

            particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, color, (size, size), size)
            screen.blit(particle_surf, (pos_x - size, pos_y - size))

        if self.state == 'run':
            sprite = self.sprites['run'][self.animation_frame]
        else:
            sprite = self.sprites.get(self.state, self.sprites['idle'])

        if not self.facing_right:
            sprite = pygame.transform.flip(sprite, True, False)

        render_x = int(self.x - camera_offset[0])
        render_y = int(self.y - camera_offset[1])
        screen.blit(sprite, (render_x, render_y))

    def reset(self, x, y):
        """Reset player to starting position."""
        self.x = x
        self.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.particles.clear()
        self.rect.topleft = (int(self.x), int(self.y))
        self.animation_frame = 0
        self.animation_timer = 0
        self.state = 'idle'
