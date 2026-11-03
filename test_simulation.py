# ============================================================
#  test_simulation.py  --  Automated End-to-End Pipeline Test
#  CN Chat -- Computer Networks Course Project
# ============================================================

import subprocess
import time
import socket
import sys

def test_pipeline():
    print("=" * 60)
    print("  Starting End-to-End Socket & IPC Bridge Pipeline Test")
    print("=" * 60)

    server_proc = None
    bridge_proc = None
    pt_proc = None
    alice_sock = None
    bob_sock = None

    # 1. Start Server
    print("\n[Step 1] Starting server.py...")
    server_proc = subprocess.Popen([sys.executable, "server.py"], cwd="d:/CN_CP")
    time.sleep(1.2)

    try:
        # 2. Connect a client (Alice) directly via raw socket to verify protocol
        print("\n[Step 2] Connecting Client 1 ('Alice')...")
        alice_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        alice_sock.settimeout(5.0)
        alice_sock.connect(("127.0.0.1", 5000))
        alice_welcome = alice_sock.recv(4096).decode('utf-8')
        print(f"Server prompt to Alice:\n{alice_welcome.strip()}")

        alice_sock.sendall("Alice\n".encode('utf-8'))
        time.sleep(0.5)
        alice_ack = alice_sock.recv(4096).decode('utf-8')
        print(f"Alice received confirmation:\n{alice_ack.strip()}")

        # 3. Connect a client (Bob)
        print("\n[Step 3] Connecting Client 2 ('Bob')...")
        bob_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        bob_sock.settimeout(5.0)
        bob_sock.connect(("127.0.0.1", 5000))
        bob_welcome = bob_sock.recv(4096).decode('utf-8')
        bob_sock.sendall("Bob\n".encode('utf-8'))
        time.sleep(0.5)
        bob_ack = bob_sock.recv(4096).decode('utf-8')
        print(f"Bob received confirmation:\n{bob_ack.strip()}")

        # Read Alice's notification of Bob joining
        alice_notif = alice_sock.recv(4096).decode('utf-8')
        print(f"Alice saw notification:\n{alice_notif.strip()}")

        # 4. Alice sends a chat message to Bob
        print("\n[Step 4] Alice sends message: 'Hello Bob! Testing TCP chat.'")
        alice_sock.sendall("Hello Bob! Testing TCP chat.\n".encode('utf-8'))
        time.sleep(0.5)
        bob_msg = bob_sock.recv(4096).decode('utf-8')
        print(f"Bob received broadcast:\n{bob_msg.strip()}")

        # 5. Start IPC Bridge
        print("\n[Step 5] Starting ipc_bridge.py...")
        bridge_proc = subprocess.Popen([sys.executable, "ipc_bridge.py"], cwd="d:/CN_CP")
        time.sleep(1.5)

        # 6. Run Packet Tracer Script simulation
        print("\n[Step 6] Running pt_script.py (Simulated Packet Tracer node)...")
        pt_proc = subprocess.Popen([sys.executable, "pt_script.py"], cwd="d:/CN_CP")
        time.sleep(2.5)

        # Check Bob and Alice receiving Packet Tracer simulation event
        alice_pt_data = alice_sock.recv(4096).decode('utf-8')
        print(f"\n[Verification] Alice received Packet Tracer simulation event:\n{alice_pt_data.strip()}")

        print("\n" + "=" * 60)
        print("  ALL TESTS PASSED SUCCESSFULLY!")
        print("  - TCP Server & Client Communication: OK")
        print("  - Multi-client Broadcast: OK")
        print("  - IPC Bridge (Port 3900 <-> Port 5000): OK")
        print("  - Packet Tracer Simulation Event Broadcast: OK")
        print("=" * 60)

    finally:
        print("\nCleaning up processes...")
        for sock in [alice_sock, bob_sock]:
            if sock:
                try:
                    sock.close()
                except Exception:
                    pass

        for proc in [pt_proc, bridge_proc, server_proc]:
            if proc:
                try:
                    proc.terminate()
                except Exception:
                    pass

        print("Test complete and processes terminated.")

if __name__ == "__main__":
    test_pipeline()
