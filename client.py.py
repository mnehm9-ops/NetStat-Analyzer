import asyncio
import json
import time
import random

CLIENT_ID = f"Client_{random.randint(1000, 9999)}"
# הגדרת מודלים מתמטיים לדימוי רשת
DROP_PROBABILITY = 0.15 # 15% הסתברות לאובדן חבילה
JITTER_MEAN_MS = 40     # תוחלת השהיה של 40ms
JITTER_STD_MS = 25      # סטיית תקן של 25ms

async def run_client():
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    print(f"{CLIENT_ID} connected to server.")
    
    sent_packets = 0
    lost_packets = 0
    rtt_list = []

    async def send_probes():
        nonlocal sent_packets, lost_packets
        while True:
            await asyncio.sleep(0.5) # קצב ייצור תעבורה
            
            # 1. מודל אובדן חבילות (התפלגות אחידה)
            if random.random() < DROP_PROBABILITY:
                lost_packets += 1
                continue
            
            # 2. מודל השהיה (התפלגות נורמלית)
            delay_ms = random.gauss(JITTER_MEAN_MS, JITTER_STD_MS)
            await asyncio.sleep(max(0, delay_ms) / 1000.0)
            
            msg = json.dumps({"type": "PROBE_SEND", "timestamp": time.time()}) + "\n"
            writer.write(msg.encode())
            await writer.drain()
            sent_packets += 1

    async def receive_acks():
        while True:
            data = await reader.readline()
            if not data: break
            msg = json.loads(data.decode())
            if msg.get("type") == "PROBE_ACK":
                rtt = (time.time() - msg["timestamp"]) * 1000
                rtt_list.append(rtt)
                if len(rtt_list) > 20: rtt_list.pop(0)

    async def report_stats():
        while True:
            await asyncio.sleep(2)
            if not rtt_list: continue
            
            avg_rtt = sum(rtt_list) / len(rtt_list)
            total = sent_packets + lost_packets
            loss_rate = (lost_packets / total) * 100 if total > 0 else 0
            
            # 3. מודל זיהוי אנומליות סטטיסטי (רכיב AI)
            status = "NORMAL"
            if avg_rtt > JITTER_MEAN_MS * 1.5 or loss_rate > 20:
                status = "ANOMALY: High Load / Loss"

            stats_msg = json.dumps({
                "type": "REPORT_STATS",
                "client_id": CLIENT_ID,
                "data": {"rtt": round(avg_rtt, 2), "loss": round(loss_rate, 2), "status": status}
            }) + "\n"
            writer.write(stats_msg.encode())
            await writer.drain()

    await asyncio.gather(send_probes(), receive_acks(), report_stats())

if __name__ == "__main__":
    asyncio.run(run_client())