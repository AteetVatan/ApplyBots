"""Together AI LLM configurations for AutoGen agents.

Standards: python_clean.mdc
- No magic strings for model names
- Configurations as constants
"""

import os
from typing import Any

# Together AI API configuration
TOGETHER_API_BASE = "https://api.together.xyz/v1"


def get_together_api_key() -> str:
    """Get Together AI API key from environment."""
    from app.config import get_settings
    return get_settings().together_api_key.get_secret_value()


# Model identifiers - no magic strings
class Models:
    """Together AI model identifiers."""

    # Orchestration and reasoning
    DEEPSEEK_R1 = "deepseek-ai/DeepSeek-R1-0528"
    DEEPSEEK_V3 = "deepseek-ai/DeepSeek-V3.1"

    # Fast extraction and scraping
    LLAMA4_SCOUT = "meta-llama/Llama-4-Scout-17B-16E-Instruct"
    LLAMA4_MAVERICK = "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"

    # Content generation
    LLAMA3_70B = "meta-llama/Llama-3.3-70B-Instruct-Turbo"

    # Document understanding
    QWEN3_235B = "Qwen/Qwen3-235B-A22B-fp8-tput"

    # Reasoning and critique
    QWEN_QWQ = "Qwen/QwQ-32B"

    # Code generation
    QWEN3_CODER = "Qwen/Qwen3-Coder-480B-A35B-Instruct"

    # Embeddings
    BGE_LARGE = "BAAI/bge-large-en-v1.5"


def create_llm_config(
    *,
    model: str,
    temperature: float = 0.7,
    timeout: int = 120,
) -> dict[str, Any]:
    """Create LLM configuration for AutoGen agent."""
    return {
        "config_list": [
            {
                "model": model,
                "api_key": get_together_api_key(),
                "base_url": TOGETHER_API_BASE,
            }
        ],
        "temperature": temperature,
        "timeout": timeout,
    }


# Pre-configured LLM configs for each agent role
LLM_CONFIG_ORCHESTRATOR = create_llm_config(
    model=Models.DEEPSEEK_R1,
    temperature=0.3,  # Lower temp for orchestration
    timeout=180,
)

LLM_CONFIG_RESUME = create_llm_config(
    model=Models.QWEN3_235B,
    temperature=0.5,
    timeout=120,
)

LLM_CONFIG_SCRAPER = create_llm_config(
    model=Models.LLAMA4_SCOUT,
    temperature=0.3,
    timeout=60,
)

LLM_CONFIG_MATCHER = create_llm_config(
    model=Models.LLAMA4_MAVERICK,
    temperature=0.4,
    timeout=90,
)

LLM_CONFIG_APPLY = create_llm_config(
    model=Models.LLAMA3_70B,
    temperature=0.7,  # Higher temp for creative writing
    timeout=120,
)

LLM_CONFIG_QC = create_llm_config(
    model=Models.DEEPSEEK_V3,
    temperature=0.2,  # Low temp for strict review
    timeout=90,
)

LLM_CONFIG_CRITIC = create_llm_config(
    model=Models.QWEN_QWQ,
    temperature=0.5,
    timeout=90,
)

LLM_CONFIG_CODER = create_llm_config(
    model=Models.QWEN3_CODER,
    temperature=0.2,
    timeout=120,
)
