
import random as r
from   typing import Union

class Position(object):
    """
    Describe a bidimensional integer position. x-coordinate increases left to
    right, y-coordinate increases bottom to top (cartesian plane).
    """

    LEFT = 0
    """Indicate the left direction."""
    UP = 1
    """Indicate the upward direction"""
    RIGHT = 2
    """Indicate the right direction"""
    DOWN = 3
    """Indicate the downward direction"""

    def __init__(self, x:int, y:int) -> 'Position':
        """
        Create a new position, based on the coordinates.

        Params
        - x: the horizontal coordinate
        - y: the vertical coordinate

        Return
        - the new position
        """
        self.x = x
        self.y = y

    def __eq__(self, other:'Position') -> bool:
        """
        Check if the positions are the same.

        Params
        - other: the other position to compare

        Return
        - true, if the positions are the same, false otherwise
        """
        return self.x == other.x and self.y == other.y

    def __iter__(self) -> int:
        """
        Iterate over the two coordinates.
        
        Return
        - the two coordinates, one after the other
        """
        yield self.x
        yield self.y

    def __str__(self) -> str:
        """
        Return the string representation of the position.

        Return
        - the string representation of the position
        """
        return str(tuple(self))

    def move(self, dir:int) -> 'Position':
        """
        Compute the postition reached starting from the current position and 
        moving in the specified direction. Valid directions are the ones
        specified in the static variables LEFT, UP, RIGHT, DOWN.

        Params
        - dir: the direction of the movement

        Return
        - the resulting position

        Raise
        - Exception: if the direction is not valid
        """
        # Check if the position is valid
        if dir not in (Position.LEFT, Position.UP, Position.RIGHT, Position.DOWN):
            raise Exception(f"{dir} is not a valid move")

        # Compute movement
        dx = 1 if dir == Position.RIGHT else (-1 if dir == Position.LEFT else 0)
        dy = 1 if dir == Position.UP    else (-1 if dir == Position.DOWN else 0)

        # Compute and return the next position
        return Position(self.x + dx, self.y + dy)

    def is_out_of_bounds(self, bounds:tuple[int,int,int,int]) -> bool:
        """
        Check if the position is out of the specified bounds. The borders are
        considered valid positions.

        Params
        - bounds: the bounds of direction left, up, right, down

        Return
        - true, if the position is outside the specified bounds, false otherwise
        """
        left, top, right, bottom = bounds
        return self.x < left or self.x > right or self.y < bottom or self.y > top

    def random_position(bounds:tuple[int,int,int,int], taboo:list['Position']=[], rand_tries:int=5):
        """
        Build a position randomly, within the specified bounds (borders
        included) and not in the taboo positions.

        Params
        - bounds: the bounds for the new position
        - taboo: the positions that cannot be accepted for the new position
        - rand_tries: the number random generations without the enumeration of
            all valid positions (faster when few taboo, very slow with few free
            cells)
        
        Return
        - the randomly generated random position

        Raise
        - Exception: if there are no free positions
        """
        left, top, right, bottom = bounds

        # Try randomly a few times (works if most of cells are free)
        for i in range(rand_tries):
            pos = Position(r.randint(left, right), r.randint(bottom, top))
            if pos not in taboo:
                return pos

        # Enumerate all free position
        positions = []
        for x in range(left, right + 1):
            for y in range(bottom, top + 1):
                curr_pos = Position(x, y)
                if curr_pos not in taboo:
                    positions.append(curr_pos)

        # Raise exception if no free position is left
        if len(positions) == 0:
            raise Exception("No free positions left")

        # Return a random position from the free ones
        return r.choice(positions)


class SnakeStatus(object):
    def __init__(self, bounds:tuple[int,int,int,int], snake:list[Position], apple:Position,
            score:int, alive:bool, won:bool) -> 'SnakeStatus':
        """
        Create an object that represents the status of the snake game.

        Params
        - bounds: the bounds of the board (left, top, right, bottom)
        - snake: the snake position
        - apple: the apple position
        - score: the score
        - alive: the flag which indicates if the snake is alive
        - won: the flag that indicates if the player has won

        Return
        - The new status
        """
        self.bounds = bounds
        self.snake = snake
        self.apple = apple
        self.score = score
        self.alive = alive
        self.won = won

    def __iter__(self) -> Union[tuple[int,int,int,int], list[Position],
            Position, int, bool, bool]:
        """
        Iterate over the elemements of the status, in order: bounds (left, top,
            right, bottom), snake position (tail to head), apple position,
            score, is alive flag, has won flag.

        Return
        - An element of the status
        """
        yield self.bounds
        yield self.snake
        yield self.apple
        yield self.score
        yield self.alive
        yield self.won

    def __str__(self):
        """
        Return the string representation of the status.

        Return
        - the string representation of the status
        """
        return \
        f"""Bounds: {self.bounds}
        Snake:  {(str(p) + ' > ' for p in self.snake)}
        Apple:  {str(self.apple)}
        Score:  {self.score}
        Alive:  {self.alive}
        Won:    {self.won}
        """


class Snake(object):
    """
    Describe a game of snake.
    """

    def __init__(self, width:int, height:int) -> 'Snake':
        """
        Create a new game of snake.

        Params
        - width: the width of the map (from 0 to width-1)
        - height: the height of the map (from 0 to height-1)

        Return
        - The new game of snake
        """
        self.width  = width
        self.height = height
        self.bounds = (0, self.height - 1, self.width -1, 0)
        self.snake  = [Position.random_position(self.bounds)]
        self.apple  = Position.random_position(self.bounds, taboo=self.snake)
        self.score  = 0
        self.alive  = True
        self.win    = False

    def play(self, dir:int) -> None:
        """
        Play a single move in the game.

        Params
        - dir: the direction of the move

        Raise
        - Exception: if the the game is over
        """

        # Raise an exception if the game is already over
        if self.is_game_over():
            raise Exception("Cannot move since the game is over")

        # Compute the potential next position
        next_pos = self.get_snake_head_position().move(dir)

        # Get status info
        out_of_bounds = next_pos.is_out_of_bounds(self.bounds)
        self_bite = next_pos in self.snake
        apple_eaten = next_pos == self.apple

        # Check if the next position makes the player lose
        if out_of_bounds or self_bite:
            self.alive = False

        # Update apple position and snake elements
        else:

            # The head always moves forward
            self.snake.append(next_pos)

            # If the apple is eaten: the tail does not move and the apple pos
            # become the head of the snake, then the apple respawn elsewhere
            if apple_eaten:
                self.score += 1
                
                # Endgame condition (win)
                if len(self.snake) == self.width * self.height:
                    self.win = True
                else:
                    self.apple = Position.random_position(self.bounds, taboo=self.snake)

            # If no apple was eaten the length of the snake does not change
            # hence the tail moves forward too
            else:
                self.snake.pop(0)

    def get_snake_head_position(self) -> Position:
        """
        Get the position of the head of the snake.

        Return
        - the position of the head of the snake
        """
        return self.snake[-1]

    def get_apple_position(self) -> Position:
        """
        Get the position of the apple.

        Return
        - the position of the apple
        """
        return self.apple

    def is_game_over(self) -> bool:
        """
        Return true if the game is over (due to victory or lost), false
        otherwise.
        """
        return not self.alive or self.win

    def get_score(self) -> int:
        """
        Return the score.

        Return
        - the score
        """
        return self.score

    def get_status(self) -> SnakeStatus:
        """
        Get the current status of the game.

        Return
        - the status of the game
        """
        return SnakeStatus(self.bounds, self.snake, self.apple, self.score, self.alive, self.win)
