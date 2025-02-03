import re


def remove_think_tag(text):
    return re.sub(r'(?s)<think>.*?</think>', '', text).strip()