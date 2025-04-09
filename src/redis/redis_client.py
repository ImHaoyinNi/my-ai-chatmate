import redis
import json
from typing import Any, Dict, List, Optional, Union

from src.utils.config import config
from src.utils.logger import logger


class RedisClient:
    """
    A client for interacting with Redis.
    """

    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0, password: Optional[str] = None):
        """
        Initialize the Redis client.

        Args:
            host: Redis server hostname
            port: Redis server port
            db: Redis database index
            password: Redis password, if any
        """
        self.connection = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True  # Auto-decode responses to strings
        )

    def ping(self) -> bool:
        """Test if the connection is alive."""
        try:
            return self.connection.ping()
        except redis.ConnectionError:
            return False

    def set(self, key: str, value: str, expiry: Optional[int] = None) -> bool:
        """
        Set a string value in Redis.

        Args:
            key: The key to set
            value: The value to set
            expiry: Optional expiration time in seconds

        Returns:
            True if successful
        """
        return self.connection.set(key, value, ex=expiry)

    # JSON operations
    def set_json(self, key: str, value: Any, expiry: Optional[int] = None) -> bool:
        """
        Store a Python object as JSON in Redis.

        Args:
            key: The key to set
            value: The Python object to store (must be JSON serializable)
            expiry: Optional expiration time in seconds

        Returns:
            True if successful
        """
        return self.set(key, json.dumps(value), expiry=expiry)

    def get_json(self, key: str) -> Any:
        """
        Retrieve a JSON object from Redis and deserialize it.

        Args:
            key: The key to retrieve

        Returns:
            The deserialized Python object or None if key doesn't exist
        """
        value = self.get(key)
        if value:
            return json.loads(value)
        return None

    # List operations
    def list_push(self, key: str, *values: str) -> int:
        """
        Push one or more values to the end of a list.

        Args:
            key: The list key
            values: One or more values to push

        Returns:
            The length of the list after the push operation
        """
        return self.connection.rpush(key, *values)

    def list_prepend(self, key: str, *values: str) -> int:
        """
        Push one or more values to the beginning of a list.

        Args:
            key: The list key
            values: One or more values to push

        Returns:
            The length of the list after the push operation
        """
        return self.connection.lpush(key, *values)

    def list_range(self, key: str, start: int = 0, end: int = -1) -> List[str]:
        """
        Get a range of elements from a list.

        Args:
            key: The list key
            start: Start index (0-based)
            end: End index (-1 means the last element)

        Returns:
            List of elements in the specified range
        """
        return self.connection.lrange(key, start, end)

    # Hash operations
    def hash_set(self, key: str, field: str, value: str) -> int:
        """
        Set a field in a hash stored at key.

        Args:
            key: The hash key
            field: The field to set
            value: The value to set

        Returns:
            1 if field is a new field and value was set, 0 if field already exists and value was updated
        """
        return self.connection.hset(key, field, value)

    def hash_get(self, key: str, field: str) -> Optional[str]:
        """
        Get a field from a hash stored at key.

        Args:
            key: The hash key
            field: The field to get

        Returns:
            The value of the field or None if field or key doesn't exist
        """
        return self.connection.hget(key, field)

    def hash_getall(self, key: str) -> Dict[str, str]:
        """
        Get all fields and values in a hash.

        Args:
            key: The hash key

        Returns:
            Dictionary of all fields and values in the hash
        """
        return self.connection.hgetall(key)

    # Set operations
    def set_add(self, key: str, *values: str) -> int:
        """
        Add one or more members to a set.

        Args:
            key: The set key
            values: One or more values to add

        Returns:
            The number of elements added to the set (excluding duplicates)
        """
        return self.connection.sadd(key, *values)

    def set_members(self, key: str) -> List[str]:
        """
        Get all members of a set.

        Args:
            key: The set key

        Returns:
            List of all members in the set
        """
        return list(self.connection.smembers(key))

    def set_is_member(self, key: str, value: str) -> bool:
        """
        Check if a value is a member of a set.

        Args:
            key: The set key
            value: The value to check

        Returns:
            True if value is a member of the set, False otherwise
        """
        return self.connection.sismember(key, value)

    # Key operations
    def delete(self, *keys: str) -> int:
        """
        Delete one or more keys.

        Args:
            keys: One or more keys to delete

        Returns:
            The number of keys that were deleted
        """
        return self.connection.delete(*keys)

    def exists(self, key: str) -> bool:
        """
        Check if a key exists.

        Args:
            key: The key to check

        Returns:
            True if the key exists, False otherwise
        """
        return bool(self.connection.exists(key))

    def expire(self, key: str, seconds: int) -> bool:
        """
        Set a key's time to live in seconds.

        Args:
            key: The key to set expiry on
            seconds: Time to live in seconds

        Returns:
            True if the timeout was set, False if key does not exist
        """
        return bool(self.connection.expire(key, seconds))

    def keys(self, pattern: str = "*") -> List[str]:
        """
        Find all keys matching the given pattern.

        Args:
            pattern: Pattern to match keys against

        Returns:
            List of matching keys
        """
        return self.connection.keys(pattern)

    # Connection operations
    def close(self) -> None:
        """Close the Redis connection."""
        self.connection.close()

host = config.redis_settings['host']
port = config.redis_settings['port']
redis_client = redis.Redis(
            host=host,
            port=port,
            db=0,
            password=None,
            decode_responses=True  # Auto-decode responses to strings
        )
logger.info("Connected to Redis")

def basic_examples():
    # Initialize the client (connects to your forwarded Redis server)
    redis = RedisClient(host='localhost', port=6379)

    # Check connection
    if not redis.ping():
        print("Could not connect to Redis server!")
        return

    print("Connected to Redis server successfully!")

    # String operations
    redis.set('greeting', 'Hello, Redis!')
    greeting = redis.get('greeting')
    print(f"Retrieved string: {greeting}")

    # JSON operations
    user = {
        'id': 1001,
        'name': 'John Doe',
        'email': 'john@example.com',
        'roles': ['user', 'admin']
    }
    redis.set_json('user:1001', user)
    retrieved_user = redis.get_json('user:1001')
    print(f"Retrieved JSON: {retrieved_user}")

    # List operations
    redis.list_push('recent_searches', 'redis python', 'machine learning', 'data science')
    searches = redis.list_range('recent_searches')
    print(f"Recent searches: {searches}")

    # Hash operations
    redis.hash_set('session:123', 'user_id', '1001')
    redis.hash_set('session:123', 'created_at', '2023-01-01T12:00:00')
    redis.hash_set('session:123', 'last_activity', '2023-01-01T12:05:30')
    session = redis.hash_getall('session:123')
    print(f"Session data: {session}")

    # Set operations
    redis.set_add('active_users', '1001', '1002', '1003')
    active_users = redis.set_members('active_users')
    print(f"Active users: {active_users}")

    # Check if a specific user is active
    is_active = redis.set_is_member('active_users', '1001')
    print(f"User 1001 is active: {is_active}")

    # Cleanup (optional)
    keys_to_delete = ['greeting', 'user:1001', 'recent_searches', 'session:123', 'active_users']
    deleted = redis.delete(*keys_to_delete)
    print(f"Deleted {deleted} keys during cleanup")

    # Close connection
    redis.close()


if __name__ == "__main__":
    basic_examples()