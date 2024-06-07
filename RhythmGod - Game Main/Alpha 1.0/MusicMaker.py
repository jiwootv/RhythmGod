from pydub import AudioSegment
from pydub.generators import Sine, Square
import simpleaudio as sa

# Define parameters for the sound
duration = 100  # milliseconds
volume = -3  # dB

# Generate a high frequency square wave tone for a sharp 'click' sound
click_sound = Square(1000).to_audio_segment(duration=duration).apply_gain(volume)

# Add a short fade-out to make it more pleasant
click_sound = click_sound.fade_out(50)

# Export sound to a wav file
click_sound.export("click_effect.wav", format="wav")

# Play the sound
wave_obj = sa.WaveObject.from_wave_file("click_effect.wav")
play_obj = wave_obj.play()

# Wait for playback to finish before exiting
play_obj.wait_done()
