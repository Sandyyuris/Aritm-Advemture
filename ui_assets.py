import pygame
import map_labirin

# --- WARNA UI ---
COLOR_SKY_TOP = (0, 102, 204)
COLOR_SKY_BOTTOM = (100, 180, 255)
COLOR_BTN_BASE = (255, 200, 0)
COLOR_BTN_HOVER = (255, 230, 50)
COLOR_BTN_HIGHLIGHT = (255, 255, 180)
COLOR_BTN_SHADOW = (180, 130, 0)
COLOR_BTN_DISABLED = (150, 150, 150)
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
            pygame.draw.rect(map_surface, (100, 180, 50), (x, y, bg_tile_size, bg_tile_size))
            if maze_data[r][c] == 1:
                pygame.draw.rect(map_surface, (255, 215, 0), (x, y, bg_tile_size, bg_tile_size))
                pygame.draw.rect(map_surface, (184, 134, 11), (x, y, bg_tile_size, bg_tile_size), 4)
                pygame.draw.line(map_surface, (184, 134, 11), (x, y+bg_tile_size//2), (x+bg_tile_size, y+bg_tile_size//2), 2)
    map_surface.set_alpha(100)
    return map_surface

def draw_heart(surface, x, y, size, color):
    """Menggambar bentuk hati yang cantik"""
    radius = size // 4
    circle_offset = int(radius * 0.8)
    
    # Lingkaran kiri & kanan
    pygame.draw.circle(surface, color, (x - circle_offset, y - radius), radius)
    pygame.draw.circle(surface, color, (x + circle_offset, y - radius), radius)
    
    # Segitiga bawah
    points = [
        (x - size // 2, y - radius * 0.8), 
        (x + size // 2, y - radius * 0.8), 
        (x, y + size // 2)                 
    ]
    pygame.draw.polygon(surface, color, points)

class Button:
    def __init__(self, text, x, y, width, height, action=None, enabled=True, font_size=30):
        self.text = text
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = (x, y)
        self.action = action
        self.is_hovered = False
        self.enabled = enabled
        self.font = pygame.font.SysFont("Arial", font_size, bold=True)

    def draw(self, screen):
        if self.enabled:
            color = COLOR_BTN_HOVER if self.is_hovered else COLOR_BTN_BASE
            shadow_color = COLOR_BTN_SHADOW
        else:
            color = COLOR_BTN_DISABLED
            shadow_color = (100, 100, 100)

        shadow_rect = self.rect.copy()
        shadow_rect.y += 6
        pygame.draw.rect(screen, shadow_color, shadow_rect, border_radius=15)
        pygame.draw.rect(screen, color, self.rect, border_radius=15)
        
        if self.enabled:
            highlight_rect = pygame.Rect(self.rect.x + 5, self.rect.y + 5, self.rect.width - 10, self.rect.height // 2 - 5)
            pygame.draw.rect(screen, COLOR_BTN_HIGHLIGHT, highlight_rect, border_radius=10)
        
        text_color = COLOR_TEXT if self.enabled else (100, 100, 100)
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
        if not self.enabled:
            lock_surf = self.font.render("🔒", True, (80, 80, 80))
            lock_rect = lock_surf.get_rect(midbottom=(self.rect.centerx, self.rect.top - 5))
            screen.blit(lock_surf, lock_rect)

    def check_hover(self, mouse_pos):
        if self.enabled:
            self.is_hovered = self.rect.collidepoint(mouse_pos)
        else:
            self.is_hovered = False

    def click(self):
        if self.enabled and self.is_hovered and self.action:
            self.action()