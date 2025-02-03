from enum import Enum

from src.service.user_session.personality import get_personality_prompt
from src.service.user_session.user_session import UserSessionManager


class COMMAND(Enum):
    HELP = "help"
    GET_CONTEXT = "get-context"
    CLEAR_CONTEXT = "clear-context"
    GET_PERSONALITY = "get-personality"
    SET_PERSONALITY = "set-personality"
    ENABLE_VOICE = "enable_voice"
    DISABLE_VOICE = "disable_voice"

def run_command(user_id, command: str, arguments: list[str]) -> str:
    user_session = UserSessionManager.get_session(user_id)
    match command.lower():
        case COMMAND.HELP.value:
            return help_doc()
        case COMMAND.GET_CONTEXT.value:
            formatted_context = format_context(user_session.get_context())
            return formatted_context
        case COMMAND.CLEAR_CONTEXT.value:
            user_session.clear_context()
            return "session cleared"
        case COMMAND.GET_PERSONALITY.value:
            personality = "Personality: " + user_session.personality
            prompt = "Prompt: " + get_personality_prompt(user_session.personality)
            return personality + "\n" + prompt
        case COMMAND.SET_PERSONALITY.value:
            user_session.set_personality(arguments[0])
            return "personality set to " + arguments[0]
        case COMMAND.ENABLE_VOICE.value:
            user_session.reply_with_voice = True
            return "voice is enabled. Bot will now reply with voice."
        case COMMAND.DISABLE_VOICE.value:
            user_session.reply_with_voice = False
            return "voice is disabled. Bot will now reply with text."
        case _:
            return "unknown command"

def format_context(context: list[object]) -> str:
    items = [str(item) for item in context]
    if not items:
        formatted_context = ""
    else:
        result = [items[0] + "\n"]
        remaining = items[1:]
        for i in range(0, len(remaining), 2):
            chunk = remaining[i:i + 2]
            result.append('\n'.join(chunk) + "\n")

        formatted_context = ''.join(result).rstrip()
    return formatted_context

def help_doc():
    doc = """Available Commands:
    /help
        Display this help message with all available commands

    /get-context
        Show the current conversation context and history

    /clear-context
        Clear all conversation history and start fresh

    /get-personality
        Display the currently active personality setting

    /set-personality
        Change the active personality
        Usage: /set-personality chick

    /enable-voice
        Enable voice interaction mode

    /disable-voice
        Disable voice interaction mode and return to text-only"""
    return doc