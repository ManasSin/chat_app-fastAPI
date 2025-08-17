import asyncio
import websockets
import json
import uuid

async def test_websocket():
    session_id = str(uuid.uuid4())
    uri = f"ws://localhost:8000/ws/chat/{session_id}"

    print(f"Connecting to {uri}")

    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket!")
        test_messages = [
            "Hello, how are you today?",
            "I love this project, it's excellent!"
        ]

        for message in test_messages:
            print(f"\nSending: {message}")

            await websocket.send(json.dumps({"content": message}))

            response = await websocket.recv()
            response_data = json.loads(response)
 
            print("Response received:")
            print(f"  Echo: {response_data['echo']}")
            print(f"  Analytics: {json.dumps(response_data['analytics'], indent=2)}")
            print(f"  Session Stats: {json.dumps(response_data['session_stats'], indent=2)}")

            await asyncio.sleep(1)

        print("\nTest completed!")

if __name__ == "__main__":
    asyncio.run(test_websocket())
