import pygame, tkinter

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

class Grid:
    """Handles all grid logic"""
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.grid = [[Box(row, col) for col in range(self.col)] for row in range(self.row)]

    def render(self, win):
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

    def algorithm(self):
        pass
    
class Box:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.colour = WHITE

        self.x = WIDTH / COL * self.col
        self.y = HEIGHT / ROW * self.row
        self.width = WIDTH / COL 
        self.height = HEIGHT / ROW
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def render(self, win):
        pygame.draw.rect(win, self.colour, self.rect)

def main():
    clock = pygame.time.Clock()
    grid = Grid(ROW, COL)

    run = True 
    gameState = "run"
    start = None
    end = None
    
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
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

            elif pygame.mouse.get_pressed()[2]: # right
                row, col = grid.on_click(pygame.mouse.get_pos())
                spot_clicked = grid.grid[row][col]
                spot_clicked.colour = WHITE

                # if delete start or end, set to None
                if spot_clicked == start:
                    start = None
                if spot_clicked == end:
                    end = None

            if event.type == pygame.QUIT:
                run = False

        grid.render(WIN)
        pygame.display.update()
    print()

main()
