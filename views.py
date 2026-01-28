import arcade
from arcade.gui import UIManager, UILabel, UIFlatButton, UIAnchorLayout, UIBoxLayout
from pyglet.graphics import Batch

from config import TILE_SCALING, MAP_WIDTH, MAP_HEIGHT, TILE_SCALED_SIZE, SCORE_X, SCORE_Y, FONT_SIZE
from custom_types import EnemyType, MoveDirection
from mobs import Hero, Enemy


class MenuView(arcade.View):
    def __init__(self):
        super().__init__()

        self.manager = UIManager()
        self.manager.enable()

        self.anchor_layout = UIAnchorLayout()
        self.box_layout = UIBoxLayout(vertical=True, space_between=10)

        self.setup_widgets()
        
        self.anchor_layout.add(self.box_layout)
        self.manager.add(self.anchor_layout)

    def setup_widgets(self):
        title = UILabel(text="Dotllector",
                        font_size=40,
                        text_color=arcade.color.WHITE,
                        align="center")
        self.box_layout.add(title)

        start_button = UIFlatButton(text="Начать игру")
        start_button.on_click = lambda event: self.window.show_view(self.window.game_view)
        self.box_layout.add(start_button)

        exit_button = UIFlatButton(text="Выйти")
        exit_button.on_click = lambda event: exit(0)
        self.box_layout.add(exit_button)

    def on_draw(self):
        self.clear()
        self.window.game_view.walls_list.draw()
        self.manager.draw()

    def on_hide(self):
        self.manager.disable()
            

class GameOverView(arcade.View):
    def __init__(self, win=False):
        super().__init__()

        self.win_screen = win
        
        self.manager = UIManager()
        self.manager.enable()

        self.anchor_layout = UIAnchorLayout()
        self.box_layout = UIBoxLayout(vertical=True, space_between=10)

        self.setup_widgets()
        
        self.anchor_layout.add(self.box_layout)
        self.manager.add(self.anchor_layout)

    def setup_widgets(self):
        text = UILabel(text="Победа!" if self.win_screen else "Игра окончена!")
        self.box_layout.add(text)

        restart_text = UILabel(text="Нажмите любую кнопку, чтобы сыграть ещё раз.")
        self.box_layout.add(restart_text)

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def on_hide(self):
        self.manager.disable()
        
    def on_key_press(self, key: int, modifiers: int):
        self.window.game_view = GameView()
        self.window.show_view(self.window.game_view)


class PauseView(arcade.View):
    def __init__(self):
        super().__init__()

        self.manager = UIManager()
        self.manager.enable()

        self.anchor_layout = UIAnchorLayout()
        self.box_layout = UIBoxLayout(vertical=True, space_between=10)

        self.setup_widgets()
        
        self.anchor_layout.add(self.box_layout)
        self.manager.add(self.anchor_layout)

    def setup_widgets(self):
        text = UILabel(text="Пауза")
        self.box_layout.add(text)

        restart_text = UILabel(text="Нажмите ESC, чтобы продолжить.")
        self.box_layout.add(restart_text)
        
    def on_draw(self):
        self.window.game_view.on_draw()
        self.manager.draw()

    def on_hide(self):
        self.manager.disable()

    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.window.game_view)
    
        
class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.mob_list = arcade.SpriteList()

        tile_map = arcade.load_tilemap("maze.tmx", scaling=TILE_SCALING)

        self.batch = Batch()
        self.score_text = arcade.Text("Счёт: 0", SCORE_X, SCORE_Y, arcade.color.WHITE, font_size=FONT_SIZE, anchor_x="left", batch=self.batch)
        self.mode_text = arcade.Text("Враги прячутся", SCORE_X, SCORE_Y - TILE_SCALED_SIZE, arcade.color.WHITE, font_size=FONT_SIZE, anchor_x="left", batch=self.batch)

        self.walls_list = tile_map.sprite_lists["walls"]
        self.food_list = tile_map.sprite_lists["food"]
        self.collision_list = tile_map.sprite_lists["collision"]

        collisions = [[False for _ in range(MAP_HEIGHT)] for _ in range(MAP_WIDTH)]
        
        for sprite in self.collision_list:
            cell_x = int(sprite.center_x / TILE_SCALED_SIZE)
            cell_y = int(sprite.center_y / TILE_SCALED_SIZE)
            
            collisions[cell_x][cell_y] = True


        self.player = Hero(collisions)

        chaser = Enemy((13, 18), collisions, self.mob_list, EnemyType.CHASER)
        waycutter = Enemy((12, 18), collisions, self.mob_list, EnemyType.WAYCUTTER)
        complexone = Enemy((14, 18), collisions, self.mob_list, EnemyType.COMPLEXONE)
        scaredycat = Enemy((11, 18), collisions, self.mob_list, EnemyType.SCAREDYCAT)
        
        self.mob_list.append(self.player)
        self.mob_list.append(chaser)
        self.mob_list.append(waycutter)
        self.mob_list.append(complexone)
        self.mob_list.append(scaredycat)

        self.chasing = False

        self.mode_timer = 0
        self.score = 0

    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.window.pause_view)

    def on_draw(self):
        self.clear()

        self.batch.draw()
        self.walls_list.draw()
        self.food_list.draw()
        self.mob_list.draw()

    def on_update(self, delta_time: float):
        self.mode_timer += delta_time
        if (self.chasing and self.mode_timer >= 20) or (not self.chasing and self.mode_timer >= 7):
            self.chasing = not self.chasing
            for mob in self.mob_list:
                if type(mob).__name__ == "Hero":
                    continue
                mob.switch_mode()
            self.mode_text.text = "Враги ищут героя" if self.chasing else "Враги прячутся"
            self.mode_timer = 0
        
        if arcade.key.UP in self.window.pressed_keys:
            self.player.move(MoveDirection.UP)
        elif arcade.key.DOWN in self.window.pressed_keys:
            self.player.move(MoveDirection.DOWN)
        elif arcade.key.LEFT in self.window.pressed_keys:
            self.player.move(MoveDirection.LEFT)
        elif arcade.key.RIGHT in self.window.pressed_keys:
            self.player.move(MoveDirection.RIGHT)

        self.mob_list.update(delta_time)

        if not self.food_list:
            self.window.show_view(self.window.win_view)
        
        # Сбор точек
        eaten_pellets = arcade.check_for_collision_with_list(self.player, self.food_list)
        for pellet in eaten_pellets:
            pellet.remove_from_sprite_lists()
            self.score += 10

        if arcade.check_for_collision_with_list(self.player, self.mob_list):
            self.window.show_view(self.window.lose_view)

        self.score_text.text = f"Счёт: {self.score}"
            
