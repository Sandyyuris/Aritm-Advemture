import pygame
import sys
import math
import random

# --- IMPORT MODULE ---
import map_labirin
import animasi_jalan

# --- KONFIGURASI UMUM ---
FPS = 60

# WARNA MENU
COLOR_SKY_TOP = (0, 102, 204)        
COLOR_SKY_BOTTOM = (100, 180, 255)   
COLOR_BTN_BASE = (255, 200, 0)      
COLOR_BTN_HOVER = (255, 230, 50)    
COLOR_BTN_HIGHLIGHT = (255, 255, 180) 
COLOR_BTN_SHADOW = (180, 130, 0)     
COLOR_TEXT = (50, 30, 10)        

def create_background_map(screen_w, screen_h):
    """Membuat surface background yang berisi map labirin transparan"""
    bg_tile_size = 60
    cols = screen_w // bg_tile_size + 2
    rows = (screen_h // 2) // bg_tile_size + 2 

    maze_data, w, h = map_labirin.generate_maze(cols, rows)
    
    map_surface = pygame.Surface((w * bg_tile_size, h * bg_tile_size))
    map_surface.fill((0, 0, 0)) 
    map_surface.set_colorkey((0,0,0)) 
    for r in range(h):
        for c in range(w):
            x = c * bg_tile_size
            y = r * bg_tile_size
            
            # Gambar Rumput
            pygame.draw.rect(map_surface, (100, 180, 50), (x, y, bg_tile_size, bg_tile_size))
            
            # Jika Tembok
            if maze_data[r][c] == 1:
                pygame.draw.rect(map_surface, (255, 215, 0), (x, y, bg_tile_size, bg_tile_size))
                pygame.draw.rect(map_surface, (184, 134, 11), (x, y, bg_tile_size, bg_tile_size), 4)
                pygame.draw.line(map_surface, (184, 134, 11), (x, y+bg_tile_size//2), (x+bg_tile_size, y+bg_tile_size//2), 2)

    map_surface.set_alpha(100)
    return map_surface

class Button:
    def __init__(self, text, x, y, width, height, action=None):
        self.text = text
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = (x, y)
        self.action = action
        self.is_hovered = False
        self.font = pygame.font.SysFont("Arial", 30, bold=True)

    def draw(self, screen):
        color = COLOR_BTN_HOVER if self.is_hovered else COLOR_BTN_BASE
        
        shadow_rect = self.rect.copy()
        shadow_rect.y += 6
        pygame.draw.rect(screen, COLOR_BTN_SHADOW, shadow_rect, border_radius=15)

        pygame.draw.rect(screen, color, self.rect, border_radius=15)
        
        highlight_rect = pygame.Rect(self.rect.x + 5, self.rect.y + 5, self.rect.width - 10, self.rect.height // 2 - 5)
        pygame.draw.rect(screen, COLOR_BTN_HIGHLIGHT, highlight_rect, border_radius=10)

        text_surf = self.font.render(self.text, True, COLOR_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def click(self):
        if self.is_hovered and self.action:
            self.action()

def run_game(screen):
    """Loop Game Utama"""
    clock = pygame.time.Clock()
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()

    maze_data, w, h = map_labirin.generate_maze(25, 21)
    
    all_sprites = pygame.sprite.Group()
    wall_sprites = pygame.sprite.Group()
    floor_sprites = pygame.sprite.Group()

    for row in range(h):
        for col in range(w):
            floor = map_labirin.GrassTile(col, row)
            floor_sprites.add(floor)
            if maze_data[row][col] == 1:
                wall = map_labirin.DetailedWall(col, row)
                wall_sprites.add(wall)
                
    # Posisi Spawn Player
    spawn_tile_x, spawn_tile_y = 1, 1
    px = spawn_tile_x * map_labirin.TILE_SIZE + map_labirin.TILE_SIZE // 2
    py = spawn_tile_y * map_labirin.TILE_SIZE + map_labirin.TILE_SIZE // 2

    CHAR_VISUAL_WIDTH = 130
    CHAR_VISUAL_HEIGHT = 160
    HITBOX_WIDTH = 50
    HITBOX_HEIGHT = 30
    PLAYER_SPEED = 8

    walk_cycle = 0
    facing_right = True
    anim_state = 2 

    # Kamera
    class GameCamera:
        def __init__(self, width, height, screen_w, screen_h):
            self.camera = pygame.Rect(0, 0, width, height)
            self.width = width
            self.height = height
            self.screen_w = screen_w
            self.screen_h = screen_h

        def apply(self, entity_rect):
            return entity_rect.move(self.camera.topleft)
        
        def update(self, target_rect):
            x = -target_rect.centerx + int(self.screen_w / 2)
            y = -target_rect.centery + int(self.screen_h / 2)
            x = min(0, max(-(self.width - self.screen_w), x))
            y = min(0, max(-(self.height - self.screen_h), y))
            self.camera = pygame.Rect(x, y, self.width, self.height)

    total_map_w = w * map_labirin.TILE_SIZE
    total_map_h = h * map_labirin.TILE_SIZE
    camera = GameCamera(total_map_w, total_map_h, SCREEN_WIDTH, SCREEN_HEIGHT)

    player_hitbox = pygame.Rect(0, 0, HITBOX_WIDTH, HITBOX_HEIGHT)
    player_hitbox.center = (px, py)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT" # Keluar total
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "MENU" # Kembali ke menu

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        is_moving = False

        if keys[pygame.K_LEFT]:
            dx = -PLAYER_SPEED; anim_state = 0; facing_right = False; is_moving = True
        elif keys[pygame.K_RIGHT]:
            dx = PLAYER_SPEED; anim_state = 0; facing_right = True; is_moving = True
        elif keys[pygame.K_UP]:
            dy = -PLAYER_SPEED; anim_state = 1; is_moving = True
        elif keys[pygame.K_DOWN]:
            dy = PLAYER_SPEED; anim_state = 2; is_moving = True

        player_hitbox.x += dx
        hits = [wall for wall in wall_sprites if player_hitbox.colliderect(wall.rect)]
        if hits: player_hitbox.x -= dx 
        
        player_hitbox.y += dy
        hits = [wall for wall in wall_sprites if player_hitbox.colliderect(wall.rect)]
        if hits: player_hitbox.y -= dy

        if is_moving: walk_cycle += 0.25
        else: 
            walk_cycle = 0
            if anim_state == 0: walk_cycle = 0 
        
        camera.update(player_hitbox)

        # RENDER
        screen.fill((20, 20, 30))
        
        view_margin = 200 
        for sprite in floor_sprites:
            offset_pos = camera.apply(sprite.rect)
            if -view_margin < offset_pos.x < SCREEN_WIDTH + view_margin and \
            -view_margin < offset_pos.y < SCREEN_HEIGHT + view_margin:
                screen.blit(sprite.image, offset_pos)

        for sprite in wall_sprites:
            offset_pos = camera.apply(sprite.rect)
            if -view_margin < offset_pos.x < SCREEN_WIDTH + view_margin and \
            -view_margin < offset_pos.y < SCREEN_HEIGHT + view_margin:
                screen.blit(sprite.image, offset_pos)

        player_img = animasi_jalan.get_player_image(
            anim_state, walk_cycle, facing_right, CHAR_VISUAL_WIDTH, CHAR_VISUAL_HEIGHT
        )
        visual_rect = player_img.get_rect()
        visual_rect.midbottom = (player_hitbox.centerx, player_hitbox.bottom + 10)
        
        final_draw_pos = camera.apply(visual_rect)
        screen.blit(player_img, final_draw_pos)

        # Info UI
        font_ui = pygame.font.SysFont("Arial", 20)
        text_esc = font_ui.render("Tekan [ESC] untuk Kembali ke Menu", True, (255, 255, 255))
        pygame.draw.rect(screen, (0,0,0), (10, 10, text_esc.get_width()+20, 40), border_radius=10)
        screen.blit(text_esc, (20, 20))

        pygame.display.flip()
        clock.tick(FPS)
    
    return "MENU"

# --- MAIN MENU ---
def main_menu():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Arithm-Adventure")
    
    w, h = screen.get_size()
    clock = pygame.time.Clock()

    bg_map = create_background_map(w, h)
    
    # State Control
    running = True
    current_state = "MENU" # MENU atau GAME

    # Tombol Action
    def start_game_action():
        nonlocal current_state
        current_state = "GAME"

    def quit_game_action():
        nonlocal running
        running = False

    # Buat Objek Tombol
    btn_play = Button("MULAI PETUALANGAN", w//2, h//2, 350, 80, start_game_action)
    btn_quit = Button("KELUAR", w//2, h//2 + 120, 350, 80, quit_game_action)
    buttons = [btn_play, btn_quit]

    # Font Judul
    title_font = pygame.font.SysFont("Verdana", 80, bold=True)
    subtitle_font = pygame.font.SysFont("Arial", 30, italic=True)

    while running:
        if current_state == "GAME":
            # Masuk ke loop game
            result = run_game(screen)
            if result == "QUIT":
                running = False
            else:
                current_state = "MENU" 
                pygame.mouse.set_visible(True) # Pastikan kursor muncul lagi
            continue

        # --- LOGIKA MENU ---
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for btn in buttons:
                        btn.click()

        for btn in buttons:
            btn.check_hover(mouse_pos)

        # 1. Background Gradient Biru (Atas)
        screen.fill(COLOR_SKY_TOP)
        pygame.draw.rect(screen, COLOR_SKY_BOTTOM, (0, h//2, w, h//2))

        # 2. Gambar Map Transparan di Bawah
        screen.blit(bg_map, (0, h - bg_map.get_height()))
        
        title_surf = title_font.render("ARITHM-ADVENTURE", True, (255, 215, 0))
        title_shadow = title_font.render("ARITHM-ADVENTURE", True, (0, 0, 0))
        
        title_rect = title_surf.get_rect(center=(w//2, h//4))
        screen.blit(title_shadow, (title_rect.x + 4, title_rect.y + 4))
        screen.blit(title_surf, title_rect)

        sub_surf = subtitle_font.render("Edisi Layar Lebar & Zoom", True, (200, 230, 255))
        sub_rect = sub_surf.get_rect(center=(w//2, h//4 + 70))
        screen.blit(sub_surf, sub_rect)

        # 4. Gambar Tombol
        for btn in buttons:
            btn.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_menu()