import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from playsound import playsound
from PIL import Image

from api_calls import generate_image_desc, create_judgemental_desc, generate_audio


class MP3Handler(FileSystemEventHandler):
    """Handles MP3 file creation events."""

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith('.mp3'):
            return
        print(f"-> Detected MP3 file creation: {event.src_path}")
        self._play_audio(event.src_path)

    @staticmethod
    def _play_audio(filepath):
        playsound(filepath)


class ImageHandler(FileSystemEventHandler):
    """Handles image file creation events, performing different actions based on the directory."""

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith(('.jpg', '.jpeg')):
            return

        directory_name = os.path.basename(os.path.dirname(event.src_path))
        file_name, _ = os.path.splitext(os.path.basename(event.src_path))
        print(f"-> Detected image file creation in {directory_name} directory: {file_name}")

        if directory_name == "tmp":
            if event.src_path.endswith('.jpg'):
                # Convert JPG to JPEG if in "tmp" directory
                self._convert_image_to_jpeg(event.src_path, file_name)
        elif directory_name == "image":
            # Analyze and speak if in "image" directory
            self._analyze_and_speak(event.src_path, file_name)

    def _convert_image_to_jpeg(self, filepath, file_name):
        """Converts an image file to JPEG format."""
        print("-- Converting tmp image to JPEG")
        with Image.open(filepath) as img:
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            output_path = os.path.join(os.path.dirname(filepath).replace("tmp", "image"), file_name + ".jpeg")
            img.save(output_path, "JPEG")
        print(f"-- Image converted to JPEG: {output_path}")

    def _analyze_and_speak(self, filepath, file_name):
        """Analyzes an image and converts its description to speech."""
        print("-> Starting image analysis:")
        neutral_desc = generate_image_desc(filepath)
        judgy_desc = create_judgemental_desc(neutral_desc)
        # output_path = os.path.join(os.path.dirname(filepath).replace("image", "audio"), file_name + ".mp3")
        # generate_audio(judgy_desc, output_path)


def setup_and_start_observer(directories):
    print("-- Launching app: Monitoring file creation...")
    observer = Observer()
    mp3_handler = MP3Handler()
    image_handler = ImageHandler()

    # Assuming directories are structured with separate paths for audio and images
    observer.schedule(mp3_handler, directories['audio'], recursive=False)
    observer.schedule(image_handler, directories['image'], recursive=False)
    observer.schedule(image_handler, directories['tmp'], recursive=False)

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Terminating monitoring")
        observer.stop()
    observer.join()

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    directories_to_watch = {
        'audio': os.path.join(current_dir, 'audio'),
        'image': os.path.join(current_dir, 'image'),
        'tmp': os.path.join(current_dir, 'tmp'),
    }

    setup_and_start_observer(directories_to_watch)
