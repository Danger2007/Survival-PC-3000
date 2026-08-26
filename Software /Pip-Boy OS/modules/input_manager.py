import pygame
from queue import Queue
from threading import Lock



class InputManager:
    def __init__(self):
        self.key_queue = Queue()
        self.get_key_lock = Lock()
        
    
    def handle_keyboard(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            self.key_queue.put(event.key)
            

    def handle_quit(self, event: pygame.event.Event):
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            quit()


    def handle_input(self, tab_manager):
        with self.get_key_lock:
            while not self.key_queue.empty():
                key = self.key_queue.get()
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
                
        
    
    def run(self):
        for event in pygame.event.get():
            self.handle_keyboard(event)
            self.handle_quit(event)
