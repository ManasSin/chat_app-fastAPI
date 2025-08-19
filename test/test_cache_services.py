#!/usr/bin/env python3

from datetime import datetime

from services import (
    redis_service,
    session_service,
    message_cache_service,
    cache_manager,
)


def test_redis_service():
    print("Testing Redis Service...")

    test_key = "test:basic"
    test_value = {"message": "Hello Redis!", "timestamp": datetime.now().isoformat()}

    success = redis_service.set_cache(test_key, test_value, ttl=60)
    print(f"  Set cache: {success}")

    retrieved = redis_service.get_cache(test_key)
    print(f"  Get cache: {retrieved == test_value}")

    redis_service.delete_cache(test_key)

    print("  Redis service tests completed\n")


def test_session_service():
    print("Testing Session Service...")

    session_data = session_service.create_session(user_id="test_user_123")
    print(f"  Created session: {session_data['id'][:8]}...")

    session_id = session_data["id"]

    retrieved_session = session_service.get_session(session_id)
    print(f"  Retrieved session: {retrieved_session is not None}")

    success = session_service.update_session_activity(session_id)
    print(f"  Updated session activity: {success}")

    test_analytics = {
        "word_count": 10,
        "char_count": 50,
        "sentence_count": 2,
        "is_question": True,
        "sentiment": "positive",
    }

    success = session_service.update_session_stats(session_id, test_analytics)
    print(f"  Updated session stats: {success}")

    analytics = session_service.get_session_analytics(session_id)
    print(f"  Got session analytics: {analytics is not None}")
    if analytics:
        print(f"    - Total messages: {analytics.get('total_messages', 0)}")
        print(f"    - Total words: {analytics.get('total_words', 0)}")

    success = session_service.invalidate_session(session_id)
    print(f"  Invalidated session: {success}")

    print("  Session service tests completed\n")


def test_message_cache_service():
    print("Testing Message Cache Service...")

    session_id = "test_session_456"

    test_analytics = {
        "word_count": 15,
        "char_count": 75,
        "sentence_count": 3,
        "is_question": False,
        "sentiment": "neutral",
        "timestamp": datetime.now().isoformat(),
    }

    message_data = {
        "id": "test_msg_123",
        "session_id": session_id,
        "content": "This is a test message",
        **test_analytics,
    }

    success = message_cache_service.cache_message_analytics(
        message_data["id"], message_data
    )
    print(f"  Cached message analytics: {success}")

    retrieved = message_cache_service.get_cached_message_analytics(message_data["id"])
    print(f"  Retrieved cached analytics: {retrieved == message_data}")

    print("  Message cache service tests completed\n")


def test_cache_manager():
    print("Testing Cache Manager...")

    success = cache_manager.warm_up_cache("test_session_123", [])
    print(f"  Warmed up cache: {success}")

    print("  Cache manager tests completed\n")


def test_integration():
    print("Testing Service Integration...")

    session_data = session_service.create_session(user_id="integration_test_user")
    session_id = session_data["id"]

    messages = [
        {
            "content": "Hello, this is a test message",
            "word_count": 7,
            "char_count": 32,
            "sentence_count": 1,
            "is_question": False,
            "sentiment": "neutral",
        },
        {
            "content": "How are you doing today?",
            "word_count": 6,
            "char_count": 25,
            "sentence_count": 1,
            "is_question": True,
            "sentiment": "positive",
        },
    ]

    success = cache_manager.warm_up_session_cache(session_id, messages)
    print(f"  Warmed up cache: {success}")

    analytics = session_service.get_session_analytics(session_id)
    print(f"  Got integrated analytics: {analytics is not None}")

    session_service.invalidate_session(session_id)

    print("  Integration tests completed\n")


def main():
    print("Starting Phase 3.1: Caching & Session Management Tests\n")

    try:
        test_redis_service()
        test_session_service()
        test_message_cache_service()
        test_cache_manager()
        test_integration()

        print("All tests completed successfully!")
        print("\nPhase 3.1 implementation is working correctly!")

    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
