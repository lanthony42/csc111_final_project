"""
TODO:
    - AI Graph class
    - Training method
"""
import pygame

import ai_constants as const
import ai_controls
import ai_neural_net
import ai_trainer
import game_runner


def test_game():
    game = game_runner.Game('data/map.csv')
    for _ in range(20):
        outcome = game.run(config={'is_visual': False})
        print(outcome)

        if outcome['force_quit']:
            break

    pygame.display.quit()
    pygame.quit()


def test_ai():
    game = game_runner.Game('data/map.csv')
    for _ in range(20):
        outcome = game.run(player_controller=ai_controls.AIController,
                           neural_net=ai_neural_net.NeuralNetGraph(const.INPUT_SIZE,
                                                                   const.OUTPUT_SIZE),
                           config={'is_visual': False})
        print(outcome)

        if outcome['force_quit']:
            break

    pygame.display.quit()
    pygame.quit()


def test_train():
    trainer = ai_trainer.AITrainer(1)
    trainer.start_training(True)


if __name__ == '__main__':
    # test_game()
    test_ai()
    # test_train()
