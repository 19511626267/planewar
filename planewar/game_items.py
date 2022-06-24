
import random
import pygame as pg

SCREEN_RECT = pg.Rect(0, 0, 480, 700)         # 游戏主窗口矩形区域
FRAME_INTERVAL = 10                               # 逐帧动画间隔帧数

HERO_BOMB_COUNT = 3                               # 英雄默认炸弹数量
# 英雄默认初始位置
HERO_DEFAULT_MID_BOTTOM = (SCREEN_RECT.centerx,
                           SCREEN_RECT.bottom - 90)

HERO_DEAD_EVENT = pg.USEREVENT                # 英雄牺牲事件
HERO_POWER_OFF_EVENT = pg.USEREVENT + 1       # 取消英雄无敌事件
HERO_FIRE_EVENT = pg.USEREVENT + 2            # 英雄发射子弹事件

THROW_SUPPLY_EVENT = pg.USEREVENT + 3         # 投放道具事件
BULLET_ENHANCED_OFF_EVENT = pg.USEREVENT + 4  # 关闭子弹增强事件


class GameSprite(pg.sprite.Sprite):

    res_path = "resources/images/"

    def __init__(self, image_name, speed, *groups):
        super().__init__(*groups)

        self.image = pg.image.load(self.res_path + image_name)
        self.rect = self.image.get_rect()
        self.speed = speed
        self.mask = pg.mask.from_surface(self.image)

    def update(self, *args):
        self.rect.y += self.speed


class Label(pg.sprite.Sprite):
    font_path = "resources/font/MarkerFelt.ttc"

    def __init__(self, text, size, color, *groups):
        super().__init__(*groups)

        self.font = pg.font.Font(self.font_path, size)
        self.color = color

        self.image = self.font.render(text, True, self.color)
        self.rect = self.image.get_rect()

    def set_text(self, text):
        self.image = self.font.render(text, True, self.color)
        self.rect = self.image.get_rect()


class Background(GameSprite):

    def __init__(self, is_alt, *groups):
        super().__init__("background.png", 1, *groups)
        if is_alt:
            self.rect.y = -self.rect.h

    def update(self, *args):
        super().update(*args)
        if self.rect.y >= self.rect.h:
            self.rect.y = -self.rect.h


class StatusButton(GameSprite):

    def __init__(self, image_names, *groups):
        super().__init__(image_names[0], 0, *groups)
        self.images = [pg.image.load(self.res_path + name)
                       for name in image_names]

    def switch_status(self, is_pause):
        self.image = self.images[1 if is_pause else 0]


class Plane(GameSprite):

    def     __init__(self, hp, speed, value, wav_name,
                 normal_names, hurt_name, destroy_names, *groups):
        """
        :param normal_name: 记录正常飞行状态的图像名称列表
        :param groups: 要添加到的精灵组
        """
        super().__init__(normal_names[0], speed, *groups)

        self.hp = hp
        self.max_hp = hp
        self.value = value
        self.wav_name = wav_name
        self.normal_images = [pg.image.load(self.res_path + name)
                              for name in normal_names]
        self.normal_index = 0
        self.hurt_image = pg.image.load(self.res_path + hurt_name)
        self.destroy_images = [pg.image.load(self.res_path + name)
                               for name in destroy_names]
        self.destroy_index = 0

    def reset_plane(self):
        self.hp = self.max_hp

        self.normal_index = 0
        self.destroy_index = 0

        self.image = self.normal_images[0]

    def update(self, *args):
        if not args[0]:
            return
        if self.hp == self.max_hp:
            self.image = self.normal_images[self.normal_index]
            count = len(self.normal_images)
            self.normal_index = (self.normal_index + 1) % count
        elif self.hp > 0:
            self.image = self.hurt_image
        else:
            if self.destroy_index < len(self.destroy_images):
                self.image = self.destroy_images[self.destroy_index]
                self.destroy_index += 1
            else:
                self.reset_plane()


class Enemy(Plane):

    def __init__(self, kind, max_speed, *groups):
        self.kind = kind
        self.max_speed = max_speed
        if kind == 0:
            super().__init__(1, 1, 1000, "enemy1_down.wav",
                             ["enemy1.png"],
                             "enemy1.png",
                             ["enemy1_down%d.png" % i for i in range(1, 5)],
                             *groups)
        elif kind == 1:
            super().__init__(6, 1, 6000, "enemy2_down.wav",
                             ["enemy2.png"],
                             "enemy2_hit.png",
                             ["enemy2_down%d.png" % i for i in range(1, 5)],
                             *groups)
        else:
            super().__init__(15, 1, 15000, "enemy3_down.wav",
                             ["enemy3_n1.png", "enemy3_n2.png"],
                             "enemy3_hit.png",
                             ["enemy3_down%d.png" % i for i in range(1, 7)],
                             *groups)
        self.reset_plane()

    def reset_plane(self):
        super().reset_plane()
        x = random.randint(0, SCREEN_RECT.w - self.rect.w)
        y = random.randint(0, SCREEN_RECT.h - self.rect.h) - SCREEN_RECT.h
        self.rect.topleft = (x, y)
        self.speed = random.randint(1, self.max_speed)

    def update(self, *args):
        super().update(*args)
        if self.hp > 0:
            self.rect.y += self.speed
        if self.rect.y >= SCREEN_RECT.h:
            self.reset_plane()


class Hero(Plane):

    def __init__(self, *groups):
        """
        :param groups: 要添加到的精灵组
        """
        super().__init__(1000, 5, 0, "me_down.wav",
                         ["me%d.png" % i for i in range(1, 3)],
                         "me1.png",
                         ["me_destroy_%d.png" % i for i in range(1, 5)],
                         *groups)

        self.is_power = False
        self.bomb_count = HERO_BOMB_COUNT
        self.bullets_kind = 0
        self.bullets_group = pg.sprite.Group()
        self.rect.midbottom = HERO_DEFAULT_MID_BOTTOM
        pg.time.set_timer(HERO_FIRE_EVENT, 200)

    def reset_plane(self):
        super().reset_plane()
        self.is_power = True
        self.bomb_count = HERO_BOMB_COUNT
        self.bullets_kind = 0
        pg.event.post(pg.event.Event(HERO_DEAD_EVENT))
        pg.time.set_timer(HERO_POWER_OFF_EVENT, 3000)

    def update(self, *args):
        """
        :param args: 0 更新图像标记 1 水平移动基数 2 垂直移动基数
        """
        # 调用父类方法更新飞机图像 args要解包
        super().update(*args)
        # 如果没有传递方向参数或者飞机坠毁那么直接返回
        if len(args) != 3 or self.hp <= 0:
            return
        # 调整水平移动距离
        self.rect.x += args[1] * self.speed
        self.rect.y += args[2] * self.speed
        # 限定在窗口内移动
        self.rect.x = 0 if self.rect.x < 0 else self.rect.x
        if self.rect.right > SCREEN_RECT.right:
            self.rect.right = SCREEN_RECT.right
        self.rect.y = 0 if self.rect.y < 0 else self.rect.y
        if self.rect.bottom > SCREEN_RECT.bottom:
            self.rect.bottom = SCREEN_RECT.bottom

    def blowup(self, enemies_group):
        """
        :param enemies_group: 敌机精灵组
        :return: 累计得分
        """
        # 如过没有足够的炸弹或者敌机被摧毁那么直接返回
        if self.bomb_count <= 0 or self.hp <= 0:
            return 0
        self.bomb_count -= 1
        score = 0
        count = 0

        # 遍历敌机精灵组，将游戏窗口内的敌机引爆
        for enemy in enemies_group.sprites():
            # 判断敌机是否进入游戏窗口
            if enemy.rect.bottom > 0:
                score += enemy.value
                count += 1
                enemy.hp = 0

        print("炸毁了 %d 架敌机，得分 %d" % (count, score))
        return score

    def fire(self, display_group):
        """
        :param display_group: 要添加的显示精灵组
        """
        groups = (self.bullets_group, display_group)
        for i in range(3):
            bullet1 = Bullet(self.bullets_kind, *groups)
            y = self.rect.y - i * 15
            if self.bullets_kind ==  0:
                bullet1.rect.midbottom = (self.rect.centerx, y)
            else:
                bullet1.rect.midbottom = (self.rect.centerx - 20, y)
                bullet2 = Bullet(self.bullets_kind, *groups)
                bullet2.rect.midbottom = (self.rect.centerx + 20, y)


class Bullet(GameSprite):
    """子弹类"""
    def __init__(self, kind, *groups):
        """
        :param kind: 子弹类型
        :param groups: 要添加到的精灵组
        """
        image_name = "bullet1.png" if kind == 0 else "bullet2.png"
        super().__init__(image_name, -12, *groups)
        self.damage = 1

    def update(self, *args):
        super().update(*args)
        if self.rect.bottom < 0:
            self.kill()


class Supply(GameSprite):

    def __init__(self, kind, *groups):
        """
        :param kind: 道具类型
        :param groups: 要添加到的精灵组
        """
        image_name = "%s_supply.png" % ("bomb" if kind == 0 else "bullet")
        super().__init__(image_name, 5, *groups)
        self.kind = kind
        self.wav_name = "get_%s.wav" % ("bomb" if kind == 0 else "bullet")
        self.rect.y = SCREEN_RECT.h

    def throw_supply(self):
        self.rect.bottom = 0
        self.rect.x = random.randint(0, SCREEN_RECT.w - self.rect.w)

    def update(self, *args):
        if self.rect.h > SCREEN_RECT.h:
            return
        super().update(*args)
