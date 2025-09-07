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
from .md import parse_markdown

class MaxAPI:
    """
    A Python wrapper for the Max Messenger WebSocket API, powered by Tornado.
    The public interface remains synchronous and blocking for user convenience.
    """

    OPCODE_MAP = {
        'HEARTBEAT': 1,
        'HANDSHAKE': 6,
        'AUTHENTICATE': 19,
        'GET_CONTACT_DETAILS': 32,
        'FIND_BY_PHONE_NUMBER': 46,
        'GET_HISTORY': 49,
        'MARK_AS_READ': 50,
        'SEND_MESSAGE': 64,
        'SUBSCRIBE_TO_CHAT': 75,
    }

    def __init__(self, auth_token: str, on_event=None):
        """
        Initializes the MaxAPI instance.
        This constructor will block until the connection is established and authenticated.
        
        Args:
            auth_token (str): The authentication token for the session.
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

        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        self.logger = logging.getLogger("MaxAPI")

        self._start_ioloop()
        
        is_ready = self.ready_event.wait(timeout=20)
        if not is_ready or not self.is_running:
            failure_reason = "Failed to connect and authenticate within the timeout period."
            if not self.is_running:
                failure_reason = "Connection failed during initialization."
            self.close()
            raise TimeoutError(failure_reason)

    def _signal_handler(self, signum, frame):
        self.logger.info(f"\nSignal {signum} received, initiating shutdown...")
        self.close()

    def _default_on_event(self, event_data):
        opcode = event_data.get("opcode")
        if opcode == 128:
            self.logger.info(f"\n[New Message Received] Event: {json.dumps(event_data, indent=2, ensure_ascii=False)}\n")
        elif opcode is not None:
            self.logger.info(f"\n[Server Event Received] Event (Opcode {opcode}): {json.dumps(event_data, indent=2, ensure_ascii=False)}\n")
        else:
            self.logger.info(f"\n[Unknown Event Received] Event: {json.dumps(event_data, indent=2, ensure_ascii=False)}\n")

    def _start_ioloop(self):
        if self.ioloop_thread is not None: return
        self.ioloop = tornado.ioloop.IOLoop()
        self.ioloop_thread = threading.Thread(target=self.ioloop.start, daemon=True)
        self.ioloop.add_callback(self._connect_and_run)
        self.ioloop_thread.start()

    @tornado.gen.coroutine
    def _connect_and_run(self):
        """Main async task: connects, launches listener, authenticates, and signals readiness."""
        while True:
            try:
                self.logger.info("Connecting...")
                self.ws = yield tornado.websocket.websocket_connect(self.ws_url)
                self.is_running = True
                self.logger.info("Connected to WebSocket.")
                self.ioloop.add_callback(self._listener_loop_async)
                yield self._handshake_async()
                yield self._authenticate_async()

                self.heartbeat_callback = tornado.ioloop.PeriodicCallback(self._send_heartbeat, 5000)
                self.heartbeat_callback.start()
                self.logger.info("API is online and ready.")
                self.ready_event.set()
                break
            except Exception as e:
                self.logger.warning(f"Connection failed: {e}. Retrying in 5 seconds...")
                yield tornado.gen.sleep(5)
        
    @tornado.gen.coroutine
    def _listener_loop_async(self):
        """Asynchronously listens for all incoming messages."""
        try:
            while self.is_running:
                message = yield self.ws.read_message()
                if message is None:
                    if self.is_running:
                        self.logger.warning("Connection closed by server.")
                    break
                self._process_message(message)
        except tornado.websocket.WebSocketClosedError:
             if self.is_running: self.logger.warning("Listener loop terminated: WebSocket closed.")
        except Exception as e:
            if self.is_running: self.logger.error(f"An error occurred in the listener loop: {e}")
        finally:
            self.is_running = False
    
    def _process_message(self, message):
        """Processes a raw message, dispatching to sync/async waiters or event handlers."""
        try:
            data = json.loads(message)
            
            if data.get("cmd") == 1:
                seq_id = data.get("seq")
                with self.response_lock:
                    pending_request = self.pending_responses.get(seq_id)
                
                if pending_request:
                    if "event" in pending_request:
                        pending_request["response"] = data
                        pending_request["event"].set()
                    elif "future" in pending_request:
                        with self.response_lock:
                            self.pending_responses.pop(seq_id, None)
                        pending_request["future"].set_result(data)
            else:
                # This is a server-push event, not a response to a command.
                if self.on_event:
                    self.ioloop.run_in_executor(None, self.on_event, data)
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")

    def close(self):
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
        if self.heartbeat_callback: self.heartbeat_callback.stop()
        if self.ws: self.ws.close()
        # Give a moment for tasks to finish before stopping the loop
        self.ioloop.call_later(0.1, self.ioloop.stop)
    
    # --- ASYNC INTERNAL COMMANDS ---

    @tornado.gen.coroutine
    def send_command_async(self, opcode: int, payload: dict, timeout: int = 10):
        """Async-native command sender for internal use. Uses Tornado Futures."""
        if not self.is_running: raise ConnectionError("Not connected.")
        
        seq_id = next(self.seq_counter)
        command = {"ver": 11, "cmd": 0, "seq": seq_id, "opcode": opcode, "payload": payload}
        
        future = tornado.gen.Future()
        with self.response_lock:
            self.pending_responses[seq_id] = {"future": future}

        try:
            yield self.ws.write_message(json.dumps(command))
            # The async future handler in _process_message already pops, so this is clean.
            response = yield tornado.gen.with_timeout(
                self.ioloop.time() + timeout,
                future
            )
            raise tornado.gen.Return(response)
        except tornado.gen.TimeoutError:
            # Cleanup on timeout
            with self.response_lock:
                self.pending_responses.pop(seq_id, None)
            raise TimeoutError(f"Async request (opcode: {opcode}, seq: {seq_id}) timed out.")

    @tornado.gen.coroutine
    def _handshake_async(self):
        self.logger.info("Performing handshake...")
        payload = {"userAgent": self.user_agent, "deviceId":"asd"}
        yield self.send_command_async(self.OPCODE_MAP['HANDSHAKE'], payload)
        self.logger.info("Handshake successful.")

    @tornado.gen.coroutine
    def _authenticate_async(self):
        self.logger.info("Authenticating...")
        payload = {
            "interactive": True, "token": self.token,
            "chatsSync": 0, "contactsSync": 0, "presenceSync": 0,
            "draftsSync": 0, "chatsCount": 50
        }
        response = yield self.send_command_async(self.OPCODE_MAP['AUTHENTICATE'], payload)
        response = response['payload']
        self.logger.info(f"Authentication successful. User: {response['profile']['contact']['names'][0]['name']}")
        self.user = response['profile']
        chats = {}
        for item in response['chats']:
            item_id = str(item.get('id'))
            new_item = item.copy()
            del new_item['id']
            chats[item_id] = new_item
        self.chats = chats

    @tornado.gen.coroutine
    def _send_heartbeat(self):
        if not self.is_running: return
        try:
            # Heartbeat doesn't need a response, so wait_for_response=False is correct
            self.send_command(self.OPCODE_MAP['HEARTBEAT'], {"interactive": False}, wait_for_response=False)
        except tornado.websocket.WebSocketClosedError:
            self.logger.warning("Heartbeat failed: WebSocket is closed.")
            self.is_running = False
        except Exception as e:
            # Catch other potential errors during send
            if self.is_running:
                self.logger.error(f"Heartbeat failed with error: {e}")
                self.is_running = False

    def send_command(self, opcode: int, payload: dict, wait_for_response: bool = True, timeout: int = 10):
        """Synchronous bridge to the async world for external callers with retries."""
        max_attempts = 3
        attempt = 0
        while attempt < max_attempts:
            attempt += 1
            if not self.is_running:
                self._reconnect()
                if not self.is_running:
                    raise ConnectionError("Unable to reconnect to WebSocket.")
            try:
                seq_id = next(self.seq_counter)
                command = {"ver": 11, "cmd": 0, "seq": seq_id, "opcode": opcode, "payload": payload}
                if not wait_for_response:
                    self.ioloop.add_callback(self.ws.write_message, json.dumps(command))
                    return None
                event = threading.Event()
                with self.response_lock:
                    self.pending_responses[seq_id] = {"event": event, "response": None}
                self.ioloop.add_callback(self.ws.write_message, json.dumps(command))
                is_set = event.wait(timeout)
                with self.response_lock:
                    pending_request = self.pending_responses.pop(seq_id, None)
                if not is_set:
                    raise TimeoutError(f"Request (opcode: {opcode}, seq: {seq_id}) timed out after {timeout} seconds.")
                if not pending_request:
                    raise RuntimeError(f"Response for request (seq: {seq_id}) was lost.")
                return pending_request.get("response")
            except (ConnectionError, tornado.websocket.WebSocketClosedError):
                self._reconnect()
            except Exception:
                if attempt == max_attempts:
                    raise
                # Small delay before retrying
                time.sleep(1)

    def _reconnect(self):
        self.logger.info("Attempting to reconnect to WebSocket...")
        self.close()
        self._start_ioloop()
        # Wait for re-initialization
        if not self.ready_event.wait(timeout=10):
            self.is_running = False
            raise ConnectionError("Failed to reconnect after multiple attempts.")

    # --- Public API Methods (Interface remains unchanged) ---
    def send_message(self, chat_id: int, text: str, reply_id: int | None = None, wait_for_response: bool = False, format: bool = False):
        client_message_id = int(time.time() * 1000)

        payload = {
            "chatId": chat_id,
            "message": {"text": text, "cid": client_message_id, "elements": [], "attaches": []},
            "notify": True
        }

        if reply_id:
            payload["message"]["link"] = {
                "type": "REPLY",
                "messageId": reply_id
            }
        if format:
            payload["message"]["elements"], payload["message"]["text"] = parse_markdown(text)
        
        self.logger.info(f"Sent message to chat {chat_id} with cid {client_message_id}")
        return self.send_command(self.OPCODE_MAP['SEND_MESSAGE'], payload, wait_for_response=wait_for_response)

    def get_history(self, chat_id: int, count: int = 30, from_timestamp: int = None):
        if from_timestamp is None: from_timestamp = int(time.time() * 1000)
        payload = {"chatId": chat_id, "from": from_timestamp, "forward": 0, "backward": count, "getMessages": True}
        return self.send_command(self.OPCODE_MAP['GET_HISTORY'], payload)

    def subscribe_to_chat(self, chat_id: int, subscribe: bool = True):
        payload = {"chatId": chat_id, "subscribe": subscribe}
        status = "Subscribed to" if subscribe else "Unsubscribed from"
        response = self.send_command(self.OPCODE_MAP['SUBSCRIBE_TO_CHAT'], payload)
        self.logger.info(f"{status} chat {chat_id}")
        return response

    def mark_as_read(self, chat_id: int, message_id: str):
        payload = {"type": "READ_MESSAGE", "chatId": chat_id, "messageId": message_id, "mark": int(time.time() * 1000)}
        return self.send_command(self.OPCODE_MAP['MARK_AS_READ'], payload)
    
    def get_contact_details(self, contact_ids: list):
        payload = {"contactIds": contact_ids}
        return self.send_command(self.OPCODE_MAP['GET_CONTACT_DETAILS'], payload)
    
    def get_contact_by_phone(self, phone_number: str):
        payload = {"phone": phone_number}
        return self.send_command(self.OPCODE_MAP['FIND_BY_PHONE_NUMBER'], payload)
    
    def get_chat_by_id(self, chat_id: str):
        return self.chats.get(chat_id)
    
    def get_all_chats(self):
        return self.chats
    
    def send_generic_command(self, command_name: str, payload: dict, wait_for_response: bool = True, timeout: int = 10):
        command_name_upper = command_name.upper()
        if command_name_upper not in self.OPCODE_MAP:
            raise ValueError(f"Unknown command name '{command_name}'. Valid names are: {list(self.OPCODE_MAP.keys())}")
        opcode = self.OPCODE_MAP[command_name_upper]
        return self.send_command(opcode, payload, wait_for_response, timeout)
    
    def get_video(self, id):
        video_info = self.send_command(83, {"videoId": id, "token": self.token})
        video_info = video_info['payload']
        url = video_info.get('MP4_1080') or video_info.get('MP4_720')
        if not url: return None

        headers = {
            'Host': 'vd526.okcdn.ru',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0',
            'Accept': 'video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'video',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'cross-site',
        }
        
        cookies = { 'tstc': 'p' }

        with requests.get(url, headers=headers, cookies=cookies, stream=True, timeout=30) as r:
            r.raise_for_status()

            content_type = r.headers.get('content-type')
            if 'video' not in content_type:
                return None
            
            video_buffer = io.BytesIO()
            
            for chunk in r.iter_content(chunk_size=8192):
                video_buffer.write(chunk)
            
            video_buffer.seek(0)

        return video_buffer
    
    def get_file(self, id, chat_id, msg_id):
        file_info = self.send_command(88, {"fileId": id, "chatId": chat_id, "messageId": msg_id})
        file_info = file_info['payload']
        url = file_info.get('url')
        if not url: return None

        with requests.get(url, timeout=30) as r:
            file = r.content
            file_name = r.headers['X-File-Name']

        return file, file_name