# radio_tab/radio_tab.py
import random
import time
import pygame
from threading import Thread
import settings
import os
from util_functs import Utils

from .radio_station_loader import RadioStationLoader
from .playlist_manager import PlaylistManager
from .visualizer import Visualizer
from ui import GenericList


class RadioTab:
    def __init__(self, screen, tab_instance, draw_space: pygame.Rect):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space

        self.tab_instance.init_footer(self)
        self.main_font = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 12)
        
        
        list_draw_space = pygame.Rect(
            self.draw_space.left,
            self.draw_space.top,
            self.draw_space.centerx - 2 * settings.TAB_SIDE_MARGIN,
            self.draw_space.height
        )
        
        self.station_list = GenericList(
            draw_space=list_draw_space,
            font=self.main_font,
            enable_dot=True
        )

        self.station_playing = False
        self.active_station_index = None
        self.previous_station_index = None

        self.current_song = None
        self.radio_music_thread_running = True

        self.loader = RadioStationLoader(settings.RADIO_BASE_FOLDER,
                                         settings.DCR_INTERMISSIONS_BASE_FOLDER)
        self.playlist_manager = PlaylistManager()
        self.visualizer = Visualizer(self.draw_space, self.screen, self)

        Thread(target=self.load_radio_stations, daemon=True).start()
        Thread(target=self.update_radio_music, daemon=True).start()

    def load_radio_stations(self):
        self.loader.load_radio_stations()
        self.station_list.set_items(list(self.loader.radio_stations.keys()))

    def play_station_switch_sound(self):
        sound = random.choice(os.listdir(settings.RADIO_STATIC_BURSTS_BASE_FOLDER))
        Utils.play_sfx(
            os.path.join(settings.RADIO_STATIC_BURSTS_BASE_FOLDER, sound),
            settings.VOLUME
        )

    def scroll(self, direction: bool):
        self.station_list.change_selection(direction)

    def select_station(self):
        if self.station_list.selected_index == self.active_station_index:
            self.station_playing = not self.station_playing
        else:
            self.station_playing = True

        if not self.station_playing:
            Utils.play_sfx(settings.RADIO_TURN_OFF_SOUND)
        else:
            self.play_station_switch_sound()

        self.active_station_index = self.station_list.selected_index


    def update_radio_music(self):
        while self.radio_music_thread_running:
            if (self.active_station_index is not None and 
                self.station_playing and 
                self.loader.radio_stations):
                station_names = list(self.loader.radio_stations.keys())
                if self.active_station_index >= len(station_names):
                    pygame.time.wait(1000)
                    continue

                station_name = station_names[self.active_station_index]
                station = self.loader.radio_stations[station_name]

                if station_name not in self.playlist_manager.station_playlists:
                    self.playlist_manager.station_playlists[station_name] = {
                        "playlist": self.playlist_manager.generate_station_playlist_for_station(
                            station, station_name
                        ),
                        "index": 0,
                        "song_start_time": None,
                        "initialized": False
                    }
                playlist_data = self.playlist_manager.station_playlists[station_name]
                playlist = playlist_data["playlist"]
                index = playlist_data["index"]

                if index >= len(playlist):
                    playlist_data["playlist"] = self.playlist_manager.generate_station_playlist_for_station(
                        station, station_name
                    )
                    playlist_data["index"] = 0
                    playlist_data["song_start_time"] = None
                    playlist_data["initialized"] = False
                    index = 0
                    playlist = playlist_data["playlist"]

                current_song = playlist[index]
                if settings.DCR_INTERMISSIONS_BASE_FOLDER in current_song:
                    duration_ms = self.loader.intermissions.get(current_song, 0)
                else:
                    duration_ms = station["music_files"].get(current_song, 0)
                duration_sec = duration_ms / 1000.0

                if playlist_data["song_start_time"] is None:
                    if not playlist_data["initialized"]:
                        random_offset = random.uniform(0, max(0, duration_sec - 1))
                        playlist_data["song_start_time"] = time.time() - random_offset
                        playlist_data["initialized"] = True
                    else:
                        playlist_data["song_start_time"] = time.time()

                song_offset = time.time() - playlist_data["song_start_time"]

                if song_offset < duration_sec:
                    if self.current_song != current_song:
                        try:
                            pygame.mixer.music.load(current_song)
                            pygame.mixer.music.set_volume(settings.MUSIC_VOLUME)
                            pygame.mixer.music.play(start=song_offset)
                            self.current_song = current_song
                        except Exception as e:
                            print(f"Error playing {current_song}: {e}")
                            playlist_data["index"] += 1
                            playlist_data["song_start_time"] = None
                            self.current_song = None
                    else:
                        if not pygame.mixer.music.get_busy():
                            pygame.mixer.music.play(start=song_offset)
                else:
                    playlist_data["index"] += 1
                    playlist_data["song_start_time"] = None
                    self.current_song = None
                    pygame.mixer.music.stop()
            else:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                self.current_song = None

            wait_time = 300 if self.active_station_index is not None else 1000
            pygame.time.wait(wait_time)

    def handle_threads(self, tab_selected: bool):
        if tab_selected:
            self.visualizer.start()
        else:
            self.visualizer.stop()

    def render_visualizer_waves(self):
        self.visualizer.render()

    def render(self):
        self.tab_instance.render_footer(self)
        self.station_list.render(self.screen, self.active_station_index, self.station_playing)
        self.render_visualizer_waves()
