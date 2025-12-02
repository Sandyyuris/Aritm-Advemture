import pygame
import math

def animate_victory_screen(screen, level):
    """Level Complete"""
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
    """Game Over"""
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