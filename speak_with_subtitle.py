from gtts import gTTS
import pygame
import os
import time

# Function to speak text in English, Hindi, or Punjabi
def speak_text(text, lang='en'):
    tts = gTTS(text=text, lang=lang)
    tts.save("temp_audio.mp3")
    pygame.mixer.init()
    pygame.mixer.music.load("temp_audio.mp3")
    pygame.mixer.music.play()
    # Wait for the audio to finish playing
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    pygame.mixer.music.stop()  # Stop the music playback
    pygame.mixer.quit()  # Quit the mixer to release the file
    os.remove("temp_audio.mp3")  # Now it's safe to delete the file

# Function to display subtitle with moving color
def display_subtitle(screen, text, font, color, bg_color):
    screen.fill(bg_color)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    x = 0
    while x < screen.get_width():
        screen.fill(bg_color)
        screen.blit(text_surface, (x, screen.get_height() // 2 - text_rect.height // 2))
        pygame.display.flip()
        x += 2  # Adjust speed of movement
        time.sleep(0.01)

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 200))
    pygame.display.set_caption("Subtitle with Moving Color")
    font = pygame.font.Font(None, 74)
    color = (255, 0, 0)  # Red color
    bg_color = (0, 0, 0)  # Black background

    # Text in English, Hindi, and Punjabi
    text_en = "Hello, how are you?"
    text_hi = "नमस्ते, आप कैसे हैं?"
    text_pa = "ਹੈਲੋ ਤੁਸੀ ਕਿਵੇਂ ਹੋ?"

    # Speak and display subtitles
    speak_text(text_en, 'en')
    display_subtitle(screen, text_en, font, color, bg_color)

    speak_text(text_hi, 'hi')
    display_subtitle(screen, text_hi, font, color, bg_color)

    speak_text(text_pa, 'pa')
    display_subtitle(screen, text_pa, font, color, bg_color)

    pygame.quit()

if __name__ == "__main__":
    main()
    