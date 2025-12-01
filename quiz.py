import pygame
import random
import cairo
import math
import ui_assets

def hex_to_rgb_norm(rgb_tuple):
    return (rgb_tuple[0]/255, rgb_tuple[1]/255, rgb_tuple[2]/255)

def cairo_to_pygame(surface):
    surface.flush()
    data = surface.get_data()
    return pygame.image.frombuffer(data, (surface.get_width(), surface.get_height()), "BGRA")

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

        # Cache untuk panel kuis agar tidak generate cairo setiap frame
        self.cached_panel = None

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

    def create_quiz_panel(self, box_w, box_h):
        """Membuat gambar panel kayu menggunakan Cairo"""
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, box_w, box_h)
        ctx = cairo.Context(surface)
        
        # Papan Kayu Luar
        ui_assets.draw_rounded_rect(ctx, 0, 0, box_w, box_h, 25)
        ctx.set_source_rgb(*hex_to_rgb_norm((80, 50, 20)))
        ctx.fill()
        
        # Papan Kayu Dalam
        ui_assets.draw_rounded_rect(ctx, 15, 15, box_w - 30, box_h - 30, 20)
        ctx.set_source_rgb(*hex_to_rgb_norm((160, 110, 60)))
        ctx.fill()
        
        # Paku Hiasan
        for px, py in [(25, 25), (box_w-25, 25), (25, box_h-25), (box_w-25, box_h-25)]:
            ctx.arc(px, py, 8, 0, 2*math.pi)
            ctx.set_source_rgb(*hex_to_rgb_norm((50, 30, 10)))
            ctx.fill()
            
            ctx.arc(px - 2, py - 2, 3, 0, 2*math.pi)
            ctx.set_source_rgb(*hex_to_rgb_norm((120, 120, 120)))
            ctx.fill()

        # Area Kertas Pertanyaan
        paper_rect_x, paper_rect_y = 50, 110
        paper_w, paper_h = box_w - 100, 180
        ui_assets.draw_rounded_rect(ctx, paper_rect_x, paper_rect_y, paper_w, paper_h, 5)
        ctx.set_source_rgb(*hex_to_rgb_norm((240, 230, 200)))
        ctx.fill()
        
        return cairo_to_pygame(surface)

    def draw(self, screen, screen_w, screen_h):
        if not self.active: return

        # Overlay Gelap (Bisa pakai Pygame Surface biasa karena fill solid)
        overlay = pygame.Surface((screen_w, screen_h))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        screen.blit(overlay, (0, 0))

        # --- Panel Kuis ---
        box_w, box_h = 550, 400
        box_x = (screen_w - box_w) // 2
        box_y = (screen_h - box_h) // 2
        
        # Buat panel jika belum ada (Cache)
        if self.cached_panel is None:
            self.cached_panel = self.create_quiz_panel(box_w, box_h)
            
        screen.blit(self.cached_panel, (box_x, box_y))

        # --- Nyawa (Hati) ---
        heart_start_x = box_x + 60
        heart_start_y = box_y + 55
        heart_spacing = 45
        
        for i in range(self.max_lives):
            hx = heart_start_x + (i * heart_spacing)
            if i < self.lives:
                # Menggunakan ui_assets cairo wrapper
                ui_assets.draw_heart(screen, hx, heart_start_y, 35, (220, 20, 60)) 
                
                # Shine pada hati (kecil, manual pygame circle gapapa atau mau cairo juga?)
                # Karena simple, pygame.draw.circle tidak apa-apa, tapi biar konsisten
                # kita bisa pakai hati yang sudah ada shine-nya di ui_assets, atau simple blit asset.
            else:
                ui_assets.draw_heart(screen, hx, heart_start_y, 35, (80, 70, 60)) 

        # Level Info (Text Render Pygame sudah cukup)
        level_surf = self.font_small.render(f"LEVEL {self.level}", True, (255, 255, 200))
        screen.blit(level_surf, (box_x + box_w - 120, box_y + 40))
        
        progress_text = f"Gembok: {self.correct_answers}/{self.questions_needed}"
        prog_surf = self.font_small.render(progress_text, True, (255, 255, 200))
        screen.blit(prog_surf, (box_x + box_w - 150, box_y + 70))

        # --- Pertanyaan Text ---
        q_text_surf = self.font_big.render(self.current_question, True, (50, 30, 10))
        paper_center_y = box_y + 110 + 180//2
        q_rect = q_text_surf.get_rect(center=(box_x + box_w//2, paper_center_y - 30))
        screen.blit(q_text_surf, q_rect)

        # --- Input Box (Dynamic) ---
        # Karena input box border berubah jika salah, kita gambar on-the-fly pakai Cairo
        input_w, input_h = box_w - 200, 50
        input_surf_cairo = cairo.ImageSurface(cairo.FORMAT_ARGB32, input_w, input_h)
        ctx = cairo.Context(input_surf_cairo)
        
        # Background Putih
        ui_assets.draw_rounded_rect(ctx, 0, 0, input_w, input_h, 10)
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill_preserve()
        
        # Border Hitam
        ctx.set_source_rgb(0, 0, 0)
        ctx.set_line_width(2)
        ctx.stroke()
        
        input_img = cairo_to_pygame(input_surf_cairo)
        input_rect = input_img.get_rect(center=(box_x + box_w//2, box_y + 245))
        screen.blit(input_img, input_rect)
        
        # Text Input
        ans_surf = self.font_big.render(self.user_input, True, (0, 0, 0))
        ans_rect = ans_surf.get_rect(center=input_rect.center)
        screen.blit(ans_surf, ans_rect)

        # Footer Instruction
        hint = self.font_small.render("Jawab untuk membuka pintu!", True, (255, 220, 180))
        hint_rect = hint.get_rect(center=(box_x + box_w//2, box_y + 350))
        screen.blit(hint, hint_rect)