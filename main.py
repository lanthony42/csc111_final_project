"""
TODO:
    - Fix seeding
    - Cull bad branches
"""
from time import time
import pygame

import ai_constants as const
import ai_controls
import ai_neural_net
import ai_trainer
import game_controls
import game_runner

import title


def test_game():
    game = game_runner.Game('data/map.csv')
    for _ in range(20):
        outcome = game.run(config={'has_ghosts': True, 'has_boosts': True, 'is_visual': True})
        print(outcome)

        if outcome['force_quit']:
            break

    pygame.display.quit()
    pygame.quit()


def test_ai():
    game = game_runner.Game('data/map.csv')
    seed = 0
    while True:
        seed += 1
        net = ai_neural_net.load_neural_network('data/test.csv')
        outcome = game.run(player_controller=ai_controls.AIController, neural_net=net,
                           seed=seed, config={'is_visual': False})
        print(outcome)

        if outcome['force_quit'] or outcome['game_win']:
            break

    print(seed)
    pygame.display.quit()
    pygame.quit()


def test_train():
    trainer = ai_trainer.AITrainer()
    trainer.start_training(input_path='data/test.csv', output_path='data/new.csv',
                           starting_stage=const.BOOST_STAGE, is_visual=False)


if __name__ == '__main__':
    t = time()
    # test_game()
    test_ai()
    # test_train()
    # title.menu.mainloop(title.surface)
    print(time() - t)
