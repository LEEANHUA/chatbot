import time
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
        start_time = time.time()
        
        llm_reault = llm.run_completion(user_utt)
        if valid_stream == False:
            assistant_utt = llm_reault.choices[0].message.content
            print(assistant_utt)
            llm.set_assistant_utterance(assistant_utt)
            
            wav_data = voicevox.get_audio_file_from_text(assistant_utt)
            
            # 時間計測
            tts_end_time = time.time()
            print(f"入力から音声が流れるまで: {tts_end_time - start_time:.2f}秒")
            
            audio_play(wav_data)
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
                            tts_end_time = time.time()
                            first_tts = False
                        audio_play(wav_data)
                        tmp_utt = ""
            if tmp_utt != "":
                print(tmp_utt)
                llm.append_assistant_utterance(tmp_utt)
                wav_data = voicevox.get_audio_file_from_text(tmp_utt)
                if first_tts:
                    tts_end_time = time.time()
                    first_tts = False
                audio_play(wav_data)
            print(f"入力から音声が流れるまで: {tts_end_time - start_time:.2f}秒")

if __name__ == "__main__":
    valid_stream = True
    chat(valid_stream)