import pygame
import cairo
import math
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

def cairo_to_pygame(surface):
    """Helper untuk mengubah surface Cairo ke surface Pygame"""
    surface.flush()
    data = surface.get_data()
    # Cairo menggunakan format ARGB, tapi pygame membacanya sebagai BGRA di buffer
    return pygame.image.frombuffer(data, (surface.get_width(), surface.get_height()), "BGRA")

def hex_to_rgb_norm(rgb_tuple):
    """Mengubah warna (255, 255, 255) menjadi (1.0, 1.0, 1.0) untuk Cairo"""
    return (rgb_tuple[0]/255, rgb_tuple[1]/255, rgb_tuple[2]/255)

def draw_rounded_rect(ctx, x, y, w, h, r):
    """Menggambar kotak dengan sudut tumpul (Rounded Rect) di Cairo"""
    ctx.new_sub_path()
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.arc(x + w - r, y + r, r, 3 * math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.close_path()

def create_background_map(screen_w, screen_h):
    """Membuat surface background yang berisi map labirin transparan menggunakan Cairo"""
    bg_tile_size = 60
    cols = screen_w // bg_tile_size + 2
    rows = (screen_h // 2) // bg_tile_size + 2

    maze_data, w, h = map_labirin.generate_maze(cols, rows)
    
    # Setup Cairo
    width_px = w * bg_tile_size
    height_px = h * bg_tile_size
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width_px, height_px)
    ctx = cairo.Context(surface)
    
    # Background Hitam Transparan (Clear)
    ctx.set_source_rgba(0, 0, 0, 0)
    ctx.paint()

    for r in range(h):
        for c in range(w):
            x = c * bg_tile_size
            y = r * bg_tile_size
            
            # Gambar Lantai (Hijau)
            ctx.rectangle(x, y, bg_tile_size, bg_tile_size)
            ctx.set_source_rgb(*hex_to_rgb_norm((100, 180, 50)))
            ctx.fill()
            
            if maze_data[r][c] == 1:
                # Gambar Dinding (Emas)
                ctx.rectangle(x, y, bg_tile_size, bg_tile_size)
                ctx.set_source_rgb(*hex_to_rgb_norm((255, 215, 0)))
                ctx.fill()
                
                # Outline Dinding
                ctx.rectangle(x, y, bg_tile_size, bg_tile_size)
                ctx.set_source_rgb(*hex_to_rgb_norm((184, 134, 11)))
                ctx.set_line_width(4)
                ctx.stroke()
                
                # Garis Detail
                ctx.move_to(x, y + bg_tile_size/2)
                ctx.line_to(x + bg_tile_size, y + bg_tile_size/2)
                ctx.set_line_width(2)
                ctx.stroke()

    # Convert ke Pygame dan set alpha
    pygame_surf = cairo_to_pygame(surface)
    pygame_surf.set_alpha(100)
    return pygame_surf

def draw_heart_cairo(size, color):
    """Membuat gambar hati menggunakan kurva Bezier Cairo"""
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size)
    ctx = cairo.Context(surface)
    
    # Normalisasi koordinat agar gambar pas di tengah surface size x size
    ctx.scale(size, size)
    
    # Gambar Hati
    ctx.move_to(0.5, 0.85)
    ctx.curve_to(0.2, 0.55, -0.1, 0.35, 0.5, 0.1)
    ctx.curve_to(1.1, 0.35, 0.8, 0.55, 0.5, 0.85)
    
    ctx.set_source_rgb(*hex_to_rgb_norm(color))
    ctx.fill_preserve()
    # ctx.set_source_rgba(0,0,0,0.2) # Optional outline
    # ctx.set_line_width(0.02)
    # ctx.stroke()
    
    return cairo_to_pygame(surface)

# Cache gambar hati agar tidak render ulang setiap frame
heart_images = {} 

def draw_heart(screen, x, y, size, color):
    """Wrapper untuk menggambar hati yang sudah dicache"""
    color_key = tuple(color)
    if (size, color_key) not in heart_images:
        heart_images[(size, color_key)] = draw_heart_cairo(size, color)
    
    img = heart_images[(size, color_key)]
    rect = img.get_rect(center=(x, y))
    screen.blit(img, rect)

class Button:
    def __init__(self, text, x, y, width, height, action=None, enabled=True, font_size=30):
        self.text = text
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = (x, y)
        self.width = width
        self.height = height
        self.action = action
        self.is_hovered = False
        self.enabled = enabled
        self.font = pygame.font.SysFont("Arial", font_size, bold=True)
        self.cache_surface = None
        self.last_state = None

    def create_button_surface(self, color, shadow_color, is_highlight):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height + 6)
        ctx = cairo.Context(surface)
        
        # Shadow (Bagian Bawah)
        ctx.set_source_rgb(*hex_to_rgb_norm(shadow_color))
        draw_rounded_rect(ctx, 0, 6, self.width, self.height, 15)
        ctx.fill()
        
        # Base Button
        ctx.set_source_rgb(*hex_to_rgb_norm(color))
        draw_rounded_rect(ctx, 0, 0, self.width, self.height, 15)
        ctx.fill()
        
        # Highlight (Kilauan atas)
        if is_highlight:
            ctx.set_source_rgba(*hex_to_rgb_norm(COLOR_BTN_HIGHLIGHT) + (0.5,)) # Transparan
            draw_rounded_rect(ctx, 5, 5, self.width - 10, self.height/2 - 5, 10)
            ctx.fill()
            
        return cairo_to_pygame(surface)

    def draw(self, screen):
        # Tentukan Warna
        if self.enabled:
            color = COLOR_BTN_HOVER if self.is_hovered else COLOR_BTN_BASE
            shadow_color = COLOR_BTN_SHADOW
        else:
            color = COLOR_BTN_DISABLED
            shadow_color = (100, 100, 100)
            
        # Cek apakah perlu render ulang (Optimization)
        current_state = (self.enabled, self.is_hovered)
        if self.cache_surface is None or self.last_state != current_state:
            self.cache_surface = self.create_button_surface(color, shadow_color, self.enabled)
            self.last_state = current_state

        # Blit tombol base
        screen.blit(self.cache_surface, (self.rect.x, self.rect.y))
        
        # Text (Tetap pakai Pygame Font agar tajam dan mudah)
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