import io
import subprocess
import time
import numpy as np
import requests
import whisper
from bark import generate_audio
import soundfile as sf
from pydub import AudioSegment

from src.service.api.text_api_interface import TextAPIInterface
from src.service.api.voice_api_interface import VoiceAPIInterface
from src.constants import Speaker


class OllamaApi(TextAPIInterface, VoiceAPIInterface):
    @property
    def api_name(self):
        return "Ollama API"

    def __init__(self, text_model="deepseek-r1:7b", api_url="http://localhost:11434/api/chat"):
        self._text_model = text_model
        self._whisper_model = None
        self.api_url = api_url
        self._api_name = "ollama"

    # TextAI interface
    def generate_text_response(self, context: list[object]) -> str:
        response = requests.post(self.api_url,
                                 json={"model": self._text_model,
                                       "messages": context,
                                       "stream": False,
                                       "options": {"compute_mode": "GPU"}
                                       })
        if response.status_code == 200:
            res = response.json()
            print(f"{self.api_name} finished generating text response. Duration: {res.get('total_duration') / 1_000_000_000} seconds")
            return res.get("message").get('content')
        else:
            print(f"Error querying model {self._text_model}: {response.status_code}, {response.text}")
            return ""

    # VoiceAI interface
    def transcribe(self, voice_buffer: io.BytesIO):
        start_time = time.time()
        print(f"{self.api_name} starts transcribing...")
        process = subprocess.run(
            ["ffmpeg", "-i", "pipe:0",  # Read input from memory
                "-ac", "1", "-ar", "16000",  # Convert to mono, 16kHz
                "-f", "wav", "-acodec", "pcm_s16le",  # Standard PCM encoding
                "pipe:1"],
            input=voice_buffer.getvalue(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if process.returncode != 0:
            raise RuntimeError(f"FFmpeg error: {process.stderr.decode()}")
        audio = np.frombuffer(process.stdout, dtype=np.int16).astype(np.float32) / 32768.0
        if self._whisper_model is None:
            self._whisper_model = whisper.load_model("tiny").to("cuda")
        result = self._whisper_model.transcribe(
            audio,
            language="en",  # Set language for better accuracy
            temperature=0,  # Make output deterministic
            word_timestamps=True  # Get word-level timestamps (useful for alignment)
        )
        end_time = time.time()
        duration = round(end_time - start_time, 1)
        print(f"{self.api_name} finished transcribing. Duration: {duration} seconds")
        return result["text"]

    def text2audio(self, text, speaker: Speaker=Speaker.WOMAN) -> io.BytesIO:
        print(f"{self.api_name} text2audio...")
        start_time = time.time()
        audio_array = generate_audio(text, history_prompt=speaker.value, silent=True)

        audio_array = np.clip(audio_array, -1.0, 1.0)  # Prevents clipping
        wav_buffer = io.BytesIO()
        sf.write(wav_buffer, audio_array, 24000, format='WAV')
        wav_buffer.seek(0)
        # Convert WAV to OGG using pydub
        audio_segment = AudioSegment.from_wav(wav_buffer)
        ogg_buffer = io.BytesIO()
        audio_segment.export(ogg_buffer, format='ogg', codec='libopus')
        ogg_buffer.seek(0)

        end_time = time.time()
        duration = round(end_time - start_time, 1)
        print(f"{self.api_name} finished text2audio. Duration: {duration} seconds")
        return ogg_buffer


ollama_api = OllamaApi()