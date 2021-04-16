import title
import pygame
import pygame_menu
from game_constants import SCREEN_SIZE

height = SCREEN_SIZE[0]
width = SCREEN_SIZE[1]

seed = 45
debug_option = False

pygame.init()
surface = pygame.display.set_mode((height, width))

effect = pygame_menu.widgets.selection.highlight.HighlightSelection()
font = pygame_menu.font.FONT_FRANCHISE
mytheme = pygame_menu.Theme(background_color=(0, 0, 0), title_background_color=(255, 145, 0),
                            title_font_shadow=True, title_font_color=(255, 247, 0), title_font=font, widget_font=font,
                            widget_font_color=(180, 180, 180), widget_selection_effect=effect)


def set_seed(set):
    global seed
    if set == '':
        seed = 45
    else:
        seed = int(set)
def debug(value, option):
    global debug_option
    debug_option = option

def back():
    title.menu.mainloop(surface)

menu = pygame_menu.Menu('Settings', height, width,
                        theme=mytheme)

menu.add.text_input('Set Seed (Int):', default='111', onchange=set_seed)
menu.add.selector('Debug: ', [('OFF', False), ('ON', True)], onchange=debug)
menu.add.button('Back', back)
menu.add.button('Quit', pygame_menu.events.EXIT)

if __name__ == '__main__':
    menu.mainloop(surface)

