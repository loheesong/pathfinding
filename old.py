import pygame, tkinter
from queue import PriorityQueue

WIDTH, HEIGHT = 650, 650
ROW, COL = 50, 50 
FPS = 60
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pathfinding")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

class Node:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.colour = WHITE

        self.x = WIDTH / COL * self.col
        self.y = HEIGHT / ROW * self.row
        self.width = WIDTH / COL 
        self.height = HEIGHT / ROW
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.neighbours = []
        self.g_score = float("inf")
        self.h_score = float("inf")


    def render(self, win):
        pygame.draw.rect(win, self.colour, self.rect)

    def update_neighbours(self):
        pass


class Grid:
    """Handles all grid logic"""
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.grid = [[Node(row, col) for col in range(self.col)] for row in range(self.row)]

    def render(self, win):
        """Render all lines and nodes"""
        gap = WIDTH / self.col

        for row in self.grid:
            for col in row:
                col.render(win)

        for i in range(self.col + 1):
            # vertical lines
            pygame.draw.line(win, GREY, (i * gap, 0), (i * gap, HEIGHT))
            # horizontal lines
            pygame.draw.line(win, GREY, (0, i * gap), (WIDTH, i * gap))
        
    def on_click(self, mouse_pos: tuple[int,int]) -> tuple:
        """Select start and end points. Make walls delete walls"""
        row = int(mouse_pos[1] // (HEIGHT / self.row))
        col = int(mouse_pos[0] // (WIDTH / self.col))
        return row,col

    def h(p1: tuple[int,int], p2: tuple[int,int]) -> int:
        """Estimated cost of path from one node to another using Manhattan Distance"""
        y1, x1 = p1
        y2, x2 = p2
        return abs(x1 - x2) + abs(y1 - y2)

    def astar(self, start: Node, end: Node):
        """Main pathfinding algorithm"""
        # f_score = g_score + h_score

        open_set = PriorityQueue()
        
        came_from = []

        # All nodes alr have g_score and h_score of infinity 
        # Distance to the root itself is zero
        start.g_score = 0
        start.h_score = 0

        # Init queue with the root node
        open_set.put((start.g_score + start.h_score, start))

        # Iterate over the priority queue until it is empty.
        while not open_set.empty():
            # Fetch next closest node
            curNode = open_set.get()

            # Mark as discovered 
            came_from.append(curNode) 

            # Iterate over unvisited neighbors
                
                # Update root minimal distance

                # Change queue priority of the neighbor

                # Add neighbor to the queue for further visiting.

        print("astar done")




def main():
    """Main game logic"""
    clock = pygame.time.Clock()
    grid = Grid(ROW, COL)

    run = True 
    gameState = "run"
    start = None
    end = None
    
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]: # LEFT
                row, col = grid.on_click(pygame.mouse.get_pos())
                spot_clicked = grid.grid[row][col]

                # if no start point and spot is not ending point
                if not start and spot_clicked != end:
                    start = spot_clicked
                    start.colour = RED
                # if no end point and spot is not starting point 
                elif not end and spot_clicked != start:
                    end = spot_clicked
                    end.colour = BLUE
                # if both start and end point are placed, place walls
                elif spot_clicked != start and spot_clicked != end:
                    spot_clicked.colour = BLACK

            elif pygame.mouse.get_pressed()[2]: # RIGHT
                row, col = grid.on_click(pygame.mouse.get_pos())
                spot_clicked = grid.grid[row][col]
                spot_clicked.colour = WHITE

                # if delete start or end, set to None
                if spot_clicked == start:
                    start = None
                if spot_clicked == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    grid.astar()

        grid.render(WIN)
        pygame.display.update()

main()
