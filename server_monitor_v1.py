import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

class ServerMonitorV1:
    def __init__(self, root):
        self.root = root
        self.root.title("ServerMonitor v1.0 — Базовый мониторинг серверов")
        self.root.geometry("780x500")
        self.init_db()
        self.create_widgets()
        self.load_data()

    def init_db(self):
        self.conn = sqlite3.connect("servers_v1.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS servers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hostname TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                cpu_load REAL NOT NULL,
                ram_load REAL NOT NULL,
                ping_ms INTEGER NOT NULL,
                status TEXT NOT NULL
            )
        """)
        self.conn.commit()

        self.cursor.execute("SELECT COUNT(*) FROM servers")
        if self.cursor.fetchone()[0] == 0:
            sample_data = [
                ("SRV-WEB-01", "192.168.10.11", 34.5, 48.0, 12, "Стабильно"),
                ("SRV-DB-MAIN", "192.168.10.12", 78.2, 84.5, 25, "Высокая нагрузка"),
                ("SRV-BACKUP-01", "192.168.10.15", 15.0, 30.2, 8, "Стабильно"),
                ("SRV-MAIL-02", "192.168.10.20", 92.4, 91.0, 110, "Критично")
            ]
            self.cursor.executemany(
                "INSERT INTO servers (hostname, ip_address, cpu_load, ram_load, ping_ms, status) VALUES (?, ?, ?, ?, ?, ?)",
                sample_data
            )
            self.conn.commit()

    def create_widgets(self):
        title_lbl = tk.Label(self.root, text="Система мониторинга серверов (Редакция 1.0)", font=("Arial", 14, "bold"))
        title_lbl.pack(pady=10)

        form_frame = tk.LabelFrame(self.root, text="Добавление узла в мониторинг", padx=10, pady=10)
        form_frame.pack(fill="x", padx=15, pady=5)

        tk.Label(form_frame, text="Имя хоста:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_host = tk.Entry(form_frame, width=16)
        self.entry_host.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="IP-адрес:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_ip = tk.Entry(form_frame, width=16)
        self.entry_ip.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(form_frame, text="CPU (%):").grid(row=0, column=4, padx=5, pady=5)
        self.entry_cpu = tk.Entry(form_frame, width=8)
        self.entry_cpu.grid(row=0, column=5, padx=5, pady=5)

        tk.Label(form_frame, text="RAM (%):").grid(row=1, column=0, padx=5, pady=5)
        self.entry_ram = tk.Entry(form_frame, width=8)
        self.entry_ram.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        tk.Label(form_frame, text="Пинг (мс):").grid(row=1, column=2, padx=5, pady=5)
        self.entry_ping = tk.Entry(form_frame, width=8)
        self.entry_ping.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        btn_add = tk.Button(form_frame, text="Добавить и рассчитать", bg="#2e7d32", fg="white", command=self.add_server)
        btn_add.grid(row=1, column=4, columnspan=2, padx=5, pady=5, sticky="ew")

        columns = ("id", "hostname", "ip", "cpu", "ram", "ping", "status")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=10)
        headers = ["ID", "Имя хоста", "IP-адрес", "CPU (%)", "RAM (%)", "Пинг (мс)", "Статус"]
        widths = [40, 130, 120, 80, 80, 90, 150]

        for col, head, w in zip(columns, headers, widths):
            self.tree.heading(col, text=head)
            self.tree.column(col, width=w, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=15, pady=10)

        self.lbl_summary = tk.Label(self.root, text="", font=("Arial", 10, "bold"))
        self.lbl_summary.pack(pady=5)

    def add_server(self):
        try:
            host = self.entry_host.get().strip()
            ip = self.entry_ip.get().strip()
            cpu = float(self.entry_cpu.get())
            ram = float(self.entry_ram.get())
            ping = int(self.entry_ping.get())

            if not host or not ip:
                messagebox.showwarning("Ошибка", "Заполните имя хоста и IP-адрес!")
                return

            avg_load = (cpu + ram) / 2
            if avg_load >= 85 or ping > 100:
                status = "Критично"
            elif avg_load >= 65:
                status = "Высокая нагрузка"
            else:
                status = "Стабильно"

            self.cursor.execute(
                "INSERT INTO servers (hostname, ip_address, cpu_load, ram_load, ping_ms, status) VALUES (?, ?, ?, ?, ?, ?)",
                (host, ip, cpu, ram, ping, status)
            )
            self.conn.commit()
            self.load_data()
            for e in (self.entry_host, self.entry_ip, self.entry_cpu, self.entry_ram, self.entry_ping):
                e.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Проверьте правильность числовых полей!")

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        self.cursor.execute("SELECT * FROM servers")
        rows = self.cursor.fetchall()
        for r in rows:
            self.tree.insert("", tk.END, values=r)

        if rows:
            avg_cpu = sum(r[3] for r in rows) / len(rows)
            self.lbl_summary.config(text=f"Всего узлов в базе: {len(rows)} | Средняя загрузка CPU по сети: {avg_cpu:.1f}%")

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerMonitorV1(root)
    root.mainloop()
