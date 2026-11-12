import sqlite3
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class AuthWindow:
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success
        self.root.title("Авторизация — ServerMonitor Enterprise v2.0")
        self.root.geometry("380x240")
        self.root.resizable(False, False)

        tk.Label(self.root, text="Вход в систему мониторинга серверов", font=("Arial", 12, "bold")).pack(pady=15)

        frame = tk.Frame(self.root)
        frame.pack(pady=5)

        tk.Label(frame, text="Логин администратора:").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_login = tk.Entry(frame, width=22)
        self.entry_login.insert(0, "admin")
        self.entry_login.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame, text="Пароль:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_pass = tk.Entry(frame, width=22, show="*")
        self.entry_pass.insert(0, "admin123")
        self.entry_pass.grid(row=1, column=1, padx=5, pady=5)

        btn_login = tk.Button(self.root, text="Войти в систему", bg="#1565c0", fg="white", width=20, command=self.check_auth)
        btn_login.pack(pady=15)

    def check_auth(self):
        login = self.entry_login.get().strip()
        password = self.entry_pass.get().strip()

        conn = sqlite3.connect("servers_v2.db")
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, full_name TEXT)")
        cur.execute("SELECT COUNT(*) FROM users")
        if cur.fetchone()[0] == 0:
            cur.execute("INSERT INTO users (username, password, full_name) VALUES ('admin', 'admin123', 'Ивангин С. Р. (Системный администратор)')")
            conn.commit()

        cur.execute("SELECT full_name FROM users WHERE username=? AND password=?", (login, password))
        user = cur.fetchone()
        conn.close()

        if user:
            self.on_success(user[0])
        else:
            messagebox.showerror("Ошибка доступа", "Неверный логин или пароль!")


class ServerMonitorV2:
    def __init__(self, root, user_fullname):
        self.root = root
        self.user_fullname = user_fullname
        self.root.title("ServerMonitor Enterprise v2.0 — Диагностика и нагрузочное моделирование")
        self.root.geometry("920x580")
        self.init_db()
        self.create_widgets()
        self.load_data()

    def init_db(self):
        self.conn = sqlite3.connect("servers_v2.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS servers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hostname TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                role TEXT NOT NULL,
                cpu_load REAL NOT NULL,
                ram_load REAL NOT NULL,
                ping_ms INTEGER NOT NULL,
                risk_index REAL NOT NULL,
                status TEXT NOT NULL
            )
        """)
        self.conn.commit()

        self.cursor.execute("SELECT COUNT(*) FROM servers")
        if self.cursor.fetchone()[0] == 0:
            sample_data = [
                ("SRV-WEB-01", "192.168.10.11", "Web-сервер", 42.0, 51.5, 14, 46.8, "Стабильно"),
                ("SRV-WEB-02", "192.168.10.12", "Web-сервер", 38.5, 49.0, 12, 43.6, "Стабильно"),
                ("SRV-DB-MAIN", "192.168.10.20", "База данных", 79.0, 86.0, 28, 82.8, "Высокая нагрузка"),
                ("SRV-API-GW", "192.168.10.25", "API-шлюз", 64.5, 68.0, 19, 66.2, "Высокая нагрузка"),
                ("SRV-BACKUP", "192.168.10.30", "Резервное копирование", 18.0, 32.0, 9, 24.5, "Стабильно"),
                ("SRV-ANALYTICS", "192.168.10.45", "Аналитика БД", 91.5, 93.0, 115, 95.4, "Критично")
            ]
            self.cursor.executemany(
                "INSERT INTO servers (hostname, ip_address, role, cpu_load, ram_load, ping_ms, risk_index, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                sample_data
            )
            self.conn.commit()

    def calculate_risk(self, cpu, ram, ping):
        # Взвешенная формула индекса отказа узла
        ping_penalty = min(ping / 5.0, 20.0)
        risk = (cpu * 0.45) + (ram * 0.40) + ping_penalty
        return round(min(risk, 100.0), 1)

    def create_widgets(self):
        top_bar = tk.Frame(self.root, bg="#e3f2fd", pady=6, padx=15)
        top_bar.pack(fill="x")
        tk.Label(top_bar, text="ServerMonitor Enterprise v2.0", font=("Arial", 12, "bold"), bg="#e3f2fd").pack(side="left")
        tk.Label(top_bar, text=f"Пользователь: {self.user_fullname}", font=("Arial", 10), bg="#e3f2fd").pack(side="right")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_monitor = ttk.Frame(self.notebook)
        self.tab_experiment = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_monitor, text="Мониторинг и учет узлов")
        self.notebook.add(self.tab_experiment, text="Вычислительный эксперимент (Стресс-тест)")

        self.build_monitor_tab()
        self.build_experiment_tab()

    def build_monitor_tab(self):
        # Панель добавления
        form = tk.LabelFrame(self.tab_monitor, text="Регистрация нового сервера", padx=10, pady=8)
        form.pack(fill="x", padx=10, pady=5)

        tk.Label(form, text="Хост:").grid(row=0, column=0, padx=4, pady=4)
        self.e_host = tk.Entry(form, width=14)
        self.e_host.grid(row=0, column=1, padx=4, pady=4)

        tk.Label(form, text="IP-адрес:").grid(row=0, column=2, padx=4, pady=4)
        self.e_ip = tk.Entry(form, width=14)
        self.e_ip.grid(row=0, column=3, padx=4, pady=4)

        tk.Label(form, text="Роль:").grid(row=0, column=4, padx=4, pady=4)
        self.cb_role = ttk.Combobox(form, values=["Web-сервер", "База данных", "API-шлюз", "Резервное копирование", "Аналитика БД"], width=18, state="readonly")
        self.cb_role.current(0)
        self.cb_role.grid(row=0, column=5, padx=4, pady=4)

        tk.Label(form, text="CPU (%):").grid(row=1, column=0, padx=4, pady=4)
        self.e_cpu = tk.Entry(form, width=8)
        self.e_cpu.grid(row=1, column=1, padx=4, pady=4, sticky="w")

        tk.Label(form, text="RAM (%):").grid(row=1, column=2, padx=4, pady=4)
        self.e_ram = tk.Entry(form, width=8)
        self.e_ram.grid(row=1, column=3, padx=4, pady=4, sticky="w")

        tk.Label(form, text="Пинг (мс):").grid(row=1, column=4, padx=4, pady=4)
        self.e_ping = tk.Entry(form, width=8)
        self.e_ping.grid(row=1, column=5, padx=4, pady=4, sticky="w")

        tk.Button(form, text="Добавить узел", bg="#2e7d32", fg="white", command=self.add_server).grid(row=0, column=6, rowspan=2, padx=10, sticky="ns")

        # Панель фильтрации и действий
        filter_bar = tk.Frame(self.tab_monitor)
        filter_bar.pack(fill="x", padx=10, pady=5)

        tk.Label(filter_bar, text="Фильтр по статусу:").pack(side="left", padx=5)
        self.cb_filter = ttk.Combobox(filter_bar, values=["Все", "Стабильно", "Высокая нагрузка", "Критично"], width=18, state="readonly")
        self.cb_filter.current(0)
        self.cb_filter.pack(side="left", padx=5)
        self.cb_filter.bind("<<ComboboxSelected>>", lambda e: self.load_data())

        tk.Button(filter_bar, text="Удалить выбранный", bg="#c62828", fg="white", command=self.delete_server).pack(side="left", padx=15)
        tk.Button(filter_bar, text="Экспорт в CSV", command=self.export_csv).pack(side="right", padx=5)

        # Таблица
        cols = ("id", "host", "ip", "role", "cpu", "ram", "ping", "risk", "status")
        self.tree = ttk.Treeview(self.tab_monitor, columns=cols, show="headings", height=12)
        headers = ["ID", "Имя хоста", "IP-адрес", "Роль узла", "CPU (%)", "RAM (%)", "Пинг", "Индекс риска", "Статус"]
        widths = [35, 110, 105, 135, 65, 65, 55, 90, 120]

        for c, h, w in zip(cols, headers, widths):
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        self.lbl_stats = tk.Label(self.tab_monitor, text="", font=("Arial", 10, "bold"))
        self.lbl_stats.pack(pady=4)

    def build_experiment_tab(self):
        ctrl_frame = tk.LabelFrame(self.tab_experiment, text="Параметры вычислительного эксперимента", padx=15, pady=10)
        ctrl_frame.pack(fill="x", padx=15, pady=10)

        tk.Label(ctrl_frame, text="Коэффициент пикового роста трафика (напр. 1.35 = +35%):").grid(row=0, column=0, padx=5, pady=5)
        self.e_multiplier = tk.Entry(ctrl_frame, width=10)
        self.e_multiplier.insert(0, "1.35")
        self.e_multiplier.grid(row=0, column=1, padx=5, pady=5)

        tk.Button(ctrl_frame, text="Запустить моделирование кластера", bg="#1565c0", fg="white", command=self.run_experiment).grid(row=0, column=2, padx=15, pady=5)

        cols = ("host", "role", "cur_cpu", "proj_cpu", "proj_ram", "proj_risk", "verdict")
        self.exp_tree = ttk.Treeview(self.tab_experiment, columns=cols, show="headings", height=10)
        headers = ["Имя хоста", "Роль", "Текущий CPU (%)", "Прогноз CPU (%)", "Прогноз RAM (%)", "Риск отказа (%)", "Вердикт эксперимента"]
        widths = [110, 135, 110, 110, 110, 110, 165]

        for c, h, w in zip(cols, headers, widths):
            self.exp_tree.heading(c, text=h)
            self.exp_tree.column(c, width=w, anchor="center")

        self.exp_tree.pack(fill="both", expand=True, padx=15, pady=5)

        self.txt_report = tk.Text(self.tab_experiment, height=6, font=("Consolas", 10), bg="#f5f5f5")
        self.txt_report.pack(fill="x", padx=15, pady=10)

    def add_server(self):
        try:
            host = self.e_host.get().strip()
            ip = self.e_ip.get().strip()
            role = self.cb_role.get()
            cpu = float(self.e_cpu.get())
            ram = float(self.e_ram.get())
            ping = int(self.e_ping.get())

            if not host or not ip:
                messagebox.showwarning("Внимание", "Введите имя хоста и IP-адрес!")
                return

            risk = self.calculate_risk(cpu, ram, ping)
            if risk >= 80:
                status = "Критично"
            elif risk >= 60:
                status = "Высокая нагрузка"
            else:
                status = "Стабильно"

            self.cursor.execute(
                "INSERT INTO servers (hostname, ip_address, role, cpu_load, ram_load, ping_ms, risk_index, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (host, ip, role, cpu, ram, ping, risk, status)
            )
            self.conn.commit()
            self.load_data()
            for entry in (self.e_host, self.e_ip, self.e_cpu, self.e_ram, self.e_ping):
                entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Ошибка", "Поля CPU, RAM и Пинг должны содержать числа!")

    def delete_server(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Выбор", "Выберите узел в таблице для удаления.")
            return
        item_id = self.tree.item(selected[0])["values"][0]
        self.cursor.execute("DELETE FROM servers WHERE id=?", (item_id,))
        self.conn.commit()
        self.load_data()

    def load_data(self):
        for r in self.tree.get_children():
            self.tree.delete(r)

        status_filter = self.cb_filter.get()
        if status_filter == "Все":
            self.cursor.execute("SELECT * FROM servers")
        else:
            self.cursor.execute("SELECT * FROM servers WHERE status=?", (status_filter,))

        rows = self.cursor.fetchall()
        for r in rows:
            self.tree.insert("", tk.END, values=r)

        self.cursor.execute("SELECT COUNT(*), AVG(cpu_load), AVG(risk_index) FROM servers")
        total, avg_cpu, avg_risk = self.cursor.fetchone()
        if total:
            self.lbl_stats.config(text=f"Всего узлов в кластере: {total} | Средняя нагрузка CPU: {avg_cpu:.1f}% | Средний индекс риска: {avg_risk:.1f}%")

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], initialfile="server_report.csv")
        if path:
            self.cursor.execute("SELECT * FROM servers")
            rows = self.cursor.fetchall()
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(["ID", "Хост", "IP", "Роль", "CPU (%)", "RAM (%)", "Пинг (мс)", "Индекс риска", "Статус"])
                writer.writerows(rows)
            messagebox.showinfo("Экспорт", "Отчет успешно сохранен в CSV!")

    def run_experiment(self):
        try:
            mult = float(self.e_multiplier.get())
            if mult <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Введите положительный коэффициент (например, 1.35)!")
            return

        for r in self.exp_tree.get_children():
            self.exp_tree.delete(r)

        self.cursor.execute("SELECT hostname, role, cpu_load, ram_load, ping_ms FROM servers")
        servers = self.cursor.fetchall()

        overloaded_count = 0
        total_proj_risk = 0.0

        for host, role, cpu, ram, ping in servers:
            proj_cpu = min(round(cpu * mult, 1), 100.0)
            proj_ram = min(round(ram * (1 + (mult - 1) * 0.7), 1), 100.0)
            proj_ping = int(ping * mult)
            proj_risk = self.calculate_risk(proj_cpu, proj_ram, proj_ping)
            total_proj_risk += proj_risk

            if proj_cpu >= 90 or proj_risk >= 85:
                verdict = "ОТКАЗ / ПЕРЕГРУЗКА"
                overloaded_count += 1
            elif proj_risk >= 65:
                verdict = "Требуется балансировка"
            else:
                verdict = "Штатная работа"

            self.exp_tree.insert("", tk.END, values=(host, role, f"{cpu}%", f"{proj_cpu}%", f"{proj_ram}%", f"{proj_risk}%", verdict))

        avg_risk = total_proj_risk / len(servers) if servers else 0
        self.txt_report.delete("1.0", tk.END)
        self.txt_report.insert(tk.END, f"=== РЕЗУЛЬТАТЫ ВЫЧИСЛИТЕЛЬНОГО ЭКСПЕРИМЕНТА (Коэффициент трафика: x{mult}) ===\n")
        self.txt_report.insert(tk.END, f"• Проанализировано серверов: {len(servers)}\n")
        self.txt_report.insert(tk.END, f"• Прогнозируемый средний индекс риска отказа: {avg_risk:.1f}%\n")
        self.txt_report.insert(tk.END, f"• Узлов под угрозой критической перегрузки: {overloaded_count}\n")
        if overloaded_count > 0:
            self.txt_report.insert(tk.END, "РЕКОМЕНДАЦИЯ: Необходимо горизонтальное масштабирование и добавление резервных нод балансировщика.")
        else:
            self.txt_report.insert(tk.END, "РЕКОМЕНДАЦИЯ: Текущая инфраструктура успешно выдерживает заданный рост нагрузки.")


def start_main_app(user_fullname):
    for widget in root.winfo_children():
        widget.destroy()
    ServerMonitorV2(root, user_fullname)


if __name__ == "__main__":
    root = tk.Tk()
    AuthWindow(root, start_main_app)
    root.mainloop()
