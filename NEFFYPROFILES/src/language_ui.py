import pygame
import os
from language_manager import lang
from design_system import design
from settings_manager import settings_manager
from menu_navigation import NavigationHelper


class PygameLanguageUI:
    def __init__(self, screen, clock, return_to_settings=True):
        self.screen = screen
        self.clock = clock
        self.return_to_settings = return_to_settings

        self.width, self.height = self.screen.get_size()
        
        
        self.ref_height = 1080       
        self.scale = self.height / self.ref_height

        
        self.font = design.get_font("title", self.scale)

        self.languages = self.load_languages()

        
        self.left_width = int(self.width * 0.5)
        self.right_width = self.width - self.left_width

        
        self.scroll_y = 0
        self.dragging = False
        self.last_mouse_y = 0
        
        self.max_scroll = 0
        self.update_max_scroll()

        self.selected = None

        
        self.scale_values = {}
        for lang_key in self.languages:
            self.scale_values[lang_key] = 1.0

        
        self.flags = {}
        self.load_flags()


        self.panel_radius = design.get_border_radius("panel")
        self.button_radius = design.get_border_radius("button")
        self.list_radius = design.get_border_radius("list_item")


        self.confirm_rect = pygame.Rect(
            self.left_width + design.get_scaled_spacing("padding_large", self.scale),
            self.height - design.get_scaled_spacing("margin_large", self.scale) * 4,
            self.right_width - design.get_scaled_spacing("margin_medium", self.scale) * 10,  #2
            design.get_scaled_size("button_height", self.scale) * 2
        )
        self.confirm_scale = 1.0

        #Hintergund
        self.gradient_surface = design.create_gradient_surface(
            self.width, self.height, "language"
        )
        
        # Aktuelle Sprache vorauswählen
        current_settings = settings_manager.get_settings()
        current_lang = current_settings.get("language", "de")
        if current_lang in self.languages:
            self.selected = current_lang
        



        self.nav_helper = None
        self.use_navigation = False
        self.nav = None


        self.nav = None
        
        # Menü Einträge für Navigation Sprachen und  Confirm Knopf
        self.nav_items = self.languages.copy() + ["confirm"]
        self.confirm_item = "confirm"
        
        # Status
        self.confirm_clicked = False

    def update_max_scroll(self):
        panel_height = design.get_scaled_size("flag_size", self.scale) + design.get_scaled_spacing("margin_medium", self.scale)
        margin = design.get_scaled_spacing("margin_medium", self.scale)
        total_height = len(self.languages) * (panel_height + margin)
        visible_height = self.height - 100
        self.max_scroll = max(0, total_height - visible_height)
        self.scroll_y = max(-self.max_scroll, min(0, self.scroll_y))

    def load_flags(self):
        base = "assets/flags"
        flag_size = design.get_scaled_size("flag_size", self.scale)

        for lang_key in self.languages:
            for ext in ["png", "jpg", "jpeg", "webp"]:
                path = os.path.join(base, f"{lang_key}.{ext}")
                if os.path.exists(path):
                    try:
                        img = pygame.image.load(path).convert_alpha()
                        img = pygame.transform.smoothscale(img, (flag_size, flag_size))
                        self.flags[lang_key] = img
                        break
                    except:
                        print(f"Flag konnte nicht geladen werden: {path}")

    def load_languages(self):
        files = []
        if os.path.exists("languages"):
            for file in os.listdir("languages"):
                if file.endswith(".json"):
                    files.append(file.replace(".json", ""))
        files.sort()
        return files

    def draw_gradient(self):
        self.screen.blit(self.gradient_surface, (0, 0))

    def draw_language_list(self, mouse, highlighted_item=None):
        panel_height = design.get_scaled_size("flag_size", self.scale) + design.get_scaled_spacing("margin_medium", self.scale)
        margin = design.get_scaled_spacing("margin_medium", self.scale)
        start_y = design.get_scaled_spacing("margin_large", self.scale) + self.scroll_y

        result = []

        for i, language in enumerate(self.languages):
            rect = pygame.Rect(
                design.get_scaled_spacing("margin_large", self.scale),
                start_y + i * (panel_height + margin),
                self.left_width - design.get_scaled_spacing("margin_medium", self.scale) * 2,
                panel_height
            )

            if rect.bottom < 0 or rect.top > self.height:
                continue

            hovered = rect.collidepoint(mouse)
            is_highlighted = (highlighted_item == language)
            is_selected = (self.selected == language)

            target_scale = design.get_animation("hover_scale") if (hovered or is_highlighted) else 1.0
            self.scale_values[language] += (target_scale - self.scale_values[language]) * design.get_animation("animation_speed")
            scale = self.scale_values[language]

            draw_rect = pygame.Rect(0, 0, int(rect.width * scale), int(rect.height * scale))
            draw_rect.center = rect.center

            if hovered or is_highlighted:
                color = design.get_color("info")
                alpha = design.get_ui("alpha_hover")
            elif is_selected:
                color = design.get_color("info") #success
                alpha = design.get_ui("alpha_selected")
            else:
                color = design.get_color("primary")
                alpha = design.get_ui("alpha_normal")

            design.draw_rounded_rect(
                self.screen,
                color,
                draw_rect,
                self.panel_radius,
                alpha
            )


            
   
            if is_highlighted:
                border_rect = draw_rect.inflate(15, 15)
                design.draw_rounded_rect(
                    self.screen,
                    design.get_color("accent"),
                    border_rect,
                    self.panel_radius,
                    150,
                    width=3
                )
            
            #Markierung Auswahl
            if is_selected:
                marker = self.font.render("O", True, design.get_color("text")) #success
                marker_rect = marker.get_rect(
                    center=(draw_rect.right - 30, draw_rect.centery)
                )
                self.screen.blit(marker, marker_rect)

            # Flaggen
            if language in self.flags:
                flag = self.flags[language]
                flag_offset = design.get_scaled_size("flag_size", self.scale) + design.get_scaled_spacing("padding_medium", self.scale)
                flag_rect = flag.get_rect(
                    center=(draw_rect.left + flag_offset, draw_rect.centery)
                )
                self.screen.blit(flag, flag_rect)

            #text
            text = self.font.render(language.upper(), True, design.get_color("text"))
            text_offset = design.get_scaled_spacing("padding_large", self.scale)
            text_rect = text.get_rect(
                center=(draw_rect.centerx + text_offset, draw_rect.centery)
            )
            self.screen.blit(text, text_rect)

            result.append((language, rect))

        return result

    def draw_right_panel(self, mouse, is_confirm_highlighted=False):
        title = self.font.render("SELECT LANGUAGE", True, design.get_color("text"))
        title_x = self.left_width + design.get_scaled_spacing("padding_large", self.scale)
        title_y = design.get_scaled_spacing("margin_large", self.scale)
        self.screen.blit(title, (title_x, title_y))

        if self.selected:
            selected_text = self.font.render(
                f"> {self.selected.upper()}",
                True,
                design.get_color("text")
            )
            selected_y = design.get_scaled_spacing("margin_large", self.scale) * 4
            self.screen.blit(selected_text, (title_x, selected_y))

        hovered = self.confirm_rect.collidepoint(mouse)
        is_highlighted = hovered or is_confirm_highlighted

        target_scale = design.get_animation("hover_scale") if is_highlighted else 1.0
        self.confirm_scale += (target_scale - self.confirm_scale) * design.get_animation("animation_speed")
        scale = self.confirm_scale

        draw_rect = pygame.Rect(0, 0, 
                               int(self.confirm_rect.width * scale),
                               int(self.confirm_rect.height * scale))
        draw_rect.center = self.confirm_rect.center

        color_name = "button_confirm_hover" if is_highlighted else "button_confirm"
        design.draw_rounded_rect(
            self.screen,
            design.get_color(color_name),
            draw_rect,
            self.button_radius,
            design.get_ui("alpha_selected")
        )
        


        if is_confirm_highlighted:
            border_rect = draw_rect.inflate(15, 15)
            design.draw_rounded_rect(
                self.screen,
                design.get_color("accent"),
                border_rect,
                self.button_radius,
                150,
                width=3
            )

        text = self.font.render("CONFIRM", True, design.get_color("text"))
        text_rect = text.get_rect(center=draw_rect.center)
        self.screen.blit(text, text_rect)



        return hovered

    def run(self, nav=None):
        self.nav = nav
        self.use_navigation = (nav is not None and nav.active)
        self.confirm_clicked = False
        
        if self.use_navigation:
            self.nav_helper = NavigationHelper(nav)
            self.nav_helper.setup_ui("language")
            self.nav_helper.set_items(self.nav_items)
            
            def on_navigate(item, index):
                 #nur Navigation keine Auswahl
                pass
            
            def on_select(item):
                print(f"LanguageUI SELECT: {item}")
                if item in self.languages:
                    # Sprache wählen aber noh nicht speichern
                    self.selected = item
                    print(f"Sprache ausgewaehlt: {item}")
                elif item == self.confirm_item:
                    #erst wenn confirm bestätigt wird Auswahl/Sprache gespeichert und wir gehen zurück in menü
                    if self.selected:
                        print(f"CONFIRM: Speichere {self.selected}")
                        settings_manager.set_language(self.selected)
                        lang.load(self.selected)
                        self.confirm_clicked = True
            
            nav.set_on_navigate(on_navigate)
            nav.set_on_select(on_select)
            
            # Initiale Hervorhebung
            if self.languages:
                nav.current_index = 0
                nav.highlighted_item = self.languages[0]

        while True:
            # Navigation update
            if self.use_navigation:
                nav.update()
            
            mouse = pygame.mouse.get_pos()
            highlighted_item = None
            is_confirm_highlighted = False
            
            if self.use_navigation and nav.active:
                highlighted_item = nav.get_highlighted_item()
                if highlighted_item == self.confirm_item:
                    is_confirm_highlighted = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                    
                    if self.use_navigation and nav.active:
                        if event.key == pygame.K_l:
                            nav.set_left(True)
                        elif event.key == pygame.K_r:
                            nav.set_right(True)



                if event.type == pygame.KEYUP:
                    if self.use_navigation and nav.active:
                        if event.key == pygame.K_l:
                            nav.set_left(False)
                        elif event.key == pygame.K_r:
                            nav.set_right(False)

                if event.type == pygame.MOUSEWHEEL:
                    scroll_step = design.get_animation("scroll_step") * int(self.scale)
                    self.scroll_y += event.y * scroll_step
                    self.scroll_y = max(-self.max_scroll, min(0, self.scroll_y))
                    if self.use_navigation:
                        nav.active = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.use_navigation:
                        nav.active = False
                    self.dragging = True
                    self.last_mouse_y = mouse[1]

                if event.type == pygame.MOUSEMOTION and self.dragging:
                    dy = mouse[1] - self.last_mouse_y
                    self.scroll_y += dy
                    self.last_mouse_y = mouse[1]
                    self.scroll_y = max(-self.max_scroll, min(0, self.scroll_y))
                    if self.use_navigation:
                        nav.active = False

                if event.type == pygame.MOUSEBUTTONUP:
                    self.dragging = False

            self.draw_gradient()

            language_rects = self.draw_language_list(mouse, highlighted_item)
            confirm_hover = self.draw_right_panel(mouse, is_confirm_highlighted)

            # Maus Verarbeitung
            if pygame.mouse.get_pressed()[0]:
                for language, rect in language_rects:
                    if rect.collidepoint(mouse):
                        self.selected = language
                        if self.use_navigation:
                            nav.active = False

                if self.confirm_rect.collidepoint(mouse):
                    if self.selected:
                        settings_manager.set_language(self.selected)
                        lang.load(self.selected)
                        if self.use_navigation:
                            nav.active = True
                        if self.return_to_settings:
                            return "settings"
                        else:
                            return self.selected

            # Navigation Auswahl verarbeiten
            if self.confirm_clicked:
                self.confirm_clicked = False
                if self.use_navigation:
                    nav.active = True
                if self.return_to_settings:
                    return "settings"
                else:
                    return self.selected

            pygame.display.flip()
            self.clock.tick(60)
