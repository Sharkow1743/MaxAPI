import tornado.ioloop
import tornado.websocket
import tornado.gen
import json
import time
import threading
import itertools
import signal
import requests
import io
import logging
from tornado.httpclient import HTTPRequest

# Mocking parse_markdown if not available
try:
    from .md import parse_markdown
except ImportError:
    def parse_markdown(text):
        return [], text

class MaxAPI:
    """
    Python api wrapper for max messenger
    """

    OPCODE_MAP = {
        'HEARTBEAT': 1,
        'HANDSHAKE': 6,
        'SEND_VERIFY_CODE': 17,
        'CHECK_VERIFY_CODE': 18,
        'AUTHENTICATE': 19,
        'AUTH_CONFIRM': 20, # Added for registration
        'GET_CONTACT_DETAILS': 32,
        'FIND_BY_PHONE_NUMBER': 46,
        'GET_HISTORY': 49,
        'MARK_AS_READ': 50,
        'SEND_MESSAGE': 64,
        'SUBSCRIBE_TO_CHAT': 75,
    }

    def __init__(self, auth_token: str = None, on_event=None):
        """
        Initializes the MaxAPI instance.
        
        Args:
            auth_token (str, optional): The authentication token for the session. If provided,
                                        the API will connect and authenticate automatically.
                                        If not provided, the API will connect and wait for
                                        manual authentication via send_verify_code and check_verify_code.
            on_event (callable, optional): A callback function to handle server-push events.
                                           It receives one argument: the event data dictionary.
        """
        self.token = auth_token
        self.ws_url = "wss://ws-api.oneme.ru/websocket"
        self.user_agent = {
            "deviceType": "WEB", "locale": "ru", "deviceLocale": "ru",
            "osVersion": "Windows", "deviceName": "Firefox",
            "headerUserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0",
            "appVersion": "25.7.13", "screen": "1080x1920 1.0x", "timezone": "Asia/Novosibirsk"
        }
        self.user = None
        self.chats = {}
        self.subscribed_chats = set()

        self.ws = None
        self.ioloop = None
        self.ioloop_thread = None
        self.heartbeat_callback = None
        
        self.is_running = False
        self.seq_counter = itertools.count()

        self.response_lock = threading.Lock()
        self.pending_responses = {}
        self.ready_event = threading.Event()

        self.on_event = on_event if callable(on_event) else self._default_on_event

        try:
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
        except ValueError:
            pass

        self.logger = logging.getLogger("MaxAPI")

        self._start_ioloop()
        
        is_ready = self.ready_event.wait(timeout=20)
        if not is_ready:
            self.close()
            raise TimeoutError("Failed to connect to WebSocket within the timeout period.")

    def _signal_handler(self, signum, frame):
        """Handles termination signals for graceful shutdown."""
        self.logger.info(f"\nSignal {signum} received, initiating shutdown...")
        self.close()

    def _default_on_event(self, event_data):
        """
        Default event handler that logs incoming server events.
        
        Args:
            event_data (dict): The event data received from the server.
        """
        opcode = event_data.get("opcode")
        if opcode == 128:
            self.logger.info(f"\n[New Message Received] Event: {json.dumps(event_data, indent=2, ensure_ascii=False)}\n")
        elif opcode is not None:
            self.logger.info(f"\n[Server Event Received] Event (Opcode {opcode}): {json.dumps(event_data, indent=2, ensure_ascii=False)}\n")
        else:
            self.logger.info(f"\n[Unknown Event Received] Event: {json.dumps(event_data, indent=2, ensure_ascii=False)}\n")

    def _start_ioloop(self):
        """Starts the Tornado I/O loop in a separate thread."""
        if self.ioloop_thread is not None: return
        self.ioloop = tornado.ioloop.IOLoop()
        self.ioloop_thread = threading.Thread(target=self.ioloop.start, daemon=True)
        self.ioloop.add_callback(self._connect_and_run)
        self.ioloop_thread.start()

    @tornado.gen.coroutine
    def _connect_and_run(self):
        """Establishes the initial WebSocket connection and runs the main loop."""
        while True:
            try:
                self.logger.info('Connecting...')
                request = HTTPRequest(
                    url=self.ws_url,
                    headers={
                        "Origin": "https://web.max.ru",
                        "User-Agent": self.user_agent["headerUserAgent"],
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "websocket",
                        "Sec-Fetch-Site": "cross-site",
                    }
                )
                self.ws = yield tornado.websocket.websocket_connect(request)
                self.is_running = True
                self.logger.info("Connected to WebSocket.")
                self.ioloop.add_callback(self._listener_loop_async)
                yield self._handshake_async()
                
                if self.token:
                    yield self._authenticate_async()
                    self.logger.info("API is online and ready.")
                else:
                    self.logger.info("API is connected. Please authenticate using verification code methods.")

                self.heartbeat_callback = tornado.ioloop.PeriodicCallback(self._send_heartbeat, 3000)
                self.heartbeat_callback.start()
                
                self.ready_event.set()
                break
            except Exception as e:
                self.logger.warning(f"Connection failed: {e}. Retrying in 5 seconds...")
                yield tornado.gen.sleep(5)
        
    @tornado.gen.coroutine
    def _listener_loop_async(self):
        """Asynchronously listens for messages from the WebSocket."""
        try:
            while self.is_running:
                message = yield self.ws.read_message()
                if message is None:
                    if self.is_running:
                        self.logger.warning("Connection closed by server. Attempting to reconnect...")
                        yield self._reconnect_async()
                    break
                self._process_message(message)
        except tornado.websocket.WebSocketClosedError:
            if self.is_running:
                self.logger.warning("Listener loop terminated: WebSocket closed by server. Reconnecting...")
                yield self._reconnect_async()
        except Exception as e:
            if self.is_running:
                self.logger.error(f"An error occurred in the listener loop: {e}")
                yield self._reconnect_async()
        finally:
            self.is_running = False

    @tornado.gen.coroutine
    def _reconnect_async(self):
        """Handles the reconnection logic when the connection is lost."""
        self.is_running = False
        if self.heartbeat_callback: self.heartbeat_callback.stop()

        if self.ws:
            try: self.ws.close()
            except: pass

        yield tornado.gen.sleep(2)

        try:
            self.logger.info('Reconnecting...')
            request = HTTPRequest(
                url=self.ws_url,
                headers={
                    "Origin": "https://web.max.ru",
                    "User-Agent": self.user_agent["headerUserAgent"],
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "websocket",
                    "Sec-Fetch-Site": "cross-site",
                }
            )
            self.ws = yield tornado.websocket.websocket_connect(request)
            self.is_running = True
            self.logger.info("Reconnected to WebSocket.")
            self.ioloop.add_callback(self._listener_loop_async)
            yield self._handshake_async()

            if self.token:
                yield self._authenticate_async()
                self.logger.info("Re-authenticated successfully.")

            if self.heartbeat_callback: self.heartbeat_callback.start()

            for chat_id in self.subscribed_chats:
                try:
                    yield self.send_command_async(self.OPCODE_MAP['SUBSCRIBE_TO_CHAT'], {"chatId": int(chat_id), "subscribe": True})
                    self.logger.debug(f"Resubscribed to chat {chat_id}")
                except Exception as e:
                    self.logger.warning(f"Failed to resubscribe to chat {chat_id}: {e}")

            self.logger.info("Reconnection and re-authentication complete.")
        except Exception as e:
            self.logger.error(f"Reconnection failed: {e}. Will retry in 5 seconds...")
            yield tornado.gen.sleep(5)
            if self.is_running:
                yield self._reconnect_async()
    
    def _process_message(self, message):
        """
        Processes incoming WebSocket messages.
        
        Args:
            message (str): The raw message string from the WebSocket.
        """
        try:
            data = json.loads(message)

            match data.get("cmd"):
                case 1:
                    seq_id = data.get("seq")
                    with self.response_lock:
                        pending_request = self.pending_responses.get(seq_id)
                    
                    if pending_request:
                        original_opcode = pending_request.get("opcode")
                        if original_opcode != self.OPCODE_MAP['HEARTBEAT']:
                            self.logger.debug(f"API Response (for Opcode {original_opcode}, Seq {seq_id}): {json.dumps(data, ensure_ascii=False)}")

                        if "event" in pending_request:
                            pending_request["response"] = data
                            pending_request["event"].set()
                        elif "future" in pending_request:
                            with self.response_lock:
                                self.pending_responses.pop(seq_id, None)
                            pending_request["future"].set_result(data)
                case 0:
                    if self.on_event:
                        self.ioloop.run_in_executor(None, self.on_event, data)
                case 3:
                    self.logger.error(f"Received API error: {json.dumps(data, indent=4, ensure_ascii=False)}")
                case _:
                    self.logger.debug(f"Received unexpected API response: {json.dumps(data, indent=4, ensure_ascii=False)}")
                    
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")

    def close(self):
        """
        Closes the WebSocket connection and stops the I/O loop.
        """
        if not self.is_running and self.ioloop is None: return
        self.logger.info("Closing connection...")
        self.is_running = False

        if self.ioloop:
            self.ioloop.add_callback(self._shutdown_async)

        if self.ioloop_thread and self.ioloop_thread.is_alive():
            self.ioloop_thread.join(timeout=5)
        
        self.ioloop = None
        self.ioloop_thread = None
        self.logger.info("Connection closed.")

    @tornado.gen.coroutine
    def _shutdown_async(self):
        """Asynchronously shuts down the WebSocket and I/O loop."""
        if self.heartbeat_callback: self.heartbeat_callback.stop()
        if self.ws: self.ws.close()
        self.ioloop.call_later(0.1, self.ioloop.stop)
    
    @tornado.gen.coroutine
    def send_command_async(self, opcode: int, payload: dict, timeout: int = 10):
        """
        Sends a command to the WebSocket API asynchronously.

        Args:
            opcode (int): The operation code for the command.
            payload (dict): The payload for the command.
            timeout (int, optional): The timeout in seconds. Defaults to 10.

        Returns:
            dict: The response from the server.
        """
        if not self.is_running: raise ConnectionError("Not connected.")
        
        seq_id = next(self.seq_counter)
        command = {"ver": 11, "cmd": 0, "seq": seq_id, "opcode": opcode, "payload": payload}
        
        future = tornado.gen.Future()
        with self.response_lock:
            self.pending_responses[seq_id] = {"future": future, "opcode": opcode}

        try:
            yield self.ws.write_message(json.dumps(command))
            response = yield tornado.gen.with_timeout(
                self.ioloop.time() + timeout,
                future
            )
            raise tornado.gen.Return(response)
        except tornado.gen.TimeoutError:
            with self.response_lock:
                self.pending_responses.pop(seq_id, None)
            raise TimeoutError(f"Async request (opcode: {opcode}, seq: {seq_id}) timed out.")

    @tornado.gen.coroutine
    def _handshake_async(self):
        """Performs the initial handshake with the WebSocket server."""
        self.logger.info("Performing handshake...")
        payload = {"userAgent": self.user_agent, "deviceId":"asd"}
        yield self.send_command_async(self.OPCODE_MAP['HANDSHAKE'], payload)
        self.logger.info("Handshake successful.")

    @tornado.gen.coroutine
    def _authenticate_async(self):
        """Authenticates the session using the provided token."""
        self.logger.info("Authenticating...")
        if not self.token:
            self.logger.error("Authentication failed: No token available.")
            return

        payload = {
            "interactive": True, "token": self.token,
            "chatsSync": 0, "contactsSync": 0, "presenceSync": 0,
            "draftsSync": 0, "chatsCount": 50
        }
        response = yield self.send_command_async(self.OPCODE_MAP['AUTHENTICATE'], payload)
        
        response_payload = response.get('payload', {})
        if response_payload.get('error'):
             raise ValueError(f"Auth Error: {response_payload.get('error')}")

        self.logger.info(f"Authentication successful. User: {response_payload['profile']['contact']['names'][0]['name']}")
        self.user = response_payload['profile']['contact']
        
        chats = {}
        if 'chats' in response_payload:
            for item in response_payload['chats']:
                item_id = str(item.get('id'))
                new_item = item.copy()
                del new_item['id']
                chats[item_id] = new_item
        self.chats = chats

    @tornado.gen.coroutine
    def _send_heartbeat(self):
        """Sends a heartbeat to keep the connection alive."""
        if not self.is_running: return
        try:
            self.ioloop.add_callback(self.ws.write_message, json.dumps({
                "ver": 11, "cmd": 0, "seq": next(self.seq_counter),
                "opcode": self.OPCODE_MAP['HEARTBEAT'],
                "payload": {"interactive": False}
            }))
        except tornado.websocket.WebSocketClosedError:
            self.logger.warning("Heartbeat failed: WebSocket is closed.")
            self.is_running = False
        except Exception as e:
            if self.is_running:
                self.logger.error(f"Heartbeat failed with error: {e}")
                self.is_running = False

    def send_command(self, opcode: int, payload: dict, wait_for_response: bool = True, timeout: int = 10):
        """
        Sends a command to the WebSocket API and waits for a response.

        Args:
            opcode (int): The operation code for the command.
            payload (dict): The payload for the command.
            wait_for_response (bool, optional): If True, waits for a response. Defaults to True.
            timeout (int, optional): The timeout in seconds. Defaults to 10.

        Returns:
            dict or None: The response from the server, or None if wait_for_response is False.
        """
        if not self.is_running:
            raise ConnectionError("Not connected. Cannot send command.")
        
        seq_id = next(self.seq_counter)
        command = {"ver": 11, "cmd": 0, "seq": seq_id, "opcode": opcode, "payload": payload}
        
        if not wait_for_response:
            self.ioloop.add_callback(self.ws.write_message, json.dumps(command))
            return None
            
        event = threading.Event()
        with self.response_lock:
            self.pending_responses[seq_id] = {"event": event, "response": None, "opcode": opcode}
            
        self.ioloop.add_callback(self.ws.write_message, json.dumps(command))
        
        is_set = event.wait(timeout)
        
        with self.response_lock:
            pending_request = self.pending_responses.pop(seq_id, None)
            
        if not is_set:
            raise TimeoutError(f"Request (opcode: {opcode}, seq: {seq_id}) timed out after {timeout} seconds.")
        if not pending_request:
            raise RuntimeError(f"Response for request (seq: {seq_id}) was lost.")
            
        return pending_request.get("response")

    def _finalize_authentication(self):
        """Helper to run the async authentication sequence from a sync context."""
        auth_event = threading.Event()
        auth_result = [None]

        def _run_authenticate():
            try:
                future = self._authenticate_async()
                self.ioloop.add_future(future, lambda f: auth_event.set())
            except Exception as e:
                auth_result[0] = e
                auth_event.set()

        self.ioloop.add_callback(_run_authenticate)
        auth_event.wait()
        if auth_result[0] is not None:
            raise auth_result[0]
        
        self.logger.info("API is online and ready.")

    # --- Public API Methods ---

    def auth(self, phone: str, first_name: str = "New", last_name: str = "User"):
        """
        Initiates the authentication process.
        
        Args:
            phone (str): The phone number (e.g., "+123456789").
            first_name (str): First name to use IF registration is required.
            last_name (str): Last name to use IF registration is required.

        Returns:
            function: A function that accepts the SMS code string.
                      Calling this function will complete login OR registration automatically.
        """
        self.send_verify_code(phone)

        def verify_code_wrapper(code: str):
            """
            Inner function to verify code. 
            Handles both existing users (Login) and new users (Register).
            """
            result = self.check_verify_code(code)

            # Check if check_verify_code determined that registration is needed
            if isinstance(result, dict) and result.get('status') == 'register':
                self.logger.info("User not found, proceeding to registration.")
                reg_token = result['token']
                # Automatically submit registration with provided names
                return self.submit_registration(first_name, last_name, reg_token)
            
            # If result is a string, it's the token, meaning we are logged in
            return result

        return verify_code_wrapper

    def send_message(self, chat_id: str, text: str, reply_id: str = None, wait_for_response: bool = False, format: bool = False):
        """
        Sends a message to a specific chat.

        Args:
            chat_id (str): The ID of the chat.
            text (str): The message content.
            reply_id (str, optional): The ID of the message to reply to. Defaults to None.
            wait_for_response (bool, optional): If True, waits for a server response. Defaults to False.
            format (bool, optional): If True, parses Markdown formatting. Defaults to False.

        Returns:
            dict or None: The server response if wait_for_response is True, otherwise None.
        """
        client_message_id = int(time.time() * 1000)

        payload = {
            "chatId": int(chat_id),
            "message": {"text": text, "cid": client_message_id, "elements": [], "attaches": []},
            "notify": True
        }

        if reply_id:
            payload["message"]["link"] = {
                "type": "REPLY",
                "messageId": int(reply_id)
            }
        if format:
            payload["message"]["elements"], payload["message"]["text"] = parse_markdown(text)
        
        self.logger.info(f"Sent message to chat {chat_id} with cid {client_message_id}")
        return self.send_command(self.OPCODE_MAP['SEND_MESSAGE'], payload, wait_for_response=wait_for_response)

    def get_history(self, chat_id: str, count: int = 30, from_timestamp: int = None):
        """
        Retrieves the message history for a chat.

        Args:
            chat_id (str): The ID of the chat.
            count (int, optional): The number of messages to retrieve. Defaults to 30.
            from_timestamp (int, optional): The timestamp to start fetching from. Defaults to the current time.

        Returns:
            dict: The server response containing the message history.
        """
        if from_timestamp is None: from_timestamp = int(time.time() * 1000)
        payload = {"chatId": int(chat_id), "from": from_timestamp, "forward": 0, "backward": count, "getMessages": True}
        return self.send_command(self.OPCODE_MAP['GET_HISTORY'], payload)

    def subscribe_to_chat(self, chat_id: str, subscribe: bool = True):
        """
        Subscribes to or unsubscribes from a chat to receive real-time updates.

        Args:
            chat_id (str): The ID of the chat.
            subscribe (bool, optional): If True, subscribes to the chat. If False, unsubscribes. Defaults to True.

        Returns:
            dict: The server response.
        """
        payload = {"chatId": int(chat_id), "subscribe": subscribe}
        status = "Subscribed to" if subscribe else "Unsubscribed from"
        response = self.send_command(self.OPCODE_MAP['SUBSCRIBE_TO_CHAT'], payload)
        self.logger.info(f"{status} chat {chat_id}")
        if subscribe:
            self.subscribed_chats.add(chat_id)
        else:
            self.subscribed_chats.discard(chat_id)
        return response

    def mark_as_read(self, chat_id: str, message_id: str):
        """
        Marks a message in a chat as read.

        Args:
            chat_id (str): The ID of the chat.
            message_id (str): The ID of the message to mark as read.

        Returns:
            dict: The server response.
        """
        payload = {"type": "READ_MESSAGE", "chatId": int(chat_id), "messageId": message_id, "mark": int(time.time() * 1000)}
        return self.send_command(self.OPCODE_MAP['MARK_AS_READ'], payload)
    
    def get_contact_details(self, contact_ids: list[str]):
        """
        Retrieves details for a list of contacts.

        Args:
            contact_ids (list[str]): A list of contact IDs.

        Returns:
            dict: The server response containing contact details.
        """
        payload = {"contactIds": [int(cid) for cid in contact_ids]}
        return self.send_command(self.OPCODE_MAP['GET_CONTACT_DETAILS'], payload)
    
    def get_contact_by_phone(self, phone_number: str):
        """
        Finds a contact by their phone number.

        Args:
            phone_number (str): The phone number to search for.

        Returns:
            dict: The server response containing the contact's information.
        """
        payload = {"phone": phone_number}
        return self.send_command(self.OPCODE_MAP['FIND_BY_PHONE_NUMBER'], payload)
    
    def get_chat_by_id(self, chat_id: str):
        """
        Retrieves a chat from the local cache by its ID.

        Args:
            chat_id (str): The ID of the chat.

        Returns:
            dict or None: The chat object if found, otherwise None.
        """
        return self.chats.get(chat_id)
    
    def get_all_chats(self):
        """
        Returns a dictionary of all cached chats.

        Returns:
            dict: A dictionary of all chats.
        """
        return self.chats
    
    def send_verify_code(self, phone_number: str):
        """
        Sends a verification code to a phone number to initiate authentication.

        Args:
            phone_number (str): The phone number to send the code to.

        Returns:
            dict: The server response.
        """
        payload = {
            "phone": phone_number, "type": "START_AUTH", "language": "ru"
        }
        res = self.send_command(self.OPCODE_MAP['SEND_VERIFY_CODE'], payload)
        if 'payload' in res and 'token' in res['payload']:
            self.token = res['payload']['token']
            self.logger.info('Saved temp auth-token')
        return res
    
    def check_verify_code(self, code: str):
        """
        Verifies the code received via SMS to complete authentication.

        Args:
            code (str): The verification code.

        Returns:
            str or dict: The final authentication token if successful, otherwise a dictionary indicating registration is needed.
        """
        if not self.token:
            raise RuntimeError("Cannot check verification code. Please call send_verify_code first.")
        
        payload = {
            "token": self.token, "verifyCode": code, "authTokenType": "CHECK_CODE"
        }
        res = self.send_command(self.OPCODE_MAP['CHECK_VERIFY_CODE'], payload, wait_for_response=True)
        
        token_attrs = res.get('payload', {}).get('tokenAttrs', {})
        login_token = token_attrs.get('LOGIN', {}).get('token')
        register_token = token_attrs.get('REGISTER', {}).get('token')

        if login_token:
            self.token = login_token
            self.logger.info("Verification successful. Finalizing authentication...")
            self._finalize_authentication()
            return self.token
        
        elif register_token:
            self.logger.info("Verification successful, but registration is required.")
            return {"status": "register", "token": register_token}
            
        self.logger.error(f"Unknown verification response: {res}")
        raise ValueError("Failed to retrieve a valid LOGIN or REGISTER token from response.")

    def submit_registration(self, first_name: str, last_name: str, reg_token: str):
        """
        Submits registration info (First/Last Name) to complete the account creation.

        Args:
            first_name (str): The user's first name.
            last_name (str): The user's last name.
            reg_token (str): The registration token received from check_verify_code.

        Returns:
            str: The final authentication token.
        """
        self.logger.info(f"Submitting registration info for {first_name} {last_name}...")
        payload = {
            "firstName": first_name,
            "lastName": last_name,
            "token": reg_token,
        }

        res = self.send_command(self.OPCODE_MAP['AUTH_CONFIRM'], payload, wait_for_response=True)
        
        payload_data = res.get("payload", {})
        if payload_data.get("error"):
             raise ValueError(f"Registration error: {payload_data.get('error')}")

        final_token = payload_data.get("token")
        if not final_token:
            raise ValueError("Registration submitted, but no final token received.")

        self.token = final_token
        self.logger.info("Registration successful. Finalizing authentication...")
        self._finalize_authentication()
        return self.token

    def send_generic_command(self, command_name: str, payload: dict, wait_for_response: bool = True, timeout: int = 10):
        """
        Sends a raw command to the API using its string name.

        Args:
            command_name (str): The name of the command (e.g., 'SEND_MESSAGE').
            payload (dict): The payload for the command.
            wait_for_response (bool, optional): If True, waits for a response. Defaults to True.
            timeout (int, optional): The timeout in seconds. Defaults to 10.

        Returns:
            dict or None: The server response if wait_for_response is True, otherwise None.
        """
        command_name_upper = command_name.upper()
        if command_name_upper not in self.OPCODE_MAP:
            raise ValueError(f"Unknown command name '{command_name}'. Valid names are: {list(self.OPCODE_MAP.keys())}")
        opcode = self.OPCODE_MAP[command_name_upper]
        return self.send_command(opcode, payload, wait_for_response, timeout)
    
    def get_video(self, id: str):
        """
        Downloads a video by its ID.

        Args:
            id (str): The ID of the video.

        Returns:
            io.BytesIO or None: A byte stream of the video content, or None if not found.
        """
        video_info = self.send_command(83, {"videoId": int(id), "token": self.token})
        video_info = video_info['payload']
        url = video_info.get('MP4_1080') or video_info.get('MP4_720')
        if not url: return None

        headers = { 'User-Agent': self.user_agent['headerUserAgent'] }
        
        with requests.get(url, headers=headers, stream=True, timeout=30) as r:
            r.raise_for_status()
            content_type = r.headers.get('content-type')
            if 'video' not in content_type: return None
            
            video_buffer = io.BytesIO()
            for chunk in r.iter_content(chunk_size=8192):
                video_buffer.write(chunk)
            
            video_buffer.seek(0)
            return video_buffer
    
    def get_file(self, id: str, chat_id: str, msg_id: str):
        """
        Downloads a file by its ID.

        Args:
            id (str): The ID of the file.
            chat_id (str): The ID of the chat the file is in.
            msg_id (str): The ID of the message the file is in.

        Returns:
            tuple or None: A tuple containing the file content (bytes) and file name, or None if not found.
        """
        file_info = self.send_command(88, {"fileId": int(id), "chatId": int(chat_id), "messageId": str(msg_id)})
        file_info = file_info['payload']
        url = file_info.get('url')
        if not url: return None

        with requests.get(url, timeout=30) as r:
            r.raise_for_status()
            file_content = r.content
            file_name = r.headers.get('X-File-Name') or "downloaded_file"

        return file_content, file_name