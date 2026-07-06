import tkinter as tk
import json
import os

class NetworkDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("NetStat-Analyzer: Network Behavior Research")
        self.root.geometry("450x350")
        self.labels = {}
        
        tk.Label(root, text="Network Behavior Dashboard", font=("Arial", 16, "bold")).pack(pady=10)
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.update_data()

    def update_data(self):
        if os.path.exists("stats.json"):
            try:
                with open("stats.json", "r") as f:
                    data = json.load(f)
                    
                for client_id, stats in data.items():
                    if client_id not in self.labels:
                        frame = tk.LabelFrame(self.frame, text=client_id, font=("Arial", 12, "bold"))
                        frame.pack(fill=tk.X, pady=5)
                        lbl = tk.Label(frame, text="", font=("Arial", 12), justify=tk.LEFT)
                        lbl.pack(anchor="w", padx=10, pady=5)
                        self.labels[client_id] = lbl
                        
                    text = f"Average RTT: {stats['rtt']} ms\nPacket Loss: {stats['loss']} %\nStatus: {stats['status']}"
                    self.labels[client_id].config(text=text)
                    
                    if "ANOMALY" in stats['status']:
                        self.labels[client_id].config(fg="red")
                    else:
                        self.labels[client_id].config(fg="green")
                        
            except json.JSONDecodeError:
                pass
        self.root.after(1000, self.update_data)

if __name__ == "__main__":
    if not os.path.exists("stats.json"):
        with open("stats.json", "w") as f: json.dump({}, f)
    root = tk.Tk()
    app = NetworkDashboard(root)
    root.mainloop()