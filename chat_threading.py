import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
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

def tts_and_save(text, index, result_queue):
    wav_data = voicevox.get_audio_file_from_text(text)
    print(color_dic["blue"] + f"TTS完了: {text}" + color_dic["end"])
    result_queue.put((index, wav_data))

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
        
        result_queue = Queue()
        # Executorオブジェクトを作成
        with ThreadPoolExecutor() as executor:
            futures = []
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
                        # Executorオブジェクトにタスクをsubmitする
                        # submitした瞬間にスレッドが生成され、非同期で実行が開始される
                        future = executor.submit(tts_and_save, tmp_utt, len(futures), result_queue)
                        futures.append(future)
                        tmp_utt = ""
            if tmp_utt != "":
                print(tmp_utt)
                llm.append_assistant_utterance(tmp_utt)
                future = executor.submit(tts_and_save, tmp_utt, len(futures), result_queue)
                futures.append(future)
            
            # 音声合成が完了したものから再生する
            # ただし、順番通りに再生するため、indexを使って順番を制御する
            def play_audio():
                count = 0
                while True:
                    index, wav_data = result_queue.get()
                    if index == count:
                        if index == 0:
                            play_start_time = time.time()
                            print(color_dic["yellow"] + f"入力から音声が流れるまで: {play_start_time - start_time:.2f}秒" + color_dic["end"])
                        audio_play(wav_data)
                        count += 1
                    else:
                        result_queue.put((index, wav_data))
                    if result_queue.empty():
                        play_end_time = time.time()
                        print(color_dic["yellow"] + f"再生開始から終了まで: {play_end_time - play_start_time:.2f}秒" + color_dic["end"])
                        break

            play_thread = executor.submit(play_audio)
            for future in as_completed(futures):
                future.result()  # TTSの各スレッドが完了するまで待機
            play_thread.result()  # 再生スレッドが完了するまで待機

if __name__ == "__main__":
    valid_stream = True
    valid_voice_input = True
    chat(valid_stream, valid_voice_input)