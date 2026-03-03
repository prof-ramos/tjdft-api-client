"""
Token counting utilities for TJDFT API Client.

Uses tiktoken for accurate token counting with OpenAI models.
"""

import tiktoken
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass


@dataclass
class TokenCount:
    """Token count result."""
    text: str
    tokens: int
    chars: int
    chars_per_token: float
    model: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tokens": self.tokens,
            "chars": self.chars,
            "chars_per_token": round(self.chars_per_token, 2),
            "model": self.model
        }


class TokenCounter:
    """
    Count tokens for OpenAI models using tiktoken.
    
    Supports:
    - cl100k_base (GPT-4, GPT-4-turbo, GPT-4o, GPT-4o-mini)
    - p50k_base (GPT-3, text-davinci)
    - r50k_base (older models)
    
    Example:
        >>> counter = TokenCounter()
        >>> count = counter.count("Olá, mundo!")
        >>> print(f"Tokens: {count.tokens}")
    """
    
    # Model to encoding mapping
    MODEL_ENCODINGS = {
        # GPT-4 family
        "gpt-4o": "cl100k_base",
        "gpt-4o-mini": "cl100k_base",
        "gpt-4-turbo": "cl100k_base",
        "gpt-4-turbo-preview": "cl100k_base",
        "gpt-4": "cl100k_base",
        "gpt-4-32k": "cl100k_base",
        
        # GPT-3.5 family
        "gpt-3.5-turbo": "cl100k_base",
        "gpt-3.5-turbo-16k": "cl100k_base",
        
        # Older models
        "text-davinci-003": "p50k_base",
        "text-davinci-002": "p50k_base",
        "davinci": "r50k_base",
    }
    
    def __init__(self, model: str = "gpt-4o-mini"):
        """
        Initialize token counter.
        
        Args:
            model: OpenAI model name (default: gpt-4o-mini)
        """
        self.model = model
        self.encoding_name = self.MODEL_ENCODINGS.get(model, "cl100k_base")
        self._encoding = None
    
    @property
    def encoding(self):
        """Lazy load encoding."""
        if self._encoding is None:
            self._encoding = tiktoken.get_encoding(self.encoding_name)
        return self._encoding
    
    def count(self, text: str) -> TokenCount:
        """
        Count tokens in text.
        
        Args:
            text: Text to count
            
        Returns:
            TokenCount with details
        """
        if not text:
            return TokenCount(
                text="",
                tokens=0,
                chars=0,
                chars_per_token=0.0,
                model=self.model
            )
        
        tokens = len(self.encoding.encode(text))
        chars = len(text)
        
        return TokenCount(
            text=text[:100] + "..." if len(text) > 100 else text,
            tokens=tokens,
            chars=chars,
            chars_per_token=chars / tokens if tokens > 0 else 0,
            model=self.model
        )
    
    def count_batch(self, texts: List[str]) -> List[TokenCount]:
        """
        Count tokens in multiple texts.
        
        Args:
            texts: List of texts
            
        Returns:
            List of TokenCount
        """
        return [self.count(text) for text in texts]
    
    def count_jurisprudencia(self, resultado: Dict[str, Any]) -> Dict[str, TokenCount]:
        """
        Count tokens in a jurisprudencia result.
        
        Args:
            resultado: Result dict from API
            
        Returns:
            Dict with token counts for each field
        """
        counts = {}
        
        for field in ["ementa", "inteiro_teor", "processo", "orgao_julgador"]:
            value = resultado.get(field, resultado.get(field.replace("_", ""), ""))
            if value:
                counts[field] = self.count(value)
        
        return counts
    
    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int = 0,
        model: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Estimate API cost in USD.
        
        Prices as of 2024:
        - gpt-4o-mini: $0.15/1M input, $0.60/1M output
        - gpt-4o: $2.50/1M input, $10.00/1M output
        - gpt-4-turbo: $10.00/1M input, $30.00/1M output
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Model name (uses self.model if not specified)
            
        Returns:
            Dict with cost breakdown
        """
        model = model or self.model
        
        # Prices per 1M tokens (USD)
        prices = {
            "gpt-4o-mini": {"input": 0.15, "output": 0.60},
            "gpt-4o": {"input": 2.50, "output": 10.00},
            "gpt-4-turbo": {"input": 10.00, "output": 30.00},
            "gpt-4": {"input": 30.00, "output": 60.00},
            "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
        }
        
        model_prices = prices.get(model, prices["gpt-4o-mini"])
        
        input_cost = (input_tokens / 1_000_000) * model_prices["input"]
        output_cost = (output_tokens / 1_000_000) * model_prices["output"]
        
        return {
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost_usd": round(input_cost, 6),
            "output_cost_usd": round(output_cost, 6),
            "total_cost_usd": round(input_cost + output_cost, 6)
        }
    
    def truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """
        Truncate text to fit within token limit.
        
        Args:
            text: Text to truncate
            max_tokens: Maximum tokens allowed
            
        Returns:
            Truncated text
        """
        encoded = self.encoding.encode(text)
        
        if len(encoded) <= max_tokens:
            return text
        
        truncated = encoded[:max_tokens]
        return self.encoding.decode(truncated)
    
    def chunk_text(
        self,
        text: str,
        chunk_size: int = 4000,
        overlap: int = 200
    ) -> List[str]:
        """
        Split text into chunks that fit within token limits.
        
        Args:
            text: Text to chunk
            chunk_size: Max tokens per chunk
            overlap: Tokens to overlap between chunks
            
        Returns:
            List of text chunks
        """
        encoded = self.encoding.encode(text)
        
        if len(encoded) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(encoded):
            end = start + chunk_size
            chunk_encoded = encoded[start:end]
            chunk_text = self.encoding.decode(chunk_encoded)
            chunks.append(chunk_text)
            
            start = end - overlap
            if start >= len(encoded):
                break
        
        return chunks
    
    def summarize_token_usage(self, counts: List[TokenCount]) -> Dict[str, Any]:
        """
        Summarize token usage across multiple counts.
        
        Args:
            counts: List of TokenCount objects
            
        Returns:
            Summary dict
        """
        if not counts:
            return {
                "total_texts": 0,
                "total_tokens": 0,
                "total_chars": 0,
                "avg_tokens_per_text": 0,
                "avg_chars_per_token": 0
            }
        
        total_tokens = sum(c.tokens for c in counts)
        total_chars = sum(c.chars for c in counts)
        
        return {
            "total_texts": len(counts),
            "total_tokens": total_tokens,
            "total_chars": total_chars,
            "avg_tokens_per_text": round(total_tokens / len(counts), 1),
            "avg_chars_per_token": round(total_chars / total_tokens, 2) if total_tokens > 0 else 0,
            "min_tokens": min(c.tokens for c in counts),
            "max_tokens": max(c.tokens for c in counts)
        }


def count_prompt_tokens(prompt: str, model: str = "gpt-4o-mini") -> int:
    """Quick function to count prompt tokens."""
    counter = TokenCounter(model)
    return counter.count(prompt).tokens


def estimate_openai_cost(
    prompt: str,
    expected_output_tokens: int = 500,
    model: str = "gpt-4o-mini"
) -> Dict[str, float]:
    """
    Estimate cost for an OpenAI API call.
    
    Args:
        prompt: Input prompt
        expected_output_tokens: Expected output tokens
        model: Model name
        
    Returns:
        Cost estimate dict
    """
    counter = TokenCounter(model)
    input_count = counter.count(prompt)
    
    return counter.estimate_cost(
        input_tokens=input_count.tokens,
        output_tokens=expected_output_tokens,
        model=model
    )
