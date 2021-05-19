import pygame, tkinter

WIDTH, HEIGHT = 650, 650
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
        win.fill(WHITE)

        gap = WIDTH / self.col
        for i in range(self.col + 1):
            # vertical lines
            pygame.draw.line(win, GREY, (i * gap, 0), (i * gap, HEIGHT))
            # horizontal lines
            pygame.draw.line(win, GREY, (0, i * gap), (WIDTH, i * gap))
    
    def on_click(self):
        pass


class Box:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def render(self):
        pass

def main():
    clock = pygame.time.Clock()
    run = True 
    gameState = "run"
    grid = Grid(50,50)

    while run:
        clock.tick(FPS)
        

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                grid.on_click()

            if event.type == pygame.QUIT:
                run = False

        grid.render(WIN)
        pygame.display.update()
    print()

main()
