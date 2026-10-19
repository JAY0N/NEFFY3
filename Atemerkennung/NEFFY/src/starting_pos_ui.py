#können erklärung jetzt abbrechen
import pygame
import sys
from language_manager import lang
from design_system import design


class MoveToStartPos:
    def __init__(self, screen, clock, audio):
        self.screen = screen
        self.clock = clock
        self.audio = audio
        self.width, self.height = self.screen.get_size()

        self.ref_height = 1080
        self.scale = self.height / self.ref_height

        
        self.text_font = design.get_font("small", self.scale)
        self.title_font = design.get_font("small", self.scale)


        self.animation_start_time = 0
        self.dot_count = 0
        self.last_dot_update = 0

        self.skip_requested = False

        
        self.gradient_surface = design.create_gradient_surface(
            self.width, self.height, "decision"
        )

        #überspringen
        button_width = int(500 * self.scale)
        button_height = int(120 * self.scale)
        button_margin = int(60 * self.scale)
        self.skip_rect = pygame.Rect(
            self.width*0.5 - 0.5* button_width,
            self.height *0.7,
            button_width,
            button_height
        )

        
        self.button_radius = design.get_border_radius("button")

    def draw_gradient(self):
        self.screen.blit(self.gradient_surface, (0, 0))

    def draw_loading_animation(self, elapsed_time, duration):
        title_text = lang.t("starting_pos") if hasattr(lang, 't') else "Übung wird vorbereitet"
        title_surface = self.title_font.render(title_text, True, design.get_color("text"))
        title_rect = title_surface.get_rect(
            center=(self.width // 2, self.height // 2 - int(100 * self.scale))
        )
        self.screen.blit(title_surface, title_rect)

        progress = min(1.0, elapsed_time / duration)
        bar_width = int(600 * self.scale)
        bar_height = int(30 * self.scale)
        bar_x = (self.width - bar_width) // 2
        bar_y = self.height // 2

        pygame.draw.rect(
            self.screen,
            design.get_color("slider_bg"),
            (bar_x, bar_y, bar_width, bar_height),
            border_radius=design.get_border_radius("slider")
        )

        
        filled_width = int(bar_width * progress)
        if filled_width > 0:
            pygame.draw.rect(
                self.screen,
                design.get_color("slider_fill"),
                (bar_x, bar_y, filled_width, bar_height),
                border_radius=design.get_border_radius("slider")
            )

        # Prozentsatz
        percentage = int(progress * 100)
        percentage_text = self.text_font.render(
            f"{percentage}%", True, design.get_color("accent")
        )
        percentage_rect = percentage_text.get_rect(
            center=(self.width // 2, bar_y - int(30 * self.scale))
        )
        self.screen.blit(percentage_text, percentage_rect)




    def draw_skip_button(self):
        mouse = pygame.mouse.get_pos()
        hovered = self.skip_rect.collidepoint(mouse)

        if hovered:
            color =design.get_color("primary_hover")
            
        else:
            color= design.get_color("text_muted")

        design.draw_rounded_rect(
            self.screen,
            color,
            self.skip_rect,
            self.button_radius,
            230
        )

        pygame.draw.rect(
            self.screen,
            (255, 255, 255),
            self.skip_rect,
            3,
            border_radius=self.button_radius
        )

        label = lang.t("skip_explanation") if hasattr(lang, 't') else "Erklärung überspringen"
        text_surface = self.text_font.render(label, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.skip_rect.center)
        self.screen.blit(text_surface, text_rect)


    def run(self, duration=4):
  
        self.animation_start_time = pygame.time.get_ticks()
        start_time = pygame.time.get_ticks()

        while True:
            current_time = pygame.time.get_ticks()
            elapsed = (current_time - start_time) / 1000.0


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

        
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.skip_rect.collidepoint(event.pos):
                        print("Skip-Button gedrückt")
                        self.skip_requested = True
                        return True


            self.draw_gradient()
            self.draw_loading_animation(elapsed, duration)
            self.draw_skip_button()
            pygame.display.flip()
            self.clock.tick(60)


            if elapsed >= duration:
                break

        return True



        
