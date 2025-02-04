import re


def remove_think_tag(text):
    return re.sub(r'(?s)<think>.*?</think>', '', text).strip()

def parse_idle_time(idle_time: str) -> int:
    """Parses a string like '2h', '30m', '1d' into seconds."""
    match = re.match(r"(\d+)([hm])", idle_time.strip().lower())
    if not match:
        raise ValueError("Invalid idle_time format. Use 'Xm' for minutes or 'Xh' for hours.")

    value, unit = int(match.group(1)), match.group(2)
    if unit == "h":
        return value * 3600
    elif unit == "m":
        return value * 60
    return 0