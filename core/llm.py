"""
NEXUS LLM & Groq Interface
Provides resilient communication with the Groq API using the official Groq SDK
or direct HTTP fallback, with automatic model negotiation and graceful missing-key handling.
"""

import os
from typing import List, Dict, Any, Optional

# Supported Groq Models
PREFERRED_MODEL = "openai/gpt-oss-120b"
FALLBACK_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "llama3-70b-8192",
    "llama-3.1-8b-instant"
]


def get_groq_api_key() -> Optional[str]:
    """Retrieves GROQ_API_KEY from environment or Streamlit secrets."""
    # 1. Environment variable
    api_key = os.environ.get("GROQ_API_KEY")
    if api_key and api_key.strip():
        return api_key.strip()
        
    # 2. Streamlit secrets
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
            val = st.secrets["GROQ_API_KEY"]
            if val and str(val).strip():
                return str(val).strip()
    except Exception:
        pass
        
    return None


def is_groq_available() -> bool:
    """Returns True if a valid Groq API key is present."""
    key = get_groq_api_key()
    return bool(key and len(key) > 5)


def call_groq_llm(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    temperature: float = 0.2,
    max_tokens: int = 1500
) -> Dict[str, Any]:
    """
    Executes a chat completion call to Groq.
    Attempts preferred model first, then fallbacks if model name has changed on Groq.
    Returns dict with {"success": bool, "content": str, "model_used": str, "error": str}.
    """
    api_key = get_groq_api_key()
    if not api_key:
        return {
            "success": False,
            "content": "",
            "model_used": "none",
            "error": "GROQ_API_KEY is not configured. Using deterministic engine with cached/rule-based synthesis."
        }
        
    candidate_models = []
    if model:
        candidate_models.append(model)
    else:
        candidate_models.append(PREFERRED_MODEL)
    for m in FALLBACK_MODELS:
        if m not in candidate_models:
            candidate_models.append(m)
            
    # Try using official Groq client first
    groq_client = None
    try:
        from groq import Groq
        groq_client = Groq(api_key=api_key)
    except ImportError:
        pass
        
    last_error = ""
    for candidate in candidate_models:
        try:
            if groq_client:
                completion = groq_client.chat.completions.create(
                    model=candidate,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                content = completion.choices[0].message.content or ""
                return {
                    "success": True,
                    "content": content,
                    "model_used": candidate,
                    "error": None
                }
            else:
                # Direct HTTP request fallback to Groq endpoint
                import urllib.request
                import json
                
                req = urllib.request.Request(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    data=json.dumps({
                        "model": candidate,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }).encode("utf-8")
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    res_json = json.loads(resp.read().decode("utf-8"))
                    content = res_json["choices"][0]["message"]["content"]
                    return {
                        "success": True,
                        "content": content,
                        "model_used": candidate,
                        "error": None
                    }
        except Exception as e:
            last_error = str(e)
            continue
            
    return {
        "success": False,
        "content": "",
        "model_used": "failed",
        "error": f"Groq API call failed across models: {last_error}"
    }
