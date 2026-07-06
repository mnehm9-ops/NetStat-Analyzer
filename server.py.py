import asyncio
import json

stats_db = {} # שמירת נתונים סטטיסטיים של כל לקוח

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"Client connected: {addr}")
    
    try:
        while True:
            data = await reader.readline()
            if not data:
                break
            
            message = json.loads(data.decode())
            msg_type = message.get("type")
            
            if msg_type == "PROBE_SEND":
                # החזרת אישור (ACK) ללקוח באופן אסינכרוני
                response = json.dumps({"type": "PROBE_ACK", "timestamp": message["timestamp"]}) + "\n"
                writer.write(response.encode())
                await writer.drain()
                
            elif msg_type == "REPORT_STATS":
                # עדכון מאגר הנתונים ושמירה לקובץ עבור הממשק הגרפי
                client_id = message["client_id"]
                stats_db[client_id] = message["data"]
                with open("stats.json", "w") as f:
                    json.dump(stats_db, f)
                
    except ConnectionResetError:
        pass
    finally:
        print(f"Client disconnected: {addr}")
        writer.close()
        await writer.wait_closed()

async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8888)
    print("Async Server running on 127.0.0.1:8888...")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())