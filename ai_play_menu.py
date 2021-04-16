import pygame
import pygame_menu
import game_runner
import settings
import ai_controls
import ai_neural_net
from game_constants import SCREEN_SIZE

import title

height = SCREEN_SIZE[0]
width = SCREEN_SIZE[1]

ai = 'data/test.csv'

high_score = 0

pygame.init()
surface = pygame.display.set_mode((height, width))

game = game_runner.Game('data/map.csv')

effect = pygame_menu.widgets.selection.highlight.HighlightSelection()
font = pygame_menu.font.FONT_FRANCHISE
mytheme = pygame_menu.Theme(background_color=(0, 0, 0), title_background_color=(255, 145, 0),
                            title_font_shadow=True, title_font_color=(255, 247, 0), title_font=font, widget_font=font,
                            widget_font_color=(180, 180, 180), widget_selection_effect=effect)

def find_file(file):
    global ai
    ai = file

def start_the_game():
    global ai
    score = game.run(player_controller=ai_controls.AIController,
                     neural_net=ai_neural_net.load_neural_network(ai),
                     seed= settings.seed,config={'is_debug': settings.debug_option})['score']
    if score >= title.high_score:
        title.high_score = score
        title.high_label.set_title('High Score: ' + str(title.high_score))

def back():
    title.menu.mainloop(surface)


menu = pygame_menu.Menu('AI Selection', height, width,
                        theme=mytheme)

menu.add.text_input('AI Play File: ', default='data/test.csv', onchange=find_file)
menu.add.button('Play', start_the_game)
menu.add.button('Back', back)
menu.add.button('Quit', pygame_menu.events.EXIT)

if __name__ == '__main__':
    menu.mainloop(surface)
