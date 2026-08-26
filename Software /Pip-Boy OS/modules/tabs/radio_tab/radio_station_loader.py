# radio_tab/radio_station_loader.py
import os
import configparser
import time
from concurrent.futures import ThreadPoolExecutor
from tinytag import TinyTag

class RadioStationLoader:
    def __init__(self, base_folder, intermissions_base_folder):
        self.base_folder = base_folder
        self.intermissions_base_folder = intermissions_base_folder
        self.radio_stations = {}
        self.intermissions = {}

    def load_music_files(self, station_folder: str):
        music_files = {}
        try:
            for entry in os.scandir(station_folder):
                if entry.name.endswith('.ogg'):
                    try:
                        tag = TinyTag.get(entry.path)
                        music_files[entry.path] = int(tag.duration * 1000)
                    except Exception:
                        continue
        except Exception:
            pass
        return music_files

    def load_intermissions(self, base_path=None):
        intermissions = {}
        intermissions_path = base_path or self.intermissions_base_folder
        if not os.path.exists(intermissions_path):
            return intermissions

        for entry in os.scandir(intermissions_path):
            if entry.is_dir():
                intermissions.update(self.load_intermissions(entry.path))  # recursive call
            elif entry.is_file() and entry.name.endswith('.ogg'):
                try:
                    tag = TinyTag.get(entry.path)
                    intermissions[entry.path] = int(tag.duration * 1000)
                except Exception:
                    continue

        return intermissions

    def load_radio_stations(self):
        def load_single_station(entry):
            if not entry.is_dir():
                return None
            ini_path = os.path.join(entry.path, "station.ini")
            if not os.path.exists(ini_path):
                return None
            try:
                config = configparser.ConfigParser()
                with open(ini_path) as f:
                    config.read_file(f)
                music_files = self.load_music_files(entry.path)
                if not music_files:
                    return None
                station_name = config.get("metadata", "station_name", fallback=entry.name)
                station_data = {
                    "ordered": config.getboolean("metadata", "ordered", fallback=False),
                    "music_files": music_files,
                    "start_timestamp": time.time()  # radio timeline starts now
                }
                return station_name, station_data
            except Exception:
                return None

        try:
            with os.scandir(self.base_folder) as entries:
                with ThreadPoolExecutor(max_workers=2) as executor:
                    self.radio_stations = {
                        name: data
                        for result in executor.map(load_single_station, entries)
                        if result
                        for name, data in [result]
                    }
        except Exception:
            self.radio_stations = {}

        try:
            self.intermissions = self.load_intermissions()
        except Exception:
            self.intermissions = {}
