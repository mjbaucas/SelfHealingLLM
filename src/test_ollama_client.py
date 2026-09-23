from src.ollama_client import OllamaClient

client = OllamaClient()

response = client.generate(
    "Explain what a prompt injection attack is in one sentence."
)

print(response)