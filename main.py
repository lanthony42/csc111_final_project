import pygame
import game_runner


if __name__ == '__main__':
    g = game_runner.Game('map.csv')
    print(g.run(debug=False))

    pygame.display.quit()
    pygame.quit()
