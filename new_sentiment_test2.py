#NEW SENTIMENT FUNCTION OF INTEREST: update_display AND animate
import pygame
from transformers import pipeline
from new_sentiment import animate, update_display
from threading import Thread
import time
import random

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Shared variables
emotion = "neutral"
running = True  # To gracefully exit the program

# Predefined emotions for testing
test_emotions = ["joy", "sadness", "neutral", "amusement", "grief", "love", "disappointment"]

# Function to handle the animation in the background
def animation_thread():
    global running
    while running:
        update_display()
        clock.tick(60)  # Control frame rate to avoid high CPU usage

# Function to simulate emotional changes
def emotion_simulation_thread():
    global emotion, running
    while running:
        # Simulate a random emotional change every 2-5 seconds
        time.sleep(random.uniform(2, 5))
        detected_emotion = random.choice(test_emotions)
        print(f"Simulated Detected Emotion: {detected_emotion}")
        animate(detected_emotion)

# Main function
def main():
    global running

    # Start the animation thread
    animation_thread_obj = Thread(target=animation_thread, daemon=True)
    animation_thread_obj.start()

    # Start the emotion simulation thread
    emotion_thread_obj = Thread(target=emotion_simulation_thread, daemon=True)
    emotion_thread_obj.start()

    # Run until the user closes the program
    try:
        while running:
            time.sleep(0.1)  # Keep the main thread alive
    except KeyboardInterrupt:
        running = False
        print("Exiting...")
        pygame.quit()

if __name__ == "__main__":
    main()
