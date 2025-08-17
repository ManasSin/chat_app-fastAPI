# Chat Analytics Backend

A FastAPI-based backend that provides real-time chat analytics through WebSocket connections. The system processes messages, stores analytics in a SQLite database, and provides real-time feedback including message analytics and session statistics.

## Features

- **WebSocket Support**: Real-time bidirectional communication
- **Message Analytics**: Word count, character count, sentence count, question detection, and sentiment analysis
- **Session Management**: Track conversation statistics across sessions
- **Database Storage**: SQLite database for persistent storage of messages and analytics
- **REST API Endpoints**: Additional endpoints for retrieving session data

## Setup

1. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Backend**:

   ```bash
   python main.py
   ```

   The server will start on `http://localhost:8000`

3. **Access API Documentation**:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## WebSocket Usage

### Connection

Connect to the WebSocket endpoint:

```
ws://localhost:8000/ws/chat/{session_id}
```

Where `{session_id}` is a unique identifier for the chat session.

### Message Format

Send messages in JSON format:

```json
{
  "content": "Your message here"
}
```

### Response Format

The server responds with:

```json
{
  "type": "message_response",
  "original_message": "Your message here",
  "echo": "You said: Your message here",
  "analytics": {
    "word_count": 3,
    "char_count": 18,
    "sentence_count": 1,
    "is_question": false,
    "sentiment": "neutral"
  },
  "session_stats": {
    "total_messages": 5,
    "total_words": 25,
    "questions_asked": 2,
    "avg_message_length": 5.0
  }
}
```

## Message Processing Logic

The backend analyzes messages for:

- **Word Count**: Number of words in the message
- **Character Count**: Total characters (including spaces)
- **Sentence Count**: Number of sentences (detected by ., ?, !)
- **Question Detection**: Identifies questions using question marks or question words (what, how, why, when, where, who)
- **Sentiment Analysis**: Basic sentiment detection using positive/negative word lists

## REST API Endpoints

### Health Check

- `GET /` - Check if the backend is running

### Session Statistics

- `GET /session/{session_id}/stats` - Get statistics for a specific session

### Session Messages

- `GET /session/{session_id}/messages` - Get all messages for a specific session

## Testing

Use the provided test client to test the WebSocket functionality:

```bash
python test_client.py
```

This will:

1. Connect to the WebSocket endpoint
2. Send several test messages
3. Display the responses and analytics

## Database Schema

### Messages Table

- `id`: Primary key
- `session_id`: Session identifier
- `message_text`: Original message content
- `word_count`: Number of words
- `char_count`: Number of characters
- `sentence_count`: Number of sentences
- `is_question`: Boolean indicating if it's a question
- `sentiment`: Sentiment analysis result
- `processed_at`: Timestamp of processing

### Sessions Table

- `id`: Session identifier
- `total_messages`: Total messages in the session
- `total_words`: Total words across all messages
- `questions_asked`: Number of questions asked
- `total_positive_messages`: Number of positive messages
- `total_negative_messages`: Number of negative messages
- `total_neutral_messages`: Number of neutral messages
- `created_at`: Session creation timestamp
- `last_updated`: Last update timestamp

## Example Usage

### JavaScript Client Example

```javascript
const sessionId = "user123";
const ws = new WebSocket(`ws://localhost:8000/ws/chat/${sessionId}`);

ws.onopen = () => {
  console.log("Connected to chat");

  // Send a message
  ws.send(
    JSON.stringify({
      message: "Hello, how are you today?",
    })
  );
};

ws.onmessage = (event) => {
  const response = JSON.parse(event.data);
  console.log("Analytics:", response.analytics);
  console.log("Session Stats:", response.session_stats);
};
```

### Python Client Example

```python
import websockets
import json
import asyncio

async def chat_client():
    uri = "ws://localhost:8000/ws/chat/user123"
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({"message": "Hello world!"}))
        response = await websocket.recv()
        print(json.loads(response))

asyncio.run(chat_client())
```

## Error Handling

The backend includes comprehensive error handling for:

- WebSocket disconnections
- Database errors
- Invalid message formats
- Connection failures
