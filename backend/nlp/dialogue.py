"""
Generate an empathic therapist reply given user text + sentiment.
Uses Phi-3-mini in instruct mode (no API key needed).
"""

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    GenerationConfig,
)

_MODEL_NAME = "microsoft/Phi-3-mini-4k-instruct"

_tokenizer = AutoTokenizer.from_pretrained(_MODEL_NAME)
_model = AutoModelForCausalLM.from_pretrained(
    _MODEL_NAME,
    trust_remote_code=True,
    device_map="auto",
)  # ⬅️ will load on CPU if no GPU

# A single place to tweak generation behaviour
_gen_cfg = GenerationConfig(
    max_new_tokens=120,
    temperature=0.7,
    top_p=0.9,
    pad_token_id=_tokenizer.eos_token_id,
)


def reply(user_text: str, mood: str) -> str:
    """
    Return the model's reply string (no role prefixes).
    """
    prompt = (
        "You are an empathetic speech therapist.\n"
        f"User sentiment: {mood}.\n"
        "Respond in a compassionate, constructive tone.\n\n"
        f"User: {user_text}\n"
        "Therapist:"
    )

    inputs = _tokenizer(prompt, return_tensors="pt").to(_model.device)
    outputs = _model.generate(**inputs, generation_config=_gen_cfg)
    full = _tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Everything after the last "Therapist:" is the answer
    return full.split("Therapist:")[-1].strip()