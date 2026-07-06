import asyncio
import json
import time
import random

CLIENT_ID = f"Client_{random.randint(1000, 9999)}"
DROP_PROBABILITY = 0.15
JITTER_MEAN_MS = 40
JITTER_STD_MS = 25


async def run_client():
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    print(f"{CLIENT_ID} connected to server.")

    sent_packets = 0
    lost_packets = 0
    rtt_list = []
    is_burst_mode = False  # מודל מתמטי לייצוג צוואר בקבוק פתאומי ברשת

    async def send_probes():
        nonlocal sent_packets, lost_packets, is_burst_mode
        while True:
            await asyncio.sleep(0.5)

            # הסתברות של 5% בכל חצי שנייה לשנות מצב רשת
            if random.random() < 0.05:
                is_burst_mode = not is_burst_mode
                if is_burst_mode:
                    print(f"[{CLIENT_ID}] Entering Burst Mode!")

            # התאמת המודלים ההסתברותיים למצב הרשת הנוכחי
            current_drop_prob = 0.45 if is_burst_mode else DROP_PROBABILITY
            current_jitter_mean = 110 if is_burst_mode else JITTER_MEAN_MS

            if random.random() < current_drop_prob:
                lost_packets += 1
                continue

            delay_ms = random.gauss(current_jitter_mean, JITTER_STD_MS)
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
        nonlocal sent_packets, lost_packets
        while True:
            await asyncio.sleep(2)
            if not rtt_list: continue

            avg_rtt = sum(rtt_list) / len(rtt_list)
            total = sent_packets + lost_packets
            loss_rate = (lost_packets / total) * 100 if total > 0 else 0

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

            # איפוס המונים מאפשר סטטיסטיקה של "חלון זמן הזזה" המשקפת מצב נוכחי
            sent_packets = 0
            lost_packets = 0

    await asyncio.gather(send_probes(), receive_acks(), report_stats())


if __name__ == "__main__":
    asyncio.run(run_client())