import logging
import os
import os.path
from copy import deepcopy

from redis import Redis

logger = logging.getLogger(__name__)

from io import BytesIO

unsubscribe_message = b'__UNSUBSCRIBE__'
"""(str): The message used to unsubscribe from and close a PubSub channel
"""


class RedisSubscription(object):
    def __init__(self, channel, pubsub):
        self.channel = channel
        self._pubsub = pubsub

    def listen(self):
        """Listen for updates in this channel

        Returns:
            (generator): A generator which yields new values in the channel
        """
        return self._listen()

    def _listen(self):
        """Listen for updates in this channel and yield the results

        Yields:
            The new values in this channel
        """
        for message in self._pubsub.listen():
            data = message['data']
            if data == unsubscribe_message:
                self._pubsub.unsubscribe()
                break
            else:
                yield data


class RedisCacheAdapter(object):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(RedisCacheAdapter, cls).__new__(cls)
        return cls.instance

    def __init__(self, **opts):
        self.cache = Redis(**opts)
        logger.info('Created redis cache connection with options: {}'.format(opts))

    def set(self, key, value, expire=None, **opts):
        """Set a value for a key in the cache

        Args:
            key: The key to use for this data
            value: The value to set this key to
            expire (int|datetime.timedelta, optional): The expiration for this value. If `int` is passed, it indicates
                milliseconds
            **opts: Additional options to use. See `FanoutCache` for more details

        Returns:
            (bool): Was this key set?
        """
        return self.cache.set(key, value, px=expire, **opts)

    def get(self, key, **opts):
        """Gets the value stored in the key

        Args:
            key: The key to get the value from
            **opts: Additional options to use.

        Returns:
            The value stored in the key
        """
        return self._decode_response(self.cache.get(key))

    def add(self, key, value, expire=None, **opts):
        """Add a key and a value to the cache if the key is not already in the cache

        Args:
            key: The key to store the value to
            value: Teh value to store in the key
            expire (int|datetime.timedelta, optional): The expiration for this value. If `int` is passed, it indicates
                milliseconds
            **opts: Additional options to use. See `FanoutCache` for more details

        Returns:
            (bool): Was the key set?
        """
        return self.cache.set(key, value, px=expire, nx=True, **opts)

    def delete(self, key):
        """Deletes a key
        """
        return self.cache.delete(key)

    def incr(self, key, amount=1):
        """Increments a key by an amount.

        If the key is not found, then its value becomes the increment amount specified

        Args:
            key: The key to increment
            amount (int, optional): The amount to increment the key by. Defaults to 1
            retry (bool, optional): Should this operation be retried if the transaction times out? Defaults to
                `self.retry`

        Returns:
            (int): The incremented value
        """
        return int(self.cache.incr(key, amount))

    def decr(self, key, amount=1):
        """Decrements a key by an amount.

        If the key is not found, then its value becomes the decrement amount specified

        Args:
            key: The key to decrement
            amount (int, optional): The amount to decrement the key by. Defaults to 1
            retry (bool, optional): Should this operation be retried if the transaction times out? Defaults to
                `self.retry`

        Returns:
            (int): The decremented value
        """
        return int(self.cache.decr(key, amount))

    def rpush(self, key, *values):
        """Pushes a value to the right of a deque.

        This operation also creates a deque for a given key if one was not already created. Otherwise it uses the
        existing deque

        Args:
            key: The key of the deque to push the values to
            *values: The values to push to the deque
        """
        return self.cache.rpush(key, *values)

    def rpop(self, key):
        """Pops a value from the right of a deque.

        If this key is not a deque then this function will return None.

        Args:
            key: The key of the deque to push the values to
            *values: The values to push to the deque

        Returns:
            The rightmost value on the deque or None if the key is not a deque or the deque is empty
        """
        return self._decode_response(self.cache.rpop(key))

    def lpush(self, key, *values):
        """Pushes a value to the left of a deque.

        This operation also creates a deque for a given key if one was not already created. Otherwise it uses the
        existing deque

        Args:
            key: The key of the deque to push the values to
            *values: The values to push to the deque
        """
        return self.cache.lpush(key, *values)

    def lpop(self, key):
        """Pops a value from the left of a deque.

        If this key is not a deque then this function will return None.

        Args:
            key: The key of the deque to push the values to
            *values: The values to push to the deque

        Returns:
            The leftmost value on the deque or None if the key is not a deque or the deque is empty
        """
        return self._decode_response(self.cache.lpop(key))

    @staticmethod
    def _decode_response(response):
        if response is None:
            return response
        try:
            return response.decode('utf-8')
        except UnicodeDecodeError:
            return response

    def subscribe(self, channel):
        """Subscribe to a channel

        Args:
            channel (str): The name of the channel to subscribe to

        Returns:
            (RedisSubscription): The subscription for this channel
        """
        subscription = self.cache.pubsub()
        subscription.subscribe(channel)
        subscription.get_message()
        return RedisSubscription(channel, subscription)

    def unsubscribe(self, channel):
        """Unsubscribe to a channel

        Args:
            channel (str): The name of the channel to subscribe to

        Returns:
            (int): The number of subscribers unsubscribed ffrom this channel
        """
        return self.cache.publish(channel, unsubscribe_message)

    def publish(self, channel, data):
        """Publish some data to a channel

        Args:
            channel (str): The name of the channel to publish the data to
            data: The data to publish

        Returns:
            The number of subscriptions which received the data
        """
        return self.cache.publish(channel, data)

    def shutdown(self):
        """Shuts down the connection to the cache

        For the Redis cache, this is not necessary. Redis's ConnectionPool should handle it
        """
        pass

    def clear(self):
        """Clears all values in the cache
        """
        self.cache.flushdb()

    def check(self):
        self.cache.info()

    def ping(self):
        """Pings the Redis cache to test the connection

        Returns:
            (Bool): True if the ping was successful, False otherwise.
        """
        return self.cache.ping()

    def scan(self, pattern=None):
        """Scans through all keys in the cache

        Args:
            pattern (str, optional): Regex Pattern to search for

        Returns:
            Iterator(str): The keys in the cache matching the pattern if specified. Else all the keys in the cache
        """
        return (key.decode('utf-8') for key in self.cache.scan_iter(pattern))

    def exists(self, key):
        """Checks to see if a key exists in the cache

        Args:
            key: The key to check

        Returns:
            bool: Does the key exist?
        """
        return bool(self.cache.exists(key))

    def lock(self, name, timeout=None, sleep=0.1, blocking_timeout=None):
        """Gets a distributed lock backed by the cache

        Args:
            name (str): The name of the lock
            timeout (float): The maximum life for the lock in seconds. If none is specified, it will remain locked
                until release() is called on the lock
            sleep (float): The amount of time to sleep per loop iteration when the lock is in blocking mode and another
                client is currently holding the lock
            blocking_timeout (float): The maximum amount of time in seconds to spend trying to acquire the lock. If
                none is specified, the lock will continue trying forever
        Returns:
            A lock
        """
        return self.cache.lock(name, timeout=timeout, sleep=sleep, blocking_timeout=blocking_timeout)

