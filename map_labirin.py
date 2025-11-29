import pygame
import random
import math

TILE_SIZE = 100 

COLOR_WALL_BASE = (255, 215, 0)      
COLOR_WALL_OUTLINE = (184, 134, 11)  
COLOR_GRASS_BASE = (100, 180, 50)    
COLOR_GRASS_DARK = (80, 160, 40)
COLOR_GRASS_LIGHT = (130, 210, 80)
COLOR_DIRT = (120, 100, 50) 

class GrassTile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(COLOR_GRASS_BASE)
        for _ in range(10):
            dx = random.randint(0, TILE_SIZE-5)
            dy = random.randint(0, TILE_SIZE-5)
            pygame.draw.rect(self.image, COLOR_DIRT, (dx, dy, 4, 4))
        for _ in range(40):
            gx = random.randint(5, TILE_SIZE-5)
            gy = random.randint(10, TILE_SIZE-5)
            color = random.choice([COLOR_GRASS_DARK, COLOR_GRASS_LIGHT])
            tilt = random.randint(-5, 5) 
            height = random.randint(8, 15)
            pygame.draw.line(self.image, color, (gx, gy), (gx + tilt, gy - height), 3)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE

class DetailedWall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(COLOR_WALL_BASE)
        pygame.draw.rect(self.image, COLOR_WALL_OUTLINE, (0, 0, TILE_SIZE, TILE_SIZE), 5)
        pygame.draw.line(self.image, COLOR_WALL_OUTLINE, (0, TILE_SIZE//2), (TILE_SIZE, TILE_SIZE//2), 4)
        pygame.draw.line(self.image, COLOR_WALL_OUTLINE, (TILE_SIZE//2, 0), (TILE_SIZE//2, TILE_SIZE//2), 4)
        pygame.draw.line(self.image, COLOR_WALL_OUTLINE, (TILE_SIZE//4, TILE_SIZE//2), (TILE_SIZE//4, TILE_SIZE), 4)
        pygame.draw.line(self.image, COLOR_WALL_OUTLINE, (TILE_SIZE*3//4, TILE_SIZE//2), (TILE_SIZE*3//4, TILE_SIZE), 4)
        pygame.draw.line(self.image, (218, 165, 32), (5, TILE_SIZE//2 + 5), (TILE_SIZE-5, TILE_SIZE//2 + 5), 2)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE

class Door(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE
        
        self.is_opening = False
        self.open_progress = 0 # 0 sampai TILE_SIZE//2
        self.finished_opening = False
        
        self.redraw()

    def update(self):
        if self.is_opening and not self.finished_opening:
            self.open_progress += 2 # Kecepatan animasi
            if self.open_progress >= TILE_SIZE // 2:
                self.open_progress = TILE_SIZE // 2
                self.finished_opening = True
            self.redraw()

    def redraw(self):
        self.image.fill((0,0,0,0)) # Clear transparan
        
        # Hitung lebar panel pintu saat ini (semakin progress nambah, semakin kecil)
        panel_width = (TILE_SIZE // 2) - self.open_progress
        
        if panel_width > 0:
            # Panel Kiri
            left_rect = pygame.Rect(0, 0, panel_width, TILE_SIZE)
            pygame.draw.rect(self.image, (101, 67, 33), left_rect) # Coklat Tua
            pygame.draw.rect(self.image, (60, 40, 20), left_rect, 4) # Border
            
            # Panel Kanan
            right_rect = pygame.Rect(TILE_SIZE - panel_width, 0, panel_width, TILE_SIZE)
            pygame.draw.rect(self.image, (101, 67, 33), right_rect)
            pygame.draw.rect(self.image, (60, 40, 20), right_rect, 4)
            
            # Gagang Pintu (Ikut bergeser)
            if panel_width > 10:
                pygame.draw.circle(self.image, (255, 215, 0), (panel_width - 10, TILE_SIZE//2), 6) # Kiri
                pygame.draw.circle(self.image, (255, 215, 0), (TILE_SIZE - panel_width + 10, TILE_SIZE//2), 6) # Kanan

class Portal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE
        self.timer = 0
        
    def update(self):
        self.timer += 0.1
        self.image.fill((0,0,0,0))
        
        center = (TILE_SIZE//2, TILE_SIZE//2)
        
        # Efek putaran portal
        max_radius = TILE_SIZE // 2 - 5
        for i in range(3):
            radius = max_radius - (i * 10) + (math.sin(self.timer + i) * 3)
            alpha = 150 + int(math.sin(self.timer * 2 + i) * 100)
            color = (100, 200, 255, alpha) # Biru langit bercahaya
            
            pygame.draw.circle(self.image, color, center, int(radius), 4)
        
        # Inti portal
        core_radius = 10 + abs(math.sin(self.timer * 3) * 5)
        pygame.draw.circle(self.image, (255, 255, 255), center, int(core_radius))

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