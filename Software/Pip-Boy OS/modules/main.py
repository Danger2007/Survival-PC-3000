# Main entry point for the Pip-Boy application.
import os
import sys
import subprocess
import pygame
import settings
import boot
import threading
from pipboy import PipBoy
from input_manager import InputManager
from hardware_input import HardwareInputManager

def run_app():
    if settings.RASPI:
        os.environ["SDL_VIDEODRIVER"] = "x11"
        os.environ["DISPLAY"] = ":0"
        os.environ["SDL_AUDIODRIVER"] = "alsa"

    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=5)
    
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.FULLSCREEN if settings.RASPI else 0)
    pygame.mouse.set_visible(False)
    
    pygame.display.set_caption("Pip-Boy")
    clock = pygame.time.Clock()
    
    boot_sequence = boot.Boot(screen)
    boot_sequence.run()
    
    input_manager = InputManager()
    hw_inputs = HardwareInputManager()
    pipboy = PipBoy(screen, clock, input_manager)
    pipboy_thread = threading.Thread(target=pipboy.run)
    pipboy_thread.daemon = True
    pipboy_thread.start()
    pipboy_thread_lock = threading.Lock()

    running = True
    should_restart = False

    while running:
        input_manager.run()
        
        with pipboy_thread_lock:
            pipboy.render()

        # Checks if settings_tab.py haas requested a restart (e.g., after changing settings)
        if getattr(pipboy, 'should_restart', False):
            should_restart = True
            running = False
            break

        clock.tick(settings.FPS)

    # Stop the Pip-Boy Loop
    pipboy.done = True

    # CLEAN CLOSING OF ALL SUBSYSTEMS
    try:
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        pygame.display.quit()
        pygame.quit()
    except Exception:
        pass

    return should_restart

def main():
    while True:
        # Reload settings.py to apply any changes made in the file without restarting the application.
        import importlib
        importlib.reload(settings)
        
        restart_requested = run_app()
        if not restart_requested:
            break

if __name__ == "__main__":
    main()