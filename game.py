from __future__ import annotations
from heapq import heappop, heappush
from typing import Callable, Deque, Dict, List, NamedTuple, Optional, Set, Tuple
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
PATH = (186,85,211) # purple
FRONTIER = (255,127,80) # orange 
EXPLORED = (255,215,0) # yellow

GREY = (128, 128, 128) # for drawing the grid lines 

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

class Queue():
    """First In First Out data structure with push and pop methods"""
    def __init__(self) -> None:
        self._container: Deque = Deque()

    @property
    def empty(self) -> bool:
        return not self._container # not is true for empty container 

    def push(self, item) -> None:
        self._container.append(item)

    # popping from the left is an O(1) operation whereas it is an O(n) operation on a list (every element must be moved one to left)
    def pop(self):
        return self._container.popleft() # FIFO

class PriorityQueue():
    """Element with highest priority is in front. Priority is defined as lowest f(n)"""
    def __init__(self) -> None:
        self._container: List = []
        
    @property
    def empty(self) -> bool:
        return not self._container # not is true for empty container 

    # heappush and heappop compares node using < operator, __lt__ in Node
    def push(self, item) -> None:
        heappush(self._container, item) # in by priority 

    def pop(self):
        return heappop(self._container) # out by priority 

class Node():
    """Strictly for maze finding algorithm only"""
    # Optional type means either Node or None
    def __init__(self, current: MazeLocation, parent: Optional[Node], cost: float = 0.0, heuristic: float = 0.0) -> None:
        self.current: MazeLocation = current
        self.parent: Optional[Node] = parent

        # for astar 
        self.cost: float = cost
        self.heuristic: float = heuristic

    def __lt__(self, other: Node) -> bool:
        """
        f(n) = g(n) + h(n) where:
            g(n) is total estimated cost of path to reach Node n 
            h(n) is estimated cost from n to goal using a heuristic
        """
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
    """Handles all maze logic, including pathfinding algorithm"""

    def __init__(self, start: Optional[MazeLocation] = None, goal: Optional[MazeLocation] = None, 
        rows: int = 10, columns: int = 10, sparseness: float = 0.2) -> None:
        
        # initialize basic instance variables
        self._rows: int = rows
        self._columns: int = columns
        self.sparseness: float = sparseness
        self.start: Optional[MazeLocation] = start
        self.goal: Optional[MazeLocation] = goal 
        
        self._grid = [[DisplayNode(row, column) for column in range(self._columns)] for row in range(self._rows)]
        
        # populate the grid with blocked cells
        self._randomly_filled(self._rows, self._columns, self.sparseness)

        # fill start and goal
        if self.start:
            self._grid[start.row][start.column].state = START
        if self.goal:
            self._grid[goal.row][goal.column].state = GOAL

    def _randomly_filled(self, rows: int, columns: int, sparseness: float):
        """Randomly fill the maze with walls"""
        # can be improved 
        for row in range(rows):
            for column in range(columns):
                if random.uniform(0, 1.0) < sparseness:
                    self._grid[row][column].state = BLOCKED

    def on_click(self, mouse_pos: Tuple[int, int]) -> MazeLocation:
        """Select start and end points. Make walls delete walls"""
        row = int(mouse_pos[1] // (HEIGHT / self._rows))
        column = int(mouse_pos[0] // (WIDTH / self._columns))
        return MazeLocation(row, column)

    def update_grid(self, ml: MazeLocation, ml_state: Tuple[int, int, int] = EMPTY) -> None:
        """
        Updates grid when user input or deletes start, goal or wall
        Also updates DisplayNode states during pathfinding algorithm
        """
        # check to make sure ml is valid 
        if 0 <= ml.row <= self._rows and 0 <= ml.column <= self._columns:
            if ml_state in (EMPTY, BLOCKED, START, GOAL, PATH, FRONTIER, EXPLORED):
                self._grid[ml.row][ml.column].state = ml_state

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

    def dfs(self, initial: MazeLocation, goal_test: Callable[[MazeLocation], bool],
        successors: Callable[[MazeLocation], List[MazeLocation]]) -> Optional[Node]:
        """Finds a path using Depth First Search and returns goal if path exists else None"""

        # frontier is where we've yet to go 
        frontier: Stack[Node] = Stack()
        frontier.push(Node(initial, None))

        # explored is where we've been 
        explored: Set[MazeLocation] = {initial}

        # keep going while there is more to explore 
        while not frontier.empty:
            current_node: Node = frontier.pop()
            current_location: MazeLocation = current_node.current
            # if we found the goal, we're done 
            if goal_test(current_location):
                return current_node

            # check where we can go next and haven't explored 
            for child in successors(current_location):
                if child in explored: # skip children we already explored 
                    continue
                # if not explored, visit them and add to explored
                explored.add(child)
                frontier.push(Node(child, current_node))
                self.update_grid(child, FRONTIER)

            # needs to update every cycle WIP
            if current_location != self.start:
                self.update_grid(current_location, EXPLORED)
                
        return None # went through everything and never found goal 
    
    def bfs(self, initial: MazeLocation, goal_test: Callable[[MazeLocation], bool], 
        successors: Callable[[MazeLocation], List[MazeLocation]]) -> Optional[Node]:
        """Finds a path using Breadth First Search and returns goal if path exists else None"""

        # frontier is where we've yet to go 
        frontier: Queue[Node] = Queue()
        frontier.push(Node(initial, None))

        # explored is where we've been 
        explored: Set[MazeLocation] = {initial}

        # keep going while there is more to explore 
        while not frontier.empty:
            current_node: Node = frontier.pop()
            current_location: MazeLocation = current_node.current
            # if we found the goal, we're done 
            if goal_test(current_location):
                return current_node

            # check where we can go next and haven't explored 
            for child in successors(current_location):
                if child in explored: # skip children we already explored 
                    continue
                explored.add(child)
                frontier.push(Node(child, current_node))

        return None # went through everything and never found goal 

    def astar(self, initial: MazeLocation, goal_test: Callable[[MazeLocation], bool], 
        successors: Callable[[MazeLocation], List[MazeLocation]],
        heuristic: Callable[[MazeLocation], float]) -> Optional[Node]:
        """Finds a path using A star and returns goal if path exists else None"""

        # frontier is where we've yet to go 
        frontier: PriorityQueue[Node] = PriorityQueue()
        frontier.push(Node(initial, None, 0.0, heuristic(initial)))

        # explored is where we've been 
        explored: Dict[MazeLocation, float] = {initial: 0.0}

        # keep going while there is more to explore 
        while not frontier.empty:
            current_node: Node = frontier.pop()
            current_location: MazeLocation = current_node.current
            # if we found the goal, we're done 
            if goal_test(current_location):
                return current_node
            # check where we can go next and haven't explored 
            for child in successors(current_location):
                # 1 assumes a grid, need a cost function for more sophisticated apps 
                new_cost: float = current_node.cost + 1 

                if child not in explored or explored[child] > new_cost:
                    explored[child] = new_cost
                    frontier.push(Node(child, current_node, new_cost, heuristic(child)))

        return None # went through everything and never found goal

    def node_to_path(self, node: Node) -> List[MazeLocation]:
        """Returns the path taken by working backwards from end to front"""
        path: List[MazeLocation] = [node.current]

        # initial node parent is None
        while node.parent is not None:
            node = node.parent
            path.append(node.current)
        path.reverse()
        return path

    def manhattan_distance(self, goal: MazeLocation) -> Callable[[MazeLocation], float]:
        """Returns a function that remembers the goal coordinates"""
        def distance(ml: MazeLocation) -> float:
            xdist: int = abs(ml.column - goal.column)
            ydist: int = abs(ml.row - goal.row)
            return (xdist + ydist)
        return distance

    def show_path(self, path: List[MazeLocation]) -> None:
        """Display path found by algorithm"""
        for maze_location in path:
            self._grid[maze_location.row][maze_location.column].state = PATH
        self._grid[self.start.row][self.start.column].state = START
        self._grid[self.goal.row][self.goal.column].state = GOAL

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
    chosen_algo: str = "DFS" # accepted values: DFS, BFS, A star

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            # press x in top right to quit 
            if event.type == pygame.QUIT:
                run = False

            # handle placing of start, goal and walls 
            if pygame.mouse.get_pressed()[0]: # LEFT
                spot_clicked: MazeLocation = maze.on_click(pygame.mouse.get_pos())

                # if no start point and spot is not ending point
                if not maze.start and spot_clicked != maze.goal:
                    maze.start = spot_clicked
                    maze.update_grid(maze.start, START)
                # if no end point and spot is not starting point 
                elif not maze.goal and spot_clicked != maze.start:
                    maze.goal = spot_clicked
                    maze.update_grid(maze.goal, GOAL)
                # if both start and end point are placed, place walls
                elif spot_clicked != maze.start and spot_clicked != maze.goal:
                    maze.update_grid(spot_clicked, BLOCKED)

            # deletes start, goal and walls
            elif pygame.mouse.get_pressed()[2]: # RIGHT
                spot_clicked: MazeLocation = maze.on_click(pygame.mouse.get_pos())
                # set spot clicked to empty 
                maze.update_grid(spot_clicked)

                # if delete start or end, set to None
                if spot_clicked == maze.start:
                    maze.start = None
                if spot_clicked == maze.goal:
                    maze.goal = None
            
            # handles activating the pathfinding algorithm
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    
                    # only attempt finding a solution if both start and goal exists
                    if maze.start and maze.goal:
                        # find solution 
                        if chosen_algo == "DFS":
                            solution: Optional[Node] = maze.dfs(maze.start, maze.goal_test, maze.neighbours)
                        elif chosen_algo == "BFS":
                            solution: Optional[Node] = maze.bfs(maze.start, maze.goal_test, maze.neighbours)
                        elif chosen_algo == "A star":
                            distance: Callable[[MazeLocation], float] = maze.manhattan_distance(maze.goal)
                            solution: Optional[Node] = maze.astar(maze.start, maze.goal_test, maze.neighbours, distance)
                        
                        # display solution 
                        if solution is None:
                            print(f"No {chosen_algo} solution")
                        else:
                            path: List[MazeLocation] = maze.node_to_path(solution)
                            maze.show_path(path)

        maze.render(WIN)
        pygame.display.update()

if __name__ == "__main__":
    main()