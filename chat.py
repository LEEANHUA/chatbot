import time
from pydub import AudioSegment
from pydub.playback import play

from stt import whisper
from llm import chatgpt
from tts import voicevox

color_dic = {"black":"\033[30m", "red":"\033[31m", "green":"\033[32m", "yellow":"\033[33m", "blue":"\033[34m", "end":"\033[0m"}

def audio_play(wav_data):
    with open("audio/tmp.wav", mode='bw') as f:
        f.write(wav_data)
    audio = AudioSegment.from_wav("audio/tmp.wav")
    play(audio)

def chat(valid_stream, valid_voice_input):
    stt = whisper.WhisperAPI()
    llm = chatgpt.ChatGPT(valid_stream)
    while True:
        if valid_voice_input:
            user_utt = stt.voice_to_text()
            print(color_dic["green"] + "あなた: " + color_dic["end"] + user_utt)
        else:
            user_utt = input(color_dic["green"] + "文章を入力：" + color_dic["end"])
            if user_utt.lower() == "q":
                break
        start_time = time.time()
        
        llm_reault = llm.run_completion(user_utt)
        if valid_stream == False:
            assistant_utt = llm_reault.choices[0].message.content
            print(assistant_utt)
            llm.set_assistant_utterance(assistant_utt)
            
            wav_data = voicevox.get_audio_file_from_text(assistant_utt)
            
            # 時間計測
            play_start_time = time.time()
            print(color_dic["yellow"] + f"入力から音声が流れるまで: {play_start_time - start_time:.2f}秒" + color_dic["end"])
            
            audio_play(wav_data)
            play_end_time = time.time()
            print(color_dic["yellow"] + f"再生開始から終了まで: {play_end_time - play_start_time:.2f}秒" + color_dic["end"])
        else:
            tmp_utt = ""
            first_tts = True   # 時間計測用の変数
            for chunk in llm_reault:
                word = chunk.choices[0].delta.content
                if word == None:
                    break
                tmp_utt += word
                for punctuation in ["。", "！", "？", "、"]:
                    if punctuation in word:
                        print(tmp_utt)
                        llm.append_assistant_utterance(tmp_utt)
                        wav_data = voicevox.get_audio_file_from_text(tmp_utt)
                        # 最初のTTSなら入力からかかった時間を計測
                        if first_tts:
                            play_start_time = time.time()
                            first_tts = False
                        audio_play(wav_data)
                        tmp_utt = ""
            if tmp_utt != "":
                print(tmp_utt)
                llm.append_assistant_utterance(tmp_utt)
                wav_data = voicevox.get_audio_file_from_text(tmp_utt)
                if first_tts:
                    play_start_time = time.time()
                    first_tts = False
                audio_play(wav_data)
            # 時間の計測結果を表示
            print(color_dic["yellow"] + f"入力から音声が流れるまで: {play_start_time - start_time:.2f}秒" + color_dic["end"])
            play_end_time = time.time()
            print(color_dic["yellow"] + f"再生開始から終了まで: {play_end_time - play_start_time:.2f}秒" + color_dic["end"])

if __name__ == "__main__":
    valid_stream = False
    valid_voice_input = True
    chat(valid_stream, valid_voice_input)