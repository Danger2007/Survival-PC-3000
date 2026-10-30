# radio_tab/visualizer.py
import random
import numpy as np
import pygame
import settings
from threading import Thread, Lock

class Visualizer:
    def __init__(self, draw_space: pygame.Rect, screen, radio_tab_instance):
        self.draw_space = draw_space
        self.screen = screen
        self.radio_tab_instance = radio_tab_instance

        self.visualizer_size = (self.draw_space.centerx -
                                settings.TAB_SIDE_MARGIN * 2 -
                                settings.RADIO_WAVE_VISUALIZER_SIZE_OFFSET)
        self.vis_x = self.draw_space.centerx + settings.RADIO_WAVE_VISUALIZER_SIZE_OFFSET // 2
        self.vis_y = self.draw_space.top
        self.midpoint_y = self.vis_y + self.visualizer_size // 2

        self.wave_points = np.zeros(64, dtype=np.float32)
        self.wave_point_lock = Lock()
        self.x_positions = np.linspace(0, self.visualizer_size, 64, dtype=np.int32)

        self.waves = np.array([
            [1.0, 0.5, 0.0, 1.0, 0.5],
            [2.0, 0.3, 0.0, 2.0, 0.3],
            [3.0, 0.2, 0.0, 3.0, 0.2]
        ], dtype=np.float32)

        self.wave_patterns = {
            'idle': np.array([[0.2, 0.8], [0.05, 0.2]], dtype=np.float32),
            'playing': np.array([[1.0, 4.0], [0.5, 1.0]], dtype=np.float32),
            'changing': np.array([[8.0, 20.0], [0.1, 0.6]], dtype=np.float32)
        }

        self.visualizer_thread = None
        self.visualizer_thread_running = False
        self.change_station_wave_counter = 0

        self.wave_surface = pygame.Surface(
            (self.draw_space.width, self.draw_space.height),
            pygame.SRCALPHA
        ).convert_alpha()
        
        self.grid_surface = self._prepare_grid()
        
        self.change_visualizer_wave(64)

    def _prepare_grid(self):
        grid_surface = pygame.Surface(
            (self.draw_space.width, self.draw_space.height),
            pygame.SRCALPHA
        ).convert_alpha()
        grid_surface.fill((0, 0, 0, 0))
        
        # Render x-axis
        pygame.draw.line(
            grid_surface, settings.PIP_BOY_LIGHT, (self.vis_x, self.vis_y + self.visualizer_size), (self.vis_x + self.visualizer_size, self.vis_y + self.visualizer_size), 1
        )
        
        # Render y-axis
        pygame.draw.line(
            grid_surface, settings.PIP_BOY_LIGHT, (self.vis_x + self.visualizer_size, self.vis_y), (self.vis_x + self.visualizer_size, self.vis_y + self.visualizer_size), 1
        )
        
        # Render small lines along big lines
        for i in range(1, settings.RADIO_WAVE_VISUALIZER_GRID_LINES):
            line_size = 5 if i % 4 == 0 else 3
            x = self.vis_x + i * (self.visualizer_size // settings.RADIO_WAVE_VISUALIZER_GRID_LINES)
            pygame.draw.line(grid_surface, settings.PIP_BOY_LIGHT, (x, self.vis_y + self.visualizer_size), (x, self.vis_y - line_size + self.visualizer_size), 1)
            y = self.vis_y + i * (self.visualizer_size // settings.RADIO_WAVE_VISUALIZER_GRID_LINES)
            pygame.draw.line(grid_surface, settings.PIP_BOY_LIGHT, (self.vis_x + self.visualizer_size, y), (self.vis_x - line_size + self.visualizer_size, y), 1)
            
        return grid_surface

    def _prepare_wave_pattern(self, pattern_name: str):
        pattern = self.wave_patterns[pattern_name]
        random_values = np.random.uniform(pattern[:, 0], pattern[:, 1], size=(len(self.waves), 2)).astype(np.float32)
        self.waves[:, 3:5] = random_values

    def change_visualizer_wave(self, batch_size):
        new_samples = []
        for _ in range(batch_size):
            # Update wave parameters towards targets
            self.waves[:, 0:2] += (self.waves[:, 3:5] - self.waves[:, 0:2]) * settings.RADIO_WAVE_SMOOTHING_FACTOR
            # Update phase
            self.waves[:, 2] = (self.waves[:, 2] + self.waves[:, 0] * 0.08) % (2 * np.pi)
            # Compute current wave value
            total_wave = np.sum(np.sin(self.waves[:, 2]) * self.waves[:, 1]) / len(self.waves)

            # State checks and pattern changes
            station_playing = self.radio_tab_instance.station_playing
            active_station_index = self.radio_tab_instance.active_station_index

            if not station_playing and abs(total_wave) < 0.05:
                self._prepare_wave_pattern('idle')
                self.change_station_wave_counter = 0
            elif active_station_index != self.radio_tab_instance.previous_station_index:
                self._prepare_wave_pattern('changing')
                self.change_station_wave_counter = random.randint(30, 90)
                self.radio_tab_instance.previous_station_index = active_station_index
            elif self.change_station_wave_counter > 0:
                self.change_station_wave_counter -= 1
                if self.change_station_wave_counter == 1:
                    self._prepare_wave_pattern('playing')
            elif abs(total_wave) < 0.05 and random.random() < 0.1:
                self._prepare_wave_pattern('playing')
                
            new_samples.append(total_wave)

        # Update wave_points with new batch
        with self.wave_point_lock:
            # Efficiently shift and update the wave points
            self.wave_points[:-batch_size] = self.wave_points[batch_size:]
            self.wave_points[-batch_size:] = new_samples

    def update_visualiser(self):
        batch_size = settings.RADIO_WAVE_BATCH_SIZE
        while self.visualizer_thread_running:
            self.change_visualizer_wave(batch_size)
            # Adjust wait time to maintain the same sample rate
            pygame.time.wait(settings.SPEED * 50)

    def start(self):
        if not self.visualizer_thread or not self.visualizer_thread.is_alive():
            self.visualizer_thread_running = True
            self.visualizer_thread = Thread(
                target=self.update_visualiser,
                daemon=True
            )
            self.visualizer_thread.start()

    def stop(self):
        if self.visualizer_thread and self.visualizer_thread.is_alive():
            self.visualizer_thread_running = False
            self.visualizer_thread.join()
            self.visualizer_thread = None

    def render_waves(self):
        with self.wave_point_lock:
            points = self.wave_points.copy()
        self.wave_surface.fill((0, 0, 0, 0))
        x_coords = self.vis_x + self.x_positions
        y_coords = self.midpoint_y + (points * (self.visualizer_size // 2)).astype(int)
        points_array = np.column_stack((x_coords, y_coords))
        pygame.draw.lines(self.wave_surface, settings.PIP_BOY_LIGHT, False, points_array, 1)
        self.screen.blit(self.wave_surface, (0, 0))

    def render(self):
        self.screen.blit(self.grid_surface, (0, 0))
        self.render_waves()