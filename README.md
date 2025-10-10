# Max Messenger API Python Wrapper

## Features

-   **Dual Authentication:** Supports both token-based authentication for existing sessions and phone number verification for new sessions.
-   **Real-Time Event Handling:** Allows for custom callback functions to handle server-push events, such as new messages and presence updates.
-   **Automatic Reconnection:** Automatically handles connection drops by reconnecting and re-authenticating the session to ensure reliability.
-   **Helper Methods:** Includes convenience methods for common actions like fetching chat history, downloading files and videos, and managing contacts.

## Installation

You can install library with pip:

```bash
pip install MaxBridge
```

## Usage

### Initialization

To get started, create an instance of the `MaxAPI` class. You can authenticate using an existing token or by verifying a phone number.

**With an authentication token:**

If you already have a valid `auth_token`, you can provide it during initialization for a quick and seamless connection.

```python
from max_api import MaxAPI

AUTH_TOKEN = "your_auth_token_here"

api = MaxAPI(auth_token=AUTH_TOKEN)
```
#### Obtaining the authentication token

1. Open your web browser and navigate to [Max Messenger Web Version](https://web.max.ru).
2. Log in to your Max account if you haven't done so already.
3. After logging in, open the Developer Tools in your web browser (right-click anywhere on the page and select "Inspect" or press `F12`).
4. Go to the "Application" tab in Developer Tools.
5. Find and click on "Local storage" in the left sidebar under the "Storage" section. Look for the cookies belonging to the `https://web.max.ru` domain.
6. Find the authentication token. This token is a value of `__oneme_auth`.
7. Copy the value of the authentication token. You'll use this value to authenticate your requests in the MaxAPI class.


**Without an authentication token (phone number verification):**

If you don't have an `auth_token`, you can authenticate by verifying your phone number.

```python
from max_api import MaxAPI

api = MaxAPI()

phone_number = "your_phone_number"  # e.g., "+11234567890"
api.send_verify_code(phone_number)

# Enter the code you receive via SMS
code = input("Enter verification code: ")
api.check_verify_code(code)
```

### Sending a Message

Once authenticated, you can easily send messages to any chat.

```python
# The ID of the chat to send the message to
chat_id = "some_chat_id"
# The text of the message
message_text = "Hello, world from the API!"

# Send the message
api.send_message(chat_id, message_text)
```

You can also send a reply to a specific message:

```python
api.send_message(chat_id, "This is a reply.", reply_id="message_id_to_reply_to")
```

### Receiving Events

You can handle real-time events, such as new messages, by passing a callback function to the `on_event` parameter during initialization.

```python
import json

def my_event_handler(event_data):
    """
    A custom callback to handle incoming events from the server.
    """
    opcode = event_data.get("opcode")
    if opcode == 128:  # New message event
        print(f"New Message Received: {json.dumps(event_data, indent=2)}")
    else:
        print(f"Server Event (Opcode {opcode}): {json.dumps(event_data, indent=2)}")

# Initialize the API with your custom event handler
api = MaxAPI(auth_token=AUTH_TOKEN, on_event=my_event_handler)

# The API will now use my_event_handler for incoming events.
# Keep the script running to listen for events.
```

### Fetching Chat History

Retrieve the message history for any chat with a simple method call.

```python
# The ID of the chat to fetch history from
chat_id = "some_chat_id"
# The number of messages to retrieve
message_count = 50

# Get the chat history
history = api.get_history(chat_id, count=message_count)
print(history)
```

### Subscribing to a Chat

To receive real-time updates for a specific chat (like new messages or typing indicators), you need to subscribe to it.

```python
# The ID of the chat to subscribe to
chat_id = "some_chat_id"

# Subscribe to the chat
api.subscribe_to_chat(chat_id)
```

### Shutdown

The API handles `SIGINT` (Ctrl+C) and `SIGTERM` signals automatically. You can also call the `close()` method manually to disconnect from the WebSocket server.

```python
api.close()
```

## API Reference

### `MaxAPI(auth_token=None, on_event=None)`

-   **`auth_token`** (`str`, optional): An authentication token for the session.
-   **`on_event`** (`callable`, optional): A callback function for server-push events, which receives one argument: the event data dictionary.

### Methods

-   **`send_message(chat_id, text, reply_id=None, wait_for_response=False, format=False)`**: Sends a message to a chat.
-   **`get_history(chat_id, count=30, from_timestamp=None)`**: Retrieves the message history for a chat.
-   **`subscribe_to_chat(chat_id, subscribe=True)`**: Subscribes to or unsubscribes from real-time chat updates.
-   **`mark_as_read(chat_id, message_id)`**: Marks a specific message as read.
-   **`get_contact_details(contact_ids)`**: Retrieves profile details for one or more contacts.
-   **`get_contact_by_phone(phone_number)`**: Finds a contact by their phone number.
-   **`get_chat_by_id(chat_id)`**: Retrieves a chat from the local cache by its ID.
-   **`get_all_chats()`**: Returns a dictionary of all cached chats.
-   **`send_verify_code(phone_number)`**: Sends a verification code to a phone number to begin authentication.
-   **`check_verify_code(code)`**: Verifies a code received via SMS to complete authentication.
-   **`send_generic_command(command_name, payload, wait_for_response=True, timeout=10)`**: Sends a raw command to the API by its string name (e.g., `'GET_HISTORY'`).
-   **`get_video(id)`**: Downloads a video by its ID and returns it as a byte stream.
-   **`get_file(id, chat_id, msg_id)`**: Downloads a file by its ID and returns its content and name.
-   **`close()`**: Disconnects from the WebSocket server and shuts down the event loop.