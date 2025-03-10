import io
import subprocess
import boto3

from src.service.api.interface.sync.tts_api_interface import TTSAPIInterface
from src.utils.config import config
from src.utils.utils import english_or_chinese


class AwsApi(TTSAPIInterface):
    @property
    def api_name(self):
        return "AWS API"

    def __init__(self, access_key: str, secret_access_key: str, region: str="us-east-1"):
        self._access_key = access_key
        self._secret_access_key = secret_access_key
        self._region = region
        self._session = boto3.Session(
            aws_access_key_id=self._access_key,
            aws_secret_access_key=self._secret_access_key,
            region_name=self._region
        )
        self.polly = self._session.client('polly')

    def text_to_speech(self, text: str, voice_id: str) -> io.BytesIO:
        lang_code = english_or_chinese(text)
        voice_id = "Ruth" if lang_code == "en" else "Zhiyu"
        res = self.polly.synthesize_speech(
            Text=text,
            OutputFormat="ogg_vorbis",
            VoiceId=voice_id,
            Engine="neural"
        )
        if "AudioStream" in res:
            return io.BytesIO(res["AudioStream"].read())
        else:
            return io.BytesIO()


aws_api = AwsApi(config.aws_access_key_id, config.aws_secret_access_key)

if __name__ == "__main__":
    text = """okay SO yesterday I totally blanked on my BFF's coffee order?? "
            "😳 Like we've been to Starbucks 100x but my brain just noped out. "
            "You ever have those moments where you forget basic human things lol?"""
    aws_api.text_to_speech(text, "Ruth")

