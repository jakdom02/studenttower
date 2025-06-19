# renderer.py
import turtle as t
import random as r
from constants import SCREEN_HEIGHT as SH, SCREEN_WIDTH as SW, GRAVITY as G


def create_base_turtle():
    # factory function for creating base turtle with common settings
    turtle_obj = t.Turtle()
    turtle_obj.speed(0)
    turtle_obj.penup()
    turtle_obj.hideturtle()
    return turtle_obj


class GeneralPen(t.Turtle):
    # base turtle class with standardized initialization

    def __init__(self):
        t.Turtle.__init__(self)
        self._setup_turtle()

    def _setup_turtle(self):
        # configure turtle with standard settings
        self.speed(0)
        self.penup()
        self.hideturtle()


class Wall(GeneralPen):
    # wall entity for game boundaries

    def __init__(self, x_position):
        GeneralPen.__init__(self)
        self._position_wall(x_position)

    def _position_wall(self, x_coord):
        # set wall position on screen
        self.goto(x_coord, 0)


class Platform(GeneralPen):
    # interactive platform objects with varying sizes

    PLATFORM_SHAPES = {
        12: "plat240.gif",
        11: "plat220.gif",
        10: "plat200.gif",
        9: "plat180.gif",
        8: "plat160.gif",
        7: "plat140.gif",
        6: "plat120.gif",
        5: "plat100.gif"
    }

    DEFAULT_SHAPE = "plat.gif"

    def __init__(self, x_coord, y_coord, platform_length):
        GeneralPen.__init__(self)
        self._initialize_platform(x_coord, y_coord, platform_length)

    def _initialize_platform(self, x, y, length):
        # setup platform with position and appearance
        self.showturtle()
        self.length = length
        self.goto(x, y)
        self.floor_num = 0
        self._set_platform_shape()
        self.bonus = None

    def _set_platform_shape(self):
        # determine platform sprite based on length
        shape_file = self.PLATFORM_SHAPES.get(self.length, self.DEFAULT_SHAPE)
        self.shape(shape_file)


class Score(GeneralPen):
    # score tracking and display system

    SCORE_FONT = ("Courier", 32, "bold")
    GAME_OVER_FONT = ("Courier", 50, "bold")
    SCORE_COLOR = "ghostwhite"
    GAME_OVER_COLOR = "crimson"

    def __init__(self):
        GeneralPen.__init__(self)
        self._initialize_score_display()
        self.play_again_button = None  # button added

    def _initialize_score_display(self):
        # setup initial score display
        self.score = 0
        score_x = -SW // 2 + 10
        score_y = SH // 2 - 60
        self.goto(score_x, score_y)
        self.pencolor(self.SCORE_COLOR)
        self._render_score()

    def _render_score(self):
        # draw current score on screen
        score_text = f"Punkty: {self.score}"
        self.write(score_text, align="left", font=self.SCORE_FONT)

    def update(self, updated_score):
        # refresh score display with new value
        self.score = updated_score
        self.clear()
        self._render_score()

    def game_over(self, screen, restart_callback):
        # display final game over screen and show restart button
        self.goto(0, -50)
        self.color(self.GAME_OVER_COLOR)
        final_message = f"Koniec gry!\nKońcowy wynik: {self.score}"
        self.write(final_message, align="center", font=self.GAME_OVER_FONT)

        # text
        text = "Zagraj ponownie"
        BUTTON_FONT = ("Courier", 12, "bold")  # mniejsza czcionka

        text_width_estimate = len(text) * BUTTON_FONT[1] * 0.6
        padding = 40
        button_width = int(text_width_estimate + padding)
        button_height = BUTTON_FONT[1] + 20

        button = t.Turtle()
        button.hideturtle()
        button.penup()
        button.goto(-button_width // 2, -250)
        button.color("crimson", "lightblue")
        button.begin_fill()
        for _ in range(2):
            button.forward(button_width)
            button.left(90)
            button.forward(button_height)
            button.left(90)
        button.end_fill()

        button.goto(0, -250 + 10)
        button.color("crimson")
        button.write(text, align="center", font=BUTTON_FONT)

        def on_click(x, y):
            if (-button_width // 2 <= x <= button_width // 2) and (-250 <= y <= -250 + button_height):
                screen.onclick(None)
                button.clear()
                self.clear()
                restart_callback()

        screen.onclick(on_click)


class Star(GeneralPen):
    # animated star objects with physics

    STAR_COLORS = [
        "yellow", "cyan", "magenta", "orange",
        "white", "lightgreen", "red", "indigo"
    ]

    ROTATION_SPEED = 15
    STAR_SIZE = 0.5

    def __init__(self, x_position, y_position):
        GeneralPen.__init__(self)
        self._configure_star(x_position, y_position)

    def _configure_star(self, x, y):
        # initialize star appearance and physics
        self.shape("turtle")
        self.shapesize(self.STAR_SIZE)
        self._set_random_color()
        self.goto(x, y)
        self._set_random_heading()
        self.showturtle()
        self._initialize_physics()

    def _set_random_color(self):
        # apply random color from predefined palette
        selected_color = r.choice(self.STAR_COLORS)
        self.color(selected_color)

    def _set_random_heading(self):
        # set random initial rotation
        random_angle = r.randint(0, 360)
        self.setheading(random_angle)

    def _initialize_physics(self):
        # setup physics properties
        self.dy = 0
        self.angle = self.heading()

    def update(self):
        # update star position and rotation
        self._apply_gravity()
        self._rotate_star()
        self._update_position()

    def _apply_gravity(self):
        # apply gravitational force to vertical velocity
        self.dy -= G

    def _rotate_star(self):
        # increment rotation angle
        self.angle += self.ROTATION_SPEED
        self.setheading(self.angle)

    def _update_position(self):
        # move star based on current velocity
        new_y = self.ycor() + self.dy
        self.goto(self.xcor(), new_y)


class Bonus(GeneralPen):
    # bonus collectible with improved shape handling

    BONUS_SHAPE = "image.gif"  #
    FALLBACK_SHAPES = ["circle", "square", "triangle"]
    HITBOX = 20
    VALUE = 500

    def __init__(self, x_coord, y_coord):
        super().__init__()
        self._setup_bonus_shape()
        self.goto(x_coord, y_coord)
        self.showturtle()

    def _setup_bonus_shape(self):
        # setup bonus shape with fallback handling
        try:
            # try to use the primary bonus image
            self.shape(self.BONUS_SHAPE)
            self.color("gold")  # set color for the image
        except Exception as e:
            # if primary shape fails, try fallback shapes
            print(f"Warning: Could not load bonus shape '{self.BONUS_SHAPE}': {e}")
            self._use_fallback_shape()

    def _use_fallback_shape(self):
        # use a fallback shape if primary image is not available
        try:
            self.shape("circle")
            self.color("gold")
            self.shapesize(0.8)
            print("Using circle fallback for bonus shape")
        except Exception as e:
            # if even basic shapes fail, use turtle default
            print(f"Warning: Even fallback shapes failed: {e}")
            self.shape("turtle")
            self.color("yellow")
            self.shapesize(0.6)