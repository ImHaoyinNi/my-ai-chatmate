from src.data.user_info import get_user, UserInfo, update_user
from src.service.message_processor.Message import Message, MessageType
from src.utils.config import config
from src.utils.constants import UserRole

image_generation_cost = config.credits_settings['image_generation_cost']
llm_cost = config.credits_settings['llm_cost']
voice_message_cost = config.credits_settings['voice_message_cost']

def charge_user(user_id: int, message: Message):
    if message.message_type == MessageType.BAD_MESSAGE:
        return
    total_cost = llm_cost
    if message.message_type == MessageType.VOICE:
        total_cost += voice_message_cost
    if message.message_type == MessageType.IMAGE:
        total_cost += image_generation_cost

    user_info: UserInfo = get_user(user_id)
    if user_info is None:
        return
    if user_info.role == UserRole.ADMIN.value:
        return
    credits_after_charge = user_info.credits - total_cost
    update_user(user_id, credits=credits_after_charge)