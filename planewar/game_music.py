
import os
import pygame as pg


class MusicPlayer:
    res_path = "resources/sound/"

    def __init__(self, music_file):
        pg.mixer.music.load(self.res_path + music_file)
        pg.mixer.music.set_volume(0.2)
        # define the dic of music
        self.sound_dict = {}
        # get the list of music
        files = os.listdir(self.res_path)
        # iterate over the list of files
        for file_name in files:
            if file_name == music_file:
                continue
            sound = pg.mixer.Sound(self.res_path + file_name)
            self.sound_dict[file_name] = sound

    #   播放音乐 time循环次数 -1 代表一直循环
    @staticmethod
    def play_music(time):
        pg.mixer.music.play(time)

    #   暂停/继续
    @staticmethod
    def pause_music(is_pause):
        if is_pause:
            pg.mixer.music.pause()
        else:
            pg.mixer.music.unpause()

    def play_sound(self, wav_name):
        """
        :param wav_name:音效文件名
        :return:
        """
        self.sound_dict[wav_name].play()



if __name__ == '__main__':
    media = MusicPlayer("bullet.wav")
    print(media.reslis)
