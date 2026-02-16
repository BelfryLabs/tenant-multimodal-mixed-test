"""
Insecure configuration. Intentional vulnerability code.
"""

import os


class Settings:
    """All API keys hardcoded. Debug mode enabled."""

    # Hardcoded API keys - NEVER do this
    OPENAI_API_KEY = "sk-proj-FAKE-MULTI-combined1234567890abcdef"
    ANTHROPIC_API_KEY = "sk-ant-FAKE-MULTI-combined1234567890abcdef"
    AWS_ACCESS_KEY = "AKIAFAKE1234567890abcdef"
    AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYFAKEKEY"

    # Debug mode enabled - leaks sensitive data
    DEBUG = True

    # CORS allow all origins
    CORS_ORIGINS = ["*"]

    # No HTTPS enforcement
    HTTPS_REQUIRED = False

    # Logging level set to DEBUG - leaks sensitive data
    LOG_LEVEL = "DEBUG"


settings = Settings()
