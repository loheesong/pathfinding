import pygame, tkinter

WIDTH, HEIGHT = 650, 650
ROW, COL = 50, 50 
FPS = 60
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pathfinding")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)

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
        
        
    
    def on_click(self, mouse_pos, mouse_button):
        """Select start and end points. Make walls delete walls"""
        row = int(mouse_pos[1] // (HEIGHT / self.row))
        col = int(mouse_pos[0] // (WIDTH / self.col))
        if mouse_button == "left":
            self.grid[row][col].colour = BLACK
        elif mouse_button == "right":
            self.grid[row][col].colour = WHITE

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
                mouse_button = "left"
                grid.on_click(pygame.mouse.get_pos(), mouse_button)
            elif pygame.mouse.get_pressed()[2]: # right
                mouse_button = "right"
                grid.on_click(pygame.mouse.get_pos(), mouse_button)

            if event.type == pygame.QUIT:
                run = False

        grid.render(WIN)
        pygame.display.update()
    print()

main()
