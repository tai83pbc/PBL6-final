import requests
import time
import difflib
from urllib.parse import urlparse, urljoin, parse_qs, urlencode, urlunparse
from bs4 import BeautifulSoup
from PyQt5.QtCore import QObject, pyqtSignal

class ScannerWorker(QObject):
    log_updated = pyqtSignal(str)
    scan_finished = pyqtSignal(list)
    progress_updated = pyqtSignal(int, int)

    def __init__(self, base_url, cookie=None):
        super().__init__()
        self.base_url = base_url if base_url.startswith('http') else "http://" + base_url
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) EthicalScanner/Pro Universal'
        })

        # --- XỬ LÝ COOKIE ---
        self.is_authenticated = False
        if cookie:
            try:
                cookie_dict = {}
                for item in cookie.split(';'):
                    if '=' in item:
                        k, v = item.strip().split('=', 1)
                        cookie_dict[k] = v
                self.session.cookies.update(cookie_dict)
                self.is_authenticated = True
            except:
                self.log_updated.emit("[!] Lỗi Cookie. Quét chế độ Guest.")

        self.found_vulns = []
        self.scanned_urls = set()
        self.crawl_queue = []
        self.forms_found = [] 

        # --- TỪ ĐIỂN LỖI ĐA DẠNG ---
        self.db_errors = {
            "MySQL": ["syntax error", "mysql_fetch", "check the manual", "warning: mysql"],
            "PostgreSQL": ["syntax error at or near", "unterminated quoted string", "pg_query"],
            "SQL Server": ["unclosed quotation mark", "sql server", "driver][sql server]", "oledb exception"],
            "Oracle": ["ora-01756", "quoted string not properly terminated"],
            "General": ["fatal error", "mysql error", "syntax error"] 
        }

        # --- PAYLOADS ---
        self.sqli_payloads_error = ["'", '"', "')"]
        
        self.sqli_payloads_time = [
            "' AND SLEEP(5)-- -",
            "'; WAITFOR DELAY '0:0:5'--",
            " AND (SELECT 5 FROM PG_SLEEP(5))"
        ]

        self.sqli_payloads_boolean = [
            (" AND 1=1", " AND 1=0"), 
            ("' AND '1'='1", "' AND '1'='0"),
            ('" AND "1"="1', '" AND "1"="0')
        ]

        self.xss_payloads = [
            "<script>alert('XSS')</script>", 
            "\"><script>alert('XSS')</script>",
            "' onmouseover='alert(1)"
        ]

        self.hidden_paths = [
            "admin/", "admin/index.php", "login.php", "dashboard.php", 
            "config.php", "upload.php", "users.php"
        ]

    def check_connection(self):
        self.log_updated.emit("[*] Đang kiểm tra kết nối...")
        try:
            res = self.session.get(self.base_url, timeout=10, allow_redirects=False)
            if res.status_code == 302 and "login" in res.headers.get("Location", ""):
                self.log_updated.emit("[!] CẢNH BÁO: Cookie hết hạn/Redirect Login.")
                return False
            elif res.status_code == 200:
                self.log_updated.emit(f"[OK] Kết nối ổn định. Status: 200")
                return True
            else:
                self.log_updated.emit(f"[INFO] Status Code: {res.status_code}")
                return True
        except Exception as e:
            self.log_updated.emit(f"[!] Lỗi kết nối: {str(e)}")
            return False

    def run_scan(self):
        self.log_updated.emit(f"[*] Bắt đầu quét ĐA NĂNG: {self.base_url}")
        
        if self.is_authenticated:
            if not self.check_connection():
                self.scan_finished.emit([])
                return

        self._discover_hidden_paths()
        self.crawl_queue.append(self.base_url)
        self._crawl_recursive()

        total_targets = len(self.scanned_urls) + len(self.forms_found)
        self.log_updated.emit(f"[*] Tổng mục tiêu: {len(self.scanned_urls)} Link + {len(self.forms_found)} Form.")

        for i, url in enumerate(self.scanned_urls):
            self.progress_updated.emit(i, total_targets)
            if "?" in url:
                self.log_updated.emit(f"-> Scan GET: {url}")
                self._attack_get(url)

        for i, form_data in enumerate(self.forms_found):
            self.progress_updated.emit(len(self.scanned_urls) + i, total_targets)
            self.log_updated.emit(f"-> Scan POST Form tại: {form_data['action']}")
            self._attack_post(form_data)

        self.scan_finished.emit(self.found_vulns)

    def _discover_hidden_paths(self):
        self.log_updated.emit("[*] Đang fuzzing các đường dẫn ẩn...")
        for path in self.hidden_paths:
            full_url = urljoin(self.base_url, path)
            try:
                res = self.session.get(full_url, timeout=5)
                if res.status_code == 200:
                    self.log_updated.emit(f"[+] Tìm thấy: {full_url}")
                    self.crawl_queue.append(full_url)
            except: pass

    def _crawl_recursive(self):
        processed = set()
        while self.crawl_queue:
            url = self.crawl_queue.pop(0)
            if url in processed: continue
            
            if any(url.endswith(ext) for ext in ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.pdf']):
                continue

            processed.add(url)
            if self.base_url not in url: continue

            try:
                res = self.session.get(url, timeout=5)
                self.scanned_urls.add(url)
                soup = BeautifulSoup(res.text, 'html.parser')

                for a in soup.find_all('a', href=True):
                    next_link = urljoin(self.base_url, a['href'])
                    if "logout" in next_link.lower(): continue
                    if self.base_url in next_link and next_link not in processed:
                        self.crawl_queue.append(next_link)

                for form in soup.find_all('form'):
                    action = form.get('action')
                    method = form.get('method', 'get').lower()
                    target_url = urljoin(url, action) if action else url    
                    
                    inputs = []
                    for inp in form.find_all('input'):
                        name = inp.get('name')
                        type_ = inp.get('type', 'text')
                        if name and type_ not in ['submit', 'button', 'image']:
                            inputs.append(name)
                    
                    if inputs:
                        form_info = {'action': target_url, 'method': method, 'inputs': inputs}
                        if form_info not in self.forms_found:
                            self.forms_found.append(form_info)
                            self.log_updated.emit(f"[+] Lưu Form {method.upper()}: {target_url}")

            except: pass

    def _attack_get(self, url):
        """
        ✅ FIX CHÍNH: Lưu URL gốc SẠCH, không kèm payload
        """
        # ============================================
        # LƯU URL GỐC NGAY TỪ ĐẦU
        # ============================================
        original_clean_url = url
        
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        try:
            original_res = self.session.get(url, timeout=10)
        except: 
            return

        for p in params:
            # 1. Test Error-based
            for payload in self.sqli_payloads_error:
                test_url = self._inject_param(url, p, payload)
                self._check_error_based(test_url, original_clean_url, payload, "GET", p)

            # 2. Test Time-based
            for payload in self.sqli_payloads_time:
                test_url = self._inject_param(url, p, payload)
                self._check_time_based(test_url, original_clean_url, payload, "GET", p)

            # 3. Test Boolean Blind
            self._check_boolean_blind(url, p, original_res.text, "GET", original_clean_url)

            # 4. Test XSS
            for payload in self.xss_payloads:
                test_url = self._inject_param(url, p, payload)
                self._send_request_xss(test_url, original_clean_url, payload, "GET", p)

    def _attack_post(self, form_data):
        """
        ✅ FIX: Lưu URL gốc cho POST
        """
        target_url = form_data['action']
        inputs = form_data['inputs']
        if form_data['method'] != 'post': return

        for inp_name in inputs:
            base_data = {key: "test" for key in inputs}
            
            # 1. Test Error SQLi POST
            for payload in self.sqli_payloads_error:
                post_data = base_data.copy()
                post_data[inp_name] = payload
                try:
                    res = self.session.post(target_url, data=post_data, timeout=5)
                    self._scan_error_in_response(res.text, target_url, inp_name, "POST", payload, post_data)
                except: pass

            # 2. Test Time-based SQLi POST
            for payload in self.sqli_payloads_time:
                post_data = base_data.copy()
                post_data[inp_name] = payload
                self._check_time_based_post(target_url, post_data, payload, inp_name)

            # 3. Test XSS POST
            for payload in self.xss_payloads:
                post_data = base_data.copy()
                post_data[inp_name] = payload
                try:
                    res = self.session.post(target_url, data=post_data, timeout=5)
                    if payload in res.text:
                         self._add_vuln("XSS (Reflected POST)", target_url, inp_name, "POST", "", post_data)
                except: pass

    # ============================================
    # CÁC HÀM KIỂM TRA ĐÃ SỬA
    # ============================================

    def _check_error_based(self, test_url, original_url, payload, method, param):
        """✅ Nhận thêm original_url"""
        try:
            res = self.session.get(test_url, timeout=5)
            self._scan_error_in_response(res.text, original_url, param, method, payload)
        except: pass

    def _scan_error_in_response(self, text, url, param, method, payload, post_data=None):
        """✅ url ở đây là URL gốc sạch"""
        text_lower = text.lower()
        for db, errors in self.db_errors.items():
            for err in errors:
                if err in text_lower:
                    self.log_updated.emit(f"[!!!] PHÁT HIỆN SQLi Error ({db}): {param}")
                    self._add_vuln(f"SQLi ({db} Error)", url, param, method, payload, post_data)
                    return True
        return False

    def _check_time_based(self, test_url, original_url, payload, method, param):
        """✅ Nhận thêm original_url"""
        try:
            start = time.time()
            self.session.get(test_url, timeout=10)
            end = time.time()
            if (end - start) >= 5:
                self.log_updated.emit(f"[!!!] PHÁT HIỆN SQLi Time-based: {param}")
                self._add_vuln("SQLi (Time-based)", original_url, param, method, payload)
        except: pass

    def _check_time_based_post(self, url, data, payload, param):
        """✅ url ở đây đã là URL gốc"""
        try:
            start = time.time()
            self.session.post(url, data=data, timeout=10)
            end = time.time()
            if (end - start) >= 5:
                self.log_updated.emit(f"[!!!] PHÁT HIỆN SQLi POST Time-based: {param}")
                self._add_vuln("SQLi POST (Time-based)", url, param, "POST", payload, data)
        except: pass

    def _check_boolean_blind(self, url, param, original_html, method, original_clean_url):
        """✅ Nhận thêm original_clean_url"""
        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        for true_pl, false_pl in self.sqli_payloads_boolean:
            try:
                qs_true = params.copy()
                qs_true[param] = [params[param][0] + true_pl]
                target_true = parsed._replace(query=urlencode(qs_true, doseq=True)).geturl()
                res_true = self.session.get(target_true, timeout=5)

                qs_false = params.copy()
                qs_false[param] = [params[param][0] + false_pl]
                target_false = parsed._replace(query=urlencode(qs_false, doseq=True)).geturl()
                res_false = self.session.get(target_false, timeout=5)

                ratio_true = difflib.SequenceMatcher(None, original_html, res_true.text).ratio()
                ratio_false = difflib.SequenceMatcher(None, original_html, res_false.text).ratio()

                if ratio_true > 0.95 and ratio_false < 0.90:
                    self.log_updated.emit(f"[!!!] PHÁT HIỆN BLIND SQLi (Boolean): {param}")
                    self._add_vuln("Blind SQLi (Boolean)", original_clean_url, param, method, true_pl)
                    return
            except: pass

    def _send_request_xss(self, test_url, original_url, payload, method, param):
        """✅ Nhận thêm original_url"""
        try:
            res = self.session.get(test_url, timeout=5)
            if payload in res.text:
                self.log_updated.emit(f"[!!!] PHÁT HIỆN XSS: {param}")
                self._add_vuln("Reflected XSS", original_url, param, method, payload)
        except: pass

    def scan_second_order_sqli(self, login_url, add_cart_url, checkout_url):
        """Giữ nguyên logic Second-Order"""
        self.log_updated.emit("[*] Bắt đầu quét Second-Order SQL Injection...")
        payload = "TestUser' AND (SELECT SLEEP(5)) AND '1'='1"
        login_data = {'email': payload, 'pass': 'password_bua'}
        
        try:
            self.session.post(login_url, data=login_data, timeout=10)
            self.session.post(add_cart_url, data={'soluong': 1}, timeout=10)
            
            start = time.time()
            self.session.get(checkout_url, timeout=20) 
            end = time.time()
            
            if (end - start) >= 5:
                self.log_updated.emit("[!!!] PHÁT HIỆN SECOND-ORDER SQLi!")
                self._add_vuln("Second-Order SQLi", checkout_url, "SESSION", "Flow", payload)
        except Exception as e:
            self.log_updated.emit(f"[!] Lỗi logic: {str(e)}")

    def _add_vuln(self, v_type, url, param, method, payload="", post_data=None):
        """
        ✅ FIX QUAN TRỌNG: url ở đây PHẢI là URL gốc sạch
        """
        vuln = {
            'type': v_type, 
            'url': url,  # ✅ ĐÂY LÀ URL GỐC, KHÔNG CÓ PAYLOAD
            'parameter': param, 
            'method': method, 
            'payload': payload
        }
        
        # Thêm post_data nếu là POST
        if post_data:
            vuln['post_data'] = urlencode(post_data)
        
        if vuln not in self.found_vulns:
            self.found_vulns.append(vuln)

    def _inject_param(self, url, param_name, payload):
        """Hàm tiện ích: Tạo URL test có payload (KHÔNG lưu vào DB)"""
        parsed = urlparse(url)
        params = parse_qs(parsed.query, keep_blank_values=True)
        params[param_name] = [payload]
        new_query = urlencode(params, doseq=True)
        return urlunparse(parsed._replace(query=new_query))
