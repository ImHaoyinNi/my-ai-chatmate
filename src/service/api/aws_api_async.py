import aioboto3
import asyncio
import io
import sounddevice as sd
import soundfile as sf
from src.service.api.interface.async_interface.tts_api_interface_async import TTSAPIInterfaceAsync
from src.utils.config import config
from src.utils.utils import english_or_chinese


class AwsApiAsync(TTSAPIInterfaceAsync):
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

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._polly:
            await self._polly.__aexit__(exc_type, exc_val, exc_tb)

aws_api_async = AwsApiAsync(config.aws_access_key_id, config.aws_secret_access_key)

async def main():
    res = await aws_api_async.text_to_speech("Hello World! I love Python!", "")
    data, samplerate = sf.read(res)
    sd.play(data, samplerate)
    sd.wait()

if __name__ == '__main__':
    asyncio.run(main())