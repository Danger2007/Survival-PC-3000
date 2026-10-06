# Main entry point for the Pip-Boy application.
import os
import sys
import subprocess
import pygame
import settings
from pipboy import PipBoy
import threading
from input_manager import InputManager
import boot

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

        # Controlla se è stato richiesto un restart da PipBoy/SettingsTab
        if getattr(pipboy, 'should_restart', False):
            should_restart = True
            running = False
            break

        clock.tick(settings.FPS)

    # Ferma il loop di Pipboy
    pipboy.done = True

    # CHIUSURA PULITA DI TUTTI I SOTTOSISTEMI
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
        # Ricarica il modulo settings se presente per assicurarsi i valori aggiornati
        import importlib
        importlib.reload(settings)
        
        restart_requested = run_app()
        if not restart_requested:
            break

if __name__ == "__main__":
    main()