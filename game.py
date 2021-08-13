from __future__ import annotations
from heapq import heappop, heappush
from typing import Callable, Deque, Dict, List, NamedTuple, Optional, Set, Tuple
import pygame 
import random

# snake_case: functions and variables 
# PascalCase: classes

# constants in call caps 
WIDTH, HEIGHT = 750, 750
ROW, COLUMN = 50, 50 
FPS = 60
WIN: pygame.Surface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pathfinding")

pygame.font.init()
smallFont = pygame.font.SysFont("tahoma", 24)
bigFont = pygame.font.SysFont("tahoma", 56)

# DisplayNode states 
EMPTY = (255, 255, 255) # white
BLOCKED = (0, 0, 0) # black
START = (255, 0, 0) # red 
GOAL = (0, 0, 255) # blue 
PATH = (186, 85, 211) # purple
FRONTIER = (255, 127, 80) # orange 
EXPLORED = (255, 215, 0) # yellow

# colours
GREY = (128, 128, 128) # for drawing the grid lines 
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (126, 249, 255)
RED = (250, 120, 114)

class MazeLocation(NamedTuple):
    """Used to refer to locations in maze, for better organization"""
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
        rows: int = ROW, columns: int = COLUMN, sparseness: float = 0.2) -> None:
        
        # initialize basic instance variables
        self._rows: int = rows
        self._columns: int = columns
        self.sparseness: float = sparseness
        self.start: Optional[MazeLocation] = start
        self.goal: Optional[MazeLocation] = goal 
        
        self._grid = [[DisplayNode(row, column) for column in range(self._columns)] for row in range(self._rows)]
        
        # fill start and goal
        if self.start:
            self._grid[start.row][start.column].state = START
        if self.goal:
            self._grid[goal.row][goal.column].state = GOAL

    def _randomly_filled(self, rows: int, columns: int, sparseness: float) -> None:
        """Randomly fill the maze with walls"""
        # can be improved 
        for row in range(rows):
            for column in range(columns):
                if random.uniform(0, 1.0) < sparseness:
                    self._grid[row][column].state = BLOCKED

    def empty(self) -> None:
        """Clear the entire maze of walls. Resets start and goal"""
        for row in self._grid:
            for d_node in row:
                d_node.state = EMPTY 
        
        self.start = None
        self.goal = None

    def maze_gen(self, gen_style: str) -> None:
        """Generate maze based on user chosen style"""
        if gen_style == "Random":
            self._randomly_filled(self._rows, self._columns, self.sparseness) 

        if gen_style == "Empty":
            self.empty()

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
            # make sure can quit the program while algo is running
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

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

            self.render(WIN)
            pygame.display.update()

            # updates where algo has checked before 
            if current_location != self.goal:
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
            # make sure can quit the program while algo is running
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

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
                self.update_grid(child, FRONTIER)

            self.render(WIN)
            pygame.display.update()

            # updates where algo has checked before 
            if current_location != self.goal:
                self.update_grid(current_location, EXPLORED)
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
            # make sure can quit the program while algo is running
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

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
                    self.update_grid(child, FRONTIER)

            self.render(WIN)
            pygame.display.update()

            # updates where algo has checked before 
            if current_location != self.goal:
                self.update_grid(current_location, EXPLORED)

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

    def reset(self) -> None:
        """Clears path, frontier, explored renders. Walls, start, goal remains. Recolour start"""
        for row in self._grid:
            for d_node in row:
                if d_node.state in (PATH, FRONTIER, EXPLORED):
                    d_node.state = EMPTY
        
        # if start is deleted and set to None, this function still works 
        if self.start:
            self._grid[self.start.row][self .start.column].state = START

    def render(self, win) -> None:
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

class Button:
    """Implements clickable button with centered text. x and y refer to button center"""
    def __init__(self, name: str, x: int, y: int, width: int = 50, height: int = 50, \
            colour: Tuple[int, int, int] = WHITE, small_font: bool = True) -> None:
        self.name: str = name
        self._x: int = x
        self._y: int = y 
        self._width: int = width 
        self._height: int = height 
        self._rect: pygame.Rect = pygame.Rect(self._x - self._width / 2, self._y - self._height / 2, self._width, self._height)
        self.button_colour: Tuple[int, int, int] = colour

        self._text_colour: Tuple[int, int, int] = BLACK
        # create a surface to render text
        self._text_render: pygame.Surface = smallFont.render(self.name, True, self._text_colour) if small_font else \
            bigFont.render(name, True, self._text_colour)
        # create a rectangle that centers the text in the button 
        self._text_rect: pygame.Rect = self._text_render.get_rect(center = (self._x, self._y))

    def is_clicked(self, mouse_pos: Tuple[int, int]) -> bool:
        """Detects if button is clicked"""
        mouse_x, mouse_y = mouse_pos 
        if self._x - self._width / 2 <= mouse_x <= self._x + self._width / 2 and \
            self._y - self._height / 2 <= mouse_y <= self._y + self._height / 2:
            return True
        return False

    def render(self, win) -> None:
        """Renders rectangular button with text in the middle"""
        pygame.draw.rect(win, self.button_colour, self._rect) 
        win.blit(self._text_render, self._text_rect)

def setting_render(win, title: Button, buttons: Dict[str, Button], instructions: List[Button]) -> None:
    """Renders all buttons and texts in game_state setting"""
    # set background colour to white 
    win.fill((255,255,255)) 

    # renders title 
    title.render(win)
    
    # renders all buttons
    for button in buttons.values():
        button.render(win)
    
    # renders instructions  
    for text in instructions:
        text.render(win)
    
def main():
    """Main game logic"""
    maze: Maze = Maze()

    run: bool = True 
    game_state: str = "setting" # accepted values: setting, run 
    chosen_algo: str = "A*" # accepted values: DFS, BFS, A*
    chosen_maze_gen: str = "Empty" 

    title = Button("Pathfinding", WIDTH / 2, 50, small_font=False)
    
    buttons: Dict[str, Button] = {"DFS": Button("DFS", WIDTH / 2 - 150, 200, width = 100, height = 50, colour = BLUE), \
        "BFS": Button("BFS", WIDTH / 2, 200, width = 100, height = 50, colour = BLUE), \
        "A*": Button("A*", WIDTH / 2 + 150, 200, width = 100, height = 50, colour = BLUE), \
        "Random": Button("Random", WIDTH / 2 - 100, 375, width = 150, height = 50, colour = BLUE), \
        "Empty": Button("Empty", WIDTH / 2 + 100, 375, width = 150, height = 50, colour = BLUE), \
        "VISUALISE": Button("VISUALISE", WIDTH / 2, 650, width = 200, height = 75, colour = BLUE)}
    
    instructions: List[Button] = [Button("Space to run", WIDTH / 2, 450), \
        Button("Backspace to go back", WIDTH / 2, 500), \
        Button("Enter to reset", WIDTH / 2, 550), \
        Button("Pathfinding Algorithm", WIDTH / 2, 135), \
        Button("Maze Generation", WIDTH / 2, 300)]
    
    # highlight the default 
    for button in buttons:
        if button == chosen_algo or button == chosen_maze_gen :
            buttons[button].button_colour = RED 

    while run:
        # set type of algo and maze generation 
        if game_state == "setting":
            for event in pygame.event.get():
                # press x in top right to quit 
                if event.type == pygame.QUIT:
                    run = False

                if pygame.mouse.get_pressed()[0]: #LEFT 
                    # check if any of the buttons are pressed 
                    for button in buttons.values():
                        if button.is_clicked(pygame.mouse.get_pos()):
                            if button.name in ["DFS", "BFS", "A*"] and button.button_colour == BLUE:
                                # deselect the previous selection
                                buttons[chosen_algo].button_colour = BLUE 

                                # select the current one and update chosen algo 
                                button.button_colour = RED
                                chosen_algo = button.name 

                            if button.name in ["Random", "Empty"] and button.button_colour == BLUE:
                                # deselect the previous selection
                                buttons[chosen_maze_gen].button_colour = BLUE

                                # select the current one and update chosen algo
                                button.button_colour = RED
                                chosen_maze_gen = button.name

                            if button.name == "VISUALISE":
                                game_state = "run" 
                                maze.maze_gen(chosen_maze_gen)
                                print(chosen_algo, chosen_maze_gen)

            setting_render(WIN, title, buttons, instructions)
        
        # select start, goal and wall placement edits, then runs the chosen algo 
        elif game_state == "run":
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
                            elif chosen_algo == "A*":
                                distance: Callable[[MazeLocation], float] = maze.manhattan_distance(maze.goal)
                                solution: Optional[Node] = maze.astar(maze.start, maze.goal_test, maze.neighbours, distance)
                            
                            # display solution 
                            if solution is None:
                                print(f"No {chosen_algo} solution")
                            else:
                                path: List[MazeLocation] = maze.node_to_path(solution)
                                maze.show_path(path)
                    
                    # reset renders for another animation 
                    if event.key == pygame.K_RETURN:
                        maze.reset()

                    # goes back to game_state setting, should also reset the whole board 
                    if event.key == pygame.K_BACKSPACE:
                        game_state = "setting"
                        maze.empty()

            maze.render(WIN)
            
        pygame.display.update()

if __name__ == "__main__":
    main()