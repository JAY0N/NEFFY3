import pygame
import sys
from language_manager import lang
from design_system import design


from MotorC import (
    CMD_BREATH_NORMAL,
    CMD_BREATH_STRESSED,
    CMD_BREATH_RELAXED,
    BREATH_RESULT_IDS,
)


class Stressidentifikation:


    def __init__(self, screen, clock, audio, motor_controller):
        self.screen = screen
        self.clock = clock
        self.audio = audio
        self.motor_controller = motor_controller

        self.width, self.height = self.screen.get_size()
        self.ref_height = 1080
        self.scale = self.height / self.ref_height

        
        self.title_font = design.get_font("title", self.scale)
        self.body_font = design.get_font("small", self.scale)

        
        self.gradient_surface = design.create_gradient_surface(
            self.width, self.height, "Volume"
        )

        #Ergebnis
        self.exercise_id = None
        self.exercise_started = False

     #je nachdem welcher Befehl vom Board geschickt wird
    def set_breath_result(self, cmd_id, payload): #aufgerufen wenn Befehl registriert wird
        if payload != 0:
            return

        if cmd_id in BREATH_RESULT_IDS:
            self.exercise_id = cmd_id
            self.exercise_started = True
            print(f"Stressidentifikation: Ergebnis 0x{cmd_id:02X}")

    #Ansonsten würde der Text aus dem Bildschirm rauslaufen
    def _wrap_text(self, text, font, max_width):
        lines = []
        paragraphs = text.split("\n")

        for paragraph in paragraphs:
            words = paragraph.split(" ")
            current_line = []

            for word in words:
                test_line = " ".join(current_line + [word])
                test_surface = font.render(test_line, True, (255, 255, 255))

                if test_surface.get_width() <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(" ".join(current_line))
                    current_line = [word]

            if current_line:
                lines.append(" ".join(current_line))

        return lines



    def zeichne_anweisungen(self):
        self.screen.blit(self.gradient_surface, (0, 0))

        max_text_width = int(self.width * 0.8)

        #Titel
        title = self.title_font.render(
            lang.t("Atemerkennung"), True, design.get_color("text")
        )
        title_rect = title.get_rect(
            center=(self.width // 2, int(self.height * 0.20))
        )
        self.screen.blit(title, title_rect)

        #Text
        instruction = lang.t("Atemerkennung_Info")
        lines = self._wrap_text(instruction, self.body_font, max_text_width)

        line_height = self.body_font.get_height() + int(15 * self.scale)
        total_height = len(lines) * line_height
        start_y = self.height // 2 - total_height // 2

        for i, line in enumerate(lines):
            line_surface = self.body_font.render(
                line, True, design.get_color("text")
            )
            line_rect = line_surface.get_rect(
                center=(self.width // 2, start_y + i * line_height)
            )
            self.screen.blit(line_surface, line_rect)


    def run(self):


        #Befehl ans Board Atemerkennung starten
        self.motor_controller.send_breath_start()

        #warrten auf Board Antwort
        while not self.exercise_started:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return None

            self.zeichne_anweisungen()
            pygame.display.flip()
            self.clock.tick(60)

        return self.exercise_id
