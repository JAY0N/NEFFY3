
#
import pygame
import sys
import os
from design_system import design
from navigation import NavigationHelper


class PreEvaluation: 
    def __init__(self, screen, clock, audio):
        self.screen = screen
        self.clock = clock
        self.audio = audio

        self.width, self.height = self.screen.get_size()

        self.base_path = "assets/Evaluation_pre"

        self.images = []
        self.image_paths = []
        self.rects = []

        self.clicked = False
        self.fade_alpha = 0
        self.choice_path = None


        self.image_radius = design.get_border_radius("card")
        

        self.gradient_surface = design.create_gradient_surface(
            self.width, self.height, "pre_evaluation"
        )


        self.nav_helper = None
        self.use_navigation = False
        self.nav = None
        

        self.nav_items = []

        self.load_images()

    def load_images(self):
        files = [
            os.path.join(self.base_path, f)
            for f in os.listdir(self.base_path)
            if f.lower().endswith(".png")
        ]

        files.sort()
        files = files[:6]

        panel_width = self.width // len(files)
        max_height = self.height - 200

        for i, file in enumerate(files):
            img = pygame.image.load(file).convert_alpha()
            
            orig_width, orig_height = img.get_size()
            aspect_ratio = orig_width / orig_height
            
            target_width = panel_width - 40
            target_height = max_height
            
            if target_width / target_height > aspect_ratio:
                new_height = target_height
                new_width = int(target_height * aspect_ratio)
            else:
                new_width = target_width
                new_height = int(target_width / aspect_ratio)
            
            img = pygame.transform.smoothscale(img, (new_width, new_height))

            rect = img.get_rect()
            rect.center = (
                panel_width * i + panel_width // 2,
                self.height // 2
            )



            self.images.append(img)
            self.image_paths.append(file)
            self.rects.append(rect)
            
       
            self.nav_items.append(f"image_{i}")

    
        

    def draw_rounded_image(self, image, rect, radius, is_highlighted=False):
        if radius <= 0:
            self.screen.blit(image, rect)
            return
        
        mask_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(mask_surface, (255, 255, 255, 255), 
                        mask_surface.get_rect(), border_radius=radius)
        
        image_with_alpha = image.copy()
        image_with_alpha.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        self.screen.blit(image_with_alpha, rect)
        

        if is_highlighted:
            border_rect = rect.inflate(20, 20)
            pygame.draw.rect(self.screen, design.get_color("accent"), border_rect, 4, border_radius=self.image_radius)

    def draw_gradient(self):
        self.screen.blit(self.gradient_surface, (0, 0))

    def run(self, nav=None):
        self.audio.play("evaluation")

        self.nav = nav
        self.use_navigation = (nav is not None and nav.active)
        
        if self.use_navigation:
            self.nav_helper = NavigationHelper(nav)
            self.nav_helper.setup_ui("pre_evaluation")
            self.nav_helper.set_items(self.nav_items)
            
            def on_navigate(item, index):
                pass
            
            def on_select(item):
                print(f"PreEvaluationUI SELECT: {item}")
                try:
                    idx = int(item.split("_")[1])
                    if 0 <= idx < len(self.image_paths):
                        self.choice_path = self.image_paths[idx]
                        self.clicked = True
                        self.click_time = pygame.time.get_ticks()
                except:
                    pass
            
            nav.set_on_navigate(on_navigate)
            nav.set_on_select(on_select)
            
            #Initiale Hervorhebung
            if self.nav_items:
                nav.current_index = 0
                nav.highlighted_item = self.nav_items[0]

        pygame.event.clear()
        pygame.time.wait(80)
        pygame.event.clear()

        self.clicked = False
        self.fade_alpha = 0
        self.choice_path = None
        self.click_time = None



        while True:
            # Navigation update
            if self.use_navigation:
                nav.update()
            
            mouse = pygame.mouse.get_pos()
            hovered = None

            for i, rect in enumerate(self.rects):
                if rect.collidepoint(mouse):
                    hovered = i

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                    
                    if self.use_navigation and nav.active:
                        if event.key == pygame.K_LEFT:
                            nav.set_left(True)
                        elif event.key == pygame.K_RIGHT:
                            nav.set_right(True)

                if event.type == pygame.KEYUP:
                    if self.use_navigation and nav.active:
                        if event.key == pygame.K_LEFT:
                            nav.set_left(False)
                        elif event.key == pygame.K_RIGHT:
                            nav.set_right(False)

                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN) and not self.clicked:
                    if self.use_navigation:
                        nav.active = True #False
                    
                    if hasattr(event, "pos"):
                        pos = event.pos
                    else:
                        pos = (
                            int(event.x * self.width),
                            int(event.y * self.height)
                        )

                    for i, rect in enumerate(self.rects):
                        if rect.collidepoint(pos):
                            self.choice_path = self.image_paths[i]
                            self.clicked = True
                            self.click_time = pygame.time.get_ticks()
                            break

            self.draw_gradient()

            # Bilder zeichnen
            for i, img in enumerate(self.images):
                rect = self.rects[i]
                
                
                is_highlighted = False
                if self.use_navigation and nav.active:
                    highlighted = nav.get_highlighted_item()
                    if highlighted == f"image_{i}":
                        is_highlighted = True

                if hovered == i:
                    scaled_img = pygame.transform.smoothscale(
                        img,
                        (int(rect.width * 1.05), int(rect.height * 1.05))
                    )
                    scaled_rect = scaled_img.get_rect(center=rect.center)
                    self.draw_rounded_image(scaled_img, scaled_rect, self.image_radius, is_highlighted)
                else:
                    self.draw_rounded_image(img, rect, self.image_radius, is_highlighted)

            if self.clicked and self.click_time is not None:
                if pygame.time.get_ticks() - self.click_time > 1:
                    
                    self.audio.stop()
                    if self.use_navigation:
                        nav.active = True
                    return os.path.basename(self.choice_path)

            pygame.display.flip()
            self.clock.tick(60)


