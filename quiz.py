import pygame
import random
import ui_assets

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