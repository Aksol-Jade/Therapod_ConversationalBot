import pygame
import numpy as np
import torch
import speech_recognition as sr
from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2FeatureExtractor
import torch.nn.functional as F
from transformers import pipeline

# Initialize pygame
pygame.init()

# Screen dimensions for the touch input window
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Touch to Speak")
font = pygame.font.Font(None, 36)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def detect_voice_emotions(emotion_model, emotion_processor, emotion_labels, audio_data, sample_rate=16000):
    inputs = emotion_processor(audio_data, sampling_rate=sample_rate, return_tensors="pt")
    with torch.no_grad():
        emotion_logits = emotion_model(inputs.input_values).logits
    probs = F.softmax(emotion_logits, dim=-1)
    top_probs, top_indices = torch.topk(probs, 3)
    return [(emotion_labels[i], top_probs[0][idx].item()) for idx, i in enumerate(top_indices[0])]

async def analyze_text_emotions(text):
    pipe = pipeline("text-classification", model="SamLowe/roberta-base-go_emotions")
    results = pipe(text, top_k=None)
    top_3_results = sorted(results, key=lambda x: x['score'], reverse=True)[:3]
    return [(res['label'], res['score']) for res in top_3_results]

async def listen_for_commands():
    emotion_model = Wav2Vec2ForSequenceClassification.from_pretrained("superb/wav2vec2-large-superb-er")
    emotion_processor = Wav2Vec2FeatureExtractor.from_pretrained("superb/wav2vec2-large-superb-er")
    emotion_labels = ["neutral", "happy", "angry", "sad", "fear", "surprise", "disgust"]

    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Adjusting for ambient noise... Please wait.")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Touch the screen to speak.")
        
        final_output = None
        while final_output is None:
            screen.fill(BLACK)
            text_surface = font.render("Touch the screen to speak.", True, WHITE)
            screen.blit(text_surface, (SCREEN_WIDTH // 2 - text_surface.get_width() // 2, SCREEN_HEIGHT // 2))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None, None
                elif event.type == pygame.MOUSEBUTTONDOWN:  # Detect touch or mouse click
                    print("Listening for command...")
                    try:
                        audio = recognizer.listen(source)
                        command_text = recognizer.recognize_google(audio)
                        command_string = str(command_text)
                        
                        # Convert audio to float for voice emotion detection
                        raw_audio_data = audio.get_raw_data()
                        audio_data_np = np.frombuffer(raw_audio_data, np.int16).astype(np.float32) / 32768.0
                        voice_emotions = detect_voice_emotions(emotion_model, emotion_processor, emotion_labels, audio_data_np)
                        voice_emotion_output = ", ".join([f"{label} ({prob:.2f})" for label, prob in voice_emotions])
                        
                        # Analyze text-based emotions
                        text_emotions = await analyze_text_emotions(command_text)
                        text_emotion_output = ", ".join([f"{label} ({score:.2f})" for label, score in text_emotions])

                        # Final formatted output
                        final_output = (
                            f"{command_text}. "
                            f"The person's speech patterns seem to indicate {voice_emotion_output}, "
                            f"and the sentiment behind the person's text is {text_emotion_output}."
                        )
                        
                        print("Final Output:")
                        print(final_output)
                        return final_output, command_string
                    
                    except sr.UnknownValueError:
                        print("Could not understand audio.")
                    except sr.RequestError as e:
                        print(f"Speech Recognition error; {e}")
                    except Exception as e:
                        print(f"An error occurred: {e}")
