import pygame
import random

# --- KONFIGURASI MAP (ZOOMED IN) ---
# Ukuran tetap 100 agar tampilan tetap 'dekat' (Zoomed)
TILE_SIZE = 100 

# Warna Utama
COLOR_WALL_BASE = (255, 215, 0)      # Emas
COLOR_WALL_OUTLINE = (184, 134, 11)  # Coklat Emas
COLOR_GRASS_BASE = (100, 180, 50)    # Hijau Dasar

# Warna Detail Rumput (Variasi)
COLOR_GRASS_DARK = (80, 160, 40)
COLOR_GRASS_LIGHT = (130, 210, 80)
COLOR_DIRT = (120, 100, 50) # Sedikit bercak tanah

class GrassTile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(COLOR_GRASS_BASE)
        
        # tekstur titik
        for _ in range(10):
            dx = random.randint(0, TILE_SIZE-5)
            dy = random.randint(0, TILE_SIZE-5)
            pygame.draw.rect(self.image, COLOR_DIRT, (dx, dy, 4, 4))

        # tekstur rumput (garis-garis)
        for _ in range(40):
            gx = random.randint(5, TILE_SIZE-5)
            gy = random.randint(10, TILE_SIZE-5)
            color = random.choice([COLOR_GRASS_DARK, COLOR_GRASS_LIGHT])
            
            tilt = random.randint(-5, 5) 
            height = random.randint(8, 15)
            
            pygame.draw.line(self.image, color, (gx, gy), (gx + tilt, gy - height), 3)

        # Border tipis
        pygame.draw.rect(self.image, (90, 170, 40), (0, 0, TILE_SIZE, TILE_SIZE), 1)
        
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE

class DetailedWall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(COLOR_WALL_BASE)
        
        # Border Luar Tebal
        pygame.draw.rect(self.image, COLOR_WALL_OUTLINE, (0, 0, TILE_SIZE, TILE_SIZE), 5)
        
        # Pola Bata Besar
        pygame.draw.line(self.image, COLOR_WALL_OUTLINE, (0, TILE_SIZE//2), (TILE_SIZE, TILE_SIZE//2), 4)
        
        # Garis Vertikal (Selang-seling)
        # Baris Atas
        pygame.draw.line(self.image, COLOR_WALL_OUTLINE, (TILE_SIZE//2, 0), (TILE_SIZE//2, TILE_SIZE//2), 4)
        # Baris Bawah (Offset)
        pygame.draw.line(self.image, COLOR_WALL_OUTLINE, (TILE_SIZE//4, TILE_SIZE//2), (TILE_SIZE//4, TILE_SIZE), 4)
        pygame.draw.line(self.image, COLOR_WALL_OUTLINE, (TILE_SIZE*3//4, TILE_SIZE//2), (TILE_SIZE*3//4, TILE_SIZE), 4)
        
        # Shadow di bawah garis tengah
        pygame.draw.line(self.image, (218, 165, 32), (5, TILE_SIZE//2 + 5), (TILE_SIZE-5, TILE_SIZE//2 + 5), 2)

        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE

def generate_maze(width, height):
    # Pastikan ukuran ganjil
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