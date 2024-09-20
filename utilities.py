import threading
from playsound import playsound
import os


class SoundPlayer:
    def __init__(self, sound_path):
        self.sound_path = sound_path
        self.playing = False
        self.thread = threading.Thread(target=self._play_loop)

    def _play_loop(self):
        while self.playing:
            playsound(self.sound_path)

    def start(self):
        if not self.playing:
            self.playing = True
            self.thread.start()

    def stop(self):
        self.playing = False
        self.thread.join()


def clean_folder(folder_path):
    # Check if the folder exists
    if not os.path.exists(folder_path):
        print("The folder does not exist.")
        return

    # Iterate over all the entries
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')