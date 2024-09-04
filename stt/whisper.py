from io import BytesIO

from openai import OpenAI
import speech_recognition as sr

color_dic = {"black":"\033[30m", "red":"\033[31m", "green":"\033[32m", "yellow":"\033[33m", "blue":"\033[34m", "end":"\033[0m"}

class WhisperAPI:
    def __init__(self) -> None:
        self.client = OpenAI()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone(sample_rate=16000)
        
    def get_audio_from_mic(self) -> sr.AudioData:
        with self.microphone as source:
            print(color_dic["green"] + "音声入力受付中..." + color_dic["end"])
            audio = self.recognizer.listen(source)
            print(color_dic["green"] + "音声を取得しました" + color_dic["end"])
            return audio
        
    def voice_to_text(self) -> str:
        audio = self.get_audio_from_mic()
        audio_data = BytesIO(audio.get_wav_data())
        audio_data.name = "from_mic.wav"
        transcription = self.client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_data,
            response_format="text"
        )
        return transcription