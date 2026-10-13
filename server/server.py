import socket
import threading
from datetime import datetime
from pathlib import Path

HOST = "0.0.0.0"
PORT = 5555

# Shared dictionary:
# client socket -> username
clients = {}

# Lock protects the shared clients dictionary because multiple
# client threads can access it at the same time.
lock = threading.Lock()

LOG_FILE = Path(__file__).resolve().parent / "chat.log"


def get_timestamp():
    """Return the current time in HH:MM:SS format."""
    return datetime.now().strftime("%H:%M:%S")


def log_event(message):
    """Append an event to the server log file."""
    timestamp = get_timestamp()

    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] {message}\n")


def send_message(client, message):
    """Send a UTF-8 message to one client."""
    try:
        client.send(message.encode("utf-8"))
    except (ConnectionResetError, BrokenPipeError, OSError):
        pass


def broadcast(message, exclude=None):
    """Send a message to all connected clients except 'exclude'."""
    with lock:
        connected_clients = list(clients.keys())

    for client in connected_clients:
        if client != exclude:
            send_message(client, message)


def get_online_users():
    """Return a list of usernames currently connected."""
    with lock:
        return list(clients.values())


def handle_command(client, username, message):
    """Handle commands beginning with '/'.

    Returns False when the client should disconnect.
    Returns True otherwise.
    """
    parts = message.split(" ", 2)
    command = parts[0].lower()

    # /quit
    if command == "/quit":
        send_message(client, "Goodbye!")
        log_event(f"{username} used /quit")
        return False

    # /users
    elif command == "/users":
        users = get_online_users()

        if users:
            send_message(
                client,
                "Online users: " + ", ".join(users)
            )
        else:
            send_message(client, "No users are online.")

        log_event(f"{username} requested online users")

    # /help
    elif command == "/help":
        help_message = """
================ CHAT COMMANDS ================

/help
    Show available commands.

/users
    Show currently online users.

/name
    Show your username.

/msg <username> <message>
    Send a private message.

/clear
    Clear your terminal.

/quit
    Leave the chat.

=================================================
"""
        send_message(client, help_message)
        log_event(f"{username} requested help")

    # /name
    elif command == "/name":
        send_message(
            client,
            f"Your username is: {username}"
        )
        log_event(f"{username} requested their username")

    # /msg
    elif command == "/msg":
        if len(parts) < 3:
            send_message(
                client,
                "Usage: /msg <username> <message>"
            )
            return True

        target_username = parts[1]
        private_message = parts[2]

        target_client = None

        with lock:
            for connected_client, connected_username in clients.items():
                if connected_username.lower() == target_username.lower():
                    target_client = connected_client
                    break

        if target_client:
            timestamp = get_timestamp()

            send_message(
                target_client,
                f"[{timestamp}] [Private] {username}: {private_message}"
            )

            send_message(
                client,
                f"[{timestamp}] [Private -> {target_username}] {private_message}"
            )

            log_event(
                f"PRIVATE {username} -> {target_username}: {private_message}"
            )
        else:
            send_message(
                client,
                f"User '{target_username}' is not online."
            )

    # Unknown command
    else:
        send_message(
            client,
            "Unknown command. Type /help for available commands."
        )

    return True


def remove_client(client):
    """Remove a client from the connected-client list and close it."""
    with lock:
        if client not in clients:
            return None

        username = clients.pop(client)

    try:
        client.close()
    except OSError:
        pass

    print(f"{username} disconnected.")
    log_event(f"{username} disconnected")

    return username


def handle_client(client, address):
    """Handle one connected client."""
    username = None

    try:
        # Receive username
        username = client.recv(1024).decode("utf-8").strip()

        if not username:
            send_message(client, "ERROR: Username cannot be empty.")
            client.close()
            return

        # Check duplicate usernames and register the client
        with lock:
            existing_users = [
                name.lower()
                for name in clients.values()
            ]

            if username.lower() in existing_users:
                send_message(
                    client,
                    "ERROR: Username already taken."
                )
                client.close()
                log_event(
                    f"Rejected duplicate username '{username}' from {address}"
                )
                return

            clients[client] = username

        print(f"{username} connected from {address}")
        log_event(f"{username} connected from {address}")

        # Welcome the new client
        send_message(
            client,
            f"Welcome {username}!"
        )

        send_message(
            client,
            "Type /help to see available commands."
        )

        # Notify all other clients
        timestamp = get_timestamp()
        broadcast(
            f"[{timestamp}] *** {username} joined the chat! ***",
            exclude=client
        )

        # Receive messages
        while True:
            data = client.recv(1024)

            if not data:
                break

            message = data.decode("utf-8").strip()

            if not message:
                continue

            # Commands
            if message.startswith("/"):
                should_continue = handle_command(
                    client,
                    username,
                    message
                )

                if not should_continue:
                    break

            # Normal message
            else:
                timestamp = get_timestamp()

                print(f"[{timestamp}] {username}: {message}")
                log_event(f"{username}: {message}")

                broadcast(
                    f"[{timestamp}] {username}: {message}",
                    exclude=client
                )

    except ConnectionResetError:
        print(f"Connection reset by {address}")
        log_event(f"Connection reset by {address}")

    except (BrokenPipeError, OSError) as error:
        print(f"Connection error with {address}: {error}")
        log_event(f"Connection error with {address}: {error}")

    except Exception as error:
        print(f"Unexpected error with {address}: {error}")
        log_event(f"Unexpected error with {address}: {error}")

    finally:
        removed_username = remove_client(client)

        if removed_username:
            timestamp = get_timestamp()

            broadcast(
                f"[{timestamp}] *** {removed_username} left the chat. ***"
            )


def receive_connections():
    """Accept incoming connections and create a thread for each client."""
    while True:
        try:
            client, address = server.accept()

            print(f"New connection from {address}")
            log_event(f"New connection from {address}")

            thread = threading.Thread(
                target=handle_client,
                args=(client, address),
                daemon=True
            )

            thread.start()

            active_connections = threading.active_count() - 1
            print(f"Active client threads: {active_connections}")

        except OSError:
            break


# Create TCP server socket
server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

# Allow the port to be reused quickly after restarting the server
server.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

server.bind((HOST, PORT))
server.listen()

print("=" * 50)
print("        NETWORK CHAT SERVER")
print("=" * 50)
print(f"Server started on port {PORT}")
print("Waiting for clients...")
print("Press Ctrl+C to stop the server.")
print("=" * 50)

log_event(f"Server started on {HOST}:{PORT}")

try:
    receive_connections()

except KeyboardInterrupt:
    print("\nServer shutting down...")
    log_event("Server stopped by administrator")

finally:
    with lock:
        connected_clients = list(clients.keys())

    for client in connected_clients:
        try:
            client.close()
        except OSError:
            pass

    server.close()
    print("Server closed.")
