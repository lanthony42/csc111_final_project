"""CSC111 Final Project

The main module for running the program.
"""
import user_interface
import ai_trainer


# Set this to True for training without visualization, which is much faster!
NON_VISUAL_TRAINING = False


if __name__ == '__main__':
    if not NON_VISUAL_TRAINING:
        # Displays menu
        menu = user_interface.UserInterface()
        menu.open_menu()
    else:
        # Trains without visualization
        trainer = ai_trainer.AITrainer()
        trainer.start_training(output_path='data/new.csv', is_visual=False)
