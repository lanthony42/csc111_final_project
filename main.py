"""
TODO:
    - AI stuff...
"""
import pygame

import controls
import game_runner


if __name__ == '__main__':
    g = game_runner.Game('map.csv')
    print(g.run(player_controller=controls.BlinkyController, config={'debug': True}))

    pygame.display.quit()
    pygame.quit()
