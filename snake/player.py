from pathlib import Path
from typing import Union

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

class TrainedPlayer(Player):
    """
    Define the interface for a snake player that requires training.
    """

    def train(self, history:list[SnakeStatus]) -> None:
        """
        Train the player on the specified game.
        
        Params
        - history: the history of a game, to be used to train

        Raise
        - NotImplementedError: if the method is not overridden by a subclass
        """
        raise NotImplementedError("This method must be override by a subclass")

    def save_model(self, filename:Union[str, Path]) -> None:
        """
        Save to file the model that defines how the choices of the player are
        computed.

        Params
        - filename: the name of the file where the model will be saved

        Raise
        - NotImplementedError: if the method is not overridden by a subclass
        """
        raise NotImplementedError("This method must be override by a subclass")

    def load_model(self, filename:Union[str, Path]) -> None:
        """
        Load from file the model that defines how the choices of the player are
        computed.

        Params
        - filename: the name of the file where the model is saved

        Raise
        - NotImplementedError: if the method is not overridden by a subclass
        """
        raise NotImplementedError("This method must be override by a subclass")
