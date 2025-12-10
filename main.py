import pygame
import sys
import map_labirin
import animasi_jalan
import ui_assets
import quiz       
import screens     
import camera     

FPS = 60
CHAR_VISUAL_WIDTH, CHAR_VISUAL_HEIGHT = 130, 160
HITBOX_WIDTH, HITBOX_HEIGHT = 50, 30
PLAYER_SPEED = 8

def run_game(screen, level=1):
    clock = pygame.time.Clock()
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()

    # --- AUDIO SETUP: GAME BGM ---
    try:
        pygame.mixer.music.load('audio/game_bgm.mp3')
        pygame.mixer.music.play(-1) 
        pygame.mixer.music.set_volume(0.4)
    except:
        pass 

    # Setup Map Dimension
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
    
    # Pathfinding untuk menjamin akses ke pintu/portal
    queue = [(1, 1)]
    visited = {(1, 1)}
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
        # Pastikan area sekitar pintu terbuka
        for ox, oy in offsets:
            nx, ny = finish_x + ox, finish_y + oy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) != (door_x, door_y):
                maze_data[ny][nx] = 1 
    else:
        door_x, door_y = finish_x - 1, finish_y

    # Instansiasi Sprite
    for row in range(h):
        for col in range(w):
            floor_sprites.add(map_labirin.GrassTile(col, row))
            
            if row == finish_y and col == finish_x:
                portal_sprite = map_labirin.Portal(col, row)
                floor_sprites.add(portal_sprite) 
            elif row == door_y and col == door_x:
                door_sprite = map_labirin.Door(col, row)
                wall_sprites.add(door_sprite) 
            elif maze_data[row][col] == 1:
                wall_sprites.add(map_labirin.DetailedWall(col, row))
                
    px = map_labirin.TILE_SIZE * 1.5
    py = map_labirin.TILE_SIZE * 1.5

    walk_cycle = 0
    facing_right = True
    anim_state = 2 

    math_quiz = quiz.MathQuiz(level)
    
    total_map_w = w * map_labirin.TILE_SIZE
    total_map_h = h * map_labirin.TILE_SIZE
    game_cam = camera.GameCamera(total_map_w, total_map_h, SCREEN_WIDTH, SCREEN_HEIGHT)

    player_hitbox = pygame.Rect(0, 0, HITBOX_WIDTH, HITBOX_HEIGHT)
    player_hitbox.center = (px, py)

    game_paused = False
    btn_resume = ui_assets.Button("LANJUTKAN", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30, 250, 70, lambda: None, font_size=25)
    btn_quit_lvl = ui_assets.Button("KELUAR KE MENU", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60, 250, 70, lambda: None, font_size=25)
    pause_buttons = [btn_resume, btn_quit_lvl]

    running = True
    is_victory = False

    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop() 
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
                        pygame.mixer.music.stop() 
                        return "GAME_OVER" 
                    elif math_quiz.state == "success":
                        door_sprite.is_opening = True

            if game_paused and event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if btn_resume.rect.collidepoint(mouse_pos):
                        game_paused = False
                    elif btn_quit_lvl.rect.collidepoint(mouse_pos):
                        pygame.mixer.music.stop() 
                        return "MENU"

        if not game_paused and not is_victory and not math_quiz.active:
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

            # Collision X
            player_hitbox.x += dx
            hits = pygame.sprite.spritecollide(type('obj', (object,), {'rect': player_hitbox}), wall_sprites, False)
            for wall in hits:
                if wall == door_sprite and not door_sprite.is_opening:
                    math_quiz.active = True
                if dx > 0: player_hitbox.right = wall.rect.left
                if dx < 0: player_hitbox.left = wall.rect.right

            # Collision Y
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
        
            game_cam.update(player_hitbox)

            if portal_sprite and player_hitbox.colliderect(portal_sprite.rect):
                is_victory = True
                pygame.mixer.music.stop() 
                return "VICTORY"

        # --- RENDER ---
        screen.fill((20, 20, 30))
        view_margin = 200 
        
        for sprite in floor_sprites:
            offset_pos = game_cam.apply(sprite.rect)
            if -view_margin < offset_pos.x < SCREEN_WIDTH + view_margin and \
               -view_margin < offset_pos.y < SCREEN_HEIGHT + view_margin:
                screen.blit(sprite.image, offset_pos)

        for sprite in wall_sprites:
            offset_pos = game_cam.apply(sprite.rect)
            if -view_margin < offset_pos.x < SCREEN_WIDTH + view_margin and \
               -view_margin < offset_pos.y < SCREEN_HEIGHT + view_margin:
                screen.blit(sprite.image, offset_pos)

        player_img = animasi_jalan.get_player_image(
            anim_state, walk_cycle, facing_right, CHAR_VISUAL_WIDTH, CHAR_VISUAL_HEIGHT
        )
        visual_rect = player_img.get_rect()
        visual_rect.midbottom = (player_hitbox.centerx, player_hitbox.bottom + 10)
        screen.blit(player_img, game_cam.apply(visual_rect))

        if math_quiz.active:
            math_quiz.draw(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
        elif game_paused:
            pause_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            pause_overlay.fill((0,0,0))
            pause_overlay.set_alpha(150)
            screen.blit(pause_overlay, (0,0))

            font_pause = pygame.font.SysFont("Verdana", 40, bold=True)
            title_pause = font_pause.render("GAME PAUSED", True, (255, 255, 255))
            screen.blit(title_pause, title_pause.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 120)))

            for btn in pause_buttons:
                btn.check_hover(mouse_pos)
                btn.draw(screen)
        else:
            font_ui = pygame.font.SysFont("Arial", 20)
            screen.blit(font_ui.render("ESC: Pause Menu", True, (200, 200, 200)), (20, 20))
            
            font_lvl = pygame.font.SysFont("Verdana", 28, bold=True)
            lvl_str = f"LEVEL {level}"
            
            # Text Shadow & Main
            for off in [(2,2), (-2,2), (0,0)]: # Simple shadow
                col = (0,0,0) if off != (0,0) else (255, 220, 50)
                txt = font_lvl.render(lvl_str, True, col)
                screen.blit(txt, (SCREEN_WIDTH - 150 + off[0], 22 + off[1]))

        pygame.display.flip()
        clock.tick(FPS)
    
    return "MENU"

def main_menu():
    pygame.init()
    pygame.mixer.init() # Inisialisasi Audio Mixer
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Arithm-Adventure")
    w, h = screen.get_size()
    clock = pygame.time.Clock()
    
    bg_map = ui_assets.create_background_map(w, h)
    
    running = True
    unlocked_level = 1
    selected_level = 1
    menu_state = "MAIN" 

    title_font = pygame.font.SysFont("Verdana", 80, bold=True)
    subtitle_font = pygame.font.SysFont("Arial", 30, italic=True)

    # --- AUDIO SETUP: MENU BGM ---
    try:
        pygame.mixer.music.load('audio/Main Menu.mp3')
        pygame.mixer.music.play(-1) 
        pygame.mixer.music.set_volume(0.5)
    except:
        pass 

    def change_state(new_state):
        nonlocal menu_state
        menu_state = new_state
    
    def quit_app():
        nonlocal running
        running = False

    while running:
        if menu_state == "GAME":
            pygame.mixer.music.stop() 
            
            result = run_game(screen, selected_level)
            
            # --- RESTART MENU MUSIC ---
            try:
                pygame.mixer.music.load('audio/Main Menu.mp3')
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(0.5)
            except:
                pass

            if result == "QUIT": running = False
            elif result == "GAME_OVER":
                if screens.animate_game_over(screen) == "QUIT": running = False
                menu_state = "LEVEL_SELECT" 
            elif result == "VICTORY":
                if selected_level == unlocked_level and unlocked_level < 5:
                    unlocked_level += 1
                if screens.animate_victory_screen(screen, selected_level) == "QUIT": running = False
                menu_state = "LEVEL_SELECT"
            else:
                menu_state = "MAIN" 
            
            pygame.mouse.set_visible(True)
            continue

        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT: running = False

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
            
            current_buttons = [
                ui_assets.Button("MULAI PERMAINAN", w//2, h//2, 350, 80, lambda: change_state("LEVEL_SELECT")),
                ui_assets.Button("KELUAR", w//2, h//2 + 120, 350, 80, lambda: quit_app())
            ]
            
        elif menu_state == "LEVEL_SELECT":
            sub_surf = subtitle_font.render("Pilih Level Tantanganmu", True, (200, 230, 255))
            screen.blit(sub_surf, sub_surf.get_rect(center=(w//2, h//4 + 70)))
            
            start_y = h//2 - 50
            gap = 120
            
            def set_lvl(l): 
                nonlocal selected_level, menu_state
                selected_level = l; menu_state = "GAME"

            current_buttons = [
                ui_assets.Button("LEVEL 1", w//2 - gap, start_y, 100, 80, lambda: set_lvl(1), enabled=(1 <= unlocked_level), font_size=20),
                ui_assets.Button("LEVEL 2", w//2, start_y, 100, 80, lambda: set_lvl(2), enabled=(2 <= unlocked_level), font_size=20),
                ui_assets.Button("LEVEL 3", w//2 + gap, start_y, 100, 80, lambda: set_lvl(3), enabled=(3 <= unlocked_level), font_size=20),
                ui_assets.Button("LEVEL 4", w//2 - gap//2 - 3, start_y + 100, 100, 80, lambda: set_lvl(4), enabled=(4 <= unlocked_level), font_size=20),
                ui_assets.Button("LEVEL 5", w//2 + gap//2 + 3, start_y + 100, 100, 80, lambda: set_lvl(5), enabled=(5 <= unlocked_level), font_size=20),
                ui_assets.Button("KEMBALI", w//2, h - 100, 200, 60, lambda: change_state("MAIN"))
            ]

        for btn in current_buttons:
            btn.check_hover(mouse_pos)
            btn.draw(screen)
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for btn in current_buttons: btn.click()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_menu()