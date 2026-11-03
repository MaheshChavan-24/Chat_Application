# ============================================================
#  pt_pc_server.py  --  Chat Server to run INSIDE Packet Tracer
#  Run this inside PC0 (or Server-PT) in Packet Tracer
# ============================================================

import socket

# IP address of this device in Packet Tracer
HOST = '192.168.1.10'   # PC0's IP in Packet Tracer
PORT = 5000            # Chat port

def start_pt_server():
    print("========================================")
    print("  Packet Tracer Internal Chat Server")
    print(f"  Listening on {HOST}:{PORT}")
    print("========================================")

    # Create TCP Stream Socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((HOST, PORT))
    server_sock.listen(1)

    print("Waiting for another PC to connect...\n")
    conn, addr = server_sock.accept()
    print(f"[CONNECTED] Remote PC joined from {addr[0]}:{addr[1]}!\n")

    print("Type your message and press Enter.")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            # 1. Receive message from the remote PC
            data = conn.recv(1024).decode('utf-8')
            if not data or data.strip().lower() == 'exit':
                print("[INFO] Remote PC disconnected.")
                break
            print(f"\n[Remote PC]: {data.strip()}")

            # 2. Send reply message
            msg = input("[You - Server]: ").strip()
            if not msg:
                msg = "Ack"
            conn.sendall((msg + "\n").encode('utf-8'))
            if msg.lower() == 'exit':
                break

        except Exception as e:
            print(f"[Error]: {e}")
            break

    conn.close()
    server_sock.close()
    print("\nChat session closed.")

if __name__ == "__main__":
    start_pt_server()
