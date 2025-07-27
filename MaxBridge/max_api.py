import websocket
import json
import time
import threading
import itertools
import signal

class MaxAPI:
    """
    A Python wrapper for the Max Messenger WebSocket API.
    
    This class handles the connection, authentication, and communication
    protocol for interacting with Max Messenger.
    """

    def __init__(self, auth_token: str, on_event=None):
        """
        Initializes the MaxAPI instance.

        Args:
            auth_token (str): The long-lived authentication token obtained from a
                              legitimate web session. This is the most critical credential.
            on_event (callable, optional): A callback function that will be executed
                                           for any server-pushed events (like new messages).
                                           It receives the full event data dictionary.
        """
        self.auth_token = auth_token
        self.ws_url = "wss://ws-api.oneme.ru/websocket"
        self.user_agent = {
            "deviceType": "WEB", "locale": "ru", "deviceLocale": "ru",
            "osVersion": "Windows", "deviceName": "Firefox",
            "headerUserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0",
            "appVersion": "25.7.13", "screen": "1080x1920 1.0x", "timezone": "Asia/Novosibirsk"
        }

        self.ws = None
        self.listener_thread = None
        self.heartbeat_thread = None
        self.is_running = False
        self.seq_counter = itertools.count()
        
        # For matching requests with responses
        self.pending_responses = {}
        self.response_lock = threading.Lock()
        
        # Callback for server-pushed events
        self.on_event = on_event if callable(on_event) else self._default_on_event

        signal.signal(signal.SIGINT, self._close)
        signal.signal(signal.SIGTERM, self._close)

        self._connect()

    def _default_on_event(self, event_data):
        """Default event handler that prints new messages."""
        if event_data.get("opcode") == 128: # New message
             print(f"\n[New Message Received] Event: {json.dumps(event_data, indent=2, ensure_ascii=False)}\n")
        else:
             print(f"\n[Event Received] Event: {json.dumps(event_data, indent=2, ensure_ascii=False)}\n")

    def _connect(self):
        """Establishes the WebSocket connection, authenticates, and starts listening."""
        if self.is_running:
            print("Already connected.")
            return

        print("Connecting...")
        self.is_running = True
        self.ws = websocket.create_connection(self.ws_url)
        print("Connected to WebSocket.")

        self.listener_thread = threading.Thread(target=self._listener_loop, daemon=True)
        self.listener_thread.start()

        self._handshake()
        self._authenticate()

        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()
        print("API is online and ready.")

    def _close(self):
        """Closes the WebSocket connection and stops all background threads."""
        if not self.is_running:
            return
        
        print("Closing connection...")
        self.is_running = False
        if self.ws:
            self.ws.close()
        # Threads will exit because self.is_running is False
        print("Connection closed.")

    def _send_command(self, opcode: int, payload: dict, wait_for_response: bool = True, timeout: int = 10):
        """
        Internal method to construct and send a command to the WebSocket server.
        """
        if not self.is_running or not self.ws:
            raise ConnectionError("Not connected to WebSocket.")
            
        seq_id = next(self.seq_counter)
        command = {
            "ver": 11,
            "cmd": 0,
            "seq": seq_id,
            "opcode": opcode,
            "payload": payload
        }
        
        event = None
        if wait_for_response:
            event = threading.Event()
            with self.response_lock:
                self.pending_responses[seq_id] = {"event": event, "response": None}

        self.ws.send(json.dumps(command))

        if wait_for_response:
            is_set = event.wait(timeout)
            with self.response_lock:
                response_data = self.pending_responses.pop(seq_id, {}).get("response")
            
            if not is_set:
                raise TimeoutError(f"Request (opcode: {opcode}, seq: {seq_id}) timed out.")
            return response_data
        return None

    def _listener_loop(self):
        """Listens for incoming messages and dispatches them."""
        while self.is_running:
            try:
                message = self.ws.recv()
                data = json.loads(message)

                if data.get("cmd") == 1:  # This is a response to a command
                    seq_id = data.get("seq")
                    with self.response_lock:
                        if seq_id in self.pending_responses:
                            self.pending_responses[seq_id]["response"] = data.get("payload")
                            self.pending_responses[seq_id]["event"].set()
                else: # This is a server-pushed event (cmd: 0)
                    if self.on_event:
                        self.on_event(data)

            except (websocket.WebSocketConnectionClosedException, ConnectionResetError):
                self._connect()
            except Exception as e:
                print(f"An error occurred in the listener thread: {e}")

    def _heartbeat_loop(self):
        """Sends a heartbeat every 5 seconds to keep the connection alive."""
        while self.is_running:
            try:
                self._send_command(1, {"interactive": False})
                time.sleep(5)
            except (ConnectionError, TimeoutError, websocket.WebSocketException):
                # The main listener will handle the disconnect
                break
    
    def _handshake(self):
        """Performs the initial handshake (opcode 6)."""
        print("Performing handshake...")
        payload = {"userAgent": self.user_agent, "deviceId": ""}
        self._send_command(6, payload)
        print("Handshake successful.")

    def _authenticate(self):
        """Performs authentication and initial sync (opcode 19)."""
        print("Authenticating...")
        payload = {
            "interactive": True, "token": self.auth_token,
            "chatsSync": 0, "contactsSync": 0, "presenceSync": 0,
            "draftsSync": 0, "chatsCount": 50
        }
        response = self._send_command(19, payload)
        print(f"Authentication successful. User: {response['profile']['contact']['names'][0]['name']}")
        return response

    # --- Public API Methods ---

    def send_message(self, chat_id: int, text: str):
        """
        Sends a message to a specific chat. This is a fire-and-forget operation.
        The confirmation comes as a push event (opcode 128).

        Args:
            chat_id (int): The ID of the chat or dialog to send the message to.
            text (str): The message text.
        """
        # The 'cid' is a client-generated ID, a millisecond timestamp is perfect.
        client_message_id = int(time.time() * 1000)
        payload = {
            "chatId": chat_id,
            "message": {
                "text": text,
                "cid": client_message_id,
                "elements": [], # For markdown/formatting
                "attaches": []  # For attachments
            },
            "notify": True
        }
        # This command doesn't get a direct response, so we don't wait.
        self._send_command(64, payload, wait_for_response=False)
        print(f"Sent message to chat {chat_id} with cid {client_message_id}")

    def get_history(self, chat_id: int, count: int = 30, from_timestamp: int = None):
        """
        Retrieves the message history for a specific chat.

        Args:
            chat_id (int): The ID of the chat.
            count (int, optional): The number of messages to retrieve. Defaults to 30.
            from_timestamp (int, optional): Unix timestamp in ms to fetch messages from.
                                            Defaults to the current time.

        Returns:
            dict: The response payload containing the list of messages.
        """
        if from_timestamp is None:
            from_timestamp = int(time.time() * 1000)
            
        payload = {
            "chatId": chat_id,
            "from": from_timestamp,
            "forward": 0,
            "backward": count,
            "getMessages": True
        }
        return self._send_command(49, payload)

    def subscribe_to_chat(self, chat_id: int, subscribe: bool = True):
        """
        Subscribes or unsubscribes to real-time events from a chat.
        You must be subscribed to a chat to receive new messages.

        Args:
            chat_id (int): The ID of the chat.
            subscribe (bool, optional): True to subscribe, False to unsubscribe. Defaults to True.
        """
        payload = {"chatId": chat_id, "subscribe": subscribe}
        status = "Subscribed to" if subscribe else "Unsubscribed from"
        print(f"{status} chat {chat_id}")
        return self._send_command(75, payload)

    def mark_as_read(self, chat_id: int, message_id: str):
        """
        Marks a message and everything before it as read in a chat.

        Args:
            chat_id (int): The ID of the chat.
            message_id (str): The server-assigned ID of the message to mark as read.
        """
        payload = {
            "type": "READ_MESSAGE",
            "chatId": chat_id,
            "messageId": message_id,
            "mark": int(time.time() * 1000)
        }
        return self._send_command(50, payload)
    
    def get_contact_details(self, contact_ids: list):
        """
        Retrieves profile information for a list of contact IDs.

        Args:
            contact_ids (list): A list of integer user IDs.

        Returns:
            dict: The response payload containing a list of contact profile objects.
        """
        payload = {"contactIds": contact_ids}
        return self._send_command(32, payload)
