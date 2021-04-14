"""
TODO:
    - Config for runner
"""
import pygame

import controls
import game_runner


if __name__ == '__main__':
    g = game_runner.Game('map.csv')
    print(g.run(debug=True))

    pygame.display.quit()
    pygame.quit()
