import game
import pygame


if __name__ == '__main__':
    g = game.Game('map.csv')
    g.run(debug=True)
    g.run(debug=False)

    pygame.display.quit()
    pygame.quit()
