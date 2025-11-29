import customtkinter as ctk
from tkinter import messagebox
import pygame
import sys
import math

# --- IMPORT MODULE ---
import map_labirin
import animasi_jalan

# --- KONFIGURASI GAME ---
FPS = 60

# UKURAN KARAKTER (DIPERBESAR AGAR TERLIHAT JELAS/DEKAT)
# Sebelumnya 100x120 -> Sekarang 130x160
CHAR_VISUAL_WIDTH = 130  
CHAR_VISUAL_HEIGHT = 160

# HITBOX (Disesuaikan sedikit agar proporsional tapi tetap "mudah masuk")
HITBOX_WIDTH = 50
HITBOX_HEIGHT = 30

# KECEPATAN (Dinaikkan karena map sekarang lebih luas secara pixel)
PLAYER_SPEED = 8

# Warna UI
COLOR_BG_MENU = "#1a1a2e"
COLOR_ACCENT = "#e94560"
COLOR_GOLD = "#ffbd69"
COLOR_BUTTON = "#16213e"
COLOR_BUTTON_HOVER = "#0f3460"

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

        # Batasi kamera
        x = min(0, max(-(self.width - self.screen_w), x))
        y = min(0, max(-(self.height - self.screen_h), y))
        
        self.camera = pygame.Rect(x, y, self.width, self.height)

def run_game_loop():
    root.withdraw()
    pygame.init()
    
    # Fullscreen
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
    
    pygame.display.set_caption("Arithm-Adventure: Big Mode")
    clock = pygame.time.Clock()

    # --- SETUP MAP ---
    # Gunakan map_labirin dengan TILE_SIZE = 100
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

    # --- SETUP PLAYER ---
    spawn_tile_x, spawn_tile_y = 1, 1
    px = spawn_tile_x * map_labirin.TILE_SIZE + map_labirin.TILE_SIZE // 2
    py = spawn_tile_y * map_labirin.TILE_SIZE + map_labirin.TILE_SIZE // 2

    walk_cycle = 0
    facing_right = True
    anim_state = 2 

    total_map_w = w * map_labirin.TILE_SIZE
    total_map_h = h * map_labirin.TILE_SIZE
    camera = GameCamera(total_map_w, total_map_h, SCREEN_WIDTH, SCREEN_HEIGHT)

    player_hitbox = pygame.Rect(0, 0, HITBOX_WIDTH, HITBOX_HEIGHT)
    player_hitbox.center = (px, py)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

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

        # Tabrakan
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

        # Rendering
        screen.fill((20, 20, 30))

        # Render Map (Optimasi Viewport)
        # Kita tambah margin buffer (200px) agar tidak flicker saat di tepi layar
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

        # Render Player
        player_img = animasi_jalan.get_player_image(
            anim_state, walk_cycle, facing_right, CHAR_VISUAL_WIDTH, CHAR_VISUAL_HEIGHT
        )
        visual_rect = player_img.get_rect()
        # Tempelkan kaki ke hitbox
        visual_rect.midbottom = (player_hitbox.centerx, player_hitbox.bottom + 10) # +10 biar makin napak
        
        final_draw_pos = camera.apply(visual_rect)
        screen.blit(player_img, final_draw_pos)

        font_ui = pygame.font.Font(None, 40)
        text_esc = font_ui.render("Tekan [ESC] untuk Menu", True, (255, 255, 255))
        screen.blit(text_esc, (30, 30))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    root.deiconify()
    root.attributes("-fullscreen", True)

# --- MENU UTAMA ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue") 

def quit_app():
    if messagebox.askyesno("Konfirmasi", "Keluar dari aplikasi?"):
        root.destroy()
        sys.exit()

root = ctk.CTk()
root.title("Arithm-Adventure")
root.attributes("-fullscreen", True)
root.configure(fg_color=COLOR_BG_MENU)

main_frame = ctk.CTkFrame(root, fg_color=COLOR_BUTTON, corner_radius=20, border_width=2, border_color=COLOR_GOLD)
main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.6, relheight=0.7)

title_label = ctk.CTkLabel(main_frame, text="ARITHM-ADVENTURE", font=ctk.CTkFont(family="Verdana", size=64, weight="bold"), text_color=COLOR_GOLD)
title_label.pack(pady=(60, 10))

subtitle_label = ctk.CTkLabel(main_frame, text="Edisi Layar Lebar & Zoom", font=ctk.CTkFont(family="Arial", size=24, slant="italic"), text_color="#a0a0a0")
subtitle_label.pack(pady=(0, 50))

btn_play = ctk.CTkButton(main_frame, text="MULAI", command=run_game_loop, font=ctk.CTkFont(family="Arial", size=28, weight="bold"), fg_color=COLOR_ACCENT, hover_color="#c2185b", height=80, width=350, corner_radius=40)
btn_play.pack(pady=30)

btn_quit = ctk.CTkButton(main_frame, text="KELUAR", command=quit_app, font=ctk.CTkFont(family="Arial", size=20), fg_color="transparent", border_width=2, border_color=COLOR_ACCENT, text_color=COLOR_ACCENT, hover_color=COLOR_BUTTON_HOVER, height=50, width=250, corner_radius=25)
btn_quit.pack(pady=10)

root.mainloop()