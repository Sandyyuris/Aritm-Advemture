import pygame
import sys
import math
import random

# --- IMPORT MODULE ---
# Pastikan file map_labirin.py dan animasi_jalan.py berada di folder yang sama
import map_labirin
import animasi_jalan

# --- KONFIGURASI UMUM ---
FPS = 60

# WARNA UI
COLOR_SKY_TOP = (0, 102, 204)        
COLOR_SKY_BOTTOM = (100, 180, 255)   
COLOR_BTN_BASE = (255, 200, 0)      
COLOR_BTN_HOVER = (255, 230, 50)    
COLOR_BTN_HIGHLIGHT = (255, 255, 180) 
COLOR_BTN_SHADOW = (180, 130, 0)
COLOR_BTN_DISABLED = (150, 150, 150) # Warna tombol terkunci
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

        # Shadow
        shadow_rect = self.rect.copy()
        shadow_rect.y += 6
        pygame.draw.rect(screen, shadow_color, shadow_rect, border_radius=15)
        
        # Main Button
        pygame.draw.rect(screen, color, self.rect, border_radius=15)
        
        # Highlight (only if enabled)
        if self.enabled:
            highlight_rect = pygame.Rect(self.rect.x + 5, self.rect.y + 5, self.rect.width - 10, self.rect.height // 2 - 5)
            pygame.draw.rect(screen, COLOR_BTN_HIGHLIGHT, highlight_rect, border_radius=10)
        
        # Text
        text_color = COLOR_TEXT if self.enabled else (100, 100, 100)
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
        # Lock Icon if disabled
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

class MathQuiz:
    def __init__(self, level):
        self.level = level
        # Tingkat kesulitan soal & jumlah nyawa berdasarkan level
        self.questions_needed = 3 
        self.max_lives = 3
        
        self.lives = self.max_lives
        self.correct_answers = 0
        
        self.current_question = ""
        self.current_answer = ""
        self.user_input = ""
        self.generate_question()
        
        self.active = False
        self.state = "playing" # playing, success, failed
        
        self.font_title = pygame.font.SysFont("Georgia", 32, bold=True)
        self.font_big = pygame.font.SysFont("Verdana", 50, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 20)

    def generate_question(self):
        # Tentukan operasi berdasarkan Level
        if self.level == 1:
            op = '+'
        elif self.level == 2:
            op = '-'
        elif self.level == 3:
            op = 'x'
        elif self.level == 4:
            op = '÷'
        else: # Level 5 Campuran
            op = random.choice(['+', '-', 'x', '÷'])

        if op == '+':
            a, b = random.randint(10, 50), random.randint(10, 50)
            ans = a + b
        elif op == '-':
            a = random.randint(20, 99)
            b = random.randint(10, a) # Pastikan hasil tidak negatif
            ans = a - b
        elif op == 'x':
            a, b = random.randint(2, 10), random.randint(2, 10)
            ans = a * b
        else: # Pembagian
            x = random.randint(2, 10) # Pembagi
            y = random.randint(2, 10) # Hasil
            ex = x * y # Bilangan yang dibagi
            a = ex
            b = x
            ans = y
        
        self.current_question = f"{a} {op} {b} = ?"
        self.current_answer = str(ans)
        self.user_input = ""

    def handle_input(self, event):
        if not self.active or self.state != "playing": return

        if event.key == pygame.K_BACKSPACE:
            self.user_input = self.user_input[:-1]
        elif event.key == pygame.K_RETURN:
            if self.user_input == self.current_answer:
                self.correct_answers += 1
                if self.correct_answers >= self.questions_needed:
                    self.state = "success"
                    self.active = False
                else:
                    self.generate_question()
            else:
                self.lives -= 1
                self.user_input = ""
                if self.lives <= 0:
                    self.state = "failed"
                    self.active = False
        else:
            if event.unicode.isnumeric():
                self.user_input += event.unicode

    def draw(self, screen, screen_w, screen_h):
        if not self.active: return

        # Overlay Gelap
        overlay = pygame.Surface((screen_w, screen_h))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        screen.blit(overlay, (0, 0))

        # --- Panel Kuis ---
        box_w, box_h = 500, 350
        box_x = (screen_w - box_w) // 2
        box_y = (screen_h - box_h) // 2
        
        # Background Panel
        panel_rect = pygame.Rect(box_x, box_y, box_w, box_h)
        pygame.draw.rect(screen, (240, 230, 200), panel_rect, border_radius=20)
        pygame.draw.rect(screen, (101, 67, 33), panel_rect, 8, border_radius=20)

        # Header: Nyawa
        heart_text = "❤" * self.lives
        lost_heart = "♡" * (self.max_lives - self.lives)
        lives_surf = self.font_title.render(heart_text + lost_heart, True, (200, 50, 50))
        screen.blit(lives_surf, (box_x + 20, box_y + 20))

        # Header: Level & Progress
        level_text = f"LEVEL {self.level}"
        prog_text = f"Soal: {self.correct_answers + 1}/{self.questions_needed}"
        
        lvl_surf = self.font_small.render(level_text, True, (0, 0, 150))
        screen.blit(lvl_surf, (box_x + box_w // 2 - lvl_surf.get_width()//2, box_y + 20))
        
        prog_surf = self.font_small.render(prog_text, True, (100, 80, 60))
        prog_rect = prog_surf.get_rect(topright=(box_x + box_w - 20, box_y + 25))
        screen.blit(prog_surf, prog_rect)

        # Pertanyaan
        q_surf = self.font_big.render(self.current_question, True, (60, 40, 20))
        q_rect = q_surf.get_rect(center=(screen_w//2, box_y + 120))
        screen.blit(q_surf, q_rect)

        # Input Box Style
        input_box = pygame.Rect(box_x + 80, box_y + 190, box_w - 160, 60)
        pygame.draw.rect(screen, (255, 255, 255), input_box, border_radius=10)
        pygame.draw.rect(screen, (101, 67, 33), input_box, 3, border_radius=10)
        
        ans_surf = self.font_big.render(self.user_input, True, (0, 0, 0))
        ans_rect = ans_surf.get_rect(center=input_box.center)
        screen.blit(ans_surf, ans_rect)

        # Footer Instruction
        hint = self.font_small.render("Jawab dengan benar untuk membuka segel...", True, (120, 100, 80))
        hint_rect = hint.get_rect(center=(screen_w//2, box_y + 300))
        screen.blit(hint, hint_rect)

def run_game(screen, level=1):
    """Loop Game Utama dengan parameter Level"""
    clock = pygame.time.Clock()
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()

    # Generate Maze (Ukuran bertambah sesuai level)
    # Level 1: Kecil, Level 5: Besar
    base_w, base_h = 17, 13
    maze_cols = base_w + ((level - 1) * 4)
    maze_rows = base_h + ((level - 1) * 2)
    
    # Pastikan ukuran ganjil untuk algoritma maze
    if maze_cols % 2 == 0: maze_cols += 1
    if maze_rows % 2 == 0: maze_rows += 1

    maze_data, w, h = map_labirin.generate_maze(maze_cols, maze_rows)
    
    wall_sprites = pygame.sprite.Group()
    floor_sprites = pygame.sprite.Group()
    door_sprite = None
    portal_sprite = None

    # --- SETUP MAP, PINTU, & FINISH ---
    finish_x, finish_y = w - 2, h - 2
    while maze_data[finish_y][finish_x] == 1: 
        finish_x -= 1
    
    queue = [(1, 1)]
    visited = set([(1, 1)])
    parent_map = {} 
    
    found_path = False
    offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while queue:
        cx, cy = queue.pop(0)
        if cx == finish_x and cy == finish_y:
            found_path = True
            break
        
        for ox, oy in offsets:
            nx, ny = cx + ox, cy + oy
            if 0 <= nx < w and 0 <= ny < h:
                if maze_data[ny][nx] == 0 and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    parent_map[(nx, ny)] = (cx, cy)
                    queue.append((nx, ny))

    door_x, door_y = 0, 0
    if found_path:
        door_x, door_y = parent_map[(finish_x, finish_y)]
        for ox, oy in offsets:
            nx, ny = finish_x + ox, finish_y + oy
            if 0 <= nx < w and 0 <= ny < h:
                if (nx, ny) != (door_x, door_y):
                    maze_data[ny][nx] = 1 
    else:
        door_x, door_y = finish_x - 1, finish_y

    for row in range(h):
        for col in range(w):
            floor = map_labirin.GrassTile(col, row)
            floor_sprites.add(floor)
            
            if row == finish_y and col == finish_x:
                portal_sprite = map_labirin.Portal(col, row)
                floor_sprites.add(portal_sprite) 

            elif row == door_y and col == door_x:
                door_sprite = map_labirin.Door(col, row)
                wall_sprites.add(door_sprite) 
            
            elif maze_data[row][col] == 1:
                wall = map_labirin.DetailedWall(col, row)
                wall_sprites.add(wall)
                
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

    # Inisialisasi Kuis sesuai Level
    math_quiz = MathQuiz(level)

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
    is_victory = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if math_quiz.active:
                        math_quiz.active = False
                    else:
                        return "MENU"
                
                if math_quiz.active:
                    math_quiz.handle_input(event)
                    if math_quiz.state == "failed":
                        return "GAME_OVER" 
                    elif math_quiz.state == "success":
                        door_sprite.is_opening = True

        if is_victory:
            pass 

        elif math_quiz.active:
            pass 

        else:
            if door_sprite:
                door_sprite.update()
                if door_sprite.finished_opening and door_sprite in wall_sprites:
                    wall_sprites.remove(door_sprite)
                    floor_sprites.add(door_sprite) 

            if portal_sprite:
                portal_sprite.update()

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
            hits = pygame.sprite.spritecollide(type('obj', (object,), {'rect': player_hitbox}), wall_sprites, False)
            for wall in hits:
                if wall == door_sprite and not door_sprite.is_opening:
                    math_quiz.active = True
                
                if dx > 0: player_hitbox.right = wall.rect.left
                if dx < 0: player_hitbox.left = wall.rect.right

            player_hitbox.y += dy
            hits = pygame.sprite.spritecollide(type('obj', (object,), {'rect': player_hitbox}), wall_sprites, False)
            for wall in hits:
                if wall == door_sprite and not door_sprite.is_opening:
                    math_quiz.active = True

                if dy > 0: player_hitbox.bottom = wall.rect.top
                if dy < 0: player_hitbox.top = wall.rect.bottom

            if is_moving: walk_cycle += 0.25
            else: 
                walk_cycle = 0
                if anim_state == 0: walk_cycle = 0 
            
            camera.update(player_hitbox)

            if portal_sprite and player_hitbox.colliderect(portal_sprite.rect):
                is_victory = True
                return "VICTORY"

        # --- RENDER ---
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

        if math_quiz.active:
            math_quiz.draw(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
        else:
            font_ui = pygame.font.SysFont("Arial", 20)
            text_esc = font_ui.render("ESC: Menu", True, (255, 255, 255))
            screen.blit(text_esc, (20, 20))
            
            # Tampilkan Level di HUD
            text_lvl = font_ui.render(f"LEVEL {level}", True, (255, 215, 0))
            screen.blit(text_lvl, (SCREEN_WIDTH - 100, 20))

        pygame.display.flip()
        clock.tick(FPS)
    
    return "MENU"

def draw_overlay_message(screen, title, subtitle, color_bg):
    w, h = screen.get_size()
    overlay = pygame.Surface((w, h))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(200)
    screen.blit(overlay, (0, 0))
    
    font_title = pygame.font.SysFont("Verdana", 60, bold=True)
    font_sub = pygame.font.SysFont("Arial", 30, italic=True)
    
    for i in range(10):
        pygame.draw.circle(screen, (*color_bg, 20), (w//2, h//2), 200 + i*5)

    title_surf = font_title.render(title, True, (255, 255, 255))
    sub_surf = font_sub.render(subtitle, True, (200, 200, 200))
    
    title_rect = title_surf.get_rect(center=(w//2, h//2 - 20))
    sub_rect = sub_surf.get_rect(center=(w//2, h//2 + 40))
    
    screen.blit(title_surf, title_rect)
    screen.blit(sub_surf, sub_rect)
    
    pygame.display.flip()
    pygame.time.delay(3000) 

# --- MAIN MENU & LEVEL SELECT ---
def main_menu():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Arithm-Adventure")
    
    w, h = screen.get_size()
    clock = pygame.time.Clock()
    bg_map = create_background_map(w, h)
    
    running = True
    
    # SYSTEM LEVEL
    unlocked_level = 1
    selected_level = 1
    
    # State: MAIN, LEVEL_SELECT, GAME
    menu_state = "MAIN" 

    def btn_start_action():
        nonlocal menu_state
        menu_state = "LEVEL_SELECT"

    def btn_quit_action():
        nonlocal running
        running = False
        
    def btn_level_action(lvl):
        nonlocal selected_level, menu_state
        selected_level = lvl
        menu_state = "GAME"
        
    def btn_back_action():
        nonlocal menu_state
        menu_state = "MAIN"

    title_font = pygame.font.SysFont("Verdana", 80, bold=True)
    subtitle_font = pygame.font.SysFont("Arial", 30, italic=True)

    while running:
        # LOGIKA GAME LOOP
        if menu_state == "GAME":
            result = run_game(screen, selected_level)
            if result == "QUIT":
                running = False
            elif result == "GAME_OVER":
                draw_overlay_message(screen, "GAGAL!", "Jangan menyerah, coba lagi!", (200, 50, 50))
                menu_state = "LEVEL_SELECT" 
            elif result == "VICTORY":
                msg_sub = "Level Selesai!"
                if selected_level == unlocked_level and unlocked_level < 5:
                    unlocked_level += 1
                    msg_sub = "Level Berikutnya Terbuka!"
                elif selected_level == 5:
                    msg_sub = "Kamu telah menamatkan semua level!"
                    
                draw_overlay_message(screen, "SUKSES!", msg_sub, (50, 200, 100))
                menu_state = "LEVEL_SELECT"
            else:
                menu_state = "MAIN" 
            
            pygame.mouse.set_visible(True)
            continue

        # LOGIKA MENU
        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        screen.fill(COLOR_SKY_TOP)
        pygame.draw.rect(screen, COLOR_SKY_BOTTOM, (0, h//2, w, h//2))
        screen.blit(bg_map, (0, h - bg_map.get_height()))

        # JUDUL
        title_surf = title_font.render("ARITHM-ADVENTURE", True, (255, 215, 0))
        title_shadow = title_font.render("ARITHM-ADVENTURE", True, (0, 0, 0))
        title_rect = title_surf.get_rect(center=(w//2, h//4))
        screen.blit(title_shadow, (title_rect.x + 4, title_rect.y + 4))
        screen.blit(title_surf, title_rect)

        # RENDER TOMBOL BERDASARKAN STATE
        current_buttons = []
        
        if menu_state == "MAIN":
            sub_surf = subtitle_font.render("Belajar Matematika Sambil Bertualang", True, (200, 230, 255))
            screen.blit(sub_surf, sub_surf.get_rect(center=(w//2, h//4 + 70)))
            
            btn_play = Button("MULAI PERMAINAN", w//2, h//2, 350, 80, btn_start_action)
            btn_quit = Button("KELUAR", w//2, h//2 + 120, 350, 80, btn_quit_action)
            current_buttons = [btn_play, btn_quit]
            
        elif menu_state == "LEVEL_SELECT":
            sub_surf = subtitle_font.render("Pilih Level Tantanganmu", True, (200, 230, 255))
            screen.blit(sub_surf, sub_surf.get_rect(center=(w//2, h//4 + 70)))
            
            # Buat tombol level 1-5
            start_y = h//2 - 50
            gap = 120
            
            # Baris 1: Level 1, 2, 3
            l1 = Button("LEVEL 1", w//2 - gap, start_y, 100, 80, lambda: btn_level_action(1), enabled=(1 <= unlocked_level), font_size=20)
            l2 = Button("LEVEL 2", w//2,       start_y, 100, 80, lambda: btn_level_action(2), enabled=(2 <= unlocked_level), font_size=20)
            l3 = Button("LEVEL 3", w//2 + gap, start_y, 100, 80, lambda: btn_level_action(3), enabled=(3 <= unlocked_level), font_size=20)
            
            # Baris 2: Level 4, 5
            l4 = Button("LEVEL 4", w//2 - gap//2 - 3, start_y + 100, 100, 80, lambda: btn_level_action(4), enabled=(4 <= unlocked_level), font_size=20)
            l5 = Button("LEVEL 5", w//2 + gap//2 + 3, start_y + 100, 100, 80, lambda: btn_level_action(5), enabled=(5 <= unlocked_level), font_size=20)
            
            btn_back = Button("KEMBALI", w//2, h - 100, 200, 60, btn_back_action)
            
            current_buttons = [l1, l2, l3, l4, l5, btn_back]

        # Update & Draw Buttons
        for btn in current_buttons:
            btn.check_hover(mouse_pos)
            btn.draw(screen)
        
        # Event Klik
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for btn in current_buttons:
                        btn.click()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_menu()