import os
from mistralai import Mistral
from dotenv import load_dotenv

from prompt_templates import FAST_PROMPT, STANDARD_PROMPT, DEEP_PROMPT
from network import measure_latency, get_network_mode
from tools import TOOLS

load_dotenv()

class AdaptiveAgent:
    def __init__(self):
        self.api_key = os.getenv("MISTRAL_API_KEY")
        self.client = Mistral(api_key=self.api_key) if self.api_key else None
        
    def call_llm(self, prompt, stream=False):
        if not self.client:
            return "Error: Mistral API Key not set."
        
        if stream:
            stream_response = self.client.chat.stream(
                model="mistral-tiny",
                messages=[{"role": "user", "content": prompt}],
            )
            for chunk in stream_response:
                if chunk.data.choices[0].delta.content:
                    yield chunk.data.choices[0].delta.content
        else:
            response = self.client.chat.complete(
                model="mistral-tiny",
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content

    def run(self, question, context=None, stream=False):
        # 1. Sense Network
        latency = measure_latency()
        mode = get_network_mode(latency)
        
        print(f"Network Latency: {latency:.1f}ms -> Mode: {mode}")
        
        # 2. Select Strategy
        # Note: Deep Mode returns a full string because of internal logic, 
        # but we can simulate streaming or just return it.
        # Fast & Standard can stream directly.
        
        if mode == "FAST":
            response = self._fast_mode(question, context, stream)
            return response, mode, latency
        elif mode == "STANDARD":
            response = self._standard_mode(question, stream)
            return response, mode, latency
        else:
            # Deep mode is complex, for MVP let's just stream the final prompt
            response = self._deep_mode(question, stream)
            return response, mode, latency

    def _fast_mode(self, question, context, stream=False):
        prompt = FAST_PROMPT.format(question=question, context=context or "None")
        return self.call_llm(prompt, stream)

    def _standard_mode(self, question, stream=False):
        tool_names = ", ".join(TOOLS.keys())
        prompt = STANDARD_PROMPT.format(question=question, tools=tool_names)
        return self.call_llm(prompt, stream)

    def _deep_mode(self, question, stream=False):
        tool_names = ", ".join(TOOLS.keys())
        prompt = DEEP_PROMPT.format(question=question, tools=tool_names)
        return self.call_llm(prompt, stream)


agent = AdaptiveAgent()
