import subprocess
import os
import pygame
import time

# Define two temporary output file names
output_file_1 = "temp_output_1.wav"
output_file_2 = "temp_output_2.wav"


def is_file_in_use(file_path):
    """Check if a file is currently being used by another process."""
    try:
        # Try to rename the file; if it succeeds, the file is not in use
        os.rename(file_path, file_path)
        return False
    except OSError:
        return True


def safe_remove(file_path):
    """Attempt to delete a file, retrying if it's in use."""
    attempts = 5
    while attempts > 0:
        if os.path.exists(file_path):
            try:
                pygame.mixer.quit()
                # Try to remove the file
                os.remove(file_path)
                print(f"Deleted: {file_path}")
                pygame.mixer.init()
                return True
            except PermissionError:
                # File is likely in use; wait and retry
                print(f"File {file_path} is in use, retrying...")
                time.sleep(0.2)  # Wait before retrying
        else:
            print(f"File {file_path} does not exist, no need to delete.")
            return True  # File doesn't exist, deletion is successful
        attempts -= 1

    print(f"Could not delete {file_path} after multiple attempts.")
    return False  # Indicate failure to delete the file


def output_with_piper(text, output_file):
    pygame.mixer.init()

    try:
        # Stop any ongoing playback and release file locks
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        pygame.mixer.quit()  # Release all file locks
        pygame.mixer.init()  # Reinitialize for new playback

        time.sleep(0.1)  # Allow time for locks to release

        # Determine the other file to delete
        other_file = output_file_1 if output_file == output_file_2 else output_file_1

        # Safely remove the other output file if it exists
        if not safe_remove(other_file):
            print(f"Warning: Could not delete {other_file}. Proceeding cautiously.")

        # Sanitize text to remove line breaks
        sanitized_text = text.replace("\n", " ")

        # Run the Piper command to generate the new file
        command = f'echo "{sanitized_text}" | .\\piper.exe -m en_GB-cori-high.onnx -f {output_file}'
        print(f"Executing command: {command}")
        subprocess.run(command, shell=True, check=True)

        # Ensure the output file exists
        if not os.path.exists(output_file):
            print(f"Error: Output file {output_file} was not created.")
            return False

        print(f"File {output_file} successfully created.")

        # Load and play the new audio file
        pygame.mixer.music.load(output_file)
        pygame.mixer.music.play()

        print(f"Speaking: {text}")

        # Wait until playback finishes
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        return True  # Indicate success

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while generating audio: {e}")
        return False
    except Exception as e:
        print(f"An error occurred during playback: {e}")
        return False

    finally:
        pygame.mixer.quit()  # Release resources
