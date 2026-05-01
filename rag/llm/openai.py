"""
ChatOpenAI

Wrapper for interacting with OpenAI LLM models using a simple
invoke interface. This class abstracts the OpenAI client and provides
a consistent method for sending prompts and receiving responses.

Features:
- Connects to OpenAI via API key authentication
- Supports configurable models
- Provides a simple `invoke(prompt)` method for text generation

Args:
    api_key (str): OpenAI API key for authentication.
    model (str, optional): Model name to use. Defaults to "gpt-4.1-mini".

Example:
    llm = ChatOpenAI(api_key="your_api_key")
    response = llm.invoke("Hello, how are you?")
    print(response)
"""

# Third-party libraries
from openai import OpenAI


class ChatOpenAI:
    def __init__(self, api_key: str = None, model: str = "gpt-4.1-mini"):
        if not api_key:
            raise ValueError("OpenAI API key is required")

        self.model = model
        self.client = OpenAI(api_key=api_key)

    def invoke(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        return response.choices[0].message.content