import os
import pygame
import settings
from threading import Thread
from data_models import IconConfig
from typing import Dict, List
from util_functs import Utils


class StatusTab:    

    def __init__(self, screen, tab_instance, draw_space: pygame.Rect):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        self.player_data = getattr(self.tab_instance, 'player_data', {'status_side_index': 0})
        self.conditionboy_thread = None
        self.conditionboy_thread_running = False
        self.small_font = pygame.font.Font(settings.ROBOTO_CONDENSED_BOLD_PATH, 12)
        
        # Initialize components
        self._init_conditionboy()
        self.player_surface = self.small_font.render(settings.PLAYER_NAME, True, settings.PIP_BOY_LIGHT)
        
        self.setup_limb_damage(settings.DEFAULT_LIMB_DAMAGE)

        self.setup_stats_display(settings.DEFAULT_STATS_DAMAGE, settings.DEFAULT_STATS_ARMOR)


    def _init_conditionboy(self):
        """Initialize vault boy animation components"""
        
        conditionboy_scale = self.draw_space.height / settings.CONDITIONBOY_SCALE
        
        self.extra_head_x = 0
        legs_index = self._get_legs_index()
        
        
        # Load conditionboy legs svgs
        self.conditionboy_legs, self.conditionboy_transforms = Utils.load_svgs(os.path.join(settings.STAT_TAB_BODY_SVG_BASE_FOLDER, f"legs{legs_index}"), conditionboy_scale, load_transforms=True)
        head_scale = conditionboy_scale / 2
        self.conditionboy_head = Utils.load_svg(head_scale, self._get_head_path())
    
        self.conditionboy_legs_centerx = self.conditionboy_legs[0].width // 2
        self.conditionboy_legs_centery = self.conditionboy_legs[0].height // 2
        
        self.conditionboy_head_offsets = self._load_conditionboy_offsets(legs_index)
        
        self.conditionboy_surface = pygame.Surface(
            (self.draw_space.width, self.draw_space.height),
            pygame.SRCALPHA
        )
        
        self.conditionboy_screen_position = self.conditionboy_surface.get_rect(
            center=(self.draw_space.x + self.draw_space.width // 2,
                     self.draw_space.y + self.draw_space.height // 2)
        )
        
        self.conditionboy_index = 0
        self.conditionboy_heads_index = 0


    def _get_legs_index(self) -> str:
        """Get the path of the legs image to use based on current limb damage."""
        # Assume that limb HP is stored in self.stats.limb_hp and that
        # settings.DEFAULT_LIMB_DAMAGE follows the order:
        # [head, left arm, right arm, torso, left leg, right leg]
        default_hp = settings.DEFAULT_LIMB_DAMAGE

        # Determine if each limb is damaged (current < max)
        left_arm_damaged = default_hp[1] <= settings.CRIPPLED_THRESHOLD
        right_arm_damaged = default_hp[2] <= settings.CRIPPLED_THRESHOLD
        left_leg_damaged = default_hp[4] <= settings.CRIPPLED_THRESHOLD
        right_leg_damaged = default_hp[5] <= settings.CRIPPLED_THRESHOLD
 
        # Use weighted values for each limb:
        # base state 1 (nothing damaged)
        state = 1
        if left_arm_damaged:
            state += 1       # weight 1
        if right_arm_damaged:
            state += 2       # weight 2
        if left_leg_damaged:
            self.extra_head_x = 3
            state += 4       # weight 4
        if right_leg_damaged:
            self.extra_head_x = 3
            state += 8       # weight 8

        # Optionally, if head damage is also considered (index 0)
        head_damaged = default_hp[0] <= settings.CRIPPLED_THRESHOLD
        if head_damaged and left_arm_damaged and right_arm_damaged and left_leg_damaged and right_leg_damaged:
            state = 16  # All limbs (including head) are damaged

        # Return the legs image path based on the computed state.
        return state

 
    def _get_head_path(self) -> str:
        """Get the path of the head image to use"""
        head_hp = settings.DEFAULT_LIMB_DAMAGE[0]
        
        paths = settings.STAT_TAB_HEADS
        crippled_limbs = len([True for x in settings.DEFAULT_LIMB_DAMAGE if x < settings.CRIPPLED_THRESHOLD])
        
        if head_hp >= settings.CRIPPLED_THRESHOLD:
            if settings.RADIATION_CURRENT > settings.DAMAGED_THRESHOLD:
                return paths["radiated"]
            elif settings.ADDICTED:
                return paths["addicted"]
            elif head_hp >= settings.DAMAGED_THRESHOLD and crippled_limbs <= 2:
                return paths["normal"]
            return paths["damaged"]
        else:
            if settings.RADIATION_CURRENT > settings.DAMAGED_THRESHOLD:
                return paths["radiated_crippled"]
            elif settings.ADDICTED:
                return paths["addicted_crippled"]
            return paths["crippled"]
        

    def scroll(self, direction: bool):
        p_data = getattr(self.tab_instance, 'player_data', self.player_data)
        current_idx = p_data.get('status_side_index', 0)
        
        if direction: # UP
            p_data['status_side_index'] = (current_idx - 1) % 3
        else: # DOWN
            p_data['status_side_index'] = (current_idx + 1) % 3
        
       

    def _load_conditionboy_offsets(self, legs_index: int) -> List:
        
        ini_file = os.path.join(settings.STAT_TAB_BODY_SVG_BASE_FOLDER, f"legs{legs_index}", settings.STAT_TAB_OFFSET_INI)
        try:
            with open(ini_file, 'r') as f:
                positions = []
                for pos in f.read().split(";"):
                    x, y = pos.split(",")
                    x = float(x) * self.draw_space.width / settings.CONDITIONBOY_SCALE
                    y = float(y) * self.draw_space.height / settings.CONDITIONBOY_SCALE
                    
                    positions.append((x, y))
                # return [tuple(map(float, pos.split(","))) for pos in f.read().split(";")]
                return positions
                
        except FileNotFoundError:
            # Fill with 0 offsets with the same length as the number of frames
            return [(0.0, 0.0) for _ in range(len(self.conditionboy_legs))]
            
                
        
    def _calculate_stats_width(self, big_rect_size: int, small_rect_size: int, 
                                num_damage_icons: int, num_armor_icons: int) -> int:
            """Calculate total width needed for stats display"""
            # Calculate margins
            total_margins = (
                settings.DAMAGE_ARMOUR_MARGIN_BIG +  # Space between damage and armor sections
                (num_damage_icons * settings.DAMAGE_ARMOUR_MARGIN_SMALL) +  # Spaces between damage icons
                (num_armor_icons * settings.DAMAGE_ARMOUR_MARGIN_SMALL)     # Spaces between armor icons
            )
            
            # Calculate icon spaces
            total_icon_space = (
                (big_rect_size * 2) +  # Space for big damage and armor icons
                (num_damage_icons * small_rect_size) +  # Space for small damage icons
                (num_armor_icons * small_rect_size)     # Space for small armor icons
            )
        
            return total_icon_space + total_margins

    def _render_stats_icons(self, icons: Dict, big_rect_size: int, small_rect_size: int):
        """Render damage and armor icons with their values"""
        margin = 0
        
        # Helper function for icon rendering
        def render_icon_section(icon_type: str):
            nonlocal margin
            
            # Render big icon
            big_icon = Utils.scale_image(
                pygame.image.load(icons[icon_type]['big']).convert_alpha(),
                settings.DAMAGE_ARMOUR_ICON_BIG_SIZE
            )
            
            big_icon = Utils.tint_image(big_icon)
            
            # Draw background rectangle
            pygame.draw.rect(
                self.stats_surface,
                settings.PIP_BOY_DARK,
                (margin, 0, big_rect_size, big_rect_size)
            )
            
            # Center and draw big icon
            self.stats_surface.blit(
                big_icon,
                (margin + (big_rect_size // 2 - big_icon.get_width() // 2),
                 big_rect_size // 2 - big_icon.get_height() // 2)
            )
            margin += big_rect_size
            
            # Render small icons
            for small_icon_path, value in zip(icons[icon_type]['small'], icons[icon_type]['values']):
                margin += settings.DAMAGE_ARMOUR_MARGIN_SMALL
                
                # Scale and load small icon
                small_icon = Utils.scale_image(
                    pygame.image.load(small_icon_path).convert_alpha(),
                    settings.DAMAGE_ARMOUR_ICON_SMALL_SIZE
                )
                
                small_icon = Utils.tint_image(small_icon)
                
                # Draw background rectangle
                pygame.draw.rect(
                    self.stats_surface,
                    settings.PIP_BOY_DARK,
                    (margin, 0, small_rect_size, big_rect_size)
                )
                
                # Center and draw small icon
                self.stats_surface.blit(
                    small_icon,
                    (margin + (small_rect_size // 2 - small_icon.get_width() // 2),
                     big_rect_size // 4 - small_icon.get_height() // 2)
                )
                
                # Render value text
                text_surface = self.small_font.render(str(value), True, settings.PIP_BOY_LIGHT)
                self.stats_surface.blit(
                    text_surface,
                    (margin + (small_rect_size // 2 - text_surface.get_width() // 2),
                     big_rect_size - text_surface.get_height() - (settings.DAMAGE_ARMOUR_ICON_MARGIN // 4))
                )
                
                margin += small_rect_size
        
        # Render damage section
        render_icon_section('damage')
        
        # Add margin between damage and armor sections
        margin += settings.DAMAGE_ARMOUR_MARGIN_BIG
        
        # Render armor section
        render_icon_section('armor')
        
    def setup_limb_damage(self, limb_damages: List[int]):
        """Initialize limb damage display with given damage values"""
        if len(limb_damages) != len(settings.LIMB_POSITIONS):
            raise ValueError("Number of damage values must match number of limb positions")
            
        width = settings.LIMB_DAMAGE_WIDTH
        height = width // 4
        center_x = self.draw_space.width // 2
        
        self.limb_damage_surface = pygame.Surface(
            (self.draw_space.width, self.draw_space.height), 
            pygame.SRCALPHA
        ).convert_alpha()
        
        for damage, pos in zip(limb_damages, settings.LIMB_POSITIONS):
            # Calculate rectangle positions
            rect = pygame.Rect(
                center_x - width // 2 + pos.x_offset,
                pos.y_position,
                width,
                height
            )
            
            # Draw damage fill
            damage_rect = rect.copy()
            damage_rect.width = int(damage_rect.width * (damage / 100))
            pygame.draw.rect(self.limb_damage_surface, settings.PIP_BOY_LIGHT, damage_rect)
            
            # Draw outline
            pygame.draw.rect(self.limb_damage_surface, settings.PIP_BOY_LIGHT, rect, 1)

    def setup_stats_display(self, damage_icons: List[IconConfig], armor_icons: List[IconConfig]):
        """Setup damage and armor statistics display"""
        icons = {
            'damage': {
                'big': settings.STAT_TAB_GUN,
                'small': [icon.path for icon in damage_icons],
                'values': [icon.value for icon in damage_icons]
            },
            'armor': {
                'big': settings.STAT_TAB_ARMOUR,
                'small': [icon.path for icon in armor_icons],
                'values': [icon.value for icon in armor_icons]
            }
        }
        
        self._create_stats_surface(icons)

    def _create_stats_surface(self, icons):
        """Create the surface for displaying damage and armor stats"""
        # Calculate dimensions        
        big_rect_size = self.draw_space.width // settings.DAMAGE_ARMOUR_ICON_ABSOLUTE_SIZE
        small_rect_size = big_rect_size // 2
        
        # Calculate total width
        total_width = self._calculate_stats_width(
            big_rect_size, small_rect_size,
            len(icons['damage']['small']), len(icons['armor']['small'])
        )
        
        self.stats_surface = pygame.Surface((total_width, big_rect_size), pygame.SRCALPHA).convert_alpha()
        self._render_stats_icons(icons, big_rect_size, small_rect_size)




    def update_conditionboy(self):
        """Update vault boy animation frame"""
        while self.conditionboy_thread_running:
            self.conditionboy_surface.fill((0, 0, 0, 0))
            x_offset_body = self.draw_space.centerx - (self.conditionboy_transforms[self.conditionboy_index][0]) - self.conditionboy_legs_centerx
            y_offset_body = self.draw_space.centery / 2 - (self.conditionboy_transforms[self.conditionboy_index][1]) - self.conditionboy_legs_centery / 2 + 10
            
                        
            self.conditionboy_surface.blit(
                self.conditionboy_legs[self.conditionboy_index],
                (x_offset_body, y_offset_body))
            
            x_offset_head = self.conditionboy_head_offsets[self.conditionboy_index][0] + self.draw_space.centerx - self.conditionboy_head.width / 2 - self.extra_head_x
            y_offset_head = self.conditionboy_head_offsets[self.conditionboy_index][1] + self.conditionboy_head.height
                        
            self.conditionboy_surface.blit(
                self.conditionboy_head,
                (x_offset_head, y_offset_head)
            )
            
            self.conditionboy_index = (self.conditionboy_index + 1) % len(self.conditionboy_legs)
            
            pygame.time.wait(settings.SPEED * 150)
    
    def handle_threads(self, tab_selected: bool):
        """ Handle the threads"""
        if tab_selected and not self.conditionboy_thread_running:
            self.conditionboy_thread_running = True
            self.conditionboy_thread = Thread(target=self.update_conditionboy, daemon=True)
            self.conditionboy_thread.start()
        elif not tab_selected and self.conditionboy_thread_running:
            self.conditionboy_thread_running = False
            self.conditionboy_thread.join()
            

    def render(self):
        """Render all components to the screen"""
        ui_style = str(getattr(settings, 'UI_STYLE', '')).lower()
        
        if ui_style == 'fallout_nv':
            return

        # --- OG Rendering: Fallout 4 ---
        self.render_conditionboy()
        self.render_player_name()
        if hasattr(self, 'stats_surface'):
            self.render_stats()
        if hasattr(self, 'limb_damage_surface'):
            self.render_limb_damage()

    def render_conditionboy(self):
        self.screen.blit(self.conditionboy_surface, self.conditionboy_screen_position)

    def render_player_name(self):
        player_pos = (
            self.draw_space.x + self.draw_space.width // 2 - self.player_surface.get_width() // 2,
            self.draw_space.y + self.draw_space.height - self.player_surface.get_height()
        )
        self.screen.blit(self.player_surface, player_pos)

    def render_stats(self):
        stats_pos = (
            self.draw_space.x + self.draw_space.width // 2 - self.stats_surface.get_width() // 2,
            self.draw_space.y + self.draw_space.height - (self.stats_surface.get_height() * 1.7)
        )
        self.screen.blit(self.stats_surface, stats_pos)

    def render_limb_damage(self):
        self.screen.blit(self.limb_damage_surface, self.draw_space)