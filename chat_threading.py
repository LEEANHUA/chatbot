import time
import threading
from queue import Queue
from pydub import AudioSegment
from pydub.playback import play

from llm import chatgpt
from tts import voicevox

color_dic = {"black":"\033[30m", "red":"\033[31m", "green":"\033[32m", "yellow":"\033[33m", "blue":"\033[34m", "end":"\033[0m"}

def audio_play(wav_data):
    with open("audio/tmp.wav", mode='bw') as f:
        f.write(wav_data)
    audio = AudioSegment.from_wav("audio/tmp.wav")
    play(audio)

def tts_worker(tts_queue, play_start_time, play_end_time):
    while True:
        assistant_utt = tts_queue.get()
        if assistant_utt == None:
            tts_queue.task_done()
            break
        wav_data = voicevox.get_audio_file_from_text(assistant_utt)
        
        # 最初の音声再生までの時間を記録
        if play_start_time[0] is None:
            play_start_time[0] = time.time()
        
        audio_play(wav_data)
        
        # 最後の音声再生が終了した時刻を記録
        play_end_time[0] = time.time()
        
        tts_queue.task_done()

def chat(valid_stream):
    llm = chatgpt.ChatGPT(valid_stream)
    tts_queue = Queue()
    
    # タイマー用変数（リストを使用して変更可能にする）
    play_start_time = [None]
    play_end_time = [None]
    
    # TTSを処理するスレッドを作成
    tts_thread = threading.Thread(target=tts_worker, args=(tts_queue, play_start_time, play_end_time))
    tts_thread.start()
    
    while True:
        user_utt = input(color_dic["green"] + "文章を入力：" + color_dic["end"])
        if user_utt.lower() == "q":
            break
        start_time = time.time()
        
        llm_reault = llm.run_completion(user_utt)
        if valid_stream == False:
            assistant_utt = llm_reault.choices[0].message.content
            print(assistant_utt)
            llm.set_assistant_utterance(assistant_utt)
            
            tts_queue.put(assistant_utt)
        else:
            tmp_utt = ""
            for chunk in llm_reault:
                word = chunk.choices[0].delta.content
                if word == None:
                    break
                tmp_utt += word
                for punctuation in ["。", "！", "？", "、"]:
                    if punctuation in word:
                        print(tmp_utt)
                        llm.append_assistant_utterance(tmp_utt)
                        tts_queue.put(tmp_utt)
                        tmp_utt = ""
            if tmp_utt != "":
                print(tmp_utt)
                llm.append_assistant_utterance(tmp_utt)
                tts_queue.put(tmp_utt)
        
        tts_queue.join()    # TTSの処理が終了するまで待機
        
        # 時間の計測結果を表示
        if play_start_time[0] is not None:
            print(color_dic["yellow"] + f"入力から音声が流れるまで: {play_start_time[0] - start_time:.2f}秒" + color_dic["end"])
        if play_end_time[0] is not None:
            print(color_dic["yellow"] + f"入力から音声終了まで: {play_end_time[0] - start_time:.2f}秒" + color_dic["end"])
            
    tts_queue.put(None) # tts_workerを終了させるためにNoneを送る
    tts_thread.join()   # スレッドが終了するまで待機

if __name__ == "__main__":
    valid_stream = True
    chat(valid_stream)