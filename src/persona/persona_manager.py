from typing import List

from src.persona.models.civen import civen
from src.persona.models.succubus import succubus
from src.persona.models.xiao_ling import xiao_ling
from src.persona.persona_model import Persona

persona_store : List[Persona] = [civen, succubus, xiao_ling]


def get_persona_prompt(persona_code: str, user_full_name: str="<USER_NAME>") -> str:
    for p in persona_store:
        if p.persona_code == persona_code:
            prompt = p.prompt
            prompt = prompt.replace("<USER_NAME>", user_full_name)
            return prompt
    else:
        return ""

def get_persona_codes() -> List[str]:
    codes = []
    for p in persona_store:
        codes.append(p.persona_code)
    return codes

def get_persona_description(persona_code: str) -> str:
    for p in persona_store:
        if p.persona_code == persona_code:
            return p.persona_description
    else:
        return ""