import pygame
import sys
import math
import random

# --- IMPORT MODULE ---
import map_labirin
import animasi_jalan
import ui_assets  # <-- Module baru kita

# --- KONFIGURASI UMUM ---
FPS = 60

class MathQuiz:
    def __init__(self, level):
        self.level = level
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
        self.font_small = pygame.font.SysFont("Arial", 22, bold=True)

    def generate_question(self):
        if self.level == 1: op = '+'
        elif self.level == 2: op = '-'
        elif self.level == 3: op = 'x'
        elif self.level == 4: op = '÷'
        else: op = random.choice(['+', '-', 'x', '÷'])

        if op == '+':
            a, b = random.randint(10, 50), random.randint(10, 50)
            ans = a + b
        elif op == '-':
            a = random.randint(20, 99)
            b = random.randint(10, a)
            ans = a - b
        elif op == 'x':
            a, b = random.randint(2, 10), random.randint(2, 10)
            ans = a * b
        else:
            x = random.randint(2, 10)
            y = random.randint(2, 10)
            ex = x * y
            a, b, ans = ex, x, y
        
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
        box_w, box_h = 550, 400
        box_x = (screen_w - box_w) // 2
        box_y = (screen_h - box_h) // 2
        
        # Papan Kayu
        pygame.draw.rect(screen, (80, 50, 20), (box_x, box_y, box_w, box_h), border_radius=25)
        pygame.draw.rect(screen, (160, 110, 60), (box_x + 15, box_y + 15, box_w - 30, box_h - 30), border_radius=20)
        
        # Paku hiasan
        for px, py in [(25, 25), (box_w-25, 25), (25, box_h-25), (box_w-25, box_h-25)]:
            pygame.draw.circle(screen, (50, 30, 10), (box_x + px, box_y + py), 8)
            pygame.draw.circle(screen, (120, 120, 120), (box_x + px - 2, box_y + py - 2), 3)

        # --- Nyawa (Hati) ---
        heart_start_x = box_x + 60
        heart_start_y = box_y + 55
        heart_spacing = 45
        
        for i in range(self.max_lives):
            hx = heart_start_x + (i * heart_spacing)
            if i < self.lives:
                # Menggunakan ui_assets
                ui_assets.draw_heart(screen, hx, heart_start_y, 35, (220, 20, 60)) 
                pygame.draw.circle(screen, (255, 200, 200), (hx - 8, heart_start_y - 8), 4)
            else:
                ui_assets.draw_heart(screen, hx, heart_start_y, 35, (80, 70, 60)) 

        # Level Info
        level_surf = self.font_small.render(f"LEVEL {self.level}", True, (255, 255, 200))
        screen.blit(level_surf, (box_x + box_w - 120, box_y + 40))
        
        progress_text = f"Gembok: {self.correct_answers}/{self.questions_needed}"
        prog_surf = self.font_small.render(progress_text, True, (255, 255, 200))
        screen.blit(prog_surf, (box_x + box_w - 150, box_y + 70))

        # --- Pertanyaan ---
        paper_rect = pygame.Rect(box_x + 50, box_y + 110, box_w - 100, 180)
        pygame.draw.rect(screen, (240, 230, 200), paper_rect, border_radius=5)
        
        q_text_surf = self.font_big.render(self.current_question, True, (50, 30, 10))
        q_rect = q_text_surf.get_rect(center=(paper_rect.centerx, paper_rect.centery - 30))
        screen.blit(q_text_surf, q_rect)

        # --- Input Box ---
        input_box = pygame.Rect(box_x + 100, box_y + 220, box_w - 200, 50)
        pygame.draw.rect(screen, (255, 255, 255), input_box, border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0), input_box, 2, border_radius=10)
        
        ans_surf = self.font_big.render(self.user_input, True, (0, 0, 0))
        ans_rect = ans_surf.get_rect(center=input_box.center)
        screen.blit(ans_surf, ans_rect)

        # Footer Instruction
        hint = self.font_small.render("Jawab untuk membuka pintu!", True, (255, 220, 180))
        hint_rect = hint.get_rect(center=(box_x + box_w//2, box_y + 350))
        screen.blit(hint, hint_rect)

def run_game(screen, level=1):
    clock = pygame.time.Clock()
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()

    base_w, base_h = 17, 13
    maze_cols = base_w + ((level - 1) * 4)
    maze_rows = base_h + ((level - 1) * 2)
    
    if maze_cols % 2 == 0: maze_cols += 1
    if maze_rows % 2 == 0: maze_rows += 1

    maze_data, w, h = map_labirin.generate_maze(maze_cols, maze_rows)
    
    wall_sprites = pygame.sprite.Group()
    floor_sprites = pygame.sprite.Group()
    door_sprite = None
    portal_sprite = None

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

    game_paused = False
    
    # Menggunakan Button dari ui_assets
    btn_resume = ui_assets.Button("LANJUTKAN", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30, 250, 70, lambda: None, font_size=25)
    btn_quit_lvl = ui_assets.Button("KELUAR KE MENU", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60, 250, 70, lambda: None, font_size=25)
    pause_buttons = [btn_resume, btn_quit_lvl]

    running = True
    is_victory = False

    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if math_quiz.active:
                        math_quiz.active = False
                    else:
                        game_paused = not game_paused
                
                if math_quiz.active and not game_paused:
                    math_quiz.handle_input(event)
                    if math_quiz.state == "failed":
                        return "GAME_OVER" 
                    elif math_quiz.state == "success":
                        door_sprite.is_opening = True

            if game_paused and event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if btn_resume.rect.collidepoint(mouse_pos):
                        game_paused = False
                    elif btn_quit_lvl.rect.collidepoint(mouse_pos):
                        return "MENU"

        if not game_paused:
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
        elif game_paused:
            pause_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            pause_overlay.fill((0,0,0))
            pause_overlay.set_alpha(150)
            screen.blit(pause_overlay, (0,0))

            font_pause = pygame.font.SysFont("Verdana", 40, bold=True)
            title_pause = font_pause.render("GAME PAUSED", True, (255, 255, 255))
            title_rect = title_pause.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 120))
            screen.blit(title_pause, title_rect)

            for btn in pause_buttons:
                btn.check_hover(mouse_pos)
                btn.draw(screen)
        else:
            font_ui = pygame.font.SysFont("Arial", 20)
            text_esc = font_ui.render("ESC: Pause Menu", True, (200, 200, 200))
            screen.blit(text_esc, (20, 20))
            
            font_lvl = pygame.font.SysFont("Verdana", 28, bold=True)
            lvl_str = f"LEVEL {level}"
            text_lvl_shadow = font_lvl.render(lvl_str, True, (0, 0, 0))
            screen.blit(text_lvl_shadow, (SCREEN_WIDTH - 148, 22))
            screen.blit(text_lvl_shadow, (SCREEN_WIDTH - 152, 22))
            screen.blit(text_lvl_shadow, (SCREEN_WIDTH - 150, 20))
            screen.blit(text_lvl_shadow, (SCREEN_WIDTH - 150, 24))

            text_lvl_main = font_lvl.render(lvl_str, True, (255, 220, 50))
            screen.blit(text_lvl_main, (SCREEN_WIDTH - 150, 22))

        pygame.display.flip()
        clock.tick(FPS)
    
    return "MENU"

def animate_victory_screen(screen, level):
    """Layar kemenangan sederhana: Hanya Teks Level Complete"""
    w, h = screen.get_size()
    clock = pygame.time.Clock()
    
    font_title = pygame.font.SysFont("Verdana", 60, bold=True)
    font_sub = pygame.font.SysFont("Arial", 30, italic=True)
    
    frame_count = 0
    running = True
    
    while running:
        frame_count += 1
        screen.fill((20, 20, 30)) 
        
        scale = 1.0 + 0.02 * math.sin(frame_count * 0.05)
        
        title_text = "LEVEL COMPLETE!"
        
        # Shadow Teks
        ts = font_title.render(title_text, True, (0, 0, 0))
        ts_rect = ts.get_rect(center=(w//2, h//2 - 20))
        screen.blit(ts, ts_rect)
        
        # Teks Utama (Warna Emas)
        tm = font_title.render(title_text, True, (255, 215, 0))
        tm = pygame.transform.rotozoom(tm, 0, scale) 
        tm_rect = tm.get_rect(center=(w//2, h//2 - 20))
        screen.blit(tm, tm_rect)

        # Subtitle
        if frame_count > 30:
            sub_text = "Klik untuk Lanjut"
            alpha = abs(math.sin(frame_count * 0.1)) * 255
            sub_surf = font_sub.render(sub_text, True, (200, 200, 200))
            sub_surf.set_alpha(int(alpha))
            sub_rect = sub_surf.get_rect(center=(w//2, h//2 + 60))
            screen.blit(sub_surf, sub_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                if frame_count > 20: 
                    return "NEXT"

        pygame.display.flip()
        clock.tick(60)

def animate_game_over(screen):
    """Layar Game Over"""
    w, h = screen.get_size()
    clock = pygame.time.Clock()
    font_big = pygame.font.SysFont("Verdana", 70, bold=True)
    font_small = pygame.font.SysFont("Arial", 30)
    
    alpha = 0
    running = True
    
    while running:
        screen.fill((0, 0, 0))
        
        alpha += 3
        if alpha > 255: alpha = 255
        
        txt = font_big.render("GAME OVER", True, (200, 0, 0))
        txt.set_alpha(alpha)
        rect = txt.get_rect(center=(w//2, h//2 - 20))
        screen.blit(txt, rect)
        
        if alpha >= 200:
            sub = font_small.render("Coba lagi...", True, (150, 150, 150))
            sub_rect = sub.get_rect(center=(w//2, h//2 + 50))
            screen.blit(sub, sub_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if (event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN) and alpha > 100:
                return "RETRY"

        pygame.display.flip()
        clock.tick(60)

# --- MAIN MENU & LEVEL SELECT ---
def main_menu():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Arithm-Adventure")
    
    w, h = screen.get_size()
    clock = pygame.time.Clock()
    
    # Menggunakan ui_assets untuk background
    bg_map = ui_assets.create_background_map(w, h)
    
    running = True
    
    unlocked_level = 1
    selected_level = 1
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
        if menu_state == "GAME":
            result = run_game(screen, selected_level)
            if result == "QUIT":
                running = False
            elif result == "GAME_OVER":
                res = animate_game_over(screen)
                if res == "QUIT": running = False
                menu_state = "LEVEL_SELECT" 
            elif result == "VICTORY":
                if selected_level == unlocked_level and unlocked_level < 5:
                    unlocked_level += 1
                
                res = animate_victory_screen(screen, selected_level)
                if res == "QUIT": running = False
                menu_state = "LEVEL_SELECT"
            else:
                menu_state = "MAIN" 
            
            pygame.mouse.set_visible(True)
            continue

        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Menggunakan warna dari ui_assets
        screen.fill(ui_assets.COLOR_SKY_TOP)
        pygame.draw.rect(screen, ui_assets.COLOR_SKY_BOTTOM, (0, h//2, w, h//2))
        screen.blit(bg_map, (0, h - bg_map.get_height()))

        title_surf = title_font.render("ARITHM-ADVENTURE", True, (255, 215, 0))
        title_shadow = title_font.render("ARITHM-ADVENTURE", True, (0, 0, 0))
        title_rect = title_surf.get_rect(center=(w//2, h//4))
        screen.blit(title_shadow, (title_rect.x + 4, title_rect.y + 4))
        screen.blit(title_surf, title_rect)

        current_buttons = []
        
        if menu_state == "MAIN":
            sub_surf = subtitle_font.render("Belajar Matematika Sambil Bertualang", True, (200, 230, 255))
            screen.blit(sub_surf, sub_surf.get_rect(center=(w//2, h//4 + 70)))
            
            # Menggunakan ui_assets.Button
            btn_play = ui_assets.Button("MULAI PERMAINAN", w//2, h//2, 350, 80, btn_start_action)
            btn_quit = ui_assets.Button("KELUAR", w//2, h//2 + 120, 350, 80, btn_quit_action)
            current_buttons = [btn_play, btn_quit]
            
        elif menu_state == "LEVEL_SELECT":
            sub_surf = subtitle_font.render("Pilih Level Tantanganmu", True, (200, 230, 255))
            screen.blit(sub_surf, sub_surf.get_rect(center=(w//2, h//4 + 70)))
            
            start_y = h//2 - 50
            gap = 120
            
            l1 = ui_assets.Button("LEVEL 1", w//2 - gap, start_y, 100, 80, lambda: btn_level_action(1), enabled=(1 <= unlocked_level), font_size=20)
            l2 = ui_assets.Button("LEVEL 2", w//2,       start_y, 100, 80, lambda: btn_level_action(2), enabled=(2 <= unlocked_level), font_size=20)
            l3 = ui_assets.Button("LEVEL 3", w//2 + gap, start_y, 100, 80, lambda: btn_level_action(3), enabled=(3 <= unlocked_level), font_size=20)
            
            l4 = ui_assets.Button("LEVEL 4", w//2 - gap//2 - 3, start_y + 100, 100, 80, lambda: btn_level_action(4), enabled=(4 <= unlocked_level), font_size=20)
            l5 = ui_assets.Button("LEVEL 5", w//2 + gap//2 + 3, start_y + 100, 100, 80, lambda: btn_level_action(5), enabled=(5 <= unlocked_level), font_size=20)
            
            btn_back = ui_assets.Button("KEMBALI", w//2, h - 100, 200, 60, btn_back_action)
            
            current_buttons = [l1, l2, l3, l4, l5, btn_back]

        for btn in current_buttons:
            btn.check_hover(mouse_pos)
            btn.draw(screen)
        
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