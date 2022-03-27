
import random as r

from snake.player import Player
from snake.game import Position, SnakeStatus

class ShortPathPlayer(Player):
    """
    Define a player that prioritize short paths to apple.
    """

    def compute_move(self, status:SnakeStatus) -> int:
        """
        Compute the next move, given the current status of the game. Prioritize
        non-losing moves and then moves that bring the snake closer to the
        apple. 

        Params
        - status: the current status of the game

        Return
        - the direction of the movement
        """
        cost = []
        for dir in (Position.LEFT, Position.UP, Position.RIGHT, Position.DOWN):
            snake_head = status.snake[-1]
            next_pos = snake_head.move(dir)
            if next_pos.is_out_of_bounds(status.bounds) or next_pos in status.snake:
                cost.append((dir, 1))
            else:
                if next_pos.distance(status.apple) >= snake_head.distance(status.apple):
                    cost.append((dir, 0))
                else:
                    cost.append((dir, -1))
        r.shuffle(cost)
        cost.sort(key=lambda x:x[1])
        return cost[0][0]

class BoringPathPlayer(Player):
    """
    Define a player that follows a path that cover all the board.
    """
    def __init__(self, width, height) -> None:
        self.idx = -1
        self.path = []

        if width % 2 == 0:
            for i in range(width):
                correction = 0 if i == 0 or i == width - 1 else -1
                if i % 2 == 0:
                    self.path += self.rep(Position.UP, height - 1 + correction)
                else:
                    self.path += self.rep(Position.DOWN, height - 1 + correction)
                if i != width - 1:
                    self.path += self.rep(Position.RIGHT, 1)
            self.path += self.rep(Position.LEFT, width - 1)

        elif height % 2 == 0:
            for i in range(height):
                correction = 0 if i == 0 or i == height - 1 else -1
                if i % 2 == 0:
                    self.path += self.rep(Position.RIGHT, width - 1 + correction)
                else:
                    self.path += self.rep(Position.LEFT, width - 1 + correction)
                if i != height - 1:
                    self.path += self.rep(Position.UP, 1)
            self.path += self.rep(Position.DOWN, width - 1)

        else:
            raise Exception("Not implemented for odd width and height")

    def rep(self, dir, k):
        return [dir for _ in range(k)]

    def compute_move(self, status:SnakeStatus) -> int:
        """
        Compute the next move, given the current status of the game. Prioritize
        non-losing moves and then moves that bring the snake closer to the
        apple. 

        Params
        - status: the current status of the game

        Return
        - the direction of the movement
        """
        if self.idx == -1:
            if status.snake[-1].x > 0:
                return Position.LEFT
            if status.snake[-1].y > 0:
                return Position.DOWN
        self.idx = (self.idx + 1) % len(self.path)
        return self.path[self.idx]

