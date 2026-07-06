import asyncio
import json

stats_db = {}


async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"Client connected: {addr}")
    client_id_tracker = None  # משתנה שיזכור את מזהה הלקוח כדי שנוכל למחוק אותו בסוף

    try:
        while True:
            data = await reader.readline()
            if not data:
                break

            message = json.loads(data.decode())
            msg_type = message.get("type")

            if msg_type == "PROBE_SEND":
                response = json.dumps({"type": "PROBE_ACK", "timestamp": message["timestamp"]}) + "\n"
                writer.write(response.encode())
                await writer.drain()

            elif msg_type == "REPORT_STATS":
                client_id_tracker = message["client_id"]  # שמירת ה-ID
                stats_db[client_id_tracker] = message["data"]
                with open("stats.json", "w") as f:
                    json.dump(stats_db, f)

    except ConnectionResetError:
        pass
    finally:
        print(f"Client disconnected: {addr}")
        # מנגנון ניקוי: אם הלקוח התנתק, מוחקים אותו מהמאגר ומעדכנים את הקובץ
        if client_id_tracker and client_id_tracker in stats_db:
            del stats_db[client_id_tracker]
            with open("stats.json", "w") as f:
                json.dump(stats_db, f)

        writer.close()
        await writer.wait_closed()


async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8888)
    print("Async Server running on 127.0.0.1:8888...")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())