from src.data.connect_db import connect_db
import io
from src.data.Message import Message, MessageType
from src.utils.logger import logger

table_name = "message_history"

def insert_message(msg: Message):
    conn = connect_db()
    if conn is None:
        return

    content_text = None
    content_blob = None

    if isinstance(msg.content, str):
        content_text = msg.content
    elif isinstance(msg.content, io.BytesIO):
        msg.content.seek(0)
        content_blob = msg.content.read()

    try:
        cur = conn.cursor()
        query = f"""
            INSERT INTO {table_name} (
                user_id,
                message_type,
                prompt,
                content_text,
                content_blob,
                timestamp
            )
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        cur.execute(query, (
            msg.user_id,
            msg.message_type.value,
            msg.prompt,
            content_text,
            content_blob,
            msg.timestamp
        ))
        conn.commit()
        logger.info(f"{msg.message_type.value.capitalize()} message stored for user {msg.user_id}.")
    except Exception as e:
        logger.info(f"Error inserting message: {e}")
        conn.rollback()
    finally:
        conn.close()

def fetch_user_messages(user_id: int):
    conn = connect_db()
    if conn is None:
        return

    try:
        cur = conn.cursor()
        query = f"""
        SELECT message_type, prompt, content_text, content_blob, timestamp
        FROM {table_name}
        WHERE user_id = %s
        ORDER BY timestamp;
        """
        cur.execute(query, (user_id,))
        rows = cur.fetchall()
        for msg_type, prompt, text, blob, ts in rows:
            print(f"\n[{ts}] Prompt: {prompt}")
            print(f"Type: {msg_type}")
            if text:
                print(f"Text Content: {text}")
            elif blob:
                print(f"Binary Content: {len(blob)} bytes")
    except Exception as e:
        print(f"Error fetching messages: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    msg1 = Message(
        message_type=MessageType.TEXT,
        content="Here's a fun fact about cats!",
        prompt="Tell me something fun about cats",
        user_id=1
    )

    # Image message
    image_data = io.BytesIO(b'\x89PNG\r\n\x1a\n...')  # Replace with actual binary image data
    msg2 = Message(
        message_type=MessageType.IMAGE,
        content=image_data,
        prompt="Show me a cute cat picture",
        user_id=1
    )

    insert_message(msg1)
    insert_message(msg2)
    fetch_user_messages(1)