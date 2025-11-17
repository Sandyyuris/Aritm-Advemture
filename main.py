import customtkinter as ctk
from tkinter import messagebox
import pygame
import sys 

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue") 

COLOR_GOLD = "#FBC02D"
COLOR_GOLD_DARK = "#DAA520"
COLOR_GOLD_LIGHT = "#FFD700"
COLOR_YELLOW_SOFT = "#FFFFE0"

def run_arithm_adventure():
    try:
        root.withdraw() 
    except NameError:
        print("Error: 'root' belum didefinisikan.")
        return
    
    try:
        pygame.init()

        SCREEN_WIDTH = 800
        SCREEN_HEIGHT = 600
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Arithm-Adventure - Game Play")

        font = pygame.font.Font(None, 48)
        game_text = font.render("GAME BERJALAN: Mulai Petualangan!", True, (0, 150, 0))
        text_rect = game_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False
            
            screen.fill((0, 0, 0))
            screen.blit(game_text, text_rect)
            
            pygame.display.flip()
            clock.tick(60)

    except Exception as e:
        messagebox.showerror("Error Pygame", f"Terjadi kesalahan saat menjalankan game: {e}")
    finally:
        pygame.quit()
        sys.exit() 

def main_game_function():
    run_arithm_adventure()

def quit_game_function():
    if messagebox.askyesno("Keluar", "Yakin ingin berhenti dari Arithm-Adventure?"):
        root.destroy() 
        sys.exit() 

root = ctk.CTk()
root.title("✨ Arithm-Adventure ✨")
root.geometry("500x300")
root.resizable(False, False)

main_frame = ctk.CTkFrame(root)
main_frame.pack(padx=20, pady=20, fill="both", expand=True)

title_label = ctk.CTkLabel(
    main_frame,
    text="💎 ARITHM-ADVENTURE 💎",
    font=ctk.CTkFont(family="Arial", size=24, weight="bold"),
    text_color=COLOR_GOLD
)
title_label.pack(pady=(20, 10))

subtitle_label = ctk.CTkLabel(
    main_frame,
    text="Petualangan Logika dan Matematika",
    font=ctk.CTkFont(family="Arial", size=14, slant="italic") 
)
subtitle_label.pack(pady=5)

play_button = ctk.CTkButton(
    main_frame,
    text="Mulai Petualangan",
    command=main_game_function,
    font=ctk.CTkFont(family="Arial", size=16, weight="bold"),
    fg_color=COLOR_GOLD_DARK,
    hover_color=COLOR_GOLD_LIGHT,
    text_color="black",
    width=200,
    height=40
)
play_button.pack(pady=(20, 10))

quit_button = ctk.CTkButton(
    main_frame,
    text="Keluar Game",
    command=quit_game_function,
    font=ctk.CTkFont(family="Arial", size=14),
    fg_color=COLOR_YELLOW_SOFT,
    hover_color=COLOR_GOLD_LIGHT,
    text_color="black",
    width=200,
    height=30
)
quit_button.pack(pady=10)

root.mainloop()