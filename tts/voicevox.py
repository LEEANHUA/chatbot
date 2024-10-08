import requests
import json
import time

def get_audio_query(text, speaker = 14):
    query_payload = {"text": text, "speaker": speaker}
    while True:
        try:
            url = "http://localhost:50021/audio_query"
            # timeout = (connect timeout, read timeout)
            r = requests.post(url, params=query_payload, timeout=(10.0, 300.0))
            if r.status_code == 200:
                return r.json()
                
        except requests.exceptions.ConnectionError:
            print('fail connect...', url)
            time.sleep(1)

def run_synthesis(query_data, speaker = 14):
    # 音声のピッチを調整
    query_data['pitchScale'] = 0.02
    
    synth_payload = {"speaker": speaker}
    while True:
        try:
            url = "http://localhost:50021/synthesis"
            r = requests.post(url, params=synth_payload, data=json.dumps(query_data), timeout=(10.0, 300.0))
            if r.status_code == 200:
                return r.content
        except requests.exceptions.ConnectionError:
            print('fail connect...', url)
            time.sleep(1)

def get_audio_file_from_text(text):
    query_data = get_audio_query(text)
    return run_synthesis(query_data)