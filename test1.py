import arcade
import random

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "My Game"

SPRITE_SCALING = 2.5
SPRITE_SCALING_ZOMBIE = 1.5
MOVEMENT_SPEED = 5  # Player
SPRITE_SPEED = 0.25  # Zombie

PLAYER_HEALTH = 300
ZOMBIE_DAMAGE = 1
ZOMBIE_COUNT = 15

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1

def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, mirrored=True)
    ]

###############################################
# ------ MAIN PLAYER SPRITE STARTS HERE ----- #
###############################################
class Player(arcade.Sprite):

    def __init__(self):

        # Set up parent class
        super().__init__()

        # Default to face-right
        self.character_face_direction = RIGHT_FACING

        # For frame of gifs
        self.gif_4 = 0
        self.gif_5 = 0
        self.gif_6 = 0

        # ----- LOAD TEXTURES -----#
        # Makes a 2D array using load_texture_pair() of individual gif images

        # Idle textures
        self.idle_textures = []
        for i in range(4):
            texture = load_texture_pair("img/adventurer/adventurer-idle-2-0" + str(i) + ".png")
            self.idle_textures.append(texture)

        # Running textures
        self.run_textures = []
        for i in range(6):
            texture = load_texture_pair("img/adventurer/adventurer-run-0" + str(i) + ".png")
            self.run_textures.append(texture)

        # Attack1 textures
        self.attack1_textures = []
        for i in range(5):
            texture = load_texture_pair("img/adventurer/attack/adventurer-attack1-0" + str(i) + ".png")
            self.attack1_textures.append(texture)

    def update_animation(self, delta_time: float = 1 / 60):

        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        self.gif_4 += 1
        self.gif_5 += 1
        self.gif_6 += 1
        if self.change_x == 0 and self.change_y == 0 and self.alpha == 255:
            if self.gif_4 > 27:  # idle gif has 4 images
                self.gif_4 = 0
            self.texture = self.idle_textures[self.gif_4 // 9][self.character_face_direction]
        elif self.alpha == 254:
            if self.gif_4 > 4:  # attack1 gif has 5 images
                self.gif_4 = 0
            self.texture = self.attack1_textures[self.gif_4][self.character_face_direction]
            if self.texture == self.attack1_textures[4][self.character_face_direction]:
                self.alpha = 255
        else:
            if self.gif_6 > 25:  # run gif has 6 images
                self.gif_6 = 0
            self.texture = self.run_textures[self.gif_6 // 5][self.character_face_direction]

    def right_facing(self):
        if self.character_face_direction == RIGHT_FACING:
            return True
        return False

#########################################
# ------ ENEMY SPRITE STARTS HERE ----- #
#########################################
class Zombie(arcade.Sprite):

    def __init__(self):
        # Set up parent class
        super().__init__()

        # Default to face-right
        self.character_face_direction = RIGHT_FACING

        # For frame of gifs
        self.gif_4 = 0
        self.gif_11 = 0

        # ----- LOAD TEXTURES -----#

        # Run textures
        self.run_textures = []
        for i in range(4):
            texture = load_texture_pair("img/zombie/zombie-run-0" + str(i) + ".png")
            self.run_textures.append(texture)

        self.die_textures = []
        for i in range(11):
            texture = load_texture_pair("img/zombie/zombie-die-0" + str(i) + ".png")
            self.die_textures.append(texture)

    def follow_sprite(self, player_sprite):
        """
        This function will move the current sprite towards whatever
        other sprite is specified as a parameter.

        We use the 'min' function here to get the sprite to line up with
        the target sprite, and not jump around if the sprite is not off
        an exact multiple of SPRITE_SPEED.
        """
        # Figure out if we need to flip face left or right
        # Zombie sprite textures actually start left facing so need to invert
        if self.alpha == 255:
            if self.center_y < player_sprite.center_y:
                self.center_y += min(SPRITE_SPEED, player_sprite.center_y - self.center_y)
            elif self.center_y > player_sprite.center_y:
                self.center_y -= min(SPRITE_SPEED, self.center_y - player_sprite.center_y)

            if self.center_x < player_sprite.center_x:
                self.center_x += min(SPRITE_SPEED, player_sprite.center_x - self.center_x)
                self.character_face_direction = RIGHT_FACING + 1
            elif self.center_x > player_sprite.center_x:
                self.center_x -= min(SPRITE_SPEED, self.center_x - player_sprite.center_x)
                self.character_face_direction = LEFT_FACING - 1

    def update_animation(self, delta_time: float = 1 / 60):

        self.gif_4 += 1
        self.gif_11 += 1

        if self.alpha == 255:
            if self.gif_4 > 27:  # idle gif has 4 images
                self.gif_4 = 0
            self.texture = self.run_textures[self.gif_4 // 9][self.character_face_direction]
        elif self.alpha == 150:
            if self.gif_11 > 100:  # idle gif has 11 images
                self.gif_11 = 0
            self.texture = self.die_textures[self.gif_11 // 10][self.character_face_direction]
            if self.texture == self.die_textures[10][self.character_face_direction]:
                self.remove_from_sprite_lists()

    def right_facing(self):
        if self.character_face_direction == RIGHT_FACING + 1:
            return True
        return False

class Shape:
    """ Generic base shape class """
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

class Rectangle(Shape):
    def draw(self):
        arcade.draw_rectangle_filled(self.x, self.y, self.width, self.height,
                                     self.color)

############################################
# ----- MAIN GAME WINDOW STARTS HERE ----- #
############################################
class MyGame(arcade.Window):
    """
    Main application class.
    """
    def __init__(self, width, height, title):

        # Call the parent class initializer
        super().__init__(width, height, title)

        # Background image will be stored in this variable
        self.background = None

        # Variables that will hold sprite lists
        self.player_list = None
        self.zombie_list = None
        self.health_bar = None

        # Set up the player info
        self.player_sprite = None

        # Track the current state of what key is pressed
        # For better key movement
        self.A_pressed = False
        self.D_pressed = False
        self.W_pressed = False
        self.S_pressed = False

        # Disable mouse cursor
        self.set_mouse_visible(False)

        # Set the background colour
        arcade.set_background_color(arcade.color.AMAZON)

    def setup(self):

        # Load the background image. Do this in the setup so we don't keep reloading it all the time.
        self.background = arcade.load_texture("img/bg.png")

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.zombie_list = arcade.SpriteList()
        self.health_bar = Rectangle(190, 682, PLAYER_HEALTH, 5, arcade.color.RED)

        # Set up the player
        self.player_sprite = Player()
        self.player_sprite.center_x = SCREEN_WIDTH//2
        self.player_sprite.center_y = SCREEN_HEIGHT//2
        self.player_sprite.scale = SPRITE_SCALING
        self.player_list.append(self.player_sprite)

        # Set up the zombie
        for i in range(ZOMBIE_COUNT):
            zombie = Zombie()
            zombie.scale = SPRITE_SCALING_ZOMBIE
            zombie.center_x = random.randrange(69, SCREEN_WIDTH-65)
            zombie.center_y = random.randrange(105, SCREEN_HEIGHT-25)
            self.zombie_list.append(zombie)

    def on_draw(self):
        """
        Render the screen.
        """
        # ALWAYS START WITH THIS COMMAND
        arcade.start_render()

        # Draw the background texture
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)

        # Draw empty health bar
        arcade.draw_rectangle_filled(190, 682, PLAYER_HEALTH, 5, arcade.color.DUTCH_WHITE)
        output = "Health Bar:"
        arcade.draw_text(output, 40, 688, arcade.color.RED, 15)

        # Draw all the sprites
        self.player_list.draw()
        self.zombie_list.draw()
        self.health_bar.draw()

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """

        # Calculate speed based on the keys pressed
        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0

        if self.W_pressed and not self.S_pressed:
            if self.player_sprite.center_y >= SCREEN_HEIGHT - 25:
                self.player_sprite.change_y = 0
            else:
                self.player_sprite.change_y = MOVEMENT_SPEED
        elif self.S_pressed and not self.W_pressed:
            if self.player_sprite.center_y <= 105:
                self.player_sprite.change_y = 0
            else:
                self.player_sprite.change_y = -MOVEMENT_SPEED
        if self.A_pressed and not self.D_pressed:
            if self.player_sprite.center_x <= 69:
                self.player_sprite.change_x = 0
            else:
                self.player_sprite.change_x = -MOVEMENT_SPEED
        elif self.D_pressed and not self.A_pressed:
            if self.player_sprite.center_x >= SCREEN_WIDTH - 65:
                self.player_sprite.change_x = 0
            else:
                self.player_sprite.change_x = MOVEMENT_SPEED

        # Check if zombie is hit by player attack
        for zombie in self.zombie_list:
            zombie.follow_sprite(self.player_sprite)
            if self.player_sprite.alpha == 254:
                if (self.player_sprite.center_y - 30 <= zombie.center_y <= self.player_sprite.center_y + 90) and \
                        (self.player_sprite.center_x - 80 <= zombie.center_x <= self.player_sprite.center_x + 80):
                    if (self.player_sprite.right_facing() and not zombie.right_facing()) or \
                            (not self.player_sprite.right_facing() and zombie.right_facing()) or \
                            ((self.player_sprite.center_y - 30 <= zombie.center_y <= self.player_sprite.center_y + 90)
                             and (self.player_sprite.center_x - 30 <= zombie.center_x <= self.player_sprite.center_x +
                                  30)):
                        zombie.alpha = 150
            if arcade.check_for_collision(self.player_sprite, zombie) and zombie.alpha == 255:
                if self.health_bar.width > 0:
                    self.health_bar.width -= ZOMBIE_DAMAGE
                    self.health_bar.x -= ZOMBIE_DAMAGE/2

        # Call update to move the sprite
        self.player_list.update()
        self.player_list.update_animation()
        self.zombie_list.update_animation()

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.
        """
        if key == arcade.key.W:
            self.W_pressed = True
        elif key == arcade.key.S:
            self.S_pressed = True
        elif key == arcade.key.A:
            self.A_pressed = True
        elif key == arcade.key.D:
            self.D_pressed = True

        if key == arcade.key.SPACE:
            self.player_sprite.alpha = 254

    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        if key == arcade.key.W:
            self.W_pressed = False
        elif key == arcade.key.S:
            self.S_pressed = False
        elif key == arcade.key.A:
            self.A_pressed = False
        elif key == arcade.key.D:
            self.D_pressed = False


def main():
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
