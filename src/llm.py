"""Pluggable LLM backend: free local (Ollama) or OpenAI."""
from src.config import config


def generate(prompt: str) -> str:
    if config.llm_backend == "openai":
        return _generate_openai(prompt)
    return _generate_ollama(prompt)


def _generate_ollama(prompt: str) -> str:
    import ollama
    resp = ollama.chat(
        model=config.ollama_model,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp["message"]["content"]


def _generate_openai(prompt: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=config.openai_api_key)
    resp = client.chat.completions.create(
        model=config.openai_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )
    return resp.choices[0].message.content
