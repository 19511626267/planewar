
from game_items import *
from game_hud import *
from game_music import *


class Game(object):
    def __init__(self):
        self.main_window = pg.display.set_mode(SCREEN_RECT.size)
        pg.display.set_caption("Plane War")
        self.is_game_over = True
        self.is_pause = False
        self.all_group = pg.sprite.Group()
        self.enemies_group = pg.sprite.Group()
        self.supplies_group = pg.sprite.Group()
        self.all_group.add(Background(False), Background(True))
        self.hud_panel = HudPanel(self.all_group)
        self.create_enemies()
        self.hero = Hero(self.all_group)
        self.hud_panel.show_bomb(self.hero.bomb_count)
        self.create_supplies()
        self.player = MusicPlayer("game_music.ogg")
        MusicPlayer.play_music(-1)

    def create_supplies(self):
        Supply(0, self.supplies_group, self.all_group)
        Supply(1, self.supplies_group, self.all_group)
        pg.time.set_timer(THROW_SUPPLY_EVENT, 10000)

    def create_enemies(self):
        # 敌机精灵组中的精灵数量
        count = len(self.enemies_group.sprites())
        # 要添加到的精灵组
        groups = (self.all_group, self.enemies_group)

        # 判断游戏级别及已有的敌机数量
        if self.hud_panel.level == 1 and count == 0:
            for i in range(16):
                Enemy(0, 3, *groups)
        elif self.hud_panel.level == 2 and count == 16:
            for enemy in self.enemies_group.sprites():
                enemy.max_speed = 5
            for i in range(8):
                Enemy(0, 5, *groups)
            for i in range(2):
                Enemy(1, 1, *groups)
        elif self.hud_panel.level == 3 and count == 26:
            for enemy in self.enemies_group.sprites():
                enemy.max_speed = 7 if enemy.kind == 0 else 3
            for i in range(8):
                Enemy(0, 7, *groups)
            for i in range(2):
                Enemy(1, 3, *groups)
            for i in range(2):
                Enemy(2, 1, *groups)

    def reset_game(self):
        self.is_game_over = False
        self.is_pause = False

        self.hud_panel.reset_panel()
        self.hero.rect.midbottom = HERO_DEFAULT_MID_BOTTOM
        for enemy in self.enemies_group:
            enemy.kill()
        for bullet in self.hero.bullets_group:
            bullet.kill()
        self.create_enemies()

    def event_handler(self):
        """
        :return: 如果监听到退出事件，返回 True，否则返回 False
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return True
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return True
            elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                if self.is_game_over:
                    self.reset_game()
                else:
                    self.is_pause = not self.is_pause
                    self.player.pause_music(self.is_pause)

            if not self.is_game_over and not self.is_pause:
                # 监听关闭子弹增强事件
                if event.type == BULLET_ENHANCED_OFF_EVENT:
                    self.hero.bullets_kind = 0

                    pg.time.set_timer(BULLET_ENHANCED_OFF_EVENT, 0)

                # 监听投放道具事件
                if event.type == THROW_SUPPLY_EVENT:
                    self.player.play_sound("supply.wav")

                    supply = random.choice(self.supplies_group.sprites())

                    supply.throw_supply()

                # 监听发射子弹事件
                if event.type == HERO_FIRE_EVENT:
                    self.player.play_sound("bullet.wav")

                    self.hero.fire(self.all_group)

                # 监听取消英雄无敌事件
                if event.type == HERO_POWER_OFF_EVENT:
                    print("取消无敌状态...")
                    self.hero.is_power = False
                    pg.time.set_timer(HERO_POWER_OFF_EVENT, 0)

                # 监听英雄牺牲事件
                if event.type == HERO_DEAD_EVENT:
                    print("英雄牺牲了...")
                    self.hud_panel.lives_count -= 1
                    self.hud_panel.show_lives()
                    self.hud_panel.show_bomb(self.hero.bomb_count)  # 生命 -1 炮弹填满

                # 监听 b，引爆炸弹
                if event.type == pg.KEYDOWN and event.key == pg.K_b:
                    if self.hero.hp > 0 and self.hero.bomb_count > 0:
                        self.player.play_sound("use_bomb.wav")
                    score = self.hero.blowup(self.enemies_group)
                    self.hud_panel.show_bomb(self.hero.bomb_count)
                    if self.hud_panel.increase_score(score):
                        self.create_enemies()

        return False

    def start(self):
        clock = pg.time.Clock()
        frame_counter = 0
        while True:
            self.is_game_over = self.hud_panel.lives_count == 0

            if self.event_handler():
                self.hud_panel.save_best_score()

                return
            if self.is_game_over:
                self.hud_panel.panel_pause(True, self.all_group)
            elif self.is_pause:
                self.hud_panel.panel_pause(False, self.all_group)
            else:
                self.hud_panel.panel_resume(self.all_group)
                self.check_collide()
                # 获得当前时刻的按键元组
                keys = pg.key.get_pressed()
                move_hor = keys[pg.K_RIGHT] - keys[pg.K_LEFT]
                move_ver = keys[pg.K_DOWN] - keys[pg.K_UP]
                frame_counter = (frame_counter + 1) % FRAME_INTERVAL
                self.all_group.update(frame_counter == 0, move_hor, move_ver)
            self.all_group.draw(self.main_window)
            pg.display.update()
            clock.tick(60)

    def check_collide(self):

        # 英雄和敌机
        if not self.hero.is_power:
            enemies = pg.sprite.spritecollide(self.hero,
                                              self.enemies_group,
                                              False,
                                              pg.sprite.collide_mask)

            enemies = list(filter(lambda x: x.hp > 0, enemies))

            if enemies:
                self.player.play_sound(self.hero.wav_name)
                self.hero.hp = 0
            for enemy in enemies:
                enemy.hp = 0

        # 敌机和子弹
        hit_enemies = pg.sprite.groupcollide(self.enemies_group,
                                             self.hero.bullets_group,
                                             False,
                                             False,
                                             pg.sprite.collide_mask)

        for enemy in hit_enemies:
            if enemy.hp <= 0:
                continue

            for bullet in hit_enemies[enemy]:
                bullet.kill()
                enemy.hp -= bullet.damage
                if enemy.hp > 0:
                    continue
                if self.hud_panel.increase_score(enemy.value):
                    self.player.play_sound("upgrade.wav")
                    self.create_enemies()
                self.player.play_sound(enemy.wav_name)
                break

        # 英雄和道具
        supplies = pg.sprite.spritecollide(self.hero,
                                           self.supplies_group,
                                           False,
                                           pg.sprite.collide_mask)
        if supplies:
            supply = supplies[0]
            self.player.play_sound(supply.wav_name)
            supply.rect.y = SCREEN_RECT.h
            if supply.kind == 0:        # 炸弹补给
                self.hero.bomb_count += 1
                self.hud_panel.show_bomb(self.hero.bomb_count)
            else:                       # 子弹增强
                self.hero.bullets_kind = 1
                pg.time.set_timer(BULLET_ENHANCED_OFF_EVENT, 8000)        # 技能八秒


if __name__ == '__main__':
    pg.init()
    Game().start()
    pg.quit()
