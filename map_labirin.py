import pygame
import random
import math
import cairo

TILE_SIZE = 100 

COLOR_WALL_BASE = (255, 215, 0)      
COLOR_WALL_OUTLINE = (184, 134, 11)  
COLOR_GRASS_BASE = (100, 180, 50)    
COLOR_GRASS_DARK = (80, 160, 40)
COLOR_GRASS_LIGHT = (130, 210, 80)
COLOR_DIRT = (120, 100, 50) 

def hex_to_rgb_norm(rgb_tuple):
    return (rgb_tuple[0]/255, rgb_tuple[1]/255, rgb_tuple[2]/255)

def cairo_to_pygame(surface):
    surface.flush()
    data = surface.get_data()
    return pygame.image.frombuffer(data, (surface.get_width(), surface.get_height()), "BGRA")

class GrassTile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Setup Cairo
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, TILE_SIZE, TILE_SIZE)
        ctx = cairo.Context(surface)
        
        # Base Color
        ctx.rectangle(0, 0, TILE_SIZE, TILE_SIZE)
        ctx.set_source_rgb(*hex_to_rgb_norm(COLOR_GRASS_BASE))
        ctx.fill()
        
        # Dirt Spots
        ctx.set_source_rgb(*hex_to_rgb_norm(COLOR_DIRT))
        for _ in range(10):
            dx = random.randint(0, TILE_SIZE-5)
            dy = random.randint(0, TILE_SIZE-5)
            ctx.rectangle(dx, dy, 4, 4)
            ctx.fill()
            
        # Grass Blades
        ctx.set_line_width(3)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        for _ in range(40):
            gx = random.randint(5, TILE_SIZE-5)
            gy = random.randint(10, TILE_SIZE-5)
            color = random.choice([COLOR_GRASS_DARK, COLOR_GRASS_LIGHT])
            tilt = random.randint(-5, 5) 
            height = random.randint(8, 15)
            
            ctx.set_source_rgb(*hex_to_rgb_norm(color))
            ctx.move_to(gx, gy)
            ctx.line_to(gx + tilt, gy - height)
            ctx.stroke()
            
        self.image = cairo_to_pygame(surface)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE

class DetailedWall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, TILE_SIZE, TILE_SIZE)
        ctx = cairo.Context(surface)

        # Fill Base
        ctx.rectangle(0, 0, TILE_SIZE, TILE_SIZE)
        ctx.set_source_rgb(*hex_to_rgb_norm(COLOR_WALL_BASE))
        ctx.fill()

        # Outline & Detail Lines
        ctx.set_source_rgb(*hex_to_rgb_norm(COLOR_WALL_OUTLINE))
        
        # Border (5px)
        ctx.set_line_width(5)
        ctx.rectangle(0, 0, TILE_SIZE, TILE_SIZE)
        ctx.stroke()
        
        # Brick Pattern
        ctx.set_line_width(4)
        
        # Horizontal lines
        ctx.move_to(0, TILE_SIZE/2)
        ctx.line_to(TILE_SIZE, TILE_SIZE/2)
        ctx.stroke()
        
        # Vertical lines
        ctx.move_to(TILE_SIZE/2, 0)
        ctx.line_to(TILE_SIZE/2, TILE_SIZE/2)
        ctx.stroke()
        
        ctx.move_to(TILE_SIZE/4, TILE_SIZE/2)
        ctx.line_to(TILE_SIZE/4, TILE_SIZE)
        ctx.stroke()
        
        ctx.move_to(TILE_SIZE*3/4, TILE_SIZE/2)
        ctx.line_to(TILE_SIZE*3/4, TILE_SIZE)
        ctx.stroke()
        
        # Accent Line
        ctx.set_source_rgb(*hex_to_rgb_norm((218, 165, 32)))
        ctx.set_line_width(2)
        ctx.move_to(5, TILE_SIZE/2 + 5)
        ctx.line_to(TILE_SIZE-5, TILE_SIZE/2 + 5)
        ctx.stroke()

        self.image = cairo_to_pygame(surface)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE

class Door(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Placeholder surface, will be replaced by redraw
        self.image = None
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
        
        # Hitung lebar panel
        panel_width = (TILE_SIZE // 2) - self.open_progress
        
        if panel_width > 0:
            ctx.set_line_width(4)
            
            # Helper function untuk menggambar panel pintu
            def draw_panel(px, py, pw, ph):
                ctx.rectangle(px, py, pw, ph)
                ctx.set_source_rgb(*hex_to_rgb_norm((101, 67, 33))) # Coklat Tua
                ctx.fill_preserve()
                ctx.set_source_rgb(*hex_to_rgb_norm((60, 40, 20))) # Border
                ctx.stroke()

            # Panel Kiri
            draw_panel(0, 0, panel_width, TILE_SIZE)
            
            # Panel Kanan
            draw_panel(TILE_SIZE - panel_width, 0, panel_width, TILE_SIZE)
            
            # Gagang Pintu
            if panel_width > 10:
                ctx.set_source_rgb(*hex_to_rgb_norm((255, 215, 0)))
                
                # Kiri
                ctx.arc(panel_width - 10, TILE_SIZE/2, 6, 0, 2*math.pi)
                ctx.fill()
                
                # Kanan
                ctx.arc(TILE_SIZE - panel_width + 10, TILE_SIZE/2, 6, 0, 2*math.pi)
                ctx.fill()
        
        self.image = cairo_to_pygame(surface)

class Portal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = None
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.timer = 0
        self.update() # Init image

    def update(self):
        self.timer += 0.1
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, TILE_SIZE, TILE_SIZE)
        ctx = cairo.Context(surface)
        
        cx, cy = TILE_SIZE/2, TILE_SIZE/2
        
        # Efek putaran portal
        max_radius = TILE_SIZE // 2 - 5
        for i in range(3):
            radius = max_radius - (i * 10) + (math.sin(self.timer + i) * 3)
            alpha = 0.6 + (math.sin(self.timer * 2 + i) * 0.4) # 0.0 - 1.0 for Cairo alpha
            
            ctx.set_source_rgba(100/255, 200/255, 255/255, alpha)
            ctx.set_line_width(4)
            ctx.arc(cx, cy, radius, 0, 2*math.pi)
            ctx.stroke()
        
        # Inti portal
        core_radius = 10 + abs(math.sin(self.timer * 3) * 5)
        ctx.set_source_rgb(1, 1, 1)
        ctx.arc(cx, cy, core_radius, 0, 2*math.pi)
        ctx.fill()
        
        self.image = cairo_to_pygame(surface)

def generate_maze(width, height):
    w = width if width % 2 != 0 else width + 1
    h = height if height % 2 != 0 else height + 1
    maze = [[1 for _ in range(w)] for _ in range(h)]
    
    def carve(x, y):
        maze[y][x] = 0
        directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 < nx < w and 0 < ny < h and maze[ny][nx] == 1:
                maze[y + dy // 2][x + dx // 2] = 0
                carve(nx, ny)
    
    carve(1, 1)
    maze[1][1] = 0 
    return maze, w, h