import tkinter as tk
import json
import os


class NetworkDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("NetStat-Analyzer: Network Behavior Research")
        self.root.geometry("450x350")

        self.labels = {}
        self.client_frames = {}  # מאגר לשמירת המסגרות כדי שנוכל להרוס אותן

        tk.Label(root, text="Network Behavior Dashboard", font=("Arial", 16, "bold")).pack(pady=10)
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.update_data()

    def update_data(self):
        if os.path.exists("stats.json"):
            try:
                with open("stats.json", "r") as f:
                    data = json.load(f)

                # 1. הוספה ועדכון של לקוחות קיימים
                for client_id, stats in data.items():
                    if client_id not in self.labels:
                        frame = tk.LabelFrame(self.main_frame, text=client_id, font=("Arial", 12, "bold"))
                        frame.pack(fill=tk.X, pady=5)

                        lbl = tk.Label(frame, text="", font=("Arial", 12), justify=tk.LEFT)
                        lbl.pack(anchor="w", padx=10, pady=5)

                        self.labels[client_id] = lbl
                        self.client_frames[client_id] = frame

                    text = f"Average RTT: {stats['rtt']} ms\nPacket Loss: {stats['loss']} %\nStatus: {stats['status']}"
                    self.labels[client_id].config(text=text)

                    if "ANOMALY" in stats['status']:
                        self.labels[client_id].config(fg="red")
                    else:
                        self.labels[client_id].config(fg="green")

                # 2. מנגנון ניקוי: מחיקת לקוחות שכבר לא מופיעים בקובץ
                disconnected_clients = [cid for cid in self.labels.keys() if cid not in data]
                for cid in disconnected_clients:
                    self.client_frames[cid].destroy()  # מחיקת המסגרת מהמסך
                    del self.labels[cid]
                    del self.client_frames[cid]

            except json.JSONDecodeError:
                pass

        self.root.after(1000, self.update_data)


if __name__ == "__main__":
    if not os.path.exists("stats.json"):
        with open("stats.json", "w") as f: json.dump({}, f)
    root = tk.Tk()
    app = NetworkDashboard(root)
    root.mainloop()