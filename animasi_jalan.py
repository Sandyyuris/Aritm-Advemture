import pygame
import cairo
import math
import sys

# --- KONFIGURASI GLOBAL ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
CHAR_SCALE = 3
CAIRO_WIDTH, CAIRO_HEIGHT = 640, 800  # 128*5, 160*5
CENTER_X = CAIRO_WIDTH // 2
BG_COLOR = (50, 50, 60)

# --- PALET WARNA ---
COLORS = {
    "SKIN": (0.92, 0.78, 0.62),
    "SKIN_SHADOW": (0.82, 0.68, 0.52),
    "HAT": (0.45, 0.30, 0.15),
    "HAT_BAND": (0.25, 0.15, 0.05),
    "SHIRT": (0.85, 0.80, 0.60),
    "SHIRT_DARK": (0.75, 0.70, 0.50),
    "VEST": (0.50, 0.40, 0.25),
    "PANTS": (0.30, 0.35, 0.40),
    "BOOTS": (0.25, 0.15, 0.05),
    "BACKPACK": (0.40, 0.35, 0.20),
    "BACKPACK_DETAIL": (0.45, 0.40, 0.25),
    "STRAP": (0.35, 0.30, 0.15)
}

def rounded_rect(ctx, x, y, w, h, r):
    ctx.new_sub_path()
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.arc(x + w - r, y + r, r, 3 * math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.close_path()

def draw_adventurer_front_fixed(walk_cycle):
    """Tampak DEPAN (Gerakan Naik-Turun)"""
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, CAIRO_WIDTH, CAIRO_HEIGHT)
    ctx = cairo.Context(surface)
    ctx.scale(5, 5)
    
    cx = 64
    offset = math.sin(walk_cycle) * 4 
    body_bob = abs(math.sin(walk_cycle)) * 1.5

    # --- LAYER 1: KAKI ---
    # Kiri
    leg_left_y = 100 + (offset if offset > 0 else 0)
    ctx.set_source_rgb(*COLORS["PANTS"])
    rounded_rect(ctx, cx - 21, leg_left_y, 22, 45, 6)
    ctx.fill()
    ctx.set_source_rgb(*COLORS["BOOTS"])
    rounded_rect(ctx, cx - 22, leg_left_y + 35, 24, 18, 5) 
    ctx.fill()

    # Kanan
    leg_right_y = 100 + (-offset if -offset > 0 else 0)
    ctx.set_source_rgb(*COLORS["PANTS"])
    rounded_rect(ctx, cx - 1, leg_right_y, 22, 45, 6)
    ctx.fill()
    ctx.set_source_rgb(*COLORS["BOOTS"])
    rounded_rect(ctx, cx - 2, leg_right_y + 35, 24, 18, 5)
    ctx.fill()

    # --- LAYER 2: LENGAN ---
    # Kiri
    arm_left_y = 55 + (-offset * 0.8) + body_bob
    ctx.set_source_rgb(*COLORS["SHIRT"])
    rounded_rect(ctx, cx - 39, arm_left_y, 18, 42, 6)
    ctx.fill()
    ctx.set_source_rgb(*COLORS["SKIN"])
    ctx.arc(cx - 30, arm_left_y + 44, 9, 0, 2*math.pi)
    ctx.fill()

    # Kanan
    arm_right_y = 55 + (offset * 0.8) + body_bob
    ctx.set_source_rgb(*COLORS["SHIRT"])
    rounded_rect(ctx, cx + 21, arm_right_y, 18, 42, 6)
    ctx.fill()
    ctx.set_source_rgb(*COLORS["SKIN"])
    ctx.arc(cx + 30, arm_right_y + 44, 9, 0, 2*math.pi)
    ctx.fill()

    # --- LAYER 3: BADAN ---
    body_y = 50 + body_bob
    
    # Baju & Tali
    ctx.set_source_rgb(*COLORS["SHIRT"])
    rounded_rect(ctx, cx - 22, body_y, 44, 60, 10) 
    ctx.fill()
    ctx.set_source_rgb(*COLORS["STRAP"])
    rounded_rect(ctx, cx - 18, body_y + 2, 6, 40, 2)
    ctx.fill()
    rounded_rect(ctx, cx + 12, body_y + 2, 6, 40, 2)
    ctx.fill()

    # Rompi & Sabuk
    ctx.set_source_rgb(*COLORS["VEST"])
    rounded_rect(ctx, cx - 22, body_y, 16, 55, 8)
    ctx.fill()
    rounded_rect(ctx, cx + 6, body_y, 16, 55, 8)
    ctx.fill()
    ctx.set_source_rgb(*COLORS["HAT_BAND"])
    rounded_rect(ctx, cx - 20, body_y + 50, 40, 8, 2)
    ctx.fill()

    # --- LAYER 4: KEPALA & WAJAH ---
    head_y = 35 + body_bob
    
    ctx.set_source_rgb(*COLORS["SKIN"])
    rounded_rect(ctx, cx - 8, head_y + 5, 16, 15, 4) # Leher
    ctx.fill()
    ctx.arc(cx, head_y, 23, 0, 2 * math.pi) # Kepala
    ctx.fill()

    # Mata & Detail
    eye_y = head_y + 1
    eye_offset = 9
    ctx.set_source_rgb(1, 1, 1)
    ctx.arc(cx - eye_offset, eye_y, 5.5, 0, 2 * math.pi)
    ctx.fill()
    ctx.arc(cx + eye_offset, eye_y, 5.5, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_source_rgb(0.1, 0.05, 0.0)
    ctx.arc(cx - eye_offset, eye_y, 3, 0, 2 * math.pi)
    ctx.fill()
    ctx.arc(cx + eye_offset, eye_y, 3, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_source_rgb(1, 1, 1)
    ctx.arc(cx - eye_offset + 1.5, eye_y - 1.5, 1.2, 0, 2 * math.pi)
    ctx.fill()
    ctx.arc(cx + eye_offset + 1.5, eye_y - 1.5, 1.2, 0, 2 * math.pi)
    ctx.fill()
    
    # Hidung & Mulut
    ctx.set_source_rgb(0.7, 0.3, 0.2)
    ctx.arc(cx, eye_y + 6, 1.5, 0, 2*math.pi)
    ctx.fill()
    ctx.set_line_width(2)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.new_sub_path()
    ctx.arc(cx, eye_y + 8, 6, 0.2 * math.pi, 0.8 * math.pi)
    ctx.stroke()

    # --- LAYER 5: TOPI ---
    ctx.set_source_rgb(*COLORS["HAT"])
    ctx.save()
    ctx.translate(cx, head_y - 10)
    ctx.scale(1, 0.5) 
    ctx.arc(0, 0, 38, 0, 2 * math.pi)
    ctx.restore()
    ctx.fill()

    ctx.set_source_rgb(*COLORS["HAT"])
    rounded_rect(ctx, cx - 22, head_y - 30, 44, 25, 10) 
    ctx.fill()
    ctx.set_source_rgb(*COLORS["HAT_BAND"])
    rounded_rect(ctx, cx - 22, head_y - 13, 44, 6, 3)
    ctx.fill()

    return surface

def draw_adventurer_back_fixed(walk_cycle):
    """Tampak BELAKANG (Gerakan Naik-Turun)"""
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, CAIRO_WIDTH, CAIRO_HEIGHT)
    ctx = cairo.Context(surface)
    ctx.scale(5, 5)
    
    cx = 64
    offset = math.sin(walk_cycle) * 4 
    
    # --- LAYER 1: ANGGOTA GERAK ---
    # Kaki Kiri
    leg_left_y = 100 + (offset if offset > 0 else 0) 
    ctx.set_source_rgb(*COLORS["PANTS"])
    rounded_rect(ctx, cx - 21, leg_left_y, 22, 45, 6)
    ctx.fill()
    ctx.set_source_rgb(*COLORS["BOOTS"])
    rounded_rect(ctx, cx - 22, leg_left_y + 35, 24, 18, 5)
    ctx.fill()

    # Kaki Kanan
    leg_right_y = 100 + (-offset if -offset > 0 else 0)
    ctx.set_source_rgb(*COLORS["PANTS"])
    rounded_rect(ctx, cx - 1, leg_right_y, 22, 45, 6)
    ctx.fill()
    ctx.set_source_rgb(*COLORS["BOOTS"])
    rounded_rect(ctx, cx - 2, leg_right_y + 35, 24, 18, 5)
    ctx.fill()

    # Tangan Kiri
    arm_left_y = 55 + (-offset * 0.8)
    ctx.set_source_rgb(*COLORS["SHIRT"])
    rounded_rect(ctx, cx - 39, arm_left_y, 18, 42, 6)
    ctx.fill()
    ctx.set_source_rgb(*COLORS["SKIN"])
    ctx.arc(cx - 30, arm_left_y + 44, 9, 0, 2*math.pi)
    ctx.fill()

    # Tangan Kanan
    arm_right_y = 55 + (offset * 0.8)
    ctx.set_source_rgb(*COLORS["SHIRT"])
    rounded_rect(ctx, cx + 21, arm_right_y, 18, 42, 6)
    ctx.fill()
    ctx.set_source_rgb(*COLORS["SKIN"])
    ctx.arc(cx + 30, arm_right_y + 44, 9, 0, 2*math.pi)
    ctx.fill()

    # --- LAYER 2: BADAN & TAS ---
    body_bob = abs(math.sin(walk_cycle)) * 1.5
    body_y = 50 + body_bob

    ctx.set_source_rgb(*COLORS["SHIRT"])
    rounded_rect(ctx, cx - 22, body_y, 44, 60, 10) 
    ctx.fill()

    # Tas
    ctx.set_source_rgb(*COLORS["BACKPACK"])
    rounded_rect(ctx, cx - 28, body_y + 2, 56, 55, 12) 
    ctx.fill()
    ctx.set_source_rgb(*COLORS["BACKPACK_DETAIL"])
    rounded_rect(ctx, cx - 28, body_y + 2, 56, 20, 12)
    ctx.fill()
    rounded_rect(ctx, cx - 15, body_y + 30, 30, 20, 5)
    ctx.fill()

    # --- LAYER 3: KEPALA & TOPI ---
    head_y = 35 + body_bob

    ctx.set_source_rgb(*COLORS["SKIN"])
    rounded_rect(ctx, cx - 8, head_y + 5, 16, 15, 4)
    ctx.fill()
    ctx.arc(cx, head_y, 23, 0, 2 * math.pi)
    ctx.fill()
    
    ctx.set_source_rgb(*COLORS["HAT"])
    rounded_rect(ctx, cx - 22, head_y - 30, 44, 25, 10) 
    ctx.fill()
    ctx.set_source_rgb(*COLORS["HAT_BAND"])
    rounded_rect(ctx, cx - 22, head_y - 13, 44, 6, 3)
    ctx.fill()
    
    ctx.set_source_rgb(*COLORS["HAT"])
    ctx.save()
    ctx.translate(cx, head_y - 10)
    ctx.scale(1, 0.5) 
    ctx.arc(0, 0, 38, 0, 2 * math.pi)
    ctx.restore()
    ctx.fill()

    return surface

def draw_dynamic_character(swing_angle):
    """Tampak SAMPING (Gerakan Rotasi)"""
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, CAIRO_WIDTH, CAIRO_HEIGHT)
    ctx = cairo.Context(surface)
    ctx.scale(5, 5)
    
    cx = 64
    rad_angle = swing_angle * (math.pi / 180)

    # --- LAYER 1: KIRI (BELAKANG) ---
    # Tangan Kiri
    ctx.save()
    ctx.translate(cx, 55)
    ctx.rotate(-rad_angle)
    ctx.set_source_rgb(*COLORS["SHIRT_DARK"])
    rounded_rect(ctx, -9, 0, 18, 42, 6)
    ctx.fill()
    ctx.set_source_rgb(*COLORS["SKIN_SHADOW"])
    ctx.arc(0, 44, 9, 0, 2*math.pi)
    ctx.fill()
    ctx.restore()

    # Kaki Kiri
    ctx.save()
    ctx.translate(cx, 100) 
    ctx.rotate(rad_angle) 
    ctx.set_source_rgb(*COLORS["PANTS"])
    rounded_rect(ctx, -11, 0, 22, 45, 6)
    ctx.fill()
    ctx.set_source_rgb(*COLORS["BOOTS"])
    rounded_rect(ctx, -12, 35, 24, 18, 5)
    ctx.fill()
    ctx.restore()

    # --- LAYER 2: BADAN UTAMA ---
    ctx.set_source_rgb(*COLORS["BACKPACK"])
    rounded_rect(ctx, cx - 35, 55, 30, 50, 8) 
    ctx.fill()

    ctx.set_source_rgb(*COLORS["SHIRT"])
    rounded_rect(ctx, cx - 20, 50, 40, 60, 10) 
    ctx.fill()
    ctx.set_source_rgb(*COLORS["VEST"])
    rounded_rect(ctx, cx - 20, 50, 40, 60, 10)
    ctx.fill()
    ctx.set_source_rgb(*COLORS["HAT_BAND"])
    rounded_rect(ctx, cx - 20, 95, 40, 8, 2)
    ctx.fill()

    # Kepala
    ctx.set_source_rgb(*COLORS["SKIN"])
    rounded_rect(ctx, cx - 8, 40, 16, 15, 4)
    ctx.fill()
    ctx.arc(cx, 35, 23, 0, 2 * math.pi)
    ctx.fill()
    ctx.arc(cx + 20, 38, 4, 0, 2 * math.pi) # Hidung
    ctx.fill()

    # Mata
    eye_x, eye_y = cx + 14, 36
    ctx.set_source_rgb(1, 1, 1)
    ctx.save()
    ctx.translate(eye_x, eye_y)
    ctx.scale(0.8, 1.0)
    ctx.arc(0, 0, 5, 0, 2 * math.pi)
    ctx.restore()
    ctx.fill()
    ctx.set_source_rgb(0.1, 0.05, 0.0)
    ctx.arc(eye_x + 1, eye_y, 2.5, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_source_rgb(1, 1, 1)
    ctx.arc(eye_x + 2, eye_y - 1.5, 1, 0, 2 * math.pi)
    ctx.fill()
    
    ctx.set_source_rgb(0.6, 0.2, 0.2)
    ctx.move_to(cx + 12, eye_y + 12)
    ctx.line_to(cx + 20, eye_y + 10)
    ctx.set_line_width(1.2)
    ctx.stroke()
    
    ctx.set_source_rgb(*COLORS["SKIN_SHADOW"])
    ctx.move_to(cx - 6,  35)
    ctx.curve_to(cx -13, 30, cx -13, 45, cx - 7, 40)
    ctx.curve_to(cx -13, 45, cx - 2, 30, cx - 6, 35)
    ctx.fill()

    ctx.set_source_rgb(*COLORS["HAT"])
    rounded_rect(ctx, cx - 30 , 25, 62, 6, 3) 
    ctx.fill()
    rounded_rect(ctx, cx - 22, 5, 44, 25, 10)
    ctx.fill()
    ctx.set_source_rgb(*COLORS["HAT_BAND"])
    rounded_rect(ctx, cx - 22, 22, 44, 6, 3)
    ctx.fill()

    # --- LAYER 3: KANAN (DEPAN) ---
    # Kaki Kanan
    ctx.save()
    ctx.translate(cx, 100) 
    ctx.rotate(-rad_angle) 
    ctx.set_source_rgb(*COLORS["PANTS"])
    rounded_rect(ctx, -11, 0, 22, 45, 6) 
    ctx.fill()
    ctx.set_source_rgb(*COLORS["BOOTS"])
    rounded_rect(ctx, -12, 35, 24, 18, 5) 
    ctx.fill()
    ctx.restore()

    # Tangan Kanan
    ctx.save()
    ctx.translate(cx, 55)
    ctx.rotate(rad_angle)
    ctx.set_source_rgb(*COLORS["SHIRT"])
    rounded_rect(ctx, -9, 0, 18, 42, 6) 
    ctx.fill()
    ctx.set_source_rgb(*COLORS["SKIN"])
    ctx.arc(0, 44, 9, 0, 2*math.pi)
    ctx.fill()
    ctx.restore()

    return surface

def cairo_to_pygame(surface):
    surface.flush()
    data = surface.get_data()
    return pygame.image.frombuffer(data, (CAIRO_WIDTH, CAIRO_HEIGHT), "BGRA")

# --- MAIN PROGRAM ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Animasi Jalan - Pycairo x Pygame")
    clock = pygame.time.Clock()

    player_x = SCREEN_WIDTH // 2
    player_y = SCREEN_HEIGHT // 2 - 100
    player_speed = 4
    
    walk_cycle = 0
    is_facing_right = True
    direction_state = 2 # 0: Samping, 1: Belakang, 2: Depan

    # Pre-calculate ukuran
    final_w = int(CAIRO_WIDTH / 5 * CHAR_SCALE)
    final_h = int(CAIRO_HEIGHT / 5 * CHAR_SCALE)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        is_moving = False
        
        # --- INPUT HANDLING ---
        if keys[pygame.K_LEFT]:
            player_x -= player_speed
            is_moving = True
            is_facing_right = False
            direction_state = 0
            
        elif keys[pygame.K_RIGHT]:
            player_x += player_speed
            is_moving = True
            is_facing_right = True
            direction_state = 0
            
        elif keys[pygame.K_UP]:
            player_y -= player_speed
            is_moving = True
            direction_state = 1
            
        elif keys[pygame.K_DOWN]:
            player_y += player_speed
            is_moving = True
            direction_state = 2

        # --- UPDATE ANIMASI ---
        angle = 0
        if is_moving:
            walk_cycle += 0.2
            angle = math.sin(walk_cycle) * 30
        else:
            walk_cycle = 0

        # --- RENDER CHARACTER ---
        if direction_state == 1:
            cairo_surf = draw_adventurer_back_fixed(walk_cycle)
        elif direction_state == 2:
            cairo_surf = draw_adventurer_front_fixed(walk_cycle)
        else:
            cairo_surf = draw_dynamic_character(angle)

        pygame_img = cairo_to_pygame(cairo_surf)

        # Flip jika menghadap kiri (hanya mode samping)
        if direction_state == 0 and not is_facing_right:
            pygame_img = pygame.transform.flip(pygame_img, True, False)

        # Resize & Draw
        pygame_img = pygame.transform.smoothscale(pygame_img, (final_w, final_h))
        
        screen.fill(BG_COLOR)
        draw_x = player_x - (final_w // 2)
        draw_y = player_y - (final_h // 2)
        screen.blit(pygame_img, (draw_x, draw_y))
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()