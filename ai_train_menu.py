import pygame
import pygame_menu
import game_runner
import settings
import ai_trainer
from game_constants import SCREEN_SIZE

import title

height = SCREEN_SIZE[0]
width = SCREEN_SIZE[1]

ai = 'data/test.csv'
ai_train = 'data/test_train.csv'
runs = 1
visual_option = False

pygame.init()
surface = pygame.display.set_mode((height, width))

game = game_runner.Game('data/map.csv')

def find_play_file(file):
    global ai
    ai = file

def find_file(file):
    global ai_train
    ai_train = file

def run():
    pass

def visual(value, option):
    global visual_option
    visual_option = option

def start_the_game():
    trainer = ai_trainer.AITrainer()
    trainer.start_training(graph_path=ai, is_visual=visual_option)

def back():
    title.menu.mainloop(surface)


menu = pygame_menu.Menu(width, height, 'AI Selection',
                        theme=pygame_menu.themes.THEME_DARK)

menu.add.text_input('AI Play File: ', default='data/test.csv', onchange=find_play_file)
menu.add.text_input('AI Train File: ', default='data/test_train.csv', onchange=find_file)
menu.add.text_input('Number of Runs (Int): ', default='1', onchange=run)
menu.add.selector('Visual: ', [('OFF', False), ('ON', True)], onchange=visual)
menu.add.button('Play', start_the_game)
menu.add.button('Back', back)
menu.add.button('Quit', pygame_menu.events.EXIT)

if __name__ == '__main__':
    menu.mainloop(surface)
