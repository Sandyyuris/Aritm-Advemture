import pygame

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
        
        # Batasi agar kamera tidak keluar dari map
        x = min(0, max(-(self.width - self.screen_w), x))
        y = min(0, max(-(self.height - self.screen_h), y))
        
        self.camera = pygame.Rect(x, y, self.width, self.height)