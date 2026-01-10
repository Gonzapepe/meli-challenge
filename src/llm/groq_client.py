from groq import Groq
from src.config import config


_client = None


def get_groq_client() -> Groq:
    """Get or create Groq client instance."""
    global _client
    
    if _client is None:
        config.validate()
        _client = Groq(api_key=config.GROQ_API_KEY)
    
    return _client


def generate_completion(
    prompt: str,
    system_prompt: str = "You are a helpful assistant.",
    temperature: float = None,
    max_tokens: int = None,
    model: str = None
) -> str:
    """
    Generate a completion using Groq.
    
    Args:
        prompt: User prompt
        system_prompt: System instructions
        temperature: Override default temperature
        max_tokens: Override default max tokens
        model: Override default model
        
    Returns:
        Generated text response
    """
    client = get_groq_client()
    
    response = client.chat.completions.create(
        model=model or config.LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature if temperature is not None else config.LLM_TEMPERATURE,
        max_tokens=max_tokens or config.LLM_MAX_TOKENS
    )
    
    return response.choices[0].message.content


def generate_json_completion(
    prompt: str,
    system_prompt: str = "You are a helpful assistant. Always respond with valid JSON only, no markdown or extra text.",
    temperature: float = 0.1
) -> str:
    """
    Generate a JSON completion using Groq.
    
    Args:
        prompt: User prompt expecting JSON response
        system_prompt: System instructions
        temperature: Generation temperature
        
    Returns:
        JSON string response
    """
    client = get_groq_client()
    
    response = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=config.LLM_MAX_TOKENS,
        response_format={"type": "json_object"}
    )
    
    content = response.choices[0].message.content
    
    if content is None or content.strip() == "":
        return '{"error": "empty_response"}'
    
    return content
