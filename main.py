import arcade
from config import WINDOW_WIDTH, WINDOW_HEIGHT

from views import *


class Dotllector(arcade.Window):
    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, type(self).__name__)

    def setup(self):
        arcade.SpriteList.DEFAULT_TEXTURE_FILTER = arcade.gl.NEAREST, arcade.gl.NEAREST  # убрать сглаживание текстур

        self.menu_view = MenuView()
        self.game_view = GameView()
        self.win_view = GameOverView(True)
        self.lose_view = GameOverView()
        self.pause_view = PauseView()
        
        self.show_view(self.menu_view)

    def on_key_press(self, key: int, modifiers: int):
        self.pressed_keys.add(key)

    def on_key_release(self, key: int, modifiers: int):
        self.pressed_keys.remove(key)


if __name__ == "__main__":
    window = Dotllector()
    window.setup()

    arcade.run()
