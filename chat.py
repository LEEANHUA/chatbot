from pydub import AudioSegment
from pydub.playback import play

from llm import chatgpt
from tts import voicevox

def audio_play(wav_data):
    with open("audio/tmp.wav", mode='bw') as f:
        f.write(wav_data)
    audio = AudioSegment.from_wav("audio/tmp.wav")
    play(audio)

def chat(valid_stream):
    llm = chatgpt.ChatGPT(valid_stream)
    while True:
        user_utt = input("文章を入力：")
        
        llm_reault = llm.run_completion(user_utt)
        if valid_stream == False:
            assistant_utt = llm_reault.choices[0].message.content
            print(assistant_utt)
            llm.set_assistant_utterance(assistant_utt)
            
            wav_data = voicevox.get_audio_file_from_text(assistant_utt)
            audio_play(wav_data)
        else:
            assistant_utt = ""
            for chunk in llm_reault:
                word = chunk.choices[0].delta.content
                if word == None:
                    break
                assistant_utt += word
                for punctuation in ["。", "！", "？", "、"]:
                    if punctuation in word:
                        print(assistant_utt)
                        wav_data = voicevox.get_audio_file_from_text(assistant_utt)
                        audio_play(wav_data)
                        assistant_utt = ""
            if assistant_utt != "":
                print(assistant_utt)
                wav_data = voicevox.get_audio_file_from_text(assistant_utt)
                audio_play(wav_data)

if __name__ == "__main__":
    valid_stream = True
    chat(valid_stream)