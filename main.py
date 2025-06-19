# main.py
import turtle
import random
from constants import (SCREEN_HEIGHT, SCREEN_WIDTH, SCREEN_MARGIN, SCROLL_THRESHOLD,
                       FAST_SCROLL_SPEED, PLAT_PIXEL_SIZE, PLAYER_PIXEL_SIZE,
                       JUMP_DISTANCE, MAX_SCROLL_SPEED, WALL_PIXEL_SIZE, GROUND_Y,
                       PLAYER_START_Y, FLOOR_SHAPE_LENGTH, FLOOR_PIXEL_LENGTH, FAST_SCROLL_Y,
                       HALF_PLAT_SIZE, HALF_SCREEN_HEIGHT, HALF_SCREEN_WIDTH, HALF_PLAYER_SIZE,
                       PLATFORM_GAP, FRAME_TIME)

from renderer import Wall, Platform, Score, Star, Bonus
from actors import Player


def init_screen():
    # initialize Main Game Screen
    screen = turtle.Screen()
    screen.tracer(0)
    screen.title("StudentTower")
    screen.setup(SCREEN_WIDTH, SCREEN_HEIGHT)
    screen.bgpic("backgroundAGH.gif")

    # register all shapes at once for better performance
    shapes = [
        "plat.gif", "plat120.gif", "plat140.gif", "plat160.gif",
        "plat180.gif", "plat200.gif", "plat220.gif", "plat240.gif",
        "student2.gif", "studentprawo.gif", "studentlewo.gif",
        "45.gif", "90.gif", "135.gif", "315.gif", "270.gif", "225.gif", "180.gif",
        "image.gif"
    ]
    for shape in shapes:
        try:
            screen.register_shape(shape)
        except:
            # if shape file doesn't exist, skip it
            print(f"Warning: Could not load shape {shape}")
            pass

    return screen


def bind_controls(screen, player):
    # keyboard & mouse bindings
    screen.listen()
    screen.onkeypress(player.go_right, "Right")
    screen.onkeyrelease(player.stop_right, "Right")
    screen.onkeypress(player.go_left, "Left")
    screen.onkeyrelease(player.stop_left, "Left")
    screen.onkeypress(player.press_space, "space")
    screen.onkeyrelease(player.release_space, "space")


def scroll_world(walls, platforms, player, stars, bonuses):

    # world scrolling with efficient platform recycling.

    # start scrolling once the player rises above threshold
    if not player.scroll_active and player.ycor() > SCROLL_THRESHOLD:
        player.scroll_active = True

    if not player.scroll_active:
        return

    # determine scroll speed
    speed = FAST_SCROLL_SPEED if player.ycor() > FAST_SCROLL_Y else player.scroll_speed

    # move all objects down in a single loop
    all_objects = platforms + walls + [player] + stars + bonuses
    for obj in all_objects:
        obj.sety(obj.ycor() - speed)

    # optimized platform recycling
    platforms_to_recycle = []
    top_y = float('-inf')
    max_floor = 0

    # single pass to find recyclable platforms and current top
    for plat in platforms:
        if plat.ycor() + HALF_PLAT_SIZE < -HALF_SCREEN_HEIGHT:
            platforms_to_recycle.append(plat)
        else:
            top_y = max(top_y, plat.ycor())
            max_floor = max(max_floor, plat.floor_num)

    # recycle platforms efficiently
    next_floor = max_floor + 1
    for plat in platforms_to_recycle:
        new_y = top_y + PLATFORM_GAP
        top_y = new_y  # Update for next platform

        plat.floor_num = next_floor
        next_floor += 1

        # calculate new x-position (FIXED)
        max_x = int((FLOOR_PIXEL_LENGTH - plat.length * 20) // 2)
        new_x = random.randint(-max_x, max_x)
        plat.goto(new_x, new_y)

    # remove bonuses that have fallen off screen
    bonuses_to_remove = []
    for bonus in bonuses:
        if bonus.ycor() < -HALF_SCREEN_HEIGHT:
            bonuses_to_remove.append(bonus)

    for bonus in bonuses_to_remove:
        bonus.hideturtle()
        bonuses.remove(bonus)


def spawn_bonus(platforms, bonuses, player):
    # spawn bonuses on platforms that are above the player with improved logic.

    # reduced chance for more balanced gameplay (1 in 300 chance per frame)
    if random.randint(1, 300) != 1:
        return

    # get player's current Y position
    player_y = player.ycor()

    # find platforms that are above the player and visible on screen
    eligible_platforms = []

    for plat in platforms:
        # platform must be above player by at least one platform gap
        min_height_above_player = player_y + PLATFORM_GAP * 1.5

        # check if platform is above player and within reasonable spawn range
        platform_y = plat.ycor()
        if (platform_y > min_height_above_player and
                platform_y < player_y + HALF_SCREEN_HEIGHT * 1.5):  # Don't spawn too far ahead

            # check if platform doesn't already have a bonus nearby
            has_bonus = False
            for bonus in bonuses:
                if (abs(bonus.xcor() - plat.xcor()) < plat.length * 15 and
                        abs(bonus.ycor() - platform_y) < 50):
                    has_bonus = True
                    break

            if not has_bonus:
                eligible_platforms.append(plat)

    # spawn bonus on random eligible platform above player
    if eligible_platforms:
        chosen_platform = random.choice(eligible_platforms)

        # place bonus on the platform with some random horizontal offset
        # FIX: Convert to integer to avoid float error with randint
        max_offset = int(chosen_platform.length * 8)
        bonus_x = chosen_platform.xcor() + random.randint(-max_offset, max_offset)
        bonus_y = chosen_platform.ycor() + HALF_PLAT_SIZE + 20  # Slightly above platform

        bonus = Bonus(bonus_x, bonus_y)
        bonuses.append(bonus)

        print(f"Bonus spawned at ({bonus_x:.0f}, {bonus_y:.0f}) - Player at {player_y:.0f}")


def check_bonus_collision(player, bonuses, score_display):

    # check if player collides with any bonuses and handle collection.

    bonuses_to_remove = []

    for bonus in bonuses:
        # collision detection using the bonus hitbox
        distance = ((player.xcor() - bonus.xcor()) ** 2 + (player.ycor() - bonus.ycor()) ** 2) ** 0.5

        if distance < bonus.HITBOX:
            # bonus collected add points and remove bonus
            score_display.score += bonus.VALUE
            bonus.hideturtle()
            bonuses_to_remove.append(bonus)
            print(f"Bonus collected! +{bonus.VALUE} points")

    # remove collected bonuses
    for bonus in bonuses_to_remove:
        bonuses.remove(bonus)


def restart_game(screen):
    # restart game state completely.
    screen.clear()

    # reload screen
    screen.bgpic("backgroundAGH.gif")
    screen.title("StudentTower")
    screen.setup(SCREEN_WIDTH, SCREEN_HEIGHT)
    screen.tracer(0)

    # reload of shapes
    shapes = [
        "plat.gif", "plat120.gif", "plat140.gif", "plat160.gif",
        "plat180.gif", "plat200.gif", "plat220.gif", "plat240.gif",
        "student2.gif", "studentprawo.gif", "studentlewo.gif",
        "45.gif", "90.gif", "135.gif", "315.gif", "270.gif", "225.gif", "180.gif",
        "image.gif"
    ]
    for shape in shapes:
        try:
            screen.register_shape(shape)
        except:
            # If shape file doesn't exist, skip it
            print(f"Warning: Could not load shape {shape}")
            pass

    # making the objects
    walls = [
        Wall(HALF_SCREEN_WIDTH - WALL_PIXEL_SIZE),
        Wall(-HALF_SCREEN_WIDTH + WALL_PIXEL_SIZE)
    ]
    platforms = create_platforms()
    player = Player(0, PLAYER_START_Y, platforms, walls)
    score_display = Score()
    stars = []
    bonuses = []

    bind_controls(screen, player)
    game_loop(screen, walls, platforms, player, score_display, stars, bonuses)


def update_stars(player, stars):
    # generate star on jump
    if player.dy > JUMP_DISTANCE:
        star = Star(player.xcor(), player.ycor() - HALF_PLAYER_SIZE)
        stars.append(star)

    # update and remove stars (reverse iteration for safe removal)
    for i in range(len(stars) - 1, -1, -1):
        star = stars[i]
        star.update()
        if star.ycor() < -HALF_SCREEN_HEIGHT:
            star.hideturtle()
            del stars[i]


def update_score(player, platforms, score_display):
    feet_y = player.ycor() - HALF_PLAYER_SIZE

    # find highest valid platform more efficiently
    best_floor = player.highest_floor
    for plat in platforms:
        if (plat.ycor() + HALF_PLAT_SIZE <= feet_y and
                plat.floor_num > best_floor):
            best_floor = plat.floor_num

    # update score if higher floor is found
    if best_floor > player.highest_floor:
        player.highest_floor = best_floor
        score_display.score = best_floor * 100

    # increase scroll speed every 3000 points (difficulty scaling)
    if (score_display.score >= player.scroll_speed_threshold and
            player.scroll_speed < MAX_SCROLL_SPEED):
        player.scroll_speed += 1
        player.scroll_speed_threshold += 3000

    # update score display
    score_display.update(score_display.score)


def game_loop(screen, walls, platforms, player, score_display, stars, bonuses):
    # update player movement
    player.update()

    # handle star effects
    update_stars(player, stars)

    # scroll world and recycle off-screen platforms
    scroll_world(walls, platforms, player, stars, bonuses)

    # spawn bonuses above the player
    spawn_bonus(platforms, bonuses, player)

    # check bonus collisions
    check_bonus_collision(player, bonuses, score_display)

    # update scoring
    update_score(player, platforms, score_display)

    # game over check
    if player.ycor() + HALF_PLAYER_SIZE < -HALF_SCREEN_HEIGHT:
        score_display.clear()
        score_display.game_over(screen, lambda: restart_game(screen))
        return

    # update screen and schedule next frame
    screen.update()
    screen.ontimer(lambda: game_loop(screen, walls, platforms, player, score_display, stars, bonuses), FRAME_TIME)


def create_platforms():
    # create initial platforms efficiently
    platforms = [Platform(0, GROUND_Y, FLOOR_SHAPE_LENGTH)]

    for i in range(30):
        length = random.randint(6, 12)
        max_x = int((FLOOR_PIXEL_LENGTH - length * 20) // 2)
        plat_x = random.randint(-max_x, max_x)
        plat_y = GROUND_Y + (i + 1) * PLATFORM_GAP

        platform = Platform(plat_x, plat_y, length)
        platform.floor_num = i + 1
        platforms.append(platform)

    return platforms


def main():
    # create screen
    screen = init_screen()

    # create walls
    walls = [
        Wall(HALF_SCREEN_WIDTH - WALL_PIXEL_SIZE),
        Wall(-HALF_SCREEN_WIDTH + WALL_PIXEL_SIZE)
    ]

    # create platforms
    platforms = create_platforms()

    # create player
    player = Player(0, PLAYER_START_Y, platforms, walls)

    # create score display
    score_display = Score()

    # create stars list
    stars = []

    # create bonuses list
    bonuses = []

    # keyboard bindings
    bind_controls(screen, player)

    # start game loop
    game_loop(screen, walls, platforms, player, score_display, stars, bonuses)

    # keep window open
    screen.mainloop()


# open only if run directly:
if __name__ == "__main__":
    main()