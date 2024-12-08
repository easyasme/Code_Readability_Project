import subprocess
import keyboard
import time

class CameraCapture:
    def __init__(self):
        self.preview_process = None

    def start_preview(self):
        self.preview_process = subprocess.Popen(["libcamera-still", "-t", "0"])

    def stop_preview(self):
        if self.preview_process and self.preview_process.poll() is None:
            self.preview_process.terminate()
            self.preview_process.wait()

    def capture_image(self, index):
        filename = f"output_{index}.jpg"
        subprocess.run(["libcamera-still", "-o", filename, "-n"])
        print(f"Image captured: {filename}")
        return index + 1  # Increment the counter

if __name__ == "__main__":
    camera_capture = CameraCapture()
    camera_capture.start_preview()
    print("Press 's' to capture an image. Press 'q' to quit.")

    capture_index = 1  # Initialize the counter

    try:
        while True:
            if keyboard.is_pressed("s"):
                camera_capture.stop_preview()  # Stop the previous preview process
                capture_index = camera_capture.capture_image(capture_index)
                camera_capture.start_preview()  # Start a new preview process
            elif keyboard.is_pressed("q"):
                break
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass

    camera_capture.stop_preview()  # Stop the preview when the program exits
