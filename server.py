# ============================================================
#  server.py  --  Multi-threaded TCP Chat Server
#  CN Chat -- Computer Networks Course Project
# ============================================================

import socket
import threading
import datetime
import sys
from config import (
    HOST, PORT, MAX_CLIENTS, BUFFER_SIZE, ENCODING,
    TAG_JOIN, TAG_LEAVE, TAG_MSG, TAG_SERVER, TAG_ERROR, TAG_USERLIST, TAG_PT,
    SEPARATOR, APP_TITLE, SERVER_NAME
)

# -- Global State ---------------------------------------------
clients = {}                     # {socket: username}
clients_lock = threading.Lock()  # Thread-safe access to clients dict


# -- Helpers --------------------------------------------------

def timestamp() -> str:
    """Return current time as a formatted string."""
    return datetime.datetime.now().strftime("%H:%M:%S")


def log(msg: str) -> None:
    """Print a server-side log message with timestamp."""
    print(f"[{timestamp()}] {msg}")


def broadcast(message: str, sender_socket=None) -> None:
    """
    Send a message to ALL connected clients.
    If sender_socket is provided, that client is excluded (echo prevention).
    """
    encoded = message.encode(ENCODING)
    with clients_lock:
        dead = []
        for client_sock in clients:
            if client_sock is sender_socket:
                continue
            try:
                client_sock.sendall(encoded)
            except OSError:
                dead.append(client_sock)
        # Clean up broken connections found during broadcast
        for sock in dead:
            _remove_client_locked(sock)


def send_user_list() -> None:
    """Broadcast the current online user list to all clients."""
    with clients_lock:
        names = list(clients.values())
    user_list_msg = f"{TAG_USERLIST} {', '.join(names)}"
    broadcast(user_list_msg)


def _remove_client_locked(sock) -> None:
    """
    Internal: remove a client socket from registry.
    MUST be called while clients_lock is already held.
    """
    clients.pop(sock, None)
    try:
        sock.close()
    except OSError:
        pass


# -- Client Handler Thread -------------------------------------

def handle_client(client_sock, addr: tuple) -> None:
    """
    Dedicated thread for each connected client.
    Handles: username registration -> message loop -> disconnect.
    """
    username = None
    try:
        # -- Step 1: Receive username --------------------------
        client_sock.sendall(
            (f"{TAG_SERVER} Welcome to {APP_TITLE}!\n"
             f"{TAG_SERVER} Enter your username: ").encode(ENCODING)
        )
        raw = client_sock.recv(BUFFER_SIZE)
        if not raw:
            client_sock.close()
            return

        username = raw.decode(ENCODING).strip()

        # Validate username
        if not username or len(username) > 20:
            client_sock.sendall(
                f"{TAG_ERROR} Invalid username. Disconnecting.".encode(ENCODING)
            )
            client_sock.close()
            return

        # Check for duplicate username
        with clients_lock:
            existing_names = list(clients.values())
            if username in existing_names:
                client_sock.sendall(
                    f"{TAG_ERROR} Username '{username}' already taken. Disconnecting.".encode(ENCODING)
                )
                client_sock.close()
                return
            clients[client_sock] = username

        log(f"[+] {username} joined from {addr[0]}:{addr[1]}")

        # -- Step 2: Announce & send user list -----------------
        broadcast(f"{TAG_JOIN} {username} has joined the chat!", sender_socket=client_sock)
        client_sock.sendall(
            (f"{TAG_SERVER} {SEPARATOR}\n"
             f"{TAG_SERVER} Hello {username}! You are connected.\n"
             f"{TAG_SERVER} Type your message and press Enter to send.\n"
             f"{TAG_SERVER} Type 'quit' to exit.\n"
             f"{TAG_SERVER} {SEPARATOR}").encode(ENCODING)
        )
        send_user_list()

        # -- Step 3: Message receive loop ----------------------
        while True:
            data = client_sock.recv(BUFFER_SIZE)
            if not data:
                break  # Client closed connection cleanly

            raw_text = data.decode(ENCODING).strip()
            for line in raw_text.split("\n"):
                message = line.strip()
                if not message:
                    continue

                if message.lower() == "quit":
                    return

                if message.startswith(TAG_PT):
                    pt_text = message[len(TAG_PT):].strip()
                    formatted = f"{TAG_PT} [{timestamp()}] {pt_text}"
                    log(f"  -> [PT Event]: {pt_text}")
                elif username == "PT_Bridge":
                    formatted = f"{TAG_PT} [{timestamp()}] {message}"
                    log(f"  -> [PT Event]: {message}")
                else:
                    formatted = f"{TAG_MSG} [{timestamp()}] {username}: {message}"
                    log(f"  -> {username}: {message}")

                broadcast(formatted, sender_socket=client_sock)

    except (ConnectionResetError, ConnectionAbortedError):
        if username:
            log(f"[!] {username} lost connection unexpectedly.")
    except Exception as e:
        log(f"[ERROR] handle_client: {e}")
    finally:
        with clients_lock:
            if client_sock in clients:
                _remove_client_locked(client_sock)
        if username:
            broadcast(f"{TAG_LEAVE} {username} has left the chat.")
            log(f"[-] {username} disconnected.")
            send_user_list()


# -- Server Entry Point ----------------------------------------

def start_server() -> None:
    """Initialize and run the TCP chat server."""
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allow port reuse immediately after restart
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_sock.bind((HOST, PORT))
        server_sock.listen(MAX_CLIENTS)
    except OSError as e:
        print(f"[FATAL] Could not bind to {HOST}:{PORT} - {e}")
        sys.exit(1)

    print(f"\n{SEPARATOR}")
    print(f"  {APP_TITLE}")
    print(f"{SEPARATOR}")
    log(f"Server started on {HOST}:{PORT}")
    log(f"Max clients: {MAX_CLIENTS}")
    log("Waiting for connections...\n")

    try:
        while True:
            try:
                client_sock, addr = server_sock.accept()
            except OSError:
                break  # Server was shut down

            with clients_lock:
                current_count = len(clients)

            if current_count >= MAX_CLIENTS:
                log(f"[!] Connection from {addr} rejected - server full ({MAX_CLIENTS} max).")
                try:
                    client_sock.sendall(
                        f"{TAG_ERROR} Server is full. Max {MAX_CLIENTS} clients allowed.".encode(ENCODING)
                    )
                except OSError:
                    pass
                client_sock.close()
                continue

            log(f"-> Incoming connection from {addr[0]}:{addr[1]}")
            thread = threading.Thread(
                target=handle_client,
                args=(client_sock, addr),
                daemon=True,
                name=f"client-{addr[0]}-{addr[1]}"
            )
            thread.start()

    except KeyboardInterrupt:
        log("\nServer shutting down...")
        broadcast(f"{TAG_SERVER} Server is shutting down. Goodbye!")
    finally:
        server_sock.close()
        log("Server socket closed.")


if __name__ == "__main__":
    start_server()