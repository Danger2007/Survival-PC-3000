import sys
import pygame
from queue import Queue
from threading import Lock


class InputManager:
    def __init__(self):
        self.key_queue = Queue()
        self.get_key_lock = Lock()

    def handle_keyboard(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            self.key_queue.put(event)  # Passiamo direttamente l'evento per supportare sia event.key che logiche complesse

    def handle_quit(self, event: pygame.event.Event, tab_manager=None):
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            if tab_manager and hasattr(tab_manager, 'tab_thread_handler'):
                for tab in tab_manager.tab_thread_handler.tab_map.values():
                    if hasattr(tab, 'handle_threads'):
                        try:
                            tab.handle_threads(False)
                        except Exception:
                            pass

            try:
                pygame.quit()
            except Exception:
                pass
            sys.exit()

    def handle_input(self, tab_manager):
        with self.get_key_lock:
            while not self.key_queue.empty():
                event = self.key_queue.get()
                key = event.key if hasattr(event, 'key') else event
                
                active_subtab = tab_manager.get_active_subtab()
                
                # Se la scheda/sottoscheda attiva gestisce direttamente l'input tramite handle_input e consuma l'evento
                if active_subtab and hasattr(active_subtab, 'handle_input'):
                    if active_subtab.handle_input(event):
                        continue  # Evento già processato internamente (evita il doppio invio/cambio scheda)

                # Se la scheda/sottoscheda attiva è in modalità editing (popup o modal aperto)
                if active_subtab and hasattr(active_subtab, 'is_editing') and active_subtab.is_editing():
                    match key:
                        case pygame.K_RETURN:
                            tab_manager.select_item()
                        case pygame.K_x:
                            tab_manager.handle_x_press()
                        case pygame.K_UP:
                            tab_manager.scroll_tab(True)
                        case pygame.K_DOWN:
                            tab_manager.scroll_tab(False)
                        case _:
                            pass
                    continue

                match key:
                    case pygame.K_LEFT:
                        tab_manager.switch_tab(False)
                    case pygame.K_RIGHT:
                        tab_manager.switch_tab(True)
                    case pygame.K_DOWN:
                        tab_manager.scroll_tab(False)
                    case pygame.K_UP:
                        tab_manager.scroll_tab(True)
                    case pygame.K_RETURN:
                        tab_manager.select_item()
                    case pygame.K_a:
                        tab_manager.switch_sub_tab(False)
                    case pygame.K_d:
                        tab_manager.switch_sub_tab(True)
                    case pygame.K_x:
                        tab_manager.handle_x_press()
                    case pygame.K_j:
                        tab_manager.navigate(0)
                    case pygame.K_i:
                        tab_manager.navigate(1)
                    case pygame.K_k:
                        tab_manager.navigate(2)
                    case pygame.K_l:
                        tab_manager.navigate(3)
                    case _:
                        pass

    def run(self, tab_manager=None):
        try:
            if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                pass

            for event in pygame.event.get():
                self.handle_keyboard(event)
                self.handle_quit(event, tab_manager)
        except pygame.error:
            return