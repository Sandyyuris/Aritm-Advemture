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
            pygame.draw.rect(map_surface, (100, 180, 50), (x, y, bg_tile_size, bg_tile_size))
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

class MathQuiz:
    def __init__(self):
        self.questions_needed = 2
        self.correct_answers = 0
        self.max_lives = 3
        self.lives = self.max_lives
        
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
        op = random.choice(['+', '-', 'x', '÷'])
        if op == '+':
            a, b = random.randint(10, 50), random.randint(10, 50)
            ans = a + b
        elif op == '-':
            a, b = random.randint(20, 99), random.randint(10, 20)
            ans = a - b
        elif op == 'x':
            a, b = random.randint(2, 12), random.randint(2, 12)
            ans = a * b
        else:
            x, y = random.randint(2, 10), random.randint(2, 9)
            ex = x * y
            a = ex
            b = x
            ans = a // b
        
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

        # --- Panel Kuis (Tema Batu/Kertas Kuno) ---
        box_w, box_h = 500, 350
        box_x = (screen_w - box_w) // 2
        box_y = (screen_h - box_h) // 2
        
        # Background Panel
        panel_rect = pygame.Rect(box_x, box_y, box_w, box_h)
        pygame.draw.rect(screen, (240, 230, 200), panel_rect, border_radius=20) # Warna Parchment
        pygame.draw.rect(screen, (101, 67, 33), panel_rect, 8, border_radius=20) # Bingkai Kayu

        # Header: Nyawa
        heart_text = "❤" * self.lives
        lost_heart = "♡" * (self.max_lives - self.lives)
        lives_surf = self.font_title.render(heart_text + lost_heart, True, (200, 50, 50))
        screen.blit(lives_surf, (box_x + 20, box_y + 20))

        # Header: Progress
        prog_text = f"Soal: {self.correct_answers + 1}/{self.questions_needed}"
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
        hint = self.font_small.render("Jawab dengan benar untuk membuka segel pintu...", True, (120, 100, 80))
        hint_rect = hint.get_rect(center=(screen_w//2, box_y + 300))
        screen.blit(hint, hint_rect)

def run_game(screen):
    """Loop Game Utama"""
    clock = pygame.time.Clock()
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()

    # Generate Maze
    maze_cols, maze_rows = 25, 21
    maze_data, w, h = map_labirin.generate_maze(maze_cols, maze_rows)
    
    wall_sprites = pygame.sprite.Group()
    floor_sprites = pygame.sprite.Group()
    door_sprite = None
    portal_sprite = None

    # --- SETUP MAP, PINTU, & FINISH (LOGIKA ANTI-CURANG) ---
    
    # 1. Cari titik Finish (pojok kanan bawah yang kosong)
    finish_x, finish_y = w - 2, h - 2
    while maze_data[finish_y][finish_x] == 1: 
        finish_x -= 1
    
    # 2. Pathfinding (BFS) dari Start (1,1) ke Finish
    # Tujuannya: Menemukan dari arah mana player DATANG
    queue = [(1, 1)]
    visited = set([(1, 1)])
    parent_map = {} # Untuk melacak langkah sebelumnya
    
    found_path = False
    offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)] # Kiri, Kanan, Atas, Bawah

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

    # 3. Tentukan Pintu & Tutup Celah Lain
    door_x, door_y = 0, 0
    if found_path:
        # Mundur 1 langkah dari Finish = Posisi Pintu yang valid
        door_x, door_y = parent_map[(finish_x, finish_y)]
        
        # CEGAH KECURANGAN:
        # Ubah semua tetangga Finish yang BUKAN pintu menjadi Tembok
        for ox, oy in offsets:
            nx, ny = finish_x + ox, finish_y + oy
            if 0 <= nx < w and 0 <= ny < h:
                if (nx, ny) != (door_x, door_y):
                    maze_data[ny][nx] = 1 # Force Wall
    else:
        # Fallback (jika labirin tidak sempurna, jarang terjadi)
        door_x, door_y = finish_x - 1, finish_y

    # 4. Generate Sprite berdasarkan maze_data yang sudah dimodifikasi
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

    math_quiz = MathQuiz()

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
            pass # Freeze saat menang

        elif math_quiz.active:
            pass # Freeze saat kuis

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

            # Collision Logic
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

# --- MAIN MENU ---
def main_menu():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Arithm-Adventure")
    
    w, h = screen.get_size()
    clock = pygame.time.Clock()
    bg_map = create_background_map(w, h)
    
    running = True
    current_state = "MENU"

    def start_game_action():
        nonlocal current_state
        current_state = "GAME"

    def quit_game_action():
        nonlocal running
        running = False

    btn_play = Button("MULAI PETUALANGAN", w//2, h//2, 350, 80, start_game_action)
    btn_quit = Button("KELUAR", w//2, h//2 + 120, 350, 80, quit_game_action)
    buttons = [btn_play, btn_quit]

    title_font = pygame.font.SysFont("Verdana", 80, bold=True)
    subtitle_font = pygame.font.SysFont("Arial", 30, italic=True)

    while running:
        if current_state == "GAME":
            result = run_game(screen)
            if result == "QUIT":
                running = False
            elif result == "GAME_OVER":
                draw_overlay_message(screen, "GAGAL!", "Kamu kehabisan kesempatan...", (200, 50, 50))
                current_state = "GAME" 
            elif result == "VICTORY":
                draw_overlay_message(screen, "SELAMAT!", "Kamu berhasil menaklukkan labirin!", (50, 200, 100))
                current_state = "MENU"
            else:
                current_state = "MENU" 
            pygame.mouse.set_visible(True)
            continue

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

        screen.fill(COLOR_SKY_TOP)
        pygame.draw.rect(screen, COLOR_SKY_BOTTOM, (0, h//2, w, h//2))
        screen.blit(bg_map, (0, h - bg_map.get_height()))
        
        title_surf = title_font.render("ARITHM-ADVENTURE", True, (255, 215, 0))
        title_shadow = title_font.render("ARITHM-ADVENTURE", True, (0, 0, 0))
        title_rect = title_surf.get_rect(center=(w//2, h//4))
        screen.blit(title_shadow, (title_rect.x + 4, title_rect.y + 4))
        screen.blit(title_surf, title_rect)

        sub_surf = subtitle_font.render("Edisi Layar Lebar & Zoom", True, (200, 230, 255))
        sub_rect = sub_surf.get_rect(center=(w//2, h//4 + 70))
        screen.blit(sub_surf, sub_rect)

        for btn in buttons:
            btn.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_menu()