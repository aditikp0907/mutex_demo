import socket
import threading
import time
import json
import os

ID = int(os.getenv("ID"))
TOTAL = 3
peers = [i for i in range(TOTAL) if i != ID]

port = 5000 + ID
lamport = 0
reply_count = 0
waiting = False

sock = socket.socket()
sock.bind(("0.0.0.0", port))
sock.listen()

def send(to, msg, ts):
    s = socket.socket()
    try:
        s.connect((f"node{to}", 5000 + to))
        s.send(json.dumps({"msg": msg, "ts": ts, "from": ID}).encode())
    except:
        pass
    s.close()

def listener():
    global reply_count, lamport, waiting
    while True:
        conn, _ = sock.accept()
        data = json.loads(conn.recv(1024).decode())
        msg, ts, src = data["msg"], data["ts"], data["from"]

        lamport = max(lamport, ts) + 1

        if msg == "REQUEST":
            if not waiting or (ts, src) < (my_ts, ID):
                send(src, "REPLY", lamport)
            else:
                deferred.add(src)

        elif msg == "REPLY":
            reply_count += 1

        conn.close()

threading.Thread(target=listener, daemon=True).start()

time.sleep(2)
lamport += 1
my_ts = lamport
waiting = True
deferred = set()

for p in peers:
    send(p, "REQUEST", my_ts)

while reply_count < len(peers):
    time.sleep(0.1)

print(f"[Node {ID}] ENTERING CS")
time.sleep(2)
print(f"[Node {ID}] EXITING CS")

for d in deferred:
    send(d, "REPLY", lamport)
