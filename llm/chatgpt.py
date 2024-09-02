from openai import OpenAI
from .constants import Constants

class ChatGPT:
    def __init__(self, valid_stream) -> None:
        self.client = OpenAI(api_key=Constants.OPENAI_API_KEY)
        self.dialogue_history = []
        self.valid_stream = valid_stream
        
    def run_completion(self, user_utterance) -> str:
        self.dialogue_history.append({"role": "user", "content": user_utterance})
        completion = self.client.chat.completions.create(
            model="gpt-4o",
            messages=self.dialogue_history,
            stream=self.valid_stream
        )
        return completion
    
    def set_assistant_utterance(self, assistant_uttrance) -> None:
        self.dialogue_history.append({"role": "assistant", "content": assistant_uttrance})
    
    def append_assistant_utterance(self, word) -> None:
        if self.dialogue_history[-1]["role"] == "user":
            self.dialogue_history.append({"role": "assistant", "content": word})
        else:
            self.dialogue_history[-1]["content"] += word
        
    # 対話履歴チェック用
    def get_dialogue_history(self) -> list:
        return self.dialogue_history