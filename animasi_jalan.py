import pygame
import cairo
import math

# --- KONFIGURASI VISUAL ---
CAIRO_WIDTH, CAIRO_HEIGHT = 640, 800
BASE_SCALE = 5  

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
    """Tampak DEPAN Lengkap"""
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, CAIRO_WIDTH, CAIRO_HEIGHT)
    ctx = cairo.Context(surface)
    ctx.scale(BASE_SCALE, BASE_SCALE)
    
    cx = 64
    offset = math.sin(walk_cycle) * 4 
    body_bob = abs(math.sin(walk_cycle)) * 1.5

    # Kaki
    leg_left_y = 100 + (offset if offset > 0 else 0)
    ctx.set_source_rgb(*COLORS["PANTS"]); rounded_rect(ctx, cx - 21, leg_left_y, 22, 45, 6); ctx.fill()
    ctx.set_source_rgb(*COLORS["BOOTS"]); rounded_rect(ctx, cx - 22, leg_left_y + 35, 24, 18, 5); ctx.fill()

    leg_right_y = 100 + (-offset if -offset > 0 else 0)
    ctx.set_source_rgb(*COLORS["PANTS"]); rounded_rect(ctx, cx - 1, leg_right_y, 22, 45, 6); ctx.fill()
    ctx.set_source_rgb(*COLORS["BOOTS"]); rounded_rect(ctx, cx - 2, leg_right_y + 35, 24, 18, 5); ctx.fill()

    # Lengan
    arm_left_y = 55 + (-offset * 0.8) + body_bob
    ctx.set_source_rgb(*COLORS["SHIRT"]); rounded_rect(ctx, cx - 39, arm_left_y, 18, 42, 6); ctx.fill()
    ctx.set_source_rgb(*COLORS["SKIN"]); ctx.arc(cx - 30, arm_left_y + 44, 9, 0, 2*math.pi); ctx.fill()

    arm_right_y = 55 + (offset * 0.8) + body_bob
    ctx.set_source_rgb(*COLORS["SHIRT"]); rounded_rect(ctx, cx + 21, arm_right_y, 18, 42, 6); ctx.fill()
    ctx.set_source_rgb(*COLORS["SKIN"]); ctx.arc(cx + 30, arm_right_y + 44, 9, 0, 2*math.pi); ctx.fill()

    # Badan
    body_y = 50 + body_bob
    ctx.set_source_rgb(*COLORS["SHIRT"]); rounded_rect(ctx, cx - 22, body_y, 44, 60, 10); ctx.fill()
    ctx.set_source_rgb(*COLORS["STRAP"])
    rounded_rect(ctx, cx - 18, body_y + 2, 6, 40, 2); ctx.fill()
    rounded_rect(ctx, cx + 12, body_y + 2, 6, 40, 2); ctx.fill()
    ctx.set_source_rgb(*COLORS["VEST"])
    rounded_rect(ctx, cx - 22, body_y, 16, 55, 8); ctx.fill()
    rounded_rect(ctx, cx + 6, body_y, 16, 55, 8); ctx.fill()
    ctx.set_source_rgb(*COLORS["HAT_BAND"]); rounded_rect(ctx, cx - 20, body_y + 50, 40, 8, 2); ctx.fill()

    # Kepala
    head_y = 35 + body_bob
    ctx.set_source_rgb(*COLORS["SKIN"])
    rounded_rect(ctx, cx - 8, head_y + 5, 16, 15, 4); ctx.fill() 
    ctx.arc(cx, head_y, 23, 0, 2 * math.pi); ctx.fill()

    # Wajah
    eye_y = head_y + 1; eye_offset = 9
    ctx.set_source_rgb(1, 1, 1)
    ctx.arc(cx - eye_offset, eye_y, 5.5, 0, 2 * math.pi); ctx.fill()
    ctx.arc(cx + eye_offset, eye_y, 5.5, 0, 2 * math.pi); ctx.fill()
    ctx.set_source_rgb(0.1, 0.05, 0.0)
    ctx.arc(cx - eye_offset, eye_y, 3, 0, 2 * math.pi); ctx.fill()
    ctx.arc(cx + eye_offset, eye_y, 3, 0, 2 * math.pi); ctx.fill()
    ctx.set_source_rgb(1, 1, 1)
    ctx.arc(cx - eye_offset + 1.5, eye_y - 1.5, 1.2, 0, 2 * math.pi); ctx.fill()
    ctx.arc(cx + eye_offset + 1.5, eye_y - 1.5, 1.2, 0, 2 * math.pi); ctx.fill()
    
    ctx.set_source_rgb(0.7, 0.3, 0.2); ctx.arc(cx, eye_y + 6, 1.5, 0, 2*math.pi); ctx.fill() # Hidung
    ctx.set_line_width(2); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.new_sub_path()
    ctx.arc(cx, eye_y + 8, 6, 0.2 * math.pi, 0.8 * math.pi); ctx.stroke() # Mulut

    # Topi
    ctx.set_source_rgb(*COLORS["HAT"])
    ctx.save(); ctx.translate(cx, head_y - 10); ctx.scale(1, 0.5); ctx.arc(0, 0, 38, 0, 2 * math.pi); ctx.restore(); ctx.fill()
    ctx.set_source_rgb(*COLORS["HAT"]); rounded_rect(ctx, cx - 22, head_y - 30, 44, 25, 10); ctx.fill()
    ctx.set_source_rgb(*COLORS["HAT_BAND"]); rounded_rect(ctx, cx - 22, head_y - 13, 44, 6, 3); ctx.fill()

    return surface

def draw_adventurer_back_fixed(walk_cycle):
    """Tampak BELAKANG Lengkap"""
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, CAIRO_WIDTH, CAIRO_HEIGHT)
    ctx = cairo.Context(surface)
    ctx.scale(BASE_SCALE, BASE_SCALE)
    
    cx = 64
    offset = math.sin(walk_cycle) * 4 
    
    # Kaki
    leg_left_y = 100 + (offset if offset > 0 else 0) 
    ctx.set_source_rgb(*COLORS["PANTS"]); rounded_rect(ctx, cx - 21, leg_left_y, 22, 45, 6); ctx.fill()
    ctx.set_source_rgb(*COLORS["BOOTS"]); rounded_rect(ctx, cx - 22, leg_left_y + 35, 24, 18, 5); ctx.fill()

    leg_right_y = 100 + (-offset if -offset > 0 else 0)
    ctx.set_source_rgb(*COLORS["PANTS"]); rounded_rect(ctx, cx - 1, leg_right_y, 22, 45, 6); ctx.fill()
    ctx.set_source_rgb(*COLORS["BOOTS"]); rounded_rect(ctx, cx - 2, leg_right_y + 35, 24, 18, 5); ctx.fill()

    # Lengan
    arm_left_y = 55 + (-offset * 0.8)
    ctx.set_source_rgb(*COLORS["SHIRT"]); rounded_rect(ctx, cx - 39, arm_left_y, 18, 42, 6); ctx.fill()
    ctx.set_source_rgb(*COLORS["SKIN"]); ctx.arc(cx - 30, arm_left_y + 44, 9, 0, 2*math.pi); ctx.fill()

    arm_right_y = 55 + (offset * 0.8)
    ctx.set_source_rgb(*COLORS["SHIRT"]); rounded_rect(ctx, cx + 21, arm_right_y, 18, 42, 6); ctx.fill()
    ctx.set_source_rgb(*COLORS["SKIN"]); ctx.arc(cx + 30, arm_right_y + 44, 9, 0, 2*math.pi); ctx.fill()

    # Badan
    body_bob = abs(math.sin(walk_cycle)) * 1.5
    body_y = 50 + body_bob

    ctx.set_source_rgb(*COLORS["SHIRT"]); rounded_rect(ctx, cx - 22, body_y, 44, 60, 10); ctx.fill()

    # Tas
    ctx.set_source_rgb(*COLORS["BACKPACK"]); rounded_rect(ctx, cx - 28, body_y + 2, 56, 55, 12); ctx.fill()
    ctx.set_source_rgb(*COLORS["BACKPACK_DETAIL"])
    rounded_rect(ctx, cx - 28, body_y + 2, 56, 20, 12); ctx.fill()
    rounded_rect(ctx, cx - 15, body_y + 30, 30, 20, 5); ctx.fill()

    # Kepala
    head_y = 35 + body_bob
    ctx.set_source_rgb(*COLORS["SKIN"]); rounded_rect(ctx, cx - 8, head_y + 5, 16, 15, 4); ctx.fill()
    ctx.arc(cx, head_y, 23, 0, 2 * math.pi); ctx.fill()
    
    # Topi
    ctx.set_source_rgb(*COLORS["HAT"]); rounded_rect(ctx, cx - 22, head_y - 30, 44, 25, 10); ctx.fill()
    ctx.set_source_rgb(*COLORS["HAT_BAND"]); rounded_rect(ctx, cx - 22, head_y - 13, 44, 6, 3); ctx.fill()
    ctx.set_source_rgb(*COLORS["HAT"])
    ctx.save(); ctx.translate(cx, head_y - 10); ctx.scale(1, 0.5); ctx.arc(0, 0, 38, 0, 2 * math.pi); ctx.restore(); ctx.fill()

    return surface

def draw_dynamic_character(swing_angle):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, CAIRO_WIDTH, CAIRO_HEIGHT)
    ctx = cairo.Context(surface)
    ctx.scale(BASE_SCALE, BASE_SCALE)
    
    cx = 64
    rad_angle = swing_angle * (math.pi / 180)

    # --- LAYER 1: KIRI (BELAKANG) ---
    # Tangan Kiri
    ctx.save(); ctx.translate(cx, 55); ctx.rotate(-rad_angle)
    ctx.set_source_rgb(*COLORS["SHIRT_DARK"]); rounded_rect(ctx, -9, 0, 18, 42, 6); ctx.fill()
    ctx.set_source_rgb(*COLORS["SKIN_SHADOW"]); ctx.arc(0, 44, 9, 0, 2*math.pi); ctx.fill()
    ctx.restore()

    # Kaki Kiri
    ctx.save(); ctx.translate(cx, 100); ctx.rotate(rad_angle) 
    ctx.set_source_rgb(*COLORS["PANTS"]); rounded_rect(ctx, -11, 0, 22, 45, 6); ctx.fill()
    ctx.set_source_rgb(*COLORS["BOOTS"]); rounded_rect(ctx, -12, 35, 24, 18, 5); ctx.fill()
    ctx.restore()

    # --- LAYER 2: BADAN UTAMA ---
    ctx.set_source_rgb(*COLORS["BACKPACK"]); rounded_rect(ctx, cx - 35, 55, 30, 50, 8); ctx.fill()
    ctx.set_source_rgb(*COLORS["SHIRT"]); rounded_rect(ctx, cx - 20, 50, 40, 60, 10); ctx.fill()
    ctx.set_source_rgb(*COLORS["VEST"]); rounded_rect(ctx, cx - 20, 50, 40, 60, 10); ctx.fill()
    ctx.set_source_rgb(*COLORS["HAT_BAND"]); rounded_rect(ctx, cx - 20, 95, 40, 8, 2); ctx.fill()

    # Kepala
    ctx.set_source_rgb(*COLORS["SKIN"]); rounded_rect(ctx, cx - 8, 40, 16, 15, 4); ctx.fill()
    ctx.arc(cx, 35, 23, 0, 2 * math.pi); ctx.fill()
    ctx.arc(cx + 20, 38, 4, 0, 2 * math.pi); ctx.fill() # Hidung

    # Mata
    eye_x, eye_y = cx + 14, 36
    ctx.set_source_rgb(1, 1, 1); ctx.save(); ctx.translate(eye_x, eye_y); ctx.scale(0.8, 1.0); ctx.arc(0, 0, 5, 0, 2 * math.pi); ctx.restore(); ctx.fill()
    ctx.set_source_rgb(0.1, 0.05, 0.0); ctx.arc(eye_x + 1, eye_y, 2.5, 0, 2 * math.pi); ctx.fill()
    ctx.set_source_rgb(1, 1, 1); ctx.arc(eye_x + 2, eye_y - 1.5, 1, 0, 2 * math.pi); ctx.fill()
    
    # Mulut
    ctx.set_source_rgb(0.6, 0.2, 0.2); ctx.move_to(cx + 12, eye_y + 12); ctx.line_to(cx + 20, eye_y + 10); ctx.set_line_width(1.2); ctx.stroke()
    
    # Kuping
    ctx.set_source_rgb(*COLORS["SKIN_SHADOW"])
    ctx.move_to(cx - 6,  35)
    ctx.curve_to(cx -13, 30, cx -13, 45, cx - 7, 40)
    ctx.curve_to(cx -13, 45, cx - 2, 30, cx - 6, 35)
    ctx.fill()

    # Topi
    ctx.set_source_rgb(*COLORS["HAT"]); rounded_rect(ctx, cx - 30 , 25, 62, 6, 3); ctx.fill() 
    rounded_rect(ctx, cx - 22, 5, 44, 25, 10); ctx.fill()
    ctx.set_source_rgb(*COLORS["HAT_BAND"]); rounded_rect(ctx, cx - 22, 22, 44, 6, 3); ctx.fill()

    # --- LAYER 3: KANAN (DEPAN) ---
    # Kaki Kanan
    ctx.save(); ctx.translate(cx, 100); ctx.rotate(-rad_angle) 
    ctx.set_source_rgb(*COLORS["PANTS"]); rounded_rect(ctx, -11, 0, 22, 45, 6); ctx.fill()
    ctx.set_source_rgb(*COLORS["BOOTS"]); rounded_rect(ctx, -12, 35, 24, 18, 5); ctx.fill()
    ctx.restore()

    # Tangan Kanan
    ctx.save(); ctx.translate(cx, 55); ctx.rotate(rad_angle)
    ctx.set_source_rgb(*COLORS["SHIRT"]); rounded_rect(ctx, -9, 0, 18, 42, 6); ctx.fill()
    ctx.set_source_rgb(*COLORS["SKIN"]); ctx.arc(0, 44, 9, 0, 2*math.pi); ctx.fill()
    ctx.restore()

    return surface

def cairo_to_pygame(surface):
    surface.flush()
    data = surface.get_data()
    return pygame.image.frombuffer(data, (CAIRO_WIDTH, CAIRO_HEIGHT), "BGRA")

def get_player_image(state, walk_cycle, facing_right, target_width, target_height):
    """
    state: 0 (Samping), 1 (Belakang), 2 (Depan)
    """
    angle = 0
    if state == 0: # Samping
        angle = math.sin(walk_cycle) * 30
        cairo_surf = draw_dynamic_character(angle)
    elif state == 1: # Belakang
        cairo_surf = draw_adventurer_back_fixed(walk_cycle)
    else: # Depan
        cairo_surf = draw_adventurer_front_fixed(walk_cycle)

    img = cairo_to_pygame(cairo_surf)

    # Flip jika hadap kiri (hanya mode samping)
    if state == 0 and not facing_right:
        img = pygame.transform.flip(img, True, False)
        
    img = pygame.transform.smoothscale(img, (target_width, target_height))
    return img