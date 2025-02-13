from enum import Enum

from src.service.persona import get_persona_prompt, get_persona_types
from src.service.user_session import UserSessionManager


class COMMAND(Enum):
    HELP = "help"
    GET_CONTEXT = "get-context"
    CLEAR_CONTEXT = "clear-context"
    MY_CHATID = "get-my-chatid"

    GET_MY_SESSION = "get-my-session"
    GET_PERSONA = "get-persona"
    SET_PERSONA = "set-persona"
    ENABLE_VOICE = "enable-voice"
    DISABLE_VOICE = "disable-voice"
    ENABLE_PUSH = "enable-push"
    DISABLE_PUSH = "disable-push"
    ENABLE_IMAGE = "enable-image"
    DISABLE_IMAGE = "disable-image"

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
        case COMMAND.MY_CHATID.value:
            return f"Your id is: {user_id}"
        case COMMAND.GET_MY_SESSION.value:
            return user_session.to_string()
        case COMMAND.GET_PERSONA.value:
            personality = "Personality: " + user_session.persona
            prompt = "Prompt: " + get_persona_prompt(user_session.persona)
            return personality + "\n" + prompt
        case COMMAND.SET_PERSONA.value:
            user_session.set_persona(arguments[0])
            return "personality set to " + arguments[0]
        case COMMAND.ENABLE_VOICE.value:
            user_session.reply_with_voice = True
            return "voice is enabled. Bot will now reply with voice."
        case COMMAND.DISABLE_VOICE.value:
            user_session.reply_with_voice = False
            return "voice is disabled. Bot will now reply with text."
        case COMMAND.ENABLE_PUSH.value:
            user_session.enable_push = True
            return "push is enabled. Bot will now initiate conversation."
        case COMMAND.DISABLE_PUSH.value:
            user_session.enable_push = False
            return "push is disabled. Bot will not initiate conversation."
        case COMMAND.ENABLE_IMAGE.value:
            user_session.enable_push = True
            return "push is enabled. Bot will now initiate conversation."
        case COMMAND.DISABLE_PUSH.value:
            user_session.enable_push = False
            return "push is disabled. Bot will not initiate conversation."
        case _:
            return "unknown command"

def format_context(context: list[dict]) -> str:
    items = [item for item in context]
    if not items:
        formatted_context = ""
    else:
        result = []
        for i in range(0, len(items)):
            chunk = items[i]
            if len(chunk["content"]) >= 50:
                chunk = chunk["role"] + ":..." + chunk["content"][-50:]
            else:
                chunk = chunk["role"] + ":" + chunk["content"]
            result.append(chunk + "\n")

        formatted_context = ''.join(result).rstrip()
    print(formatted_context)
    return formatted_context

def help_doc():
    doc = f"""Available Commands:
    /help
        Display this help message with all available commands
    /get-context
        Show the current conversation context and history
    /clear-context
        Clear all conversation history and start fresh
    /get-my-session:
        Display the current conversation settings
    /get-my-chatid:
        Display your user id
        
    /get-persona
        Display the currently active personality setting
    /set-persona
        Available persona: {get_persona_types()}
        Usage: /set-personality chick

    /enable-voice
        Enable voice interaction mode
    /disable-voice
        Disable voice interaction mode and return to text-only
    
    /enable-image
        Allow bot to send images
    /disable-image
        Disallow bot to send images
        
    /enable-push
        Bot may initiate a conversation
    /disable-voice
        Bot won't initiate a conversation
    """
    return doc