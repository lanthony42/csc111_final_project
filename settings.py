import title
import pygame
import pygame_menu
from game_constants import SCREEN_SIZE

height = SCREEN_SIZE[0]
width = SCREEN_SIZE[1]

seed = 111
debug_option = False

pygame.init()
surface = pygame.display.set_mode((height, width))


def set_seed(set):
    global seed
    seed = int(set)

def debug(value, option):
    global debug_option
    debug_option = option

def back():
    title.menu.mainloop(surface)

menu = pygame_menu.Menu(width, height, 'Settings',
                        theme=pygame_menu.themes.THEME_DARK)

menu.add.text_input('Set Seed (Int):', default='111', onchange=set_seed)
menu.add.selector('Debug: ', [('OFF', False), ('ON', True)], onchange=debug)
menu.add.button('Back', back)
menu.add.button('Quit', pygame_menu.events.EXIT)

if __name__ == '__main__':
    menu.mainloop(surface)

