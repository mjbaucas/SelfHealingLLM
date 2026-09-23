import requests

class OllamaClient:
    def __init__(
        self,
        model: str = "qwen3:4b",
        base_url: str = "http://localhost:11434",
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
    
    def generate(
        self, 
        prompt: str, 
        system_prompt: str | None = None,
    ) -> str:

        request_data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        if system_prompt:
            request_data["system"] = system_prompt

        response = requests.post(
            f"{self.base_url}/api/generate",
            json=request_data,
            timeout=300,
        )
        response.raise_for_status()
        return response.json()["response"]
