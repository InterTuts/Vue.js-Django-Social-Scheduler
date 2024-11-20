# System Utils
from typing import Any, Set
from django.core.cache import cache

class CacheManager:
    def __init__(self, user_id: int, page_number: int = 0):
        # Set user's id in session
        self.user_id = user_id
        # Set time limit for cache
        self.timeout = 86400
        # Generate cache key
        self.cache_key = self.generate_cache_key(page_number)

    def generate_cache_key(self, page_number: int) -> str:
        # Generate cache
        return f"user_{self.user_id}_page_{page_number}"

    def get_cache(self) -> Any:
        # Get cache
        return cache.get(self.cache_key)

    def set_cache(self, data) -> None:
        # Retrieve the set of cache keys for the user or initialize a new set if not found
        user_cache_keys: Set[str] = cache.get(f"user_{self.user_id}", set())

        # Add the new cache key to the set of user's cache keys
        user_cache_keys.add(self.cache_key)
        
        # Save the updated set of cache keys back to the cache store
        cache.set(f"user_{self.user_id}", user_cache_keys, timeout=self.timeout)

        # Save cache
        cache.set(self.cache_key, data, timeout=self.timeout)

    def clear_cache(self) -> None:
 
        # Retrieve the set of cache keys for the user or initialize a new set if not found
        user_cache_keys: Set[str] = cache.get(f"user_{self.user_id}", set())

        # Check if the cache group exists
        if user_cache_keys:
            # Iterate over the keys in the group and remove them
            for key in list(set(user_cache_keys)):
                # Delete cache
                cache.delete(key)

        # Update Cache
        cache.set(f"user_{self.user_id}", set(), timeout=self.timeout)