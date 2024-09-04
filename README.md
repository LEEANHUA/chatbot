# 概要
マイク入力をWhisper APIを用いて文字起こしし、
それをOpenAI APIに投げて返答をVOICEVOXを用いて音声合成することで、
ChatGPTとの音声対話システムを構築します。

# 環境設定
OpenAIのAPIキーを環境変数に設定してください。
```
export OPENAI_API_KEY=...
```
必要なパッケージをインストールしてください。
```
pip install -r requirements.txt
```
その後[公式ホームページ](https://voicevox.hiroshiba.jp/)よりVOICEVOXをインストールしてください。

# chat.py
遅いモデルです。StreamをオンにすることでChatGPTの応答を逐次的に表示することができます。
```
python chat.py
```

# chat_threading.py
Streamをオンにして逐次的に出力されるChatGPTの応答を受け取った後、マルチスレッドで音声合成を行うことで高速化したモデルです。
```
python chat_threading.py
```