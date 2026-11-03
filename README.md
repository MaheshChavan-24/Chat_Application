# Computer Networks Course Project: Multi-Client Chat & Packet Tracer IPC Simulation

## 📌 Project Overview
This project is a multi-threaded, connection-oriented **TCP Chat Application** built using Python's native `socket` and `threading` libraries, integrated with **Cisco Packet Tracer (v8.2.2)** through an **Inter-Process Communication (IPC)** bridge.

The project demonstrates:
1. **Core Socket Programming (Transport Layer):** TCP three-way handshakes, stream sockets (`SOCK_STREAM`), multi-threaded client handling, concurrent message broadcasting, buffer chunking, and graceful disconnection.
2. **Network Simulation (Packet Tracer):** A virtual network topology (Clients, Switch, Router, Server) modeled in Cisco Packet Tracer.
3. **IPC Bridge:** A bidirectional relay mechanism connecting Packet Tracer simulation events with live running Python socket processes on localhost.

---

## 🏗️ Architecture

```
                               ┌────────────────────────────────┐
                               │       [server.py :5000]        │
                               │   Multi-threaded TCP Server    │
                               │   - Max Clients: 6             │
                               │   - Broadcast engine           │
                               │   - Username registry          │
                               └─────────▲───────▲──────────────┘
                                         │       │
                     ┌───────────────────┘       └───────────────────┐
                     │ (TCP:5000)                                    │ (TCP:5000)
                     ▼                                               ▼
          ┌──────────────────────┐                       ┌──────────────────────┐
          │  [client.py :5000]   │                       │  [ipc_bridge.py]     │
          │  Alice / Bob / Charlie│                      │  Special client      │
          │  CLI Chat Terminal   │                       │  'PT_Bridge'         │
          └──────────────────────┘                       └──────────▲───────────┘
                                                                    │ (TCP:3900 IPC)
                                                                    ▼
                                                         ┌──────────────────────┐
                                                         │   [pt_script.py]     │
                                                         │ Cisco Packet Tracer  │
                                                         │ Router / PC node     │
                                                         │ (PT 8.2.2 Desktop)   │
                                                         └──────────────────────┘
```

---

## 📂 File Directory

| File | Purpose |
| :--- | :--- |
| `config.py` | Shared network constants (`HOST`, `PORT=5000`, `MAX_CLIENTS=6`, `BRIDGE_PORT=3900`, protocol tags). |
| `server.py` | Multi-threaded TCP chat server. Manages client connections, thread pool, username registry, and message distribution. |
| `client.py` | CLI client featuring non-blocking background message receiving and user input dispatching. |
| `ipc_bridge.py` | IPC bridge communicating with Packet Tracer on port `3900` and the Chat Server on port `5000`. |
| `pt_script.py` | Script configured to run inside Packet Tracer's Python environment (or as a simulated PT node) sending network simulation events. |

---

## ⚙️ Networking Concepts Implemented

1. **TCP (Transmission Control Protocol):** Connection-oriented stream (`socket.AF_INET, socket.SOCK_STREAM`) with reliable, in-order packet delivery.
2. **Port Multiplexing & Concurrency:** The server listens on port `5000` and dispatches separate threads per incoming socket connection (`threading.Thread`).
3. **Thread Safety:** Uses `threading.Lock` to synchronize access to the connected client dictionary during joins, departures, and message broadcasts.
4. **Application-Layer Protocol Framing:** Messages are tagged (`[JOIN]`, `[LEAVE]`, `[MSG]`, `[PT]`, `[SERVER]`, `[USERS]`, `[ERROR]`) to separate control-plane signaling from chat-plane payloads.
5. **IPC (Inter-Process Communication):** Bridge translates Packet Tracer events to standard application sockets, linking simulated topology nodes with real OS sockets.

---

## 🚀 How to Run the Demo

### Step 1: Start the Chat Server
Open a terminal in the project directory:
```bash
python server.py
```
*Output: Server starts listening on `127.0.0.1:5000` with max 6 clients.*

---

### Step 2: Connect Chat Clients (Alice, Bob, etc.)
Open one or more new terminals and launch clients:
```bash
# Terminal 2 (Client 1)
python client.py

# Terminal 3 (Client 2)
python client.py
```
Follow the prompt to enter unique usernames (e.g., `Alice`, `Bob`). They can now send messages back and forth in real-time.

---

### Step 3: Start the IPC Bridge
Open another terminal:
```bash
python ipc_bridge.py
```
*Output: The bridge connects to `server.py:5000` under the identity `PT_Bridge`, and connects with Packet Tracer on port `3900`.*

---

### Step 4: Run the Packet Tracer Integration (PT 8.2.2)

#### Option A: Running from Packet Tracer 8.2.2 Desktop
1. Open Cisco Packet Tracer 8.2.2.
2. Place a **PC** or **Server** device on the workspace connected to a switch/router.
3. Click the PC device → go to the **Desktop** tab → click **Python Interpreter** (or **Programming** tab).
4. Paste the code from `pt_script.py` and click **Run**.
5. Watch the simulation events appear in the live chat terminals of Alice and Bob!

#### Option B: Running Simulated PT Node externally
If you want to quickly test or demonstrate without opening the PT GUI:
```bash
python pt_script.py
```
The script transmits simulated router/switch routing and ARP/TCP handshake events through `ipc_bridge.py` directly into the live chat room!

---

## 🧪 Packet Tracer Suggested Topology (Demo)

```
        [PC0: 192.168.1.10] ───┐
                               ├─── [Switch 2960] ─── [Router 1941] ─── [Server-PT: 192.168.1.1]
        [PC1: 192.168.1.20] ───┘
```
- In Packet Tracer, assign IP addresses in subnet `192.168.1.0/24`.
- The real Python chat server represents `Server-PT` (`192.168.1.1:5000`).
- The clients represent `PC0` and `PC1`.
- When packets traverse the switch and router in simulation mode, the bridge relays events directly to the chat log.

---

## 🔮 Future Enhancements
- [ ] Graphical User Interface (Tkinter or Web frontend)
- [ ] Direct Peer-to-Peer (P2P) mode option
- [ ] File and image transfer using binary socket chunking
- [ ] End-to-end symmetric encryption (AES / XOR)