import game
import pygame


if __name__ == '__main__':
    g = game.Game('map.csv')
    print(g.run(lives=100, debug=True))

    pygame.display.quit()
    pygame.quit()
