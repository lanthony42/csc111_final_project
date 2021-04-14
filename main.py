"""
TODO:
    - Config ghosts, boosts
    - AI Controller Input Nodes
    - AI Graph class
    - AI Controller Output Nodes
"""
import pygame

import controls
import game_runner


if __name__ == '__main__':
    g = game_runner.Game('map.csv')
    for _ in range(100):
        print(g.run(player_controller=controls.BlinkyController, config={'visual': True}))

    pygame.display.quit()
    pygame.quit()
