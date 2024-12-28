import pygame
import math
import time
import sys
import random
import threading  # For parallel speech and animation
from transformers import pipeline

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (30, 144, 255)

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Robot Eye Animation")

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Eye parameters
eye_radius = 100
pupil_radius = 30
blink_duration = 200
blink_timer = pygame.time.get_ticks()
is_blinking = False
emotion = "neutral"
pupil_offset_x = 0
pupil_offset_y = 0
random_movement_timer = pygame.time.get_ticks()
random_emotion_timer = pygame.time.get_ticks()  # New timer for random emotions

# Sentiment analysis pipeline
pipe = pipeline("text-classification", model="SamLowe/roberta-base-go_emotions")

def analyze_text_emotions(text):
    results = pipe(text, top_k=None)
    top_result = max(results, key=lambda x: x['score'])
    return top_result['label']

def animate(detected_emotion):
    global emotion

    # Map emotions to visual states
    emotion_map = {
        "joy": "happy",
        "amusement": "happy",
        "approval": "happy",
        "gratitude": "happy",
        "love": "happy",
        "sadness": "sad",
        "grief": "sad",
        "disappointment": "sad",
        "remorse": "sad",
        "neutral": "neutral"
    }

    # Set emotion based on the detected sentiment
    emotion = emotion_map.get(detected_emotion, "neutral")

# def draw_eye(center_x, center_y, emotion, pupil_offset_x=0, pupil_offset_y=0, is_blinking=False):
#     if is_blinking:
#         pygame.draw.line(screen, WHITE, (center_x - eye_radius, center_y), (center_x + eye_radius, center_y), 10)
#     else:
#         if emotion == "happy":
#             pygame.draw.arc(screen, WHITE, (center_x - eye_radius, center_y - (eye_radius // 2), eye_radius * 2, eye_radius), math.radians(40), math.radians(140), 10)
#         elif emotion == "sad":
#             pygame.draw.arc(screen, WHITE, (center_x - eye_radius, center_y - (eye_radius // 2), eye_radius * 2, eye_radius), math.radians(220), math.radians(320), 10)
#         else:
#             pygame.draw.circle(screen, WHITE, (center_x, center_y), eye_radius)
#             pygame.draw.circle(screen, BLUE, (center_x + pupil_offset_x, center_y + pupil_offset_y), pupil_radius)
def draw_eye(center_x, center_y, emotion, is_blinking=False):
    eye_width = eye_radius * 2  # The width of the eye
    eye_height = eye_radius * 1.5  # The height of the eye
    corner_radius = 20  # Radius for rounded corners

    if is_blinking:
        # Draw a horizontal line to represent a closed eye
        pygame.draw.line(screen, WHITE, (center_x - eye_width // 2, center_y),
                         (center_x + eye_width // 2, center_y), 10)
    else:
        if emotion == "happy":
            # Draw a curved lower eyelid for happy (smile shape)
            arc_rect = pygame.Rect(center_x - eye_width // 2, center_y - eye_height // 4, eye_width, eye_height // 2)
            pygame.draw.arc(screen, WHITE, arc_rect, math.radians(30), math.radians(150), 10)

            # Add blush for the left or right eye
            blush_width = 70  # Increased blush size (wider)
            blush_height = 35  # Increased blush size (taller)
            blush_color = (255, 182, 193)  # Light pink color
            blush_offset_x = 60  # Horizontal offset for blush
            blush_offset_y = 60  # Vertical offset for blush (lower on cheek)

            if center_x < SCREEN_WIDTH // 2:  # Left eye
                pygame.draw.ellipse(screen, blush_color,
                                    (center_x - blush_offset_x, center_y + blush_offset_y, blush_width, blush_height))
            elif center_x >= SCREEN_WIDTH // 2:  # Right eye
                pygame.draw.ellipse(screen, blush_color,
                                    (center_x + blush_offset_x - blush_width, center_y + blush_offset_y, blush_width, blush_height))

        elif emotion == "sad":
            # Draw a curved upper eyelid for sad (frown shape)
            arc_rect = pygame.Rect(center_x - eye_width // 2, center_y - eye_height // 2, eye_width, eye_height // 2)
            pygame.draw.arc(screen, WHITE, arc_rect, math.radians(210), math.radians(330), 10)
        else:
            # Neutral emotion: draw the rounded square eye
            rect = pygame.Rect(center_x - eye_width // 2, center_y - eye_height // 2, eye_width, eye_height)
            pygame.draw.rect(screen, WHITE, rect, border_radius=corner_radius)



# def update_display():
#     global blink_timer, is_blinking, random_movement_timer, pupil_offset_x, pupil_offset_y, random_emotion_timer, emotion

#     # Clear screen
#     screen.fill(BLACK)

#     # Eye positions
#     left_eye_center = (SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2)
#     right_eye_center = (2 * SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2)

#     # Handle random pupil movement when the emotion is neutral
#     current_time = pygame.time.get_ticks()
#     if emotion == "neutral" and current_time - random_movement_timer > random.randint(2000, 5000):
#         random_movement_timer = current_time
#         direction = random.choice(["left", "right", "upper_left", "upper_right", "lower_left", "lower_right", "center"])
#         if direction == "left":
#             pupil_offset_x, pupil_offset_y = -30, 0
#         elif direction == "right":
#             pupil_offset_x, pupil_offset_y = 30, 0
#         elif direction == "upper_left":
#             pupil_offset_x, pupil_offset_y = -30, -30
#         elif direction == "upper_right":
#             pupil_offset_x, pupil_offset_y = 30, -30
#         elif direction == "lower_left":
#             pupil_offset_x, pupil_offset_y = -30, 30
#         elif direction == "lower_right":
#             pupil_offset_x, pupil_offset_y = 30, 30
#         else:
#             pupil_offset_x, pupil_offset_y = 0, 0

#     # Handle blinking
#     if not is_blinking and current_time - blink_timer > random.randint(2000, 5000):
#         is_blinking = True
#         blink_timer = current_time

#     if is_blinking and current_time - blink_timer > blink_duration:
#         is_blinking = False
#         blink_timer = current_time

#     # Draw both eyes
#     draw_eye(left_eye_center[0], left_eye_center[1], emotion, pupil_offset_x, pupil_offset_y, is_blinking)
#     draw_eye(right_eye_center[0], right_eye_center[1], emotion, pupil_offset_x, pupil_offset_y, is_blinking)

#     # Update the screen
#     pygame.display.flip()
def update_display():
    global blink_timer, is_blinking, random_movement_timer, random_emotion_timer, emotion

    # Clear screen
    screen.fill(BLACK)

    # Eye positions
    left_eye_center = (SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2)
    right_eye_center = (2 * SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2)

    # Handle blinking
    current_time = pygame.time.get_ticks()
    if not is_blinking and current_time - blink_timer > random.randint(2000, 5000):
        is_blinking = True
        blink_timer = current_time

    if is_blinking and current_time - blink_timer > blink_duration:
        is_blinking = False
        blink_timer = current_time

    # Draw both eyes
    draw_eye(left_eye_center[0], left_eye_center[1], emotion, is_blinking)
    draw_eye(right_eye_center[0], right_eye_center[1], emotion, is_blinking)

    # Update the screen
    pygame.display.flip()

def main():
    global emotion

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:  # Happy
                    emotion = "happy"
                elif event.key == pygame.K_s:  # Sad
                    emotion = "sad"
                elif event.key == pygame.K_n:  # Neutral
                    emotion = "neutral"
                elif event.key == pygame.K_RETURN:
                    # Sample text input
                    text_to_speak = "I am feeling very happy today!"
                    detected_emotion = analyze_text_emotions(text_to_speak)
                    print(f"Text: {text_to_speak} -> Detected Emotion: {detected_emotion}")
                    animate(detected_emotion)

        # Update the display
        update_display()
        clock.tick(60)

if __name__ == "__main__":
    main()
