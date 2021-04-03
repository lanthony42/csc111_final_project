import game
import pygame


if __name__ == '__main__':
    g = game.Game('map.csv')
    print(g.run(debug=False))

    pygame.display.quit()
    pygame.quit()
