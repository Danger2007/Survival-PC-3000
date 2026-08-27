import os
from threading import Thread, Lock
from turtle import position
import pygame
import settings
from ui import GenericList, AnimatedImage, WireframeItem
from items import Inventory
from util_functs import Utils

            
class InvBase:
    def __init__(self, screen, tab_instance, draw_space: pygame.Rect, category: str, enable_turntable: bool = True, enable_dot: bool = False):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        self.enable_turntable = enable_turntable
        
        self.inv_font = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 10)
        self.footer_font = tab_instance.footer_font               
        inventory = Inventory()
        self.inv_items = inventory.get_all_items(category)
        self.weight = sum(item.weight for item in inventory.get_all_items())
        self._init_icons()
        
        self.no_items = True if not self.inv_items else False
        if self.no_items:
            return
                
        self.item_selected = False
        self.active_item_index = None
        self.previous_item_index = None
        
        self.unique_items = inventory.get_unique_items(category)
        
        item_names = inventory.get_item_names(category)

           
        self.list_draw_space = pygame.Rect(
            self.draw_space.left,
            self.draw_space.top + 2 * settings.LIST_TOP_MARGIN,
            self.draw_space.centerx + (self.draw_space.centerx // 6),
            self.draw_space.height - 2 * settings.LIST_TOP_MARGIN
        )
        
        self.inv_list = GenericList(
            draw_space=self.list_draw_space,
            font=self.inv_font,
            items=item_names,
            enable_dot=enable_dot,
        )
        
        if self.enable_turntable:
            self._init_turntable()
        

    def _init_turntable(self):
        self.turntable_draw_space = pygame.Rect(
            self.list_draw_space.right + settings.TURNTABLE_LEFT_MARGIN,
            self.draw_space.top,
            self.draw_space.width - self.list_draw_space.width,
            self.list_draw_space.height // 2
        )
        
        self.turntable_lock = Lock
        self.item_turntable = None

    
    def _init_icons(self):
        self.big_icon_size = settings.BOTTOM_BAR_HEIGHT - (settings.BOTTOM_BAR_HEIGHT // 4)
        self.small_icon_size = settings.BOTTOM_BAR_HEIGHT - (settings.BOTTOM_BAR_HEIGHT // 2)
        
        self.weight_icon = Utils.load_svg(self.big_icon_size, settings.WEIGHT_ICON)
        self.caps_icon = Utils.load_svg(self.big_icon_size, settings.CAPS_ICON)
        
        
        self.damage_icons = {
            dtype: Utils.load_svg(self.small_icon_size, path)
            for dtype, path in settings.DAMAGE_TYPES_ICONS.items()
        }        
        

    def select_item(self):    
        if self.no_items:
            return
        
        if self.inv_list.selected_index == self.active_item_index:
            self.item_selected = not self.item_selected
        else:
            self.item_selected = True  # Set to True for new selections
        self.active_item_index = self.inv_list.selected_index
        


    def scroll(self, direction: bool):
        if self.no_items:
            return
        prev_index = self.inv_list.change_selection(direction)

        if self.enable_turntable and self.inv_list.selected_index != prev_index:
            Thread(target=self.start_item_animation).start() 
        
    
    
    def init_footer_weight(self):
        
        weight_text= f"{self.weight}/{settings.MAX_CARRY_WEIGHT}"
        weight_surface = self.footer_font.render(weight_text, True, settings.PIP_BOY_LIGHT)
        footer_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        
        y_pos = settings.BOTTOM_BAR_HEIGHT // 2 - weight_surface.get_height() // 2
        
        footer_surface.blit(self.weight_icon, (y_pos, 3))
        
        footer_surface.blit(weight_surface, (self.weight_icon.get_width() + settings.BOTTOM_BAR_MARGIN, 2))

        return footer_surface

    
    def init_footer_caps(self):
        
        caps_text= f"{settings.CAPS}"
        caps_surface = self.footer_font.render(caps_text, True, settings.PIP_BOY_LIGHT)
        footer_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        
        y_pos = settings.BOTTOM_BAR_HEIGHT // 2 - caps_surface.get_height() // 2

        
        footer_surface.blit(self.caps_icon, (settings.SCREEN_WIDTH //4 + 4, y_pos))
        
        footer_surface.blit(caps_surface, (settings.SCREEN_WIDTH // 4 + self.caps_icon.get_width() + settings.BOTTOM_BAR_MARGIN, 2))

        return footer_surface

        
        

    def start_item_animation(self):
        
        if self.item_turntable:
            self.item_turntable.stop()
            self.item_turntable = None
        selected_item = self.unique_items[self.inv_list.selected_index]   
        if not selected_item.icons: 
            return  
        #2D image animation (original code) - commented out by kelmes1
        # icons = Utils.load_images(folder) 
        # if not icons:
        #     return
        # icons = [Utils.scale_image_abs(image, height=self.turntable_draw_space.height) for image in icons]

    #DanieleM' s addition to load images from the correct folder path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        tabs_dir = os.path.dirname(current_dir)
        modules_dir = os.path.dirname(tabs_dir)
        project_root = os.path.dirname(modules_dir)
        folder_name = selected_item.icons.replace("_", "").replace("-", "")
        folder_path = os.path.join(settings.ITEMS_BASE_FOLDER, folder_name)
        folder = os.path.join(project_root, "images", "inventory", "items", folder_name)
        icons = Utils.load_images(folder)
        #Debug tool to check if the icons are loaded correctly
        #print(f"PIP-BOY DEBUG:Loaded {len(icons)} icons from {folder}")
        #print("List 'icons' :")
        #print(f"Main variable type: {type(icons)}")
        #if len(icons) > 0:
        #    print(f"First element type: {type(icons[0])}")
        #    print(f"First element content: {icons[0]}")
        #
        if not icons:
            return
        if isinstance(icons, dict):
            icons = list(icons.values())
        elif isinstance(icons, list) and len(icons) > 0 and isinstance(icons[0], tuple):
            icons = [item[1] for item in icons]

        icons = [Utils.scale_image_abs(image, height=self.turntable_draw_space.height) for image in icons]
                
        class Animation2D:
            def __init__(self, screen, position, images, frame_duration):
                self.screen = screen
                self.position = position
                self.images = images
                self.frame_duration = frame_duration
                self.current_frame = 0
                self.last_update = pygame.time.get_ticks()

            def start(self):
                pass

            def stop(self):
                pass

            def render(self):
                now = pygame.time.get_ticks()
                if now - self.last_update > self.frame_duration:
                    self.current_frame = (self.current_frame + 1) % len(self.images)
                    self.last_update = now
                self.screen.blit(self.images[self.current_frame], self.position)
        self.item_turntable = Animation2D(
            self.screen,
            (self.turntable_draw_space.x, self.turntable_draw_space.y),
            icons,
            frame_duration=settings.SPEED * 100 #Rotation speed = funny number(smaller= faster)
        )
        self.item_turntable.start()
    #End of DanieleM's addition
        # try to get obj that matches icons name, otherwise use first obj in folder
        model_path = f"{settings.ITEMS_BASE_FOLDER}/{selected_item.icons}/{selected_item.icons}.obj"
        if not Utils.file_exists(model_path):
            try:
                model_path = f"{settings.ITEMS_BASE_FOLDER}/{selected_item.icons}/{os.listdir(f'{settings.ITEMS_BASE_FOLDER}/{selected_item.icons}')[0]}"
            except (FileNotFoundError, IndexError):
                return
     
        #3D model rendering added by kelmes1 (a replacement of the original 2D image animation)
        #self.item_turntable = WireframeItem(
        #    self.screen,
        #    (self.turntable_draw_space.x, self.turntable_draw_space.y),
        #    self.turntable_draw_space,
        #    model_path,
        #    frame_duration=settings.SPEED * 100,
        #    loop=True
        #)

        #self.item_turntable.start()

    def handle_threads(self, tab_selected: bool):
        """ Handle the threads"""
        if self.no_items:
            return
        if tab_selected and self.enable_turntable:
            Thread(target=self.start_item_animation).start()
        elif not tab_selected and self.enable_turntable and self.item_turntable :
            self.item_turntable.stop()
            self.item_turntable = None
            
    def calculate_grid_space(self):
        list_space = self.list_draw_space
        grid_top = list_space.top + (list_space.height * 0.38)
        grid_height = list_space.bottom - grid_top
        return pygame.Rect(
            list_space.right + settings.GRID_LEFT_MARGIN,
            grid_top,
            self.draw_space.width - list_space.width - settings.GRID_RIGHT_MARGIN,
            grid_height
            )
        
        
    def render(self):
        self.tab_instance.render_footer(self)
        if self.no_items:
            return
        self.inv_list.render(self.screen, self.active_item_index, self.item_selected)
        if self.enable_turntable and self.item_turntable:
            self.item_turntable.render()
            

