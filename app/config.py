import os
from dataclasses import dataclass


DEFAULT_CRITIC_MODEL = "llama-3.3-70b-versatile"
DEFAULT_WRITER_MODEL = "llama-3.1-8b-instant"


@dataclass(frozen=True)
class Settings:
    groq_api_key: str
    tavily_api_key: str
    critic_model: str
    writer_model: str
    search_max_results: int
    max_revisions: int


def _read_int(name: str, default: int, minimum: int, maximum: int) -> int:
    raw_value = os.getenv(name)
    if not raw_value:
        return default

    try:
        value = int(raw_value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer.") from exc

    if value < minimum or value > maximum:
        raise RuntimeError(f"{name} must be between {minimum} and {maximum}.")
    return value


def load_settings(validate_keys: bool = True) -> Settings:
    groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
    tavily_api_key = os.getenv("TAVILY_API_KEY", "").strip()

    if validate_keys:
        missing = [
            name
            for name, value in {
                "GROQ_API_KEY": groq_api_key,
                "TAVILY_API_KEY": tavily_api_key,
            }.items()
            if not value
        ]
        if missing:
            raise RuntimeError(
                "Missing required environment variable(s): " + ", ".join(missing)
            )

    return Settings(
        groq_api_key=groq_api_key,
        tavily_api_key=tavily_api_key,
        critic_model=os.getenv("OMNI_CRITIC_MODEL", DEFAULT_CRITIC_MODEL),
        writer_model=os.getenv("OMNI_WRITER_MODEL", DEFAULT_WRITER_MODEL),
        search_max_results=_read_int("OMNI_SEARCH_MAX_RESULTS", 5, 1, 10),
        max_revisions=_read_int("OMNI_MAX_REVISIONS", 2, 1, 5),
    )
