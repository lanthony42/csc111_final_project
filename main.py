"""
TODO:
    - AI Graph class
    - Training method
"""
import pygame

import ai_trainer
import game_runner


def test_game():
    game = game_runner.Game('data/map.csv')
    for _ in range(5):
        outcome = game.run(config={'is_visual': True})
        print(outcome)

        if outcome['force_quit']:
            break

    pygame.display.quit()
    pygame.quit()


def test_train():
    trainer = ai_trainer.AITrainer(1)
    trainer.start_training(True)


if __name__ == '__main__':
    test_game()
    # test_train()
