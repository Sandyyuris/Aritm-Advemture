import pygame
import cairo
import math
import map_labirin

COLOR_SKY_TOP = (0, 102, 204)
COLOR_SKY_BOTTOM = (100, 180, 255)
COLOR_BTN_BASE = (255, 200, 0)
COLOR_BTN_HOVER = (255, 230, 50)
COLOR_BTN_HIGHLIGHT = (255, 255, 180)
COLOR_BTN_SHADOW = (180, 130, 0)
COLOR_BTN_DISABLED = (150, 150, 150)
COLOR_TEXT = (50, 30, 10)

def cairo_to_pygame(surface):
    surface.flush()
    return pygame.image.frombuffer(surface.get_data(), (surface.get_width(), surface.get_height()), "BGRA")

def hex_to_rgb_norm(rgb_tuple):
    return (rgb_tuple[0]/255, rgb_tuple[1]/255, rgb_tuple[2]/255)

def draw_rounded_rect(ctx, x, y, w, h, r):
    ctx.new_sub_path()
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.arc(x + w - r, y + r, r, 3 * math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.close_path()

def create_background_map(screen_w, screen_h):
    bg_tile_size = 60
    cols = screen_w // bg_tile_size + 2
    rows = (screen_h // 2) // bg_tile_size + 2
    maze_data, w, h = map_labirin.generate_maze(cols, rows)
    
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w * bg_tile_size, h * bg_tile_size)
    ctx = cairo.Context(surface)
    ctx.set_source_rgba(0, 0, 0, 0) # Clear
    ctx.paint()

    for r in range(h):
        for c in range(w):
            x, y = c * bg_tile_size, r * bg_tile_size
            # Lantai
            ctx.rectangle(x, y, bg_tile_size, bg_tile_size)
            ctx.set_source_rgb(*hex_to_rgb_norm((100, 180, 50)))
            ctx.fill()
            
            # Dinding
            if maze_data[r][c] == 1:
                ctx.rectangle(x, y, bg_tile_size, bg_tile_size)
                ctx.set_source_rgb(*hex_to_rgb_norm((255, 215, 0)))
                ctx.fill()
                
                ctx.rectangle(x, y, bg_tile_size, bg_tile_size)
                ctx.set_source_rgb(*hex_to_rgb_norm((184, 134, 11)))
                ctx.set_line_width(4)
                ctx.stroke()
                
                ctx.move_to(x, y + bg_tile_size/2)
                ctx.line_to(x + bg_tile_size, y + bg_tile_size/2)
                ctx.set_line_width(2)
                ctx.stroke()

    pygame_surf = cairo_to_pygame(surface)
    pygame_surf.set_alpha(100)
    return pygame_surf

def draw_heart_cairo(size, color):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size)
    ctx = cairo.Context(surface)
    ctx.scale(size, size)
    
    ctx.move_to(0.5, 0.85)
    ctx.curve_to(0.2, 0.55, -0.1, 0.35, 0.5, 0.1)
    ctx.curve_to(1.1, 0.35, 0.8, 0.55, 0.5, 0.85)
    
    ctx.set_source_rgb(*hex_to_rgb_norm(color))
    ctx.fill_preserve()
    return cairo_to_pygame(surface)

heart_images = {} 
def draw_heart(screen, x, y, size, color):
    color_key = tuple(color)
    if (size, color_key) not in heart_images:
        heart_images[(size, color_key)] = draw_heart_cairo(size, color)
    img = heart_images[(size, color_key)]
    screen.blit(img, img.get_rect(center=(x, y)))

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
        
        # Shadow
        ctx.set_source_rgb(*hex_to_rgb_norm(shadow_color))
        draw_rounded_rect(ctx, 0, 6, self.width, self.height, 15)
        ctx.fill()
        
        # Base
        ctx.set_source_rgb(*hex_to_rgb_norm(color))
        draw_rounded_rect(ctx, 0, 0, self.width, self.height, 15)
        ctx.fill()
        
        # Highlight
        if is_highlight:
            ctx.set_source_rgba(*hex_to_rgb_norm(COLOR_BTN_HIGHLIGHT) + (0.5,))
            draw_rounded_rect(ctx, 5, 5, self.width - 10, self.height/2 - 5, 10)
            ctx.fill()
        return cairo_to_pygame(surface)

    def draw(self, screen):
        if self.enabled:
            color = COLOR_BTN_HOVER if self.is_hovered else COLOR_BTN_BASE
            shadow_color = COLOR_BTN_SHADOW
        else:
            color = COLOR_BTN_DISABLED
            shadow_color = (100, 100, 100)
            
        current_state = (self.enabled, self.is_hovered)
        if self.cache_surface is None or self.last_state != current_state:
            self.cache_surface = self.create_button_surface(color, shadow_color, self.enabled)
            self.last_state = current_state

        screen.blit(self.cache_surface, (self.rect.x, self.rect.y))
        
        text_color = COLOR_TEXT if self.enabled else (100, 100, 100)
        text_surf = self.font.render(self.text, True, text_color)
        screen.blit(text_surf, text_surf.get_rect(center=self.rect.center))
        
        if not self.enabled:
            lock_surf = self.font.render("🔒", True, (80, 80, 80))
            screen.blit(lock_surf, lock_surf.get_rect(midbottom=(self.rect.centerx, self.rect.top - 5)))

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos) if self.enabled else False

    def click(self):
        if self.enabled and self.is_hovered and self.action:
            self.action()