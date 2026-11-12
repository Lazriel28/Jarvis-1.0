# ============================================================================
# Runtime Settings contract
# ============================================================================
# The real Settings object is constructed by load_settings() below. This
# file keeps a frozen dataclass here so call sites can import the typed
# contract without triggering the full config build at import time.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class Settings:
    db_path: str
    sqlite_vss_path: Optional[str]
    llm_provider: str
    llm_base_url: str
    llm_api_key: str
    llm_chat_model: str
    llm_thinking_enabled: bool
    embedding_provider: str
    embedding_base_url: str
    embedding_api_key: str
    embedding_model: str
    ollama_base_url: str
    ollama_embed_model: str
    ollama_chat_model: str
    llm_chat_timeout_sec: float
    llm_tools_timeout_sec: float
    llm_digest_timeout_sec: float
    llm_embedding_timeout_sec: float
    use_stdin: bool
    voice_debug: bool
    tts_enabled: bool
    tts_engine: str
    tts_voice: Optional[str]
    tts_rate: Optional[int]
    tts_chatterbox_device: str
    tts_chatterbox_audio_prompt: Optional[str]
    tts_chatterbox_exaggeration: float
    tts_chatterbox_cfg_weight: float
    tts_piper_model_path: Optional[str]
    tts_piper_speaker: Optional[int]
    tts_piper_length_scale: float
    tts_piper_noise_scale: float
    tts_piper_noise_w: float
    tts_piper_sentence_silence: float
    voice_device: Optional[str]
    sample_rate: int
    voice_min_energy: float
    voice_collect_seconds: float
    voice_max_collect_seconds: float
    wake_word: str
    wake_aliases: list[str]
    wake_fuzzy_ratio: float
    stop_commands: list[str]
    stop_command_fuzzy_ratio: float
    whisper_model: str
    whisper_backend: str
    whisper_device: str
    whisper_compute_type: str
    whisper_min_confidence: float
    whisper_no_speech_threshold: float
    whisper_min_audio_duration: float
    vad_enabled: bool
    vad_aggressiveness: int
    vad_frame_ms: int
    vad_pre_roll_ms: int
    endpoint_silence_ms: int
    max_utterance_ms: int
    tts_max_utterance_ms: int
    tune_enabled: bool
    hot_window_enabled: bool
    hot_window_seconds: float
    low_power_mode: bool
    echo_energy_threshold: float
    echo_tolerance: float
    fast_model: str
    intent_judge_timeout_sec: float
    intent_judge_thinking_enabled: bool
    transcript_buffer_duration_sec: float
    dialogue_memory_timeout: float
    memory_enrichment_max_results: int
    memory_enrichment_source: str
    tool_carryover_max_turns: int
    tool_carryover_per_entry_chars: int
    memory_digest_enabled: Optional[bool]
    tool_result_digest_enabled: Optional[bool]
    agentic_max_turns: int
    tool_selection_strategy: str
    tool_search_max_calls: int
    planner_enabled: bool
    planner_timeout_sec: float
    location_enabled: bool
    location_cache_minutes: int
    location_ip_address: Optional[str]
    location_auto_detect: bool
    location_cgnat_resolve_public_ip: bool
    web_search_enabled: bool
    brave_search_api_key: str
    wikipedia_fallback_enabled: bool
    dictation_enabled: bool
    dictation_hotkey: str
    dictation_filler_removal: bool
    dictation_thinking_enabled: bool
    dictation_custom_dictionary: list[Any]
    mcps: Dict[str, Any]
    _mcp_catalogue: Dict[str, Any]


# Re-export so import sites can do `from jarvis.config import Settings`
__all__ = ["Settings"]
