# ============================================================
#  pt_pc_client.py  --  Chat Client to run INSIDE Packet Tracer
#  Run this inside PC1 in Packet Tracer
# ============================================================

import socket

# Target Server IP (PC0's IP) and Port in Packet Tracer
SERVER_HOST = '192.168.1.10'
SERVER_PORT = 5000

def start_pt_client():
    print("========================================")
    print("  Packet Tracer Internal Chat Client")
    print(f"  Connecting to {SERVER_HOST}:{SERVER_PORT} ...")
    print("========================================")

    # Create TCP Stream Socket
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_sock.connect((SERVER_HOST, SERVER_PORT))
        print("Successfully connected to the other PC!\n")
        print("Type your message and press Enter.")
        print("Type 'exit' to quit.\n")

        while True:
            # 1. Send message to Server PC
            msg = input("[You - Client]: ").strip()
            if not msg:
                continue

            client_sock.sendall((msg + "\n").encode('utf-8'))
            if msg.lower() == 'exit':
                break

            # 2. Receive reply from Server PC
            data = client_sock.recv(1024).decode('utf-8')
            if not data or data.strip().lower() == 'exit':
                print("[INFO] Remote PC disconnected.")
                break
            print(f"\n[Remote PC]: {data.strip()}")

    except Exception as e:
        print(f"[Connection Error]: {e}")
    finally:
        client_sock.close()
        print("\nDisconnected from chat.")

if __name__ == "__main__":
    start_pt_client()
