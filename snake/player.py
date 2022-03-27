
from snake.game import SnakeStatus

class Player(object):
    """
    Define the interface for a snake player.
    """

    def compute_move(self, status:SnakeStatus) -> int:
        """
        Compute the next move, given the current status of the game.

        Params
        - status: the current status of the game

        Return
        - the direction of the movement (must be in Position.LEFT, Position.UP,
            Position.RIGHT, Position.DOWN)
        
        Raise
        - NotImplementedError: if the method is not overridden by a subclass
        """
        raise NotImplementedError("This method must be override by a subclass")
