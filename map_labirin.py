import pygame
import random
import sys

# --- KONFIGURASI ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 64
MAP_WIDTH = 25
MAP_HEIGHT = 25
CAMERA_SPEED = 10

# --- PALET WARNA BARU ---
# Kuning untuk Tembok (Nuansa Emas/Batu Bata)
COLOR_WALL_BASE = (255, 215, 0)      # Emas Terang
COLOR_WALL_SHADOW = (218, 165, 32)   # Emas Gelap (Goldenrod)
COLOR_WALL_HIGHLIGHT = (255, 255, 224)# Kuning Pucat (Highlight)
COLOR_WALL_OUTLINE = (184, 134, 11)  # Coklat Emas Gelap

# Hijau untuk Rumput
COLOR_GRASS_BASE = (100, 180, 50)    # Hijau Rumput Segar
COLOR_GRASS_DARK = (60, 140, 30)     # Hijau Gelap (Detail)
COLOR_GRASS_LIGHT = (130, 200, 80)   # Hijau Terang (Detail)

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target_rect):
        x = -target_rect.centerx + int(SCREEN_WIDTH / 2)
        y = -target_rect.centery + int(SCREEN_HEIGHT / 2)
        
        # Batasi kamera agar tidak keluar map
        x = min(0, max(-(self.width - SCREEN_WIDTH), x))
        y = min(0, max(-(self.height - SCREEN_HEIGHT), y))
        
        self.camera = pygame.Rect(x, y, self.width, self.height)

class GrassTile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(COLOR_GRASS_BASE)
        
        # Tambahkan detail rumput (garis-garis acak)
        for _ in range(15): # 15 helai rumput per kotak
            gx = random.randint(5, TILE_SIZE-5)
            gy = random.randint(5, TILE_SIZE-5)
            color = random.choice([COLOR_GRASS_DARK, COLOR_GRASS_LIGHT])
            # Gambar helai rumput kecil
            pygame.draw.line(self.image, color, (gx, gy), (gx + random.randint(-2, 2), gy - random.randint(3, 8)), 2)
            
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE

class DetailedWall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(COLOR_WALL_BASE)
        
        # 1. Gambar pola batu bata
        brick_height = TILE_SIZE // 3
        for i in range(3): # 3 baris bata
            by = i * brick_height
            # Geser bata setiap baris genap
            offset = (TILE_SIZE // 2) if i % 2 == 0 else 0
            
            # Garis horizontal antar bata
            pygame.draw.line(self.image, COLOR_WALL_OUTLINE, (0, by), (TILE_SIZE, by), 3)
            
            # Garis vertikal (pemisah bata)
            pygame.draw.line(self.image, COLOR_WALL_OUTLINE, (offset, by), (offset, by + brick_height), 3)
            pygame.draw.line(self.image, COLOR_WALL_OUTLINE, (offset + TILE_SIZE//2 + 2, by), (offset + TILE_SIZE//2 + 2, by + brick_height), 3)

            # Tambahkan shading/highlight pada bata agar terlihat timbul (3D effect)
            # Bagian bawah bata (gelap)
            pygame.draw.rect(self.image, COLOR_WALL_SHADOW, (0, by + brick_height - 5, TILE_SIZE, 5))
            # Bagian atas bata (terang)
            pygame.draw.rect(self.image, COLOR_WALL_HIGHLIGHT, (0, by, TILE_SIZE, 3))

        # Border luar tebal
        pygame.draw.rect(self.image, COLOR_WALL_OUTLINE, (0, 0, TILE_SIZE, TILE_SIZE), 3)

        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE

# --- GENERATOR LABIRIN ---
def generate_maze(width, height):
    maze = [[1 for _ in range(width)] for _ in range(height)]
    def carve(x, y):
        maze[y][x] = 0
        directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 < nx < width and 0 < ny < height and maze[ny][nx] == 1:
                maze[y + dy // 2][x + dx // 2] = 0
                carve(nx, ny)
    carve(1, 1)
    return maze

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Visual Map: Kuning & Rumput")
    clock = pygame.time.Clock()

    # Grup Sprite
    all_sprites = pygame.sprite.Group()
    wall_sprites = pygame.sprite.Group()
    floor_sprites = pygame.sprite.Group()

    # Generate Data Labirin
    actual_w = MAP_WIDTH if MAP_WIDTH % 2 != 0 else MAP_WIDTH + 1
    actual_h = MAP_HEIGHT if MAP_HEIGHT % 2 != 0 else MAP_HEIGHT + 1
    maze_grid = generate_maze(actual_w, actual_h)

    # Buat Objek Visual dari Data Labirin
    print("Membangun map...")
    for row in range(actual_h):
        for col in range(actual_w):
            # Kita buat lantai di SEMUA tempat dulu (di bawah tembok juga ada tanahnya)
            floor = GrassTile(col, row)
            floor_sprites.add(floor)
            all_sprites.add(floor)

            if maze_grid[row][col] == 1:
                wall = DetailedWall(col, row)
                wall_sprites.add(wall)
                all_sprites.add(wall)

    # Setup Kamera (Dummy Target untuk navigasi map)
    total_map_w = actual_w * TILE_SIZE
    total_map_h = actual_h * TILE_SIZE
    camera = Camera(total_map_w, total_map_h)
    
    # Titik tengah kamera (dummy object invisible)
    camera_target = pygame.Rect(TILE_SIZE*2, TILE_SIZE*2, TILE_SIZE, TILE_SIZE)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- KONTROL KAMERA MANUAL (Panah) ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: camera_target.x -= CAMERA_SPEED
        if keys[pygame.K_RIGHT]: camera_target.x += CAMERA_SPEED
        if keys[pygame.K_UP]: camera_target.y -= CAMERA_SPEED
        if keys[pygame.K_DOWN]: camera_target.y += CAMERA_SPEED

        # Update Kamera
        camera.update(camera_target)

        # Draw
        screen.fill((0, 0, 0)) # Background hitam (jika ada yang tidak tertutup)

        # Gambar Lantai Dulu
        for sprite in floor_sprites:
            offset_rect = camera.apply(sprite.rect)
            if -TILE_SIZE < offset_rect.x < SCREEN_WIDTH and -TILE_SIZE < offset_rect.y < SCREEN_HEIGHT:
                screen.blit(sprite.image, offset_rect)

        # Gambar Tembok Kemudian (di atas lantai)
        for sprite in wall_sprites:
            offset_rect = camera.apply(sprite.rect)
            if -TILE_SIZE < offset_rect.x < SCREEN_WIDTH and -TILE_SIZE < offset_rect.y < SCREEN_HEIGHT:
                screen.blit(sprite.image, offset_rect)

        # Info Kontrol
        font = pygame.font.Font(None, 36)
        text = font.render("Gunakan PANAH untuk geser Map", True, (255, 255, 255))
        screen.blit(text, (20, 20))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()