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
ai_train = 'data/new.csv'
runs = 1

pygame.init()
surface = pygame.display.set_mode((height, width))

game = game_runner.Game('data/map.csv')

effect = pygame_menu.widgets.selection.highlight.HighlightSelection()
font = pygame_menu.font.FONT_FRANCHISE
mytheme = pygame_menu.Theme(background_color=(0, 0, 0), title_background_color=(255, 145, 0),
                            title_font_shadow=True, title_font_color=(255, 247, 0), title_font=font, widget_font=font,
                            widget_font_color=(180, 180, 180), widget_selection_effect=effect)

def find_play_file(file):
    global ai
    ai = file

def find_file(file):
    global ai_train
    ai_train = file

def start_the_game():
    trainer = ai_trainer.AITrainer()
    trainer.start_training(input_path=ai, output_path=ai_train, is_visual=True)

def back():
    title.menu.mainloop(surface)


menu = pygame_menu.Menu('AI Selection', height, width,
                        theme=mytheme)

menu.add.text_input('AI Play File: ', default='data/test.csv', onchange=find_play_file)
menu.add.text_input('AI Train File: ', default='data/new.csv', onchange=find_file)
menu.add.button('Play', start_the_game)
menu.add.button('Back', back)
menu.add.button('Quit', pygame_menu.events.EXIT)

if __name__ == '__main__':
    menu.mainloop(surface)
