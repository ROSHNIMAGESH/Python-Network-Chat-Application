import os
import socket
import threading
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

HOST = "127.0.0.1"
PORT = 5555

client = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

try:
    client.connect((HOST, PORT))
except ConnectionRefusedError:
    print(Fore.RED + "Could not connect to the server.")
    print("Make sure server.py is running first.")
    raise SystemExit

username = input("Enter your username: ").strip()

while not username:
    print(Fore.YELLOW + "Username cannot be empty.")
    username = input("Enter your username: ").strip()

client.send(username.encode("utf-8"))


def receive_messages():
    """Continuously receive messages from the server."""
    while True:
        try:
            message = client.recv(1024).decode("utf-8")

            if not message:
                print(
                    Fore.RED +
                    "\nServer closed the connection."
                )
                break

            # Display server/system messages in different colors
            if "joined the chat" in message:
                print(
                    "\n" +
                    Fore.GREEN +
                    message +
                    Style.RESET_ALL
                )

            elif "left the chat" in message:
                print(
                    "\n" +
                    Fore.YELLOW +
                    message +
                    Style.RESET_ALL
                )

            elif "[Private]" in message:
                print(
                    "\n" +
                    Fore.MAGENTA +
                    message +
                    Style.RESET_ALL
                )

            elif message.startswith("Welcome"):
                print(
                    "\n" +
                    Fore.CYAN +
                    message +
                    Style.RESET_ALL
                )

            elif "ERROR:" in message:
                print(
                    "\n" +
                    Fore.RED +
                    message +
                    Style.RESET_ALL
                )

            else:
                print(
                    "\n" +
                    Fore.WHITE +
                    message +
                    Style.RESET_ALL
                )

            print("You: ", end="", flush=True)

        except (ConnectionResetError, BrokenPipeError, OSError):
            print(
                Fore.RED +
                "\nDisconnected from server."
            )
            break


def send_messages():
    """Read user input and send messages to the server."""
    while True:
        try:
            message = input("You: ").strip()

            if not message:
                continue

            # /clear is handled locally and does not go to the server
            if message.lower() == "/clear":
                os.system(
                    "cls" if os.name == "nt" else "clear"
                )
                continue

            client.send(message.encode("utf-8"))

            if message.lower() == "/quit":
                break

        except (ConnectionResetError, BrokenPipeError, OSError):
            print(
                Fore.RED +
                "\nUnable to send message. "
                "The server may be offline."
            )
            break

        except (EOFError, KeyboardInterrupt):
            print("\nLeaving chat...")
            try:
                client.send("/quit".encode("utf-8"))
            except OSError:
                pass
            break

    try:
        client.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass

    client.close()


print()
print(Fore.CYAN + "=" * 50)
print(Fore.CYAN + f"       Welcome to the Chat, {username}!")
print(Fore.CYAN + "=" * 50)
print(Fore.YELLOW + "Type /help to see available commands.")
print()

# Thread 1: receives messages while the user is typing
receive_thread = threading.Thread(
    target=receive_messages,
    daemon=True
)

receive_thread.start()

# Main thread: sends messages
send_messages()
