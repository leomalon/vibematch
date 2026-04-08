"""
ChatOllama

Wrapper for interacting with Ollama Cloud LLM models using a simple
invoke interface. This class abstracts the Ollama client and provides
a consistent method for sending prompts and receiving responses.

Features:
- Connects to Ollama Cloud via API key authentication
- Supports configurable models
- Provides a simple `invoke(prompt)` method for text generation

Args:
    api_key (str): Ollama API key for authentication.
    model (str, optional): Model name to use. Defaults to "gpt-oss:120b-cloud".

Example:
    llm = ChatOllama(api_key="your_api_key")
    response = llm.invoke("Hello, how are you?")
    print(response)
"""

#Third-party libraries
from ollama import Client

class ChatOllama:
    def __init__(self, api_key: str = None, model: str = "gpt-oss:120b-cloud"):
        self.api_key = api_key
        self.model = model

        if not self.api_key:
            raise ValueError("Ollama API key is required")

        self.client = Client(
            host="https://ollama.com",
            headers={
                "Authorization": f"Bearer {self.api_key}"
            }
        )

    def invoke(self, prompt: str) -> str:
        messages = [
            {"role": "user", "content": prompt}
        ]

        response = self.client.chat(
            model=self.model,
            messages=messages
        )

        return response.message.content