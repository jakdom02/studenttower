# actors.py
import turtle
import os
import winsound
from constants import (ACCELERATION, TURN_FACTOR, JUMP_DISTANCE,
                       JUMP_FACTOR, GRAVITY, FRICTION,
                       PLAYER_PIXEL_SIZE, PLAT_PIXEL_SIZE,
                       WALL_BOUNCE_FACTOR, WALL_PIXEL_SIZE,
                       MAX_SPEED, ROTATION_SPEED, PLAYER_HALF_SIZE,
                       PLAT_HALF_SIZE, WALL_HALF_SIZE, PLAYER_COLLISION_TOLERANCE,
                       AIR_FRICTION, TURN_ACCELERATION, NEG_MAX_SPEED, CELEBRATION_THRESHOLD
                       )

#  sprite lists and lookups for O(1) access
ROTATION_SPRITES = [
    "student2.gif", "45.gif", "90.gif", "135.gif",
    "180.gif", "315.gif", "270.gif", "225.gif"
]
SPRITE_COUNT = len(ROTATION_SPRITES)
ANGLE_TO_SPRITE = 45  # 360 / 8 sprites
GROUND_SPRITES = ["studentlewo.gif", "student2.gif", "studentprawo.gif"]  # -1, 0, +1 mapping


class Actor(turtle.Turtle):
    # actor base class
    __slots__ = ()  # prevent dict creation for memory optimization

    def __init__(self):
        super().__init__()
        self.speed(0)
        self.penup()


class Player(Actor):
    # player class with minimal overhead

    # using __slots__ to prevent dictionary creation and reduce memory overhead
    __slots__ = ('rotation_sprites', 'keys_right', 'keys_left', 'keys_space',
                 'platforms', 'walls', 'can_jump', 'dx', 'dy', 'next_x', 'next_y',
                 'scroll_active', 'scroll_speed', 'scroll_speed_threshold',
                 'highest_floor', 'last_dy', 'rotation_angle', 'spin_dir',
                 '_xcor_cache', '_ycor_cache')

    def __init__(self, start_x, start_y, platforms, walls):
        super().__init__()

        self.rotation_sprites = ROTATION_SPRITES
        self.shape(self.rotation_sprites[0])

        self.keys_right = False
        self.keys_left = False
        self.keys_space = False

        self.goto(start_x, start_y)

        self.platforms = platforms
        self.walls = walls

        self.can_jump = True
        self.dx = self.dy = 0
        self.next_x = start_x
        self.next_y = start_y
        self.scroll_active = False
        self.scroll_speed = 1
        self.scroll_speed_threshold = 3000
        self.highest_floor = 0
        self.last_dy = 0
        self.rotation_angle = 0
        self.spin_dir = 1

        self._xcor_cache = self.xcor
        self._ycor_cache = self.ycor

    def go_right(self):
        self.keys_right = True

    def go_left(self):
        self.keys_left = True

    def stop_right(self):
        self.keys_right = False

    def stop_left(self):
        self.keys_left = False

    def press_space(self):
        self.keys_space = True

    def release_space(self):
        self.keys_space = False

    def update(self):
        # single update method with everything inlined
        dx = self.dx

        if self.keys_right:
            dx += TURN_ACCELERATION if dx < 0 else ACCELERATION
        if self.keys_left:
            dx -= TURN_ACCELERATION if dx > 0 else ACCELERATION

        if self.keys_space and self.can_jump:
            winsound.PlaySound("cartoonjump.wav", winsound.SND_ASYNC)
            self.dy = JUMP_DISTANCE + abs(dx) * JUMP_FACTOR
            self.can_jump = False
            self.spin_dir = 1 if dx >= 0 else -1

        dy = self.dy

        # Gravity
        if not self.can_jump:
            dy -= GRAVITY
            dx *= AIR_FRICTION
        elif not (self.keys_right or self.keys_left):
            dx *= FRICTION

        # speed limits
        dx = min(MAX_SPEED, max(NEG_MAX_SPEED, dx))

        current_x = self._xcor_cache()
        current_y = self._ycor_cache()

        next_x = current_x + dx
        next_y = current_y + dy

        player_left = next_x - PLAYER_HALF_SIZE
        player_right = next_x + PLAYER_HALF_SIZE

        for wall in self.walls:
            wall_x = wall.xcor()
            wall_left = wall_x - WALL_HALF_SIZE
            wall_right = wall_x + WALL_HALF_SIZE

            if player_right > wall_left and current_x < wall_x:
                self.setx(wall_left - PLAYER_HALF_SIZE)
                dx = -abs(dx) * WALL_BOUNCE_FACTOR
                dy += abs(dx) * WALL_BOUNCE_FACTOR

            elif player_left < wall_right and current_x > wall_x:
                self.setx(wall_right + PLAYER_HALF_SIZE)
                dx = abs(dx) * WALL_BOUNCE_FACTOR
                dy += abs(dx) * WALL_BOUNCE_FACTOR

        if dy <= 0:
            player_bottom = current_y - PLAYER_HALF_SIZE

            for plat in self.platforms:
                plat_top = plat.ycor() + PLAT_HALF_SIZE
                plat_length_10 = plat.length * 10
                plat_left = plat.xcor() - plat_length_10
                plat_right = plat.xcor() + plat_length_10

                if (plat_left - PLAYER_COLLISION_TOLERANCE <= current_x <= plat_right + PLAYER_COLLISION_TOLERANCE and
                        abs(player_bottom - plat_top) <= max(1, -dy)):
                    self.sety(plat_top + PLAYER_HALF_SIZE)
                    dy = 0
                    self.can_jump = True
                    break
            else:
                self.can_jump = False
        else:
            self.can_jump = False

        # Apply movement threshold
        if abs(dx) < 0.1:
            dx = 0

        # Update position
        self.goto(current_x + dx, current_y + dy)
        self.dx = dx
        self.dy = dy

        # sound and animations
        if self.last_dy <= CELEBRATION_THRESHOLD < dy:
            winsound.PlaySound("yay.wav", winsound.SND_ASYNC)
        self.last_dy = dy

        # sprite updates
        if not self.can_jump and dx != 0:  # airborne spinning
            # fast modulo using bitwise operations where possible
            self.rotation_angle = (self.rotation_angle + ROTATION_SPEED * self.spin_dir) % 360
            sprite_idx = (self.rotation_angle // ANGLE_TO_SPRITE) % SPRITE_COUNT
            self.shape(self.rotation_sprites[sprite_idx])
        else:  # grounded
            self.rotation_angle = 0
            # branchless sprite selection using sign conversion
            sprite_idx = (dx > 0) - (dx < 0) + 1  # Maps to 0, 1, 2
            self.shape(GROUND_SPRITES[sprite_idx])

