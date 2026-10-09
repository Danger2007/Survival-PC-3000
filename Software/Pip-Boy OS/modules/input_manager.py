import sys
import pygame
from queue import Queue
from threading import Lock

class InputManager:
    def __init__(self):
        self.key_queue = Queue()
        self.get_key_lock = Lock()
        
        # Gestione Key-Repeat Globale
        self.pressed_key_event = None
        self.key_press_time = 0
        self.last_repeat_time = 0
        self.is_holding = False
        self.hold_delay = 350      # ms di attesa prima di iniziare la ripetizione
        self.hold_interval = 45    # ms tra ogni scatto continuo

    def handle_keyboard(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            now = pygame.time.get_ticks()
            self.pressed_key_event = event
            self.key_press_time = now
            self.last_repeat_time = now
            self.is_holding = False
            self.key_queue.put(event)

        elif event.type == pygame.KEYUP:
            if self.pressed_key_event and event.key == self.pressed_key_event.key:
                self.pressed_key_event = None
                self.is_holding = False
            self.key_queue.put(event)

    def update_key_repeat(self):
        """Genera eventi ripetuti se un tasto rimane premuto."""
        if not self.pressed_key_event:
            return

        keys_state = pygame.key.get_pressed()
        if not keys_state[self.pressed_key_event.key]:
            self.pressed_key_event = None
            self.is_holding = False
            return

        now = pygame.time.get_ticks()

        if not self.is_holding:
            if now - self.key_press_time >= self.hold_delay:
                self.is_holding = True
                self.last_repeat_time = now
                self.key_queue.put(self.pressed_key_event)
        else:
            if now - self.last_repeat_time >= self.hold_interval:
                self.last_repeat_time = now
                self.key_queue.put(self.pressed_key_event)

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
        # Aggiorna il ciclo di ripetizione tasti ad ogni frame
        self.update_key_repeat()

        with self.get_key_lock:
            while not self.key_queue.empty():
                event = self.key_queue.get()
                key = event.key if hasattr(event, 'key') else event

                active_subtab = tab_manager.get_active_subtab()

                target_subtab = active_subtab
                if active_subtab and getattr(active_subtab, 'mode', None) == "SETTINGS" and hasattr(active_subtab, 'settings_tab'):
                    target_subtab = active_subtab.settings_tab

                # 1. Passa l'evento alla sottoscheda target
                if target_subtab and hasattr(target_subtab, 'handle_input'):
                    if target_subtab.handle_input(event):
                        continue

                if getattr(event, 'type', None) == pygame.KEYUP:
                    continue

                # 2. Se in modalità editing
                if target_subtab and hasattr(target_subtab, 'is_editing') and target_subtab.is_editing():
                    match key:
                        case pygame.K_RETURN | pygame.K_KP_ENTER:
                            tab_manager.select_item()
                        case pygame.K_x:
                            tab_manager.handle_x_press()
                        case pygame.K_UP:
                            if not (hasattr(target_subtab, 'editing_mode') and target_subtab.editing_mode is not None):
                                tab_manager.scroll_tab(True)
                        case pygame.K_DOWN:
                            if not (hasattr(target_subtab, 'editing_mode') and target_subtab.editing_mode is not None):
                                tab_manager.scroll_tab(False)
                        case _:
                            pass
                    continue

                # 3. Navigazione standard Pip-Boy
                match key:
                    case pygame.K_LEFT:
                        tab_manager.switch_tab(False)
                    case pygame.K_RIGHT:
                        tab_manager.switch_tab(True)
                    case pygame.K_DOWN:
                        tab_manager.scroll_tab(False)
                    case pygame.K_UP:
                        tab_manager.scroll_tab(True)
                    case pygame.K_RETURN | pygame.K_KP_ENTER:
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
            for event in pygame.event.get():
                self.handle_keyboard(event)
                self.handle_quit(event, tab_manager)
        except pygame.error:
            return