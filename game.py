from __future__ import annotations
from enum import Enum
from typing import Callable, List, NamedTuple, Optional, Tuple
import pygame 
import random

# snake_case: functions and variables 
# PascalCase: classes

WIDTH, HEIGHT = 750, 750
ROW, COLUMN = 10, 10 
FPS = 60
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pathfinding")

# DisplayNode states 
EMPTY = (255, 255, 255) # white
BLOCKED = (0, 0, 0) # black
START = (255, 0, 0) # red 
GOAL = (0, 0, 255) # blue 
PATH = (0, 255, 0) # green
GREY = (128, 128, 128)

class MazeLocation(NamedTuple):
    row: int
    column: int

class Stack():
    """Last In First Out data structure with push and pop methods"""
    def __init__(self) -> None:
        self._container: List = []

    @property
    def empty(self) -> bool:
        return not self._container # not is true for empty container 

    def push(self, item) -> None:
        self._container.append(item)

    def pop(self):
        return self._container.pop() # LIFO

    def __repr__(self) -> str:
        return repr(self._container)

class Node():
    """Strictly for maze finding algorithm only"""
    # Optional type means either Node or None
    def __init__(self, state, parent: Optional[Node], cost: float = 0.0, heuristic: float = 0.0) -> None:
        self.state = state
        self.parent: Optional[Node] = parent

        # for astar 
        self.cost: float = cost
        self.heuristic: float = heuristic

    def __lt__(self, other: Node) -> bool:
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)

class DisplayNode:
    """For visual representation of Nodes in Maze"""
    def __init__(self, row, column):
        self.row: int = row
        self.column: int = column
        self.state: Tuple[int, int, int] = EMPTY

        # drawing purposes 
        self._x: float = WIDTH / COLUMN * self.column
        self._y: float = HEIGHT / ROW * self.row
        self._width: float = WIDTH / COLUMN
        self._height: float = HEIGHT / ROW
        self._rect: pygame.Rect = pygame.Rect(self._x, self._y, self._width, self._height)

    def render(self, win):
        pygame.draw.rect(win, self.state, self._rect)


class Maze:
    """Handles all maze logic"""

    def __init__(self, rows: int = 10, columns: int = 10, sparseness: float = 0.2, 
        start: MazeLocation = MazeLocation(0,0), goal: MazeLocation = MazeLocation(9,9)) -> None:
        
        # initialize basic instance variables
        self._rows: int = rows
        self._columns: int = columns
        self.sparseness: float = sparseness
        self.start: MazeLocation = start
        self.goal: MazeLocation = goal 
        
        self._grid = [[DisplayNode(row, column) for column in range(self._columns)] for row in range(self._rows)]
        self._randomly_filled(self._rows, self._columns, self.sparseness)

        # populate the grid with blocked cells
        self._grid[start.row][start.column].state = START
        self._grid[goal.row][goal.column].state = GOAL

    def _randomly_filled(self, rows: int, columns: int, sparseness: float):
        """Randomly fill the maze with walls"""
        # can be improved 
        for row in range(rows):
            for column in range(columns):
                if random.uniform(0, 1.0) < sparseness:
                    self._grid[row][column].state = BLOCKED

    def goal_test(self, ml: MazeLocation) -> bool:
        """Check whether current maze location is the goal"""
        return ml == self.goal
  
    def neighbours(self, ml: MazeLocation) -> List[MazeLocation]:
        """Finds the possible next location from a given maze location"""
        locations: List[MazeLocation] = []

        # down 
        if ml.row + 1 < self._rows and self._grid[ml.row + 1][ml.column].state != BLOCKED:
            locations.append(MazeLocation(ml.row + 1, ml.column))

        # up
        if ml.row - 1 >= 0 and self._grid[ml.row - 1][ml.column].state != BLOCKED:
            locations.append(MazeLocation(ml.row - 1, ml.column))

        # right
        if ml.column + 1 < self._columns and self._grid[ml.row][ml.column + 1].state != BLOCKED:
            locations.append(MazeLocation(ml.row, ml.column + 1))

        # left 
        if ml.column - 1 >= 0 and self._grid[ml.row][ml.column - 1].state != BLOCKED:
            locations.append(MazeLocation(ml.row, ml.column - 1))

        return locations

    def dfs(self):
        pass

    def manhattan_distance(goal: MazeLocation) -> Callable[[MazeLocation], float]:
        """Returns a function that remembers the goal coordinates"""
        def distance(ml: MazeLocation) -> float:
            xdist: int = abs(ml.column - goal.column)
            ydist: int = abs(ml.row - goal.row)
            return (xdist + ydist)
        return distance

    def render(self, win):
        """Render all lines and nodes"""
        gap: float = WIDTH / self._columns

        for row in self._grid:
            for display in row:
                display.render(win)

        for i in range(self._columns + 1):
            # vertical lines
            pygame.draw.line(win, GREY, (i * gap, 0), (i * gap, HEIGHT))
            # horizontal lines
            pygame.draw.line(win, GREY, (0, i * gap), (WIDTH, i * gap))

    
def main():
    """Main game logic"""
    clock = pygame.time.Clock()
    maze: Maze = Maze()

    run: bool = True 
    game_state: str = "run"
    start = None
    end = None
    
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            # press x in top right to quit 
            if event.type == pygame.QUIT:
                run = False

            # handle placing of start, goal and walls 
            if pygame.mouse.get_pressed()[0]: # LEFT
                pass
            elif pygame.mouse.get_pressed()[2]: # RIGHT
                pass
            
            # handles activating the pathfinding algorithm
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    maze.dfs()

        maze.render(WIN)
        pygame.display.update()




if __name__ == "__main__":
    main()