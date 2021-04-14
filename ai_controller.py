import pygame

import controls


class AIController(controls.Controller):
    def control(self, grid: list[list[int]]) -> None:
        pass

    def draw_debug(self, screen: pygame.Surface) -> None:
        pass


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['pygame', 'controls'],
        'max-line-length': 100,
        'disable': ['E1136']
    })

    import python_ta.contracts
    python_ta.contracts.DEBUG_CONTRACTS = True
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()
