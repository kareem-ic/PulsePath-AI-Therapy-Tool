import queue, threading, numpy as np, sounddevice as sd, whisper

_MODEL = whisper.load_model("large-v3-turbo")   # loads once per process


class ASR:
    """Stream microphone → text chunks via Whisper."""
    def __init__(self, samplerate: int = 16_000):
        self.samplerate = samplerate
        self._audio_q = queue.Queue()
        self._buf = b""

    def _audio_cb(self, indata, frames, *_):
        self._audio_q.put(bytes(indata))

    def start_stream(self, on_text):
        """Call on_text(str) every ~3 s of speech."""
        sd.RawInputStream(
            samplerate=self.samplerate,
            channels=1,
            dtype="int16",
            callback=self._audio_cb,
        ).__enter__()
        threading.Thread(target=self._worker, args=(on_text,), daemon=True).start()

    def _worker(self, on_text):
        while True:
            self._buf += self._audio_q.get()
            if len(self._buf) >= self.samplerate * 3 * 2:  # 3 s * 2 bytes
                pcm = (np.frombuffer(self._buf, np.int16)
                         .astype(np.float32) / 32768)
                txt = _MODEL.transcribe(pcm, fp16=False)["text"].strip()
                if txt:
                    on_text(txt)
                self._buf = b""
