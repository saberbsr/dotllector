import arcade
from math import hypot

from custom_types import MoveDirection, EnemyType, DIRECTION_LIST
from config import (PLAYER_SPAWN_TILE_X, PLAYER_SPAWN_TILE_Y, TILE_SCALED_SIZE, PLAYER_MOVE_ANIMATION_FRAMES,
                    MOB_DEFAULT_WIDTH, MOB_DEFAULT_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT, MAP_WIDTH, MAP_HEIGHT,
                    DEFAULT_MOB_SPEED)


class Mob(arcade.Sprite):
    def __init__(self, collisions: list[list[bool]], direction: MoveDirection, moving: bool, spawn_tile: list[int]):
        super().__init__()

        self.collisions = collisions
        self.direction = direction
        self.moving = moving

        self.center_x = spawn_tile[0] * TILE_SCALED_SIZE + (TILE_SCALED_SIZE / 2)
        self.center_y = spawn_tile[1] * TILE_SCALED_SIZE + (TILE_SCALED_SIZE / 2)
        self.target_x, self.target_y = self.center_x, self.center_y

    def is_aligned_with_grid(self) -> bool:
        return (self.center_x - TILE_SCALED_SIZE / 2) % TILE_SCALED_SIZE == 0 and \
           (self.center_y - TILE_SCALED_SIZE / 2) % TILE_SCALED_SIZE == 0
        
    def move(self, new_direction: MoveDirection):
        if not self.moving or self.is_aligned_with_grid():
            self.direction = new_direction

            self.target_x, self.target_y = (self.center_x + TILE_SCALED_SIZE * self.direction[0],
                                            self.center_y + TILE_SCALED_SIZE * self.direction[1])

            self.moving = not self.collisions[int(self.target_x / TILE_SCALED_SIZE)][int(self.target_y / TILE_SCALED_SIZE)]
            
    def update(self, delta_time: float):
        if self.center_x <= -(self.width / 2):
            self.center_x = WINDOW_WIDTH + self.width / 2
            self.move(self.direction)
        elif self.center_x >= WINDOW_WIDTH + self.width / 2:
            self.center_x = -(self.width / 2)
            self.move(self.direction)

        if self.moving:
            dest_x = self.target_x - self.center_x
            dest_y = self.target_y - self.center_y
            
            if abs(dest_x) > 0:
                step = min(abs(dest_x), DEFAULT_MOB_SPEED) * (1 if dest_x > 0 else -1)
                self.center_x += step
            if abs(dest_y) > 0:
                step = min(abs(dest_y), DEFAULT_MOB_SPEED) * (1 if dest_y > 0 else -1)
                self.center_y += step

            if self.center_x == self.target_x and self.center_y == self.target_y:
                self.move(self.direction)


class Enemy(Mob):
    def __init__(self, init_pos: tuple[int, int], collisions: list[list[bool]], mob_list: arcade.SpriteList, enemy_type=EnemyType.CHASER):
        super().__init__(collisions, MoveDirection.LEFT, True, init_pos)
        self.enemy_type = enemy_type
        self.mob_list = mob_list

        self.chase = False
        
        if enemy_type == EnemyType.CHASER:
            self.texture = arcade.load_texture(":resources:/images/enemies/ladybug.png")
        elif enemy_type == EnemyType.WAYCUTTER:
            self.texture = arcade.load_texture(":resources:/images/enemies/fishPink.png")
        elif enemy_type == EnemyType.COMPLEXONE:
            self.texture = arcade.load_texture(":resources:/images/enemies/slimeBlue.png")
        else:
            self.texture = arcade.load_texture(":resources:/images/enemies/bee.png")
        self.width = MOB_DEFAULT_WIDTH
        self.height = MOB_DEFAULT_HEIGHT

        self.target_pos = (self.center_x, self.center_y)

    def switch_mode(self):
        opp_dir = MoveDirection.opposite(self.direction)
        if not self.collisions[int(self.center_x / TILE_SCALED_SIZE) + opp_dir[0]][int(self.center_y / TILE_SCALED_SIZE) + opp_dir[1]]:
            self.move(opp_dir)
        self.chase = not self.chase

    def chase_ai(self):
        hero = list(filter(lambda o: type(o).__name__ == "Hero", self.mob_list))[0]
        if self.enemy_type == EnemyType.WAYCUTTER:
            self.target_pos = (
                hero.center_x // TILE_SCALED_SIZE + 4 * hero.direction[0],
                hero.center_y // TILE_SCALED_SIZE + 4 * hero.direction[1]
            )
        elif self.enemy_type == EnemyType.COMPLEXONE:
            chaser = list(filter(lambda o: type(o).__name__ == "Enemy" and o.enemy_type == EnemyType.CHASER, self.mob_list))[0]
                
            self.target_pos = (
                (chaser.center_x + 2 * ((hero.center_x + 2 * hero.direction[0]) - chaser.center_x)) // TILE_SCALED_SIZE,
                (chaser.center_y + 2 * ((hero.center_y + 2 * hero.direction[1]) - chaser.center_y)) // TILE_SCALED_SIZE
            )
        else:
            self.target_pos = (hero.center_x // TILE_SCALED_SIZE, hero.center_y // TILE_SCALED_SIZE)
            if self.enemy_type == EnemyType.SCAREDYCAT and hypot(self.center_x - hero.center_x, self.center_y - hero.center_y) // TILE_SCALED_SIZE <= 8:
                self.target_pos = (0, 0)
                
    def scatter_ai(self):
        if self.enemy_type == EnemyType.CHASER:
            self.target_pos = (MAP_WIDTH, MAP_HEIGHT)
        elif self.enemy_type == EnemyType.WAYCUTTER:
            self.target_pos = (0, MAP_HEIGHT)
        elif self.enemy_type == EnemyType.COMPLEXONE:
            self.target_pos = (MAP_WIDTH, 0)
        else:
            self.target_pos = (0, 0)

    def move(self, new_direction: MoveDirection | None):
        if not self.moving or self.is_aligned_with_grid():
            self.moving = True
            if new_direction is not None:
                self.direction = new_direction
                self.target_x, self.target_y = (self.center_x + TILE_SCALED_SIZE * self.direction[0],
                                            self.center_y + TILE_SCALED_SIZE * self.direction[1])
                return
            
            if self.chase:
                self.chase_ai()
            else:
                self.scatter_ai()

            possible_ways = []
            for direction in DIRECTION_LIST:
                if direction == MoveDirection.opposite(self.direction):
                    continue

                new_pos = (
                    self.center_x + TILE_SCALED_SIZE * direction[0],
                    self.center_y + TILE_SCALED_SIZE * direction[1]
                )
                
                if not self.collisions[int(new_pos[0] / TILE_SCALED_SIZE)][int(new_pos[1] / TILE_SCALED_SIZE)]:
                    possible_ways.append((direction, new_pos))

            try:
                best_dir, best_pos = min(
                    possible_ways,
                    key=lambda o: abs(o[1][0] // TILE_SCALED_SIZE - self.target_pos[0]) + abs(o[1][1] // TILE_SCALED_SIZE - self.target_pos[1])
                )
            except ValueError:
                return

            self.direction = best_dir
            self.target_x, self.target_y = best_pos

    def update(self, delta_time: float):
        if self.center_x <= -(self.width / 2):
            self.center_x = WINDOW_WIDTH + self.width / 2
            self.move(self.direction)
        elif self.center_x >= WINDOW_WIDTH + self.width / 2:
            self.center_x = -(self.width / 2)
            self.move(self.direction)

        if self.moving:
            dest_x = self.target_x - self.center_x
            dest_y = self.target_y - self.center_y
            
            if abs(dest_x) > 0:
                step = min(abs(dest_x), DEFAULT_MOB_SPEED) * (1 if dest_x > 0 else -1)
                self.center_x += step
            if abs(dest_y) > 0:
                step = min(abs(dest_y), DEFAULT_MOB_SPEED) * (1 if dest_y > 0 else -1)
                self.center_y += step

            if self.center_x == self.target_x and self.center_y == self.target_y:
                self.move(None)


class Hero(Mob):
    def __init__(self, collisions: list[list[bool]]):
        super().__init__(collisions, MoveDirection.LEFT, True, [PLAYER_SPAWN_TILE_X, PLAYER_SPAWN_TILE_Y])

        self.cur_anim_frame = PLAYER_MOVE_ANIMATION_FRAMES // 2

        self.idle_texture = arcade.load_texture(":resources:/images/animated_characters/male_adventurer/maleAdventurer_idle.png")
        self.move_animation = [arcade.load_texture(f":resources:/images/animated_characters/male_adventurer/maleAdventurer_walk{i}.png") for i in range(PLAYER_MOVE_ANIMATION_FRAMES)]
        
        self.texture = self.move_animation[self.cur_anim_frame]
        self.width = MOB_DEFAULT_WIDTH
        self.height = MOB_DEFAULT_HEIGHT

    def update(self, delta_time: float):
        super().update(delta_time)

        if self.moving:
            self.cur_anim_frame = (self.cur_anim_frame + 1) % PLAYER_MOVE_ANIMATION_FRAMES
            new_texture = self.move_animation[self.cur_anim_frame]
            if self.direction == MoveDirection.LEFT:
                self.texture = new_texture.flip_horizontally()
            else:
                self.texture = new_texture
        else:
            self.texture = self.idle_texture
