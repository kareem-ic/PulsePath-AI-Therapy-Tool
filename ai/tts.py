import pyttsx3
import io
import wave
import struct

def synthesize(text: str) -> bytes:
    # Initialize the TTS engine
    engine = pyttsx3.init()
    
    # Set properties (optional)
    engine.setProperty('rate', 150)    # Speed of speech
    engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
    
    # Get available voices and set a female voice if available
    voices = engine.getProperty('voices')
    for voice in voices:
        if 'female' in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
    
    # Create a temporary file to store the audio
    temp_file = "temp_audio.wav"
    engine.save_to_file(text, temp_file)
    engine.runAndWait()
    
    # Read the generated WAV file
    with open(temp_file, 'rb') as f:
        audio_data = f.read()
    
    # Clean up the temporary file
    import os
    os.remove(temp_file)
    
    return audio_data
