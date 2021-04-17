from dataclasses import dataclass
from typing import Optional
import pygame
import pygame_menu

import ai_constants as ai_const
import ai_controls
import ai_neural_net
import ai_trainer
import game_constants as g_const
import game_runner


@dataclass
class UserSettings:
    high_score: int
    seed: int
    is_debug: bool


class UserInterface:
    screen: pygame.Surface
    game: game_runner.Game
    trainer: ai_trainer.AITrainer
    theme: pygame_menu.Theme
    main_menu: Optional[pygame_menu.Menu]
    sub_menu: Optional[pygame_menu.Menu]
    settings: UserSettings

    def __init__(self) -> None:
        self.settings = UserSettings(0, ai_const.SIMULATION_SEED, False)
        self.game = game_runner.Game('data/map.csv')
        self.trainer = ai_trainer.AITrainer()

        pygame.init()
        self.screen = pygame.display.set_mode(g_const.SCREEN_SIZE.tuple())

        effect = pygame_menu.widgets.selection.highlight.HighlightSelection()
        font = pygame_menu.font.FONT_FRANCHISE
        self.theme = pygame_menu.Theme(background_color=(0, 0, 0),
                                       title_background_color=(255, 145, 0),
                                       title_font_shadow=True, title_font_color=(255, 247, 0),
                                       title_font=font, widget_font=font,
                                       widget_font_color=(180, 180, 180),
                                       widget_selection_effect=effect)
        self.main_menu = None
        self.sub_menu = None

    def open_menu(self) -> None:
        self.main_menu = pygame_menu.Menu('PAC-MAN', g_const.SCREEN_SIZE[0], g_const.SCREEN_SIZE[1],
                                          theme=self.theme)

        self.main_menu.add.image('data/pacman.jpg')
        self.main_menu.add.label('High Score: ' + str(self.settings.high_score), label_id='score')

        self.main_menu.add.button('Play', self.play_game)
        self.main_menu.add.button('AI Play', self.ai_play_menu)
        self.main_menu.add.button('AI Train', self.ai_train_menu)
        self.main_menu.add.button('Settings', self.settings_menu)
        self.main_menu.add.button('Quit', pygame_menu.events.EXIT)

        self.main_menu.mainloop(self.screen)

    def play_game(self) -> None:
        outcome = self.game.run(config={'is_debug': self.settings.is_debug})

        if outcome['score'] > self.settings.high_score:
            self.settings.high_score = outcome['score']

        self.open_menu()

    def ai_play_menu(self) -> None:
        self.sub_menu = pygame_menu.Menu('AI Selection', g_const.SCREEN_SIZE[0],
                                         g_const.SCREEN_SIZE[1], theme=self.theme)

        self.sub_menu.add.text_input('AI Play File: ', default='data/test.csv', textinput_id='path')
        self.sub_menu.add.button('Play', self.ai_play_game)
        self.sub_menu.add.button('Back', self.open_menu)
        self.sub_menu.add.button('Quit', pygame_menu.events.EXIT)

        self.sub_menu.mainloop(self.screen)

    def ai_play_game(self) -> None:
        path = self.sub_menu.get_input_data()['path']
        outcome = self.game.run(player_controller=ai_controls.AIController,
                                neural_net=ai_neural_net.load_neural_network(path),
                                seed=self.settings.seed,
                                config={'is_debug': self.settings.is_debug})

        if outcome['score'] > self.settings.high_score:
            self.settings.high_score = outcome['score']

    def ai_train_menu(self) -> None:
        self.sub_menu = pygame_menu.Menu('AI Selection', g_const.SCREEN_SIZE[0],
                                         g_const.SCREEN_SIZE[1], theme=self.theme)

        self.sub_menu.add.text_input('AI Play File: ', default='data/test.csv', textinput_id='in')
        self.sub_menu.add.text_input('AI Train File: ', default='data/new.csv', textinput_id='out')
        self.sub_menu.add.button('Play', self.ai_train_game)
        self.sub_menu.add.button('Back', self.open_menu)
        self.sub_menu.add.button('Quit', pygame_menu.events.EXIT)

        self.sub_menu.mainloop(self.screen)

    def ai_train_game(self) -> None:
        self.trainer.start_training(input_path=self.sub_menu.get_input_data()['in'],
                                    output_path=self.sub_menu.get_input_data()['out'],
                                    is_visual=True)

    def settings_menu(self) -> None:
        self.sub_menu = pygame_menu.Menu('Settings', g_const.SCREEN_SIZE[0], g_const.SCREEN_SIZE[1],
                                         theme=self.theme)

        self.sub_menu.add.text_input('Set Seed (Int):', default=str(self.settings.seed),
                                     onchange=self.set_seed)
        self.sub_menu.add.selector('Debug: ', [('OFF', False), ('ON', True)],
                                   onchange=self.set_debug)
        self.sub_menu.add.button('Back', self.open_menu)
        self.sub_menu.add.button('Quit', pygame_menu.events.EXIT)

        self.sub_menu.mainloop(self.screen)

    def set_seed(self, seed: str) -> None:
        if seed.isdigit():
            self.settings.seed = int(seed)
        else:
            self.settings.seed = ai_const.SIMULATION_SEED

    def set_debug(self, *args) -> None:
        self.settings.is_debug = bool(args[1])


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['dataclasses', 'pygame', 'pygame_menu', 'ai_constants', 'ai_controls',
                          'ai_neural_net', 'ai_trainer', 'game_constants', 'game_runner'],
        'max-line-length': 100,
        'disable': ['E1136', 'E1101']
    })

    import python_ta.contracts
    python_ta.contracts.DEBUG_CONTRACTS = True
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()
