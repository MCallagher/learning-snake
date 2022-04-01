

from snake.game import Snake, SnakeStatus
from snake.player import Player

def play_game(game:Snake, player:Player) -> list[SnakeStatus]:
    """
    Play a full game of snake for the given player.

    Params
    - game: the snake game
    - player: the player that plays snake

    Return
    - the list of statuses of the whole game
    """
    history = []
    while not game.is_game_over():
        status = game.get_status()
        direction = player.compute_move(status)
        game.play(direction)
        history.append(status)
    return history
