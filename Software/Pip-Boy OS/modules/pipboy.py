import pygame
from boot import Boot
import threading
import settings
import overlays
from tab_manager import TabManager
import random  

class PipBoy:
    def __init__(self, screen, clock, input_manager):
        """
        Initialize the PipBoy object.
        """
        self.screen = screen
        self.clock = clock
        self.states = iter(["boot", "main"])
        self.current_sequence = "main"   
        
        self.tab_manager = TabManager(self.screen)
        
        self.input_manager = input_manager        
        

        if settings.BOOT_SCREEN:
            self.current_sequence = "boot"
            self.boot_instance = Boot(self.screen)
            self.boot_thread = threading.Thread(target=self.boot_instance.run, daemon=True)
            self.boot_thread.start()


        if settings.SHOW_CRT:
            self.overlay_instance = overlays.Overlays(self.screen)
            threading.Thread(target=self.overlay_instance.run, daemon=True).start()

        self.done = False

    def play_hum(self, sound: str, volume: float, loops: int):
        sound = pygame.mixer.Sound(sound)
        sound.set_volume(volume)
        sound.play(loops)

    
    def render(self):
        self.screen.fill(settings.BACKGROUND)
        
        match self.current_sequence:
            case "boot":
                self.boot_instance.render()
            case "main":
                self.tab_manager.render()
            case _:
                pass
        
        # Bloom effect implementation
        if settings.BLOOM_EFFECT:
            green_tint = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
            green_tint.fill(settings.PIP_BOY_LIGHT)
            green_tint.set_alpha(10)
            
            # Blend the blurred image with additive blending
            self.screen.blit(green_tint, (0, 0))
        
        # Render CRT overlay
        if settings.SHOW_CRT:
            self.overlay_instance.render()
        
        pygame.display.flip()

    def run(self):
        # Main loop
        while True:   
            self.input_manager.handle_input(self.tab_manager)
            self.input_manager.run()
            
            if not self.done:
                match self.current_sequence:
                    case "boot":
                        self.boot_instance.start()
                        self.boot_thread.join()
                        self.current_sequence = next(self.states)
                    case "main":
                        self.boot_instance = None
                        if settings.SOUND_ON:
                            self.play_hum(settings.BACKGROUND_HUM, settings.VOLUME / 10, -1)
                        self.done = True
                    case _:
                        pass

            pygame.time.wait(settings.SPEED)




