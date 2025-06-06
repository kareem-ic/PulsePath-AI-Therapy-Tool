"""
Simple wrapper around Coqui-TTS.
Call speak("Hello") to hear the phrase out loud.
"""

import numpy as np
import sounddevice as sd
from TTS.api import TTS  

_tts = TTS("tts_models/en/jenny/jenny")

def speak(text: str, samplerate: int = 24_000):
    """Synthesize text to speech and play it blocking."""
    if not text.strip():
        return
    wav = _tts.tts(text)
    sd.play(np.asarray(wav), samplerate)
    sd.wait()             