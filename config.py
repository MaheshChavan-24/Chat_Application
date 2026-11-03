# ============================================================
#  config.py  —  Shared configuration for CN Chat Project
# ============================================================

# ── Network Settings ─────────────────────────────────────────
HOST            = "127.0.0.1"   # Server IP  (localhost for demo) 
PORT            = 5000          # Main chat server port
MAX_CLIENTS     = 6             # Maximum simultaneous clients
BUFFER_SIZE     = 4096          # Socket receive buffer (bytes)
ENCODING        = "utf-8"       # Message encoding

# ── IPC Bridge Settings (Packet Tracer ↔ Python) ────────────
BRIDGE_HOST     = "127.0.0.1"   # Bridge listens on localhost
BRIDGE_PORT     = 3900          # PT External App connects here

# ── Protocol Tags ────────────────────────────────────────────
# Used to distinguish control messages from chat messages
TAG_JOIN        = "[JOIN]"      # Client joined notification
TAG_LEAVE       = "[LEAVE]"     # Client left notification
TAG_MSG         = "[MSG]"       # Regular chat message
TAG_SERVER      = "[SERVER]"    # Server announcement
TAG_PT          = "[PT]"        # Message originating from PT bridge
TAG_ERROR       = "[ERROR]"     # Error message
TAG_USERLIST    = "[USERS]"     # Server sends current user list

# ── UI / Display ─────────────────────────────────────────────
SEPARATOR       = "-" * 60
APP_TITLE       = "CN Chat - Computer Networks Course Project"
SERVER_NAME     = "SERVER"

# ── Timeouts ─────────────────────────────────────────────────
RECV_TIMEOUT    = None          # Blocking receive (None = no timeout)
CONNECT_TIMEOUT = 10            # Seconds to wait when connecting
