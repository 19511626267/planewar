
from game_items import *


class HudPanel:
    """指示器面板类"""
    margin = 10  # 精灵之间的间距
    white = (255, 255, 255)  # 白色
    gray = (64, 64, 64)  # 灰色

    reward_score = 100000  # 关卡奖励分数
    level2_score = 10000  # 关卡级别2的预设分值
    level3_score = 50000  # 关卡级别3的预设分值

    record_filename = "record.txt"

    def __init__(self, display_group):
        """
        构造方法
        :param display_group:面板中的精灵要被添加到的显示精灵组
        """
        # 游戏属性
        self.score = 0  # 游戏得分
        self.lives_count = 3  # 生命数
        self.level = 1  # 关卡级别
        self.best_score = 0  # 最好成绩
        self.load_best_score()
        # 创建图像精灵
        # 状态精灵
        self.status_sprite = StatusButton(["pause.png", "resume.png"], display_group)
        self.status_sprite.rect.topleft = (self.margin, self.margin)
        # 炸弹精灵
        self.bomb_sprite = GameSprite("bomb.png", 0, display_group)
        self.bomb_sprite.rect.x = self.margin
        self.bomb_sprite.rect.bottom = SCREEN_RECT.bottom - self.margin
        # 生命计数精灵
        self.lives_sprite = GameSprite("life.png", 0, display_group)
        self.lives_sprite.rect.right = SCREEN_RECT.right - self.margin
        self.lives_sprite.rect.bottom = SCREEN_RECT.bottom - self.margin

        # 创建标签精灵
        # 分数标签
        self.score_label = Label("%d" % self.score, 32, self.gray, display_group)
        self.score_label.rect.midleft = (self.status_sprite.rect.right + self.margin, self.status_sprite.rect.centery)
        # 炸弹标签
        self.bomb_label = Label("X 3", 32, self.gray, display_group)
        self.bomb_label.rect.midleft = (self.bomb_sprite.rect.right + self.margin, self.bomb_sprite.rect.centery)
        # 生命计数标签
        self.lives_label = Label("X %d" % self.lives_count, 32, self.gray, display_group)
        self.lives_label.rect.midright = (SCREEN_RECT.right - self.margin, self.bomb_label.rect.centery)
        # 调整生命计数精灵位置
        self.lives_sprite.rect.right = self.lives_label.rect.left - self.margin
        # 最好成绩标签
        self.best_label = Label("Best: %d" % self.best_score, 36, self.white)
        # self.best_label.rect.center = SCREEN_RECT.center
        # 状态标签
        self.status_label = Label("Game Over!", 48, self.white)
        # self.status_label.rect.midbottom = (self.best_label.rect.centerx, self.best_label.rect.y - 2 * self.margin)
        # 提示标签
        self.tip_label = Label("Press space to play again.", 22, self.white)
        # self.tip_label.rect.midtop = (self.best_label.rect.centerx, self.best_label.rect.bottom + 8 * self.margin)

    def show_bomb(self, count):
        """显示炸弹数量
        :param count :要显示的炸弹数量
        """
        # 设置炸弹标签文字
        self.bomb_label.set_text("X %d" % count)
        # 设置炸弹标签位置
        self.bomb_label.rect.midleft = (self.bomb_sprite.rect.right + self.margin, self.bomb_sprite.rect.centery)

    def show_lives(self):
        """显示生命计数"""
        # 设置生命计数标签文字
        self.lives_label.set_text("X %d" % self.lives_count)
        # 设置生命计数标签位置
        self.lives_label.rect.midright = (SCREEN_RECT.right - self.margin, self.bomb_label.rect.centery)
        # 调整生命计数精灵位置
        self.lives_sprite.rect.right = self.lives_label.rect.left - self.margin

    def increase_score(self, enemy_score):
        """增加游戏得分
        :param enemy_score:摧毁敌机的分值
        :return: 增加enemy_score后，关卡级别是否提升
        """
        # 游戏得分
        score = self.score + enemy_score
        # 判断是否奖励生命
        if score // self.reward_score != self.score // self.reward_score:
            self.lives_count += 1
            self.show_lives()
        self.score = score
        # 最好成绩
        self.best_score = score if score > self.best_score else self.best_score
        # 关卡级别
        if score < self.level2_score:
            level = 1
        elif score < self.level3_score:
            level = 2
        else:
            level = 3
        is_upgrade = level != self.level
        self.level = level
        # 修改得分标签内容和位置
        self.score_label.set_text("%d" % self.score)
        self.score_label.rect.midleft = (self.status_sprite.rect.right + self.margin, self.status_sprite.rect.centery)
        return is_upgrade

    def save_best_score(self):
        """将最好成绩写入record.txt"""
        file = open(self.record_filename, "w")
        file.write("%d" % self.best_score)
        file.close()

    def load_best_score(self):
        """从record.txt加载最好成绩"""
        try:
            file = open(self.record_filename)
            txt = file.readline()
            file.close()
            self.best_score = int(txt)
        except (FileNotFoundError, ValueError):
            print("文件不存在或类型转换错误")

    def panel_pause(self, is_game_over, display_group):
        """
        面板暂停
        :param is_game_over:是否因为游戏结束需要停止
        :param display_group: 显示精灵组
        """
        # 判断是否已经添加了精灵，结果是直接返回
        if display_group.has(self.status_label, self.tip_label, self.best_label):
            return
        # 根据是否结束游戏决定要显示的文字
        text = "Game Over!" if is_game_over else "Game Paused!"
        tip = "Press space to"
        tip += "play again." if is_game_over else "continue."
        # 设置标签文字
        self.best_label.set_text("Best: %d" % self.best_score)
        self.status_label.set_text(text)
        self.tip_label.set_text(tip)
        # 设置标签位置
        self.best_label.rect.center = SCREEN_RECT.center
        best_rect = self.best_label.rect
        self.status_label.rect.midbottom = (best_rect.centerx, best_rect.y - 2 * self.margin)
        self.tip_label.rect.midtop = (best_rect.centerx, best_rect.bottom + 8 * self.margin)
        # 添加到精灵组
        display_group.add(self.best_label, self.status_label, self.tip_label)
        # 切换精灵的状态
        self.status_sprite.switch_status(True)

    def panel_resume(self, display_group):
        """
        面板恢复
        :param display_group:显示精灵组
        """
        # 从精灵组移除3个标签精灵
        display_group.remove(self.status_label, self.tip_label, self.best_label)
        # 切换精灵的状态
        self.status_sprite.switch_status(False)

    def reset_panel(self):
        self.score = 0
        self.lives_count = 3
        self.increase_score(0)
        self.show_bomb(3)
        self.show_lives()
