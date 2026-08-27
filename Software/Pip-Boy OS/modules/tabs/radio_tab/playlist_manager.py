# radio_tab/playlist_manager.py
import os
import random
import settings

class PlaylistManager:
    def __init__(self):
        self.station_playlists = {}

    def add_intermissions_to_playlist(self, playlist: list) -> list:
        if not playlist:
            return playlist

        freq = settings.INTERMISSION_FREQUENCY
        max_count = min(freq * 2, len(playlist) // 3)
        count = random.randint(1, max_count) if max_count >= 1 else 0
        if count == 0:
            return playlist

        indices = random.sample(range(len(playlist)), count)
        intermission_choices = {}
        base_path = settings.DCR_INTERMISSIONS_BASE_FOLDER

        for i in indices:
            song = playlist[i]
            file_name = os.path.splitext(os.path.basename(song))[0]
            parts = file_name.split('_')
            if len(parts) < 2:
                continue

            artist = parts[-2]
            song_name = parts[-1]
            artist_path = os.path.join(base_path, artist)

            pre_options = []
            after_options = []

            def gather_ogg_files(path):
                if os.path.exists(path):
                    for entry in os.scandir(path):
                        if entry.is_file() and entry.name.endswith('.ogg'):
                            yield entry.path

            pre_options.extend(gather_ogg_files(artist_path))
            after_options.extend(gather_ogg_files(artist_path))

            pre_dir = os.path.join(artist_path, 'pre')
            pre_options.extend(gather_ogg_files(pre_dir))

            after_dir = os.path.join(artist_path, 'after')
            after_options.extend(gather_ogg_files(after_dir))

            song_dir = os.path.join(artist_path, song_name)
            pre_options.extend(gather_ogg_files(song_dir))
            after_options.extend(gather_ogg_files(song_dir))

            song_pre_dir = os.path.join(song_dir, 'pre')
            pre_options.extend(gather_ogg_files(song_pre_dir))

            song_after_dir = os.path.join(song_dir, 'after')
            after_options.extend(gather_ogg_files(song_after_dir))

            has_pre = len(pre_options) > 0
            has_after = len(after_options) > 0

            if not (has_pre or has_after):
                continue

            choice = random.choice(['pre', 'after']) if has_pre and has_after else ('pre' if has_pre else 'after')
            if choice == 'pre':
                selected = random.choice(pre_options)
                intermission_choices.setdefault(song, {})['pre'] = selected
            else:
                selected = random.choice(after_options)
                intermission_choices.setdefault(song, {})['after'] = selected

        new_playlist = []
        for song in playlist:
            if song in intermission_choices and 'pre' in intermission_choices[song]:
                new_playlist.append(intermission_choices[song]['pre'])
            new_playlist.append(song)
            if song in intermission_choices and 'after' in intermission_choices[song]:
                new_playlist.append(intermission_choices[song]['after'])

        return new_playlist

    def generate_station_playlist_for_station(self, station, station_name=None) -> list:
        playlist = list(station["music_files"].keys())
        if not station["ordered"]:
            random.shuffle(playlist)
        if station_name and station_name == "Diamond City Radio":
            playlist = self.add_intermissions_to_playlist(playlist)
        return playlist
