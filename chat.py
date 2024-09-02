from pydub import AudioSegment
from pydub.playback import play

from llm import chatgpt
from tts import voicevox

def audio_play(wav_data):
    with open("audio/tmp.wav", mode='bw') as f:
        f.write(wav_data)
    audio = AudioSegment.from_wav("audio/tmp.wav")
    play(audio)

if __name__ == "__main__":
    valid_stream = False
    llm = chatgpt.ChatGPT(valid_stream)
    while True:
        user_q = input("文章を入力：")
        
        llm_reault = llm.run_completion(user_q)
        assistant_response = llm_reault.choices[0].message.content
        llm.set_assistant_utterance(assistant_response)
        
        wav_data = voicevox.get_audio_file_from_text(assistant_response)
        audio_play(wav_data)
        
        print(assistant_response)