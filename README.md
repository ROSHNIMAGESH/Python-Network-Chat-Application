# Network Chat Application using Python

A multi-client terminal chat application built with Python TCP sockets and multithreading. The server accepts multiple clients, broadcasts public messages, routes private messages, and records activity in a log file.

## Project structure

```text
network_chat/
├── server/
│   └── server.py
├── client/
│   └── client.py
├── README.md
└── requirements.txt
```

## Features

- Multiple simultaneous clients using TCP sockets
- A dedicated thread for each connected client
- Public message broadcasting
- Private messages using `/msg username message`
- Commands: `/help`, `/users`, `/name`, `/msg`, `/clear`, and `/quit`
- Duplicate username prevention
- Join/leave notifications and timestamps
- Server activity logging to `server/chat.log`
- Basic connection and error handling
- Colored client output using Colorama

## Requirements

- Python 3.12 or another compatible Python 3 version
- `colorama` (installed from `requirements.txt`)

## Installation on Windows

Open Command Prompt or the VS Code terminal in the main `network_chat` folder. Check Python:

```bash
python --version
```

Install the dependency:

```bash
python -m pip install --user -r requirements.txt
```

Or install it directly:

```bash
python -m pip install --user colorama
```

You do not need to upgrade pip just to run this project.

## Run the application

Run each command from the main `network_chat` folder, using separate terminals.

**Terminal 1 — start the server:**

```bash
python server/server.py
```

**Terminal 2 — start the first client:**

```bash
python client/client.py
```

**Terminal 3 — start another client:**

```bash
python client/client.py
```

Enter a different username in each client. Keep the server terminal running while clients are connected. The server writes activity to `server/chat.log`.

### Connection settings

The server binds to `0.0.0.0` on TCP port `5555`, allowing local connections and connections from other devices when the network and firewall permit them. The client defaults to `127.0.0.1`, which means it connects to a server running on the same computer.

For testing across a local network, change `HOST` in `client/client.py` to the server computer's LAN IP address and allow TCP port `5555` through the firewall. Do not expose this educational server to the public internet without adding security controls.

## Commands

| Command | Description | Example |
|---|---|---|
| `/help` | Show available commands | `/help` |
| `/users` | List connected users | `/users` |
| `/name` | Show your username | `/name` |
| `/msg <username> <message>` | Send a private message | `/msg Bob Hello Bob!` |
| `/clear` | Clear your local terminal | `/clear` |
| `/quit` | Leave the chat | `/quit` |

Messages that do not start with `/` are broadcast to other connected clients.

## How it works

### TCP sockets

The server uses an IPv4 TCP socket (`socket.AF_INET`, `socket.SOCK_STREAM`), binds to port `5555`, and listens for connections. Each client connects to the server's IP address and port.

### Multithreading

The server creates a thread for each connected client. This allows the server to receive messages from multiple clients concurrently. A `threading.Lock` protects shared client information.

### Broadcasting and private messages

Public messages are sent to all connected clients except the sender. The `/msg` command sends a message to the specified online username and confirms delivery to the sender.

### Logging

The server writes connection events, disconnections, commands, and chat activity to `server/chat.log`. The log can contain message content, so do not use it for sensitive conversations or commit real chat logs to a public repository.

## Testing checklist

- [ ] Start the server using `python server/server.py`.
- [ ] Connect two or more clients using `python client/client.py`.
- [ ] Send a public message and confirm other clients receive it.
- [ ] Test `/help`, `/users`, and `/name`.
- [ ] Send a private message with `/msg`.
- [ ] Try connecting with a duplicate username.
- [ ] Test `/clear` and `/quit`.
- [ ] Disconnect a client unexpectedly and verify the server remains available.
- [ ] Check `server/chat.log` for recorded activity.

## Limitations and security notes

This is an educational project, not a production-ready chat service.

- The current protocol uses `recv(1024)` without explicit message framing. TCP is a byte stream, so messages can be split or combined in unexpected ways.
- Messages are not encrypted.
- Usernames are not authenticated.
- Chat content is logged in plain text.
- The server should not be exposed to untrusted networks as-is.

Possible future improvements include message framing, authentication, TLS encryption, persistent chat history, rate limiting, and automated tests.

## Learning outcomes

This project demonstrates Python socket programming, TCP/IP, client-server architecture, multithreading, concurrency, shared-state synchronization, message broadcasting, private messaging, exception handling, and logging.
