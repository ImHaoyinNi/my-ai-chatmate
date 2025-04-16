import re

import aioboto3
import asyncio
import io
import sounddevice as sd
import soundfile as sf
from src.service.api.interface.tts_api_interface import TTSAPIInterface
from src.utils.config import config
from src.utils.utils import english_or_chinese


class AwsApi(TTSAPIInterface):
    @property
    def api_name(self):
        return "AWS API"

    def __init__(self, access_key: str, secret_access_key: str, region: str = "us-east-1"):
        self._access_key = access_key
        self._secret_access_key = secret_access_key
        self._region = region
        self._session = aioboto3.Session(
            aws_access_key_id=self._access_key,
            aws_secret_access_key=self._secret_access_key,
            region_name=self._region
        )
        self._polly = None

    async def _get_polly(self):
        if self._polly is None:
            self._polly = await self._session.client('polly').__aenter__()
        return self._polly

    async def text_to_speech(self, text: str, voice_id: str) -> io.BytesIO:
        text = self.remove_emojis(text)
        lang_code = english_or_chinese(text)
        voice_id = "Ruth" if lang_code == "en" else "Zhiyu"

        polly = await self._get_polly()
        res = await polly.synthesize_speech(
            Text=text,
            OutputFormat="ogg_vorbis",
            VoiceId=voice_id,
            Engine="neural"
        )

        if "AudioStream" not in res:
            return io.BytesIO()
        audio_data = await res["AudioStream"].read()
        if config.env == "production":
            return io.BytesIO(audio_data)

        process = await asyncio.create_subprocess_exec(
            "ffmpeg",
            "-i", "pipe:0",
            "-c:a", "libopus",
            "-b:a", "32k",
            "-f", "ogg",
            "pipe:1",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL
        )
        stdout, _ = await process.communicate(input=audio_data)
        return io.BytesIO(stdout)

    def remove_emojis(self, text: str) -> str:
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F700-\U0001F77F"  # alchemical symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess Symbols
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\U00002702-\U000027B0"  # Dingbats
            "\U000024C2-\U0001F251" 
            "]+", flags=re.UNICODE)

        return emoji_pattern.sub(r'', text)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._polly:
            await self._polly.__aexit__(exc_type, exc_val, exc_tb)

aws_api_async = AwsApi(config.aws_access_key_id, config.aws_secret_access_key)

async def main():
    res = await aws_api_async.text_to_speech("Hello World! I love Python!", "")
    data, samplerate = sf.read(res)
    sd.play(data, samplerate)
    sd.wait()

if __name__ == '__main__':
    asyncio.run(main())