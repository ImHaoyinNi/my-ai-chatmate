from dataclasses import dataclass


@dataclass
class Persona:
    prompt: str
    persona_code: str
    persona_description: str