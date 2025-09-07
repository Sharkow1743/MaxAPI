# Max API Interface

The Max API Interface allows you to interact with the Max Messenger WebSocket API for sending messages, retrieving histories, and subscribing to real-time events.

## Getting Started

### Prerequisites

- Python 3.x

### Installing

To install this library, run the following command in your terminal:
```bash
pip install MaxBridge
```

### Obtaining the Authentication Token

To interact with the Max API, you'll need to authenticate and obtain a long-lived authentication token (from a legitimate web session). Follow these steps:

1. Open your web browser and navigate to [Max Messenger Web Version](https://web.max.ru).
   
2. Log in to your Max account if you haven't done so already.

3. After logging in, open the Developer Tools in your web browser (right-click anywhere on the page and select "Inspect" or press `F12`).

4. Go to the "Application" tab in Developer Tools.

5. Find and click on "Local storage" in the left sidebar under the "Storage" section. Look for the cookies belonging to the `https://web.max.ru` domain.

6. Find the authentication token. This token is a value of `__oneme_auth`.

7. Copy the value of the authentication token. You'll use this value to authenticate your requests in the MaxAPI class.

## Using the Max API Interface

### Initializing the MaxAPI class

To create an instance of the MaxAPI, pass the authentication token obtained from the previous step:

```python
from MaxBridge import MaxAPI

auth_token = 'YOUR_AUTH_TOKEN_HERE'
api = MaxAPI(auth_token)
```

### Available Methods

1. **Sending a Message:**

   To send a message, use:
   ```python
   api.send_message(chat_id=12345678, text="Hello, World!")
   ```

2. **Retrieving Message History:**

   To retrieve message history, use:
   ```python
   response = api.get_history(chat_id=12345678, count=20)
   ```

3. **Subscribing to a Chat:**

   To subscribe to real-time events from a chat, use:
   ```python
   api.subscribe_to_chat(chat_id=12345678, subscribe=True)
   ```

4. **Marking Messages as Read:**

   To mark a specific message as read, use:
   ```python
   api.mark_as_read(chat_id=12345678, message_id="12345678")
   ```

5. **Getting video or file**

   To get video, use:
   ```python
   api.get_video(id=12345678)
   ```
   To get file, use:
   ```python
   api.get_file(id=12345678, chat_id=12345678, msg_id="12345678")
   ```

6. **Finding Contact by Phone Number:**

   To find a contact by their phone number, use:
   ```python
   api.get_contact_by_phone(phone_number="+12345678901")
   ```

7. **Getting Chat by ID:**

   To retrieve a specific chat by its ID, use:
   ```python
   api.get_chat_by_id(chat_id="12345678")
   ```

8. **Getting All Chats:**

   To retrieve all available chats, use:
   ```python
   api.get_all_chats()
   ```

The chat ID is required for most operations. You can obtain it from the chat URL or through other means specific to your application.