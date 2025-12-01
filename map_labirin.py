import pygame
import random
import math
import cairo

TILE_SIZE = 100 
COLOR_WALL_BASE = (255, 215, 0)      
COLOR_WALL_OUTLINE = (184, 134, 11)  
COLOR_GRASS_BASE = (100, 180, 50)    
COLOR_DIRT = (120, 100, 50) 

def hex_to_rgb_norm(rgb_tuple):
    return (rgb_tuple[0]/255, rgb_tuple[1]/255, rgb_tuple[2]/255)

def cairo_to_pygame(surface):
    surface.flush()
    return pygame.image.frombuffer(surface.get_data(), (surface.get_width(), surface.get_height()), "BGRA")

class GrassTile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, TILE_SIZE, TILE_SIZE)
        ctx = cairo.Context(surface)
        
        ctx.rectangle(0, 0, TILE_SIZE, TILE_SIZE)
        ctx.set_source_rgb(*hex_to_rgb_norm(COLOR_GRASS_BASE)); ctx.fill()
        
        ctx.set_source_rgb(*hex_to_rgb_norm(COLOR_DIRT))
        for _ in range(10):
            ctx.rectangle(random.randint(0, TILE_SIZE-5), random.randint(0, TILE_SIZE-5), 4, 4)
            ctx.fill()
            
        ctx.set_line_width(3); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        for _ in range(40):
            gx, gy = random.randint(5, TILE_SIZE-5), random.randint(10, TILE_SIZE-5)
            ctx.set_source_rgb(*hex_to_rgb_norm(random.choice([(80, 160, 40), (130, 210, 80)])))
            ctx.move_to(gx, gy)
            ctx.line_to(gx + random.randint(-5, 5), gy - random.randint(8, 15))
            ctx.stroke()
            
        self.image = cairo_to_pygame(surface)
        self.rect = self.image.get_rect(topleft=(x * TILE_SIZE, y * TILE_SIZE))

class DetailedWall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, TILE_SIZE, TILE_SIZE)
        ctx = cairo.Context(surface)

        ctx.rectangle(0, 0, TILE_SIZE, TILE_SIZE)
        ctx.set_source_rgb(*hex_to_rgb_norm(COLOR_WALL_BASE)); ctx.fill()

        ctx.set_source_rgb(*hex_to_rgb_norm(COLOR_WALL_OUTLINE))
        ctx.set_line_width(5)
        ctx.rectangle(0, 0, TILE_SIZE, TILE_SIZE); ctx.stroke()
        
        ctx.set_line_width(4)
        for px, py, tx, ty in [(0, 0.5, 1, 0.5), (0.5, 0, 0.5, 0.5), (0.25, 0.5, 0.25, 1), (0.75, 0.5, 0.75, 1)]:
            ctx.move_to(px * TILE_SIZE, py * TILE_SIZE)
            ctx.line_to(tx * TILE_SIZE, ty * TILE_SIZE)
            ctx.stroke()
        
        ctx.set_source_rgb(*hex_to_rgb_norm((218, 165, 32)))
        ctx.set_line_width(2)
        ctx.move_to(5, TILE_SIZE/2 + 5); ctx.line_to(TILE_SIZE-5, TILE_SIZE/2 + 5); ctx.stroke()

        self.image = cairo_to_pygame(surface)
        self.rect = self.image.get_rect(topleft=(x * TILE_SIZE, y * TILE_SIZE))

class Door(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.is_opening = False
        self.open_progress = 0 
        self.finished_opening = False
        self.redraw()

    def update(self):
        if self.is_opening and not self.finished_opening:
            self.open_progress += 2 
            if self.open_progress >= TILE_SIZE // 2:
                self.open_progress = TILE_SIZE // 2
                self.finished_opening = True
            self.redraw()

    def redraw(self):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, TILE_SIZE, TILE_SIZE)
        ctx = cairo.Context(surface)
        panel_width = (TILE_SIZE // 2) - self.open_progress
        
        if panel_width > 0:
            ctx.set_line_width(4)
            for px in [0, TILE_SIZE - panel_width]:
                ctx.rectangle(px, 0, panel_width, TILE_SIZE)
                ctx.set_source_rgb(*hex_to_rgb_norm((101, 67, 33))); ctx.fill_preserve()
                ctx.set_source_rgb(*hex_to_rgb_norm((60, 40, 20))); ctx.stroke()

            if panel_width > 10:
                ctx.set_source_rgb(*hex_to_rgb_norm((255, 215, 0)))
                ctx.arc(panel_width - 10, TILE_SIZE/2, 6, 0, 2*math.pi); ctx.fill()
                ctx.arc(TILE_SIZE - panel_width + 10, TILE_SIZE/2, 6, 0, 2*math.pi); ctx.fill()
        self.image = cairo_to_pygame(surface)

class Portal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.timer = 0
        self.update()

    def update(self):
        self.timer += 0.1
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, TILE_SIZE, TILE_SIZE)
        ctx = cairo.Context(surface)
        cx, cy = TILE_SIZE/2, TILE_SIZE/2
        
        for i in range(3):
            radius = (TILE_SIZE // 2 - 5) - (i * 10) + (math.sin(self.timer + i) * 3)
            ctx.set_source_rgba(100/255, 200/255, 255/255, 0.6 + (math.sin(self.timer * 2 + i) * 0.4))
            ctx.set_line_width(4)
            ctx.arc(cx, cy, radius, 0, 2*math.pi); ctx.stroke()
        
        ctx.set_source_rgb(1, 1, 1)
        ctx.arc(cx, cy, 10 + abs(math.sin(self.timer * 3) * 5), 0, 2*math.pi); ctx.fill()
        self.image = cairo_to_pygame(surface)

def generate_maze(width, height):
    w = width + (1 if width % 2 == 0 else 0)
    h = height + (1 if height % 2 == 0 else 0)
    maze = [[1] * w for _ in range(h)]
    
    def carve(x, y):
        maze[y][x] = 0
        dirs = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 < nx < w and 0 < ny < h and maze[ny][nx] == 1:
                maze[y + dy // 2][x + dx // 2] = 0
                carve(nx, ny)
    
    carve(1, 1)
    maze[1][1] = 0 
    return maze, w, h