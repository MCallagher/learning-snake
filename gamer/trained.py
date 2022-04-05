
import pickle
from   pathlib import Path
import random as r
from   typing import Union

from   snake.game import Position, SnakeStatus
from   snake.player import TrainedPlayer


class ProximityPlayer(TrainedPlayer):
    """
    Define a player that bases its moves on elements nearby. It is trained with
    Q-learning with alpha = 1.
    """
    MAP_DEATH = 1
    """Value that indicates a position that causes death"""
    MAP_NONE = 0
    """Value that indicates a non-dangerous position"""
    REWARD_DEATH = -1
    """The reward associated to death"""
    REWARD_NONE = 0
    """The reward associated to not-death and not-eating"""
    REWARD_APPLE = 100
    """The reward associated to eating"""

    def __init__(self, radius:int, gamma:float) -> 'ProximityPlayer':
        """
        Create a new proximity player.

        Params
        - radius: the distance at which the player can see danger and apples
        - gamma: the discount factor

        Return
        - the new player
        """
        self.radius = radius
        self.gamma = gamma
        self.exp_reward:dict[tuple[int], dict[int,int]] = {}

    def compute_move(self, status:SnakeStatus) -> int:
        """
        Compute the next move, given the current status of the game.

        Params
        - status: the current status of the game

        Return
        - the direction of the movement
        """
        # Get the map
        map = self._retrieve_proximity_map(status)
        if map not in self.exp_reward:
            self._add_map(map)

        # Compute the max reward and corresponding directions
        max_reward = max([self.exp_reward[map][dir] for dir in Position.DIRECTIONS])
        dirs = [dir for dir in Position.DIRECTIONS if self.exp_reward[map][dir] == max_reward]

        return r.choice(dirs)

    def train(self, history:list[SnakeStatus]) -> None:
        """
        Train the player on the specified game.
        
        Params
        - history: the history of a game, to be used to train
        """
        samples = self._history_to_samples(history)
        for i in range(len(samples) - 1, -1, -1):
            curr_map, next_map, move, reward = samples[i]

            # Add maps to exp_reward
            for map in [curr_map, next_map]:
                if map not in self.exp_reward:
                    self._add_map(map)

            # Compute next max reward
            next_max_reward = max([self.exp_reward[next_map][dir] for dir in Position.DIRECTIONS])

            # Update reward
            self.exp_reward[curr_map][move] = int(reward + self.gamma * next_max_reward)

    def save_model(self, filename:Union[str, Path]) -> None:
        """
        Save to file the model that defines how the choices of the player are
        computed.

        Params
        - filename: the name of the file where the model will be saved
        """
        if isinstance(filename, str):
            filename = Path(filename)
        with open(filename, "wb") as f:
            f.write(pickle.dumps(self.exp_reward))

    def load_model(self, filename:Union[str, Path]) -> None:
        """
        Load from file the model that defines how the choices of the player are
        computed.

        Params
        - filename: the name of the file where the model is saved
        """
        if isinstance(filename, str):
            filename = Path(filename)
        with open(filename, "rb") as f:
            self.exp_reward = pickle.loads(f.read())

    def _add_map(self, map:tuple[int]) -> None:
        """
        Add a map to the expected reward dictionary, assignign default values to
        all directions.

        Params
        - map: the map to add to the reward dictionary
        """
        self.exp_reward[map] = {}
        for dir in Position.DIRECTIONS:
            self.exp_reward[map][dir] = ProximityPlayer.REWARD_NONE

    def _history_to_samples(self, history:list[SnakeStatus]) -> list[tuple[tuple[int],int,int]]:
        """
        Convert a game history into a sequence of samples. Each sample contains
        the linearized version of the map, the direction of the move and the
        reward associated with that move.

        Params
        - history: the history in the game as a sequence of statuses

        Return
        - the list of samples
        """
        samples = []
        for i in range(len(history) - 1):
            curr_status = history[i]
            next_status = history[i + 1]

            proximity_map = self._retrieve_proximity_map(curr_status)
            next_proximity_map = self._retrieve_proximity_map(next_status)
            move = self._retrieve_movement(curr_status, next_status)
            reward = self._retrieve_reward(curr_status, next_status)

            samples.append((proximity_map, next_proximity_map, move, reward))

        return samples

    def _retrieve_proximity_map(self, status:SnakeStatus) -> tuple[int]:
        """
        Compute an encoding of the dangers nearby and the position of the apple.

        Params
        - status: the status containing containing snake and apple positions

        Return
        - the information as a monodimensional encoding
        """
        proximity_map = []

        # Danger in proximity
        for dy in range(-self.radius, self.radius + 1):
            for dx in range(-self.radius, self.radius + 1):
                pos = Position(status.snake[-1].x + dx, status.snake[-1].y + dy)
                if pos.is_out_of_bounds(status.bounds) or pos in status.snake:
                    proximity_map.append(ProximityPlayer.MAP_DEATH)
                else:
                    proximity_map.append(ProximityPlayer.MAP_NONE)

        # Apple position
        a_dx = status.apple.x - status.snake[-1].x
        if a_dx > self.radius:
            a_dx = self.radius + 1
        elif a_dx < - self.radius:
            a_dx = - self.radius - 1
        a_dy = status.apple.y - status.snake[-1].y
        if a_dy > self.radius:
            a_dy = self.radius + 1
        elif a_dy < - self.radius:
            a_dy = - self.radius - 1
        proximity_map.append(a_dx)
        proximity_map.append(a_dy)

        return tuple(proximity_map)

    def _retrieve_movement(self, curr_status:SnakeStatus, next_status:SnakeStatus) -> int:
        """
        Discover the move that brought from the current status to the next one.

        Params
        - curr_status: the current status
        - next_status: the next status

        Return
        - the move that brought from the current status to the next one

        Raise
        - Exception: if the next status cannot be reached with a single move
            from the current one
        """
        curr_head = curr_status.snake[-1]
        next_head = next_status.snake[-1]
        if curr_head.x > next_head.x:
            return Position.LEFT
        if curr_head.y < next_head.y:
            return Position.UP
        if curr_head.x < next_head.x:
            return Position.RIGHT
        if curr_head.y > next_head.y:
            return Position.DOWN
        raise Exception("Non-consecutive statuses")

    def _retrieve_reward(self, curr_status:SnakeStatus, next_status:SnakeStatus) -> int:
        """
        Compute the reward gained by moving from the current status to the next
        one.

        Params
        - curr_status: the current status
        - next_status: the next status

        Return
        - the reward obtained for moving from the current status to the next one
        """
        if not next_status.alive:
            return ProximityPlayer.REWARD_DEATH
        if curr_status.score < next_status.score:
            return ProximityPlayer.REWARD_APPLE
        return ProximityPlayer.REWARD_NONE
