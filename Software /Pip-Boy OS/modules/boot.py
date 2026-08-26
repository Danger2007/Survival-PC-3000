import os
import pygame
import settings
from util_functs import Utils
from ui import AnimatedImage


class BootText():
    def __init__(self, screen):
        self.font = pygame.font.Font(settings.TECH_MONO_FONT_PATH, 8)
        self.font_height = self.font.get_height()
        self.boot_text_start = ("* 1 0 0x0000A4 0x00000000000000000 start memory discovery 0 0x0000A4 \n"
                                "0x00000000000000000 1 0 0x000014 0x00000000000000000 CPUO starting cell \n"
                                "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009 \n"
                                "0x00000000000000000 CPUO launch EFI0 0x0000A4 0x00000000000000000 1 0 \n"
                                "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4 \n"
                                "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory \n"
                                "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000 \n"
                                "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014 \n"
                                "0x00000000000000000 CPUO starting cell relocation0 0x0000A4 \n"
                                "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0 \n"
                                "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO \n"
                                "starting EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4 \n"
                                "0x00000000000000000 start memory discovery0 0x0000A4 0x00000000000000000 \n"
                                "1 0 0x0000A4 0x00000000000000000 start memory discovery 0 0x0000A4 \n"
                                "0x00000000000000000 1 0 0x000014 0x00000000000000000 CPUO starting cell \n"
                                "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009 \n"
                                "0x00000000000000000 CPUO launch EFI0 0x0000A4 0x00000000000000000 1 0 \n"
                                "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4 \n"
                                "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory \n"
                                "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000 \n"
                                "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014 \n"
                                "0x00000000000000000 CPUO starting cell relocation0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0  \n"
                                "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO  \n"
                                "starting EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4  \n"
                                "0x00000000000000000 start memory discovery0 0x0000A4 0x00000000000000000  \n"
                                "1 0 0x0000A4 0x00000000000000000 start memory discovery 0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x000014 0x00000000000000000 CPUO starting cell  \n"
                                "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009  \n"
                                "0x00000000000000000 CPUO launch EFI0 0x0000A4 0x00000000000000000 1 0  \n"
                                "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory  \n"
                                "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000  \n"
                                "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014  \n"
                                "0x00000000000000000 CPUO starting cell relocation0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0  \n"
                                "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO  \n"
                                "starting EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4  \n"
                                "0x00000000000000000 start memory discovery0 0x0000A4 0x00000000000000000  \n"
                                "1 0 0x0000A4 0x00000000000000000 start memory discovery 0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x000014 0x00000000000000000 CPUO starting cell  \n"
                                "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009  \n"
                                "0x00000000000000000 CPUO launch EFI0 0x0000A4 0x00000000000000000 1 0  \n"
                                "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory  \n"
                                "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000  \n"
                                "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014  \n"
                                "0x00000000000000000 CPUO starting cell relocation0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0  \n"
                                "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO  \n"
                                "starting EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4  \n"
                                "0x00000000000000000 start memory discovery0 0x0000A4 0x00000000000000000  \n"
                                "1 0 0x0000A4 0x00000000000000000 start memory discovery 0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x000014 0x00000000000000000 CPUO starting cell  \n"
                                "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009  \n"
                                "0x00000000000000000 CPUO launch EFI0 0x0000A4 0x00000000000000000 1 0  \n"
                                "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory  \n"
                                "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000  \n"
                                "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014  \n"
                                "0x00000000000000000 CPUO starting cell relocation0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0  \n"
                                "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO  \n"
                                "starting EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4  \n"
                                "0x00000000000000000 start memory discovery0 0x0000A4 0x00000000000000000  \n"
                                "1 0 0x0000A4 0x00000000000000000 start memory discovery 0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x000014 0x00000000000000000 CPUO starting cell  \n"
                                "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009  \n"
                                "0x00000000000000000 CPUO launch EFI0 0x0000A4 0x00000000000000000 1 0  \n"
                                "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory  \n"
                                "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000  \n"
                                "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014  \n"
                                "0x00000000000000000 CPUO starting cell relocation0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0  \n"
                                "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO  \n"
                                "starting EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4  \n"
                                "0x00000000000000000 start memory discovery0 0x0000A4 0x00000000000000000  \n"
                                "1 0 0x0000A4 0x00000000000000000 start memory discovery 0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x000014 0x00000000000000000 CPUO starting cell  \n"
                                "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009  \n"
                                "0x00000000000000000 CPUO launch EFI0 0x0000A4 0x00000000000000000 1 0  \n"
                                "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory  \n"
                                "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000  \n"
                                "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014  \n"
                                "0x00000000000000000 CPUO starting cell relocation0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0  \n"
                                "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO  \n"
                                "starting EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4  \n"
                                "0x00000000000000000 start memory discovery0 0x0000A4 0x00000000000000000  \n"
                                "1 0 0x0000A4 0x00000000000000000 start memory discovery 0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x000014 0x00000000000000000 CPUO starting cell  \n"
                                "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009  \n"
                                "0x00000000000000000 CPUO launch EFI0 0x0000A4 0x00000000000000000 1 0  \n"
                                "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory  \n"
                                "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000  \n"
                                "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014  \n"
                                "0x00000000000000000 CPUO starting cell relocation0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0  \n"
                                "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO  \n"
                                "starting EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4  \n"
                                "0x00000000000000000 start memory discovery0 0x0000A4 0x00000000000000000 END\n")
        self.boot_text_lines = self.boot_text_start.split("\n")
        self.visible_lines_count = settings.SCREEN_HEIGHT // self.font_height
        self.first_iteration = True
        self.screen = screen


        self.start_y = settings.SCREEN_HEIGHT
        self.y_offset = self.start_y

        # Create a surface large enough to contain all the text
        self.full_text_surface = pygame.Surface(((settings.SCREEN_WIDTH), len(self.boot_text_lines) * self.font_height))

        # Render each line of text into the surface
        for i, line in enumerate(self.boot_text_lines):
            line_surface = self.font.render(line, True, settings.PIP_BOY_LIGHT)
            self.full_text_surface.blit(line_surface, (0, i * self.font_height))
            


    def display_text_sequence(self):
        """Display text sequence with scrolling effect"""
        if self.first_iteration:
            Utils.play_sfx(settings.BOOT_SOUND_A)
            self.first_iteration = False
        
        pygame.time.wait(settings.SPEED * 30)
        self.y_offset -= self.font_height  # Scroll the text upward
        if self.y_offset < -len(self.boot_text_lines) * self.font_height:
            return True  # Stop the sequence if the text has scrolled off the screen
        return False  

    def render(self):
        self.screen.blit(self.full_text_surface, (0, self.y_offset))  # Draw the text at the current y_offset


class BootCopyright():
    def __init__(self, screen):
        self.font = pygame.font.Font(settings.TECH_MONO_FONT_PATH, 12)
        self.font_height = self.font.get_height()
        self.copyright_text = ("*************** PIP-05 (R) V7 .1.0.8 ***************\n"
                            "\n"
                            "\n"
                            "\n"
                            " COPYRIGHT 2075 ROBCO(R)\n"
                            " LOADER VI.1\n"
                            " EXEC VERSION 41.10\n"
                            " 264k RAM SYSTEM\n"
                            " 38911 BYTES FREE\n"
                            " NO HOLOTAPE FOUND\n"
                            " LOAD ROM(1): DEITRIX 303").split('\n')
        self.copyright_text_rendered = []
        self.states = iter(["cursor_initial", "lines", "cursor_bottom", "scroll"])
        self.current_state = next(self.states)
        self.cursor_surface = self.font.render("▮", True, settings.PIP_BOY_LIGHT)
        self.cursor_position = [0, 0]
        self.cur_cursor_position = 0
        self.current_line = 0
        self.current_char = 0
        self.text_surface = None
        self.cursor_blink_count = 0  # Track blink cycles
        self.cursor_blink_state = False
        self.text_scroll_y = 0
        self.cursor_pause = False
        self.scroll_pause = False
        self.screen = screen


    def render(self): 
        for line in range(len(self.copyright_text_rendered)):
            self.text_surface = self.font.render(self.copyright_text_rendered[line], True, settings.PIP_BOY_LIGHT)
            self.screen.blit(self.text_surface, (0, (line * self.font_height) + self.text_scroll_y))
        if self.cursor_blink_state and "cursor" in self.current_state:
            self.screen.blit(self.cursor_surface, (self.cursor_position))
        elif self.current_state == "lines":
            self.screen.blit(self.cursor_surface, (self.cursor_position))

    def blink_cursor(self):
        pygame.time.wait(settings.SPEED * 150)
        self.cursor_blink_state = not self.cursor_blink_state
        self.cursor_blink_count += 1 
                
                       
    def display_copyright_text(self):

        match self.current_state:
            case "cursor_initial":
                if self.cursor_blink_count > 7:
                    Utils.play_sfx(settings.BOOT_SOUND_B)
                    self.current_state = next(self.states)
                    self.cursor_blink_count = 0
                    self.cur_cursor_position = 1
                    return False
                
                self.blink_cursor()
                
            case "lines":
                pygame.time.wait(settings.SPEED * 17)
                if self.current_line >= len(self.copyright_text):
                    self.current_state = next(self.states)
                    return False
                line = self.copyright_text[self.current_line]

                # Ensure the current line exists in the rendered list
                while len(self.copyright_text_rendered) <= self.current_line:
                    self.copyright_text_rendered.append("")

                if self.current_char < len(line):
                    self.copyright_text_rendered[self.current_line] += line[self.current_char]
                    self.current_char += 1
                    
                    # Update cursor position after adding the character
                    self.cursor_position = (self.font.size(self.copyright_text_rendered[self.current_line])[0], 
                                             self.current_line * self.font_height)
                else:
                    self.current_line += 1
                    self.current_char = 0
                    
            case "cursor_bottom":
                if not self.cursor_pause:
                    pygame.time.wait(settings.SPEED * 50)
                    text_width = self.text_surface.get_width() if self.text_surface else 0
                    self.cursor_position = text_width, (self.current_line * self.font_height) - self.font_height
                    self.cursor_pause = True
                
                if self.cursor_blink_count > 7:
                    self.current_state = next(self.states)
                    return False
                
                self.blink_cursor()
                                               
               
            case "scroll":
                
                if not self.scroll_pause:
                    pygame.time.wait(settings.SPEED * 200)
                    self.scroll_pause = True
                
                pygame.time.wait(settings.SPEED * 20)
                self.text_scroll_y -= 5
                if self.text_scroll_y < -len(self.copyright_text) * self.font_height:
                    return True
                    

class BootThumbs():
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(settings.TECH_MONO_FONT_PATH, 10)

        self.current_frame = 0
        self.real_frame = 0
        images = Utils.load_images(settings.BOOT_THUMBS)
        self.images = [Utils.scale_image(image, 0.5) for image in images]
        self.image_center = self.images[0].get_rect().center
        self.init_surface = self.font.render("INITIATING...", True, settings.PIP_BOY_LIGHT)
        self.init_surface_center = self.init_surface.get_rect().center
        self.screen_center = self.screen.get_rect().center
        self.blink = 255
        self.blink_direction = 1
        self.first_iteration = True
        
        frameorder = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 5, 6, 7, 7, 7, 7, 7, 7, 7, 7,
                      7,
                      7, 7, 7, 7, 7, 7, 7, 7, 7]        
        image_position =  (self.screen_center[0] - 59, self.screen_center[1] - 80)
        self.animated_thumbs = AnimatedImage(self.screen, self.images, image_position, settings.SPEED * 116, frame_order=frameorder, loop=False)
        
    def display_thumbs(self):
        if self.first_iteration:
            Utils.play_sfx(settings.BOOT_SOUND_C)
            pygame.time.wait(settings.SPEED * 600)
            self.animated_thumbs.start()
            self.first_iteration = False
        
        if self.animated_thumbs.current_frame_index  >= len(self.animated_thumbs.frame_order) - 1:
            self.animated_thumbs.stop()
            return True

        self.blink += self.blink_direction
        if self.blink >= 255:
            self.blink_direction = -6
        elif self.blink <= 50:
            self.blink_direction = 6
        self.init_surface.set_alpha(self.blink)

        pygame.time.wait(settings.SPEED * 20)
        
        
    def render(self):
        
        self.screen.blit(self.init_surface, (self.screen_center[0] - self.init_surface_center[0], self.screen_center[1] + (self.screen_center[1] // 2)))
        
        self.animated_thumbs.render()        
            
               

class Boot:
    def __init__(self, screen):
        self.screen = screen
        self.states = iter(["text", "copyright", "thumbs", "done"])
        self.current_sequence = next(self.states)        
        self.boot_text = BootText(self.screen)
        self.copyright_text = BootCopyright(self.screen)
        self.boot_thumbs = BootThumbs(self.screen)   
        self.copyright_pause = False
        self.text_pause = False
        self.thumbs_pause = False
        self.running = False

    def start(self):
        self.running = True
        
        
        
    def run(self):
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
            match self.current_sequence:
                case "text":
                    if not self.text_pause:
                        pygame.time.wait(settings.SPEED * 100)
                        self.text_pause = True
                    if self.boot_text.display_text_sequence():
                        self.current_sequence = next(self.states)
                case "copyright":
                    if not self.copyright_pause:
                        pygame.time.wait(settings.SPEED * 100)
                        self.copyright_pause = True
                    if self.copyright_text.display_copyright_text():
                        self.current_sequence = next(self.states)
                case "thumbs":
                    if not self.thumbs_pause:
                        pygame.time.wait(settings.SPEED * 500)
                        self.thumbs_pause = True
                    if self.boot_thumbs.display_thumbs():
                        self.current_sequence = next(self.states)
                case "done":
                    pygame.time.wait(settings.SPEED * 10)
                    break
            self.screen.fill((0, 0, 0))
            self.render()
            pygame.display.flip()
            clock.tick(60)
                    
    def render(self):
        match self.current_sequence:
            case "text":
                self.boot_text.render()
            case "copyright":
                self.copyright_text.render()       
            case "thumbs":
                self.boot_thumbs.render()           
