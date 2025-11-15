import requests
import time
from urllib.parse import urlparse, urljoin, parse_qs, urlencode
from bs4 import BeautifulSoup
from PyQt5.QtCore import QObject, pyqtSignal

class ScannerWorker(QObject):
    log_updated = pyqtSignal(str)
    scan_finished = pyqtSignal(list)
    progress_updated = pyqtSignal(int, int)

    def __init__(self, base_url):
        super().__init__()
        # --- FIX: Chuẩn hóa URL gốc ---
        parsed_url = urlparse(base_url)
        if not parsed_url.scheme:
            base_url = "http://" + base_url
        self.base_url = base_url
        
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'EthicalScanner/1.0'})
        
        # --- FIX: Sử dụng 2 set riêng biệt để dễ quản lý ---
        self.scanned_links = set()
        self.scanned_forms = set()
        self.tasks_to_run = []
        
        self.vulnerabilities_found = []

        self.sql_payloads = self._load_payloads('payloads/sql_injection.txt')
        self.xss_payloads = self._load_payloads('payloads/xss.txt')

    def _load_payloads(self, filepath):
        try:
            with open(filepath, 'r') as f:
                return [line.strip() for line in f if line.strip() and not line.startswith('#')]
        except FileNotFoundError:
            self.log_updated.emit(f"[ERROR] Payload file not found: {filepath}")
            return []

    def run_scan(self):
        self.log_updated.emit(f"[INFO] Starting scan on base URL: {self.base_url}")
        self._crawl(self.base_url)
        
        # Tạo danh sách các tác vụ sau khi crawl
        self.tasks_to_run.extend(list(self.scanned_links))
        self.tasks_to_run.extend(list(self.scanned_forms))
        
        self.log_updated.emit(f"[INFO] Crawling complete. Found {len(self.tasks_to_run)} unique items to test.")
        
        total_tasks = len(self.tasks_to_run)
        for i, task in enumerate(self.tasks_to_run):
            self.progress_updated.emit(i + 1, total_tasks)
            if isinstance(task, str): # URL (GET)
                self.log_updated.emit(f"-> Testing GET URL: {task}")
                self._scan_get_url(task)
            elif isinstance(task, tuple): # Form (POST)
                # --- FIX: Chuyển đổi tuple ngược lại thành dict ở đây ---
                form_details = dict(task)
                # Chuyển đổi tuple của inputs ngược lại thành list của dicts
                form_details['inputs'] = [dict(inp) for inp in form_details['inputs']]
                
                self.log_updated.emit(f"-> Testing POST Form on: {form_details['action']}")
                self._scan_post_form(form_details)
        
        self.log_updated.emit(f"[INFO] Scan finished. Found {len(self.vulnerabilities_found)} vulnerabilities.")
        self.scan_finished.emit(self.vulnerabilities_found)

    def _crawl(self, url):
        # Loại bỏ các tham số query để tránh crawl lặp lại cùng một trang
        url = url.split('?')[0].split('#')[0]
        
        if url in self.scanned_links or not url.startswith(self.base_url):
            return
        
        self.log_updated.emit(f"[CRAWL] Discovering on: {url}")
        self.scanned_links.add(url)
        
        try:
            res = self.session.get(url, timeout=5, verify=False)
            soup = BeautifulSoup(res.content, 'html.parser')
            
            for anchor in soup.find_all('a', href=True):
                absolute_link = urljoin(self.base_url, anchor['href'])
                # Gọi đệ quy để crawl link mới
                self._crawl(absolute_link)
            
            for form in soup.find_all('form'):
                action = form.get('action')
                method = form.get('method', 'get').lower()
                form_action_url = urljoin(self.base_url, action)
                
                if method == 'post':
                    form_details = {
                        "action": form_action_url,
                        "method": "post",
                        "inputs": []
                    }
                    for input_tag in form.find_all(['input', 'textarea', 'select']):
                        if input_tag.get('name'):
                            input_details = {
                                "name": input_tag.get('name'),
                                "type": input_tag.get('type', 'text'),
                                "value": input_tag.get('value', '')
                            }
                            # Chuyển dict của input thành tuple để nó hashable
                            form_details["inputs"].append(tuple(input_details.items()))
                    
                    # --- FIX: Chuyển list của inputs thành tuple ---
                    form_details["inputs"] = tuple(form_details["inputs"])
                    
                    # Bây giờ toàn bộ cấu trúc là hashable
                    form_tuple = tuple(form_details.items())

                    if form_tuple not in self.scanned_forms:
                        self.scanned_forms.add(form_tuple)
        
        except requests.RequestException as e:
            self.log_updated.emit(f"[WARN] Failed to crawl {url}: {e}")

    def _scan_get_url(self, url):
        parsed_url = urlparse(url)
        # parse_qs sẽ trả về một dict, ví dụ: {'frame': ['timkiem']}
        original_params = parse_qs(parsed_url.query)

        # Lặp qua từng TÊN tham số (key) trong dict
        for param_name in original_params.keys():
            original_value = original_params[param_name][0]

            # 1. Quét XSS
            for payload in self.xss_payloads:
                test_params = original_params.copy()
                test_params[param_name] = [payload] # Chèn payload vào đúng tham số
                # urlencode cần doseq=True để xử lý list đúng cách
                test_query = urlencode(test_params, doseq=True)
                test_url = parsed_url._replace(query=test_query).geturl()
                try:
                    res = self.session.get(test_url, timeout=5, verify=False)
                    if payload in res.text:
                        # Lưu lại TÊN tham số một cách chính xác
                        self._add_vulnerability("Reflected XSS", test_url, param_name, payload)
                        # Đã tìm thấy lỗi XSS trên param này, chuyển sang param tiếp theo
                        break 
                except requests.RequestException:
                    pass
            
            # 2. Quét SQL Injection
            for payload in [p for p in self.sql_payloads if 'SLEEP' in p.upper()]:
                test_params = original_params.copy()
                # Chèn payload vào sau giá trị gốc
                test_params[param_name] = [original_value + payload]
                test_query = urlencode(test_params, doseq=True)
                test_url = parsed_url._replace(query=test_query).geturl()
                
                start_time = time.time()
                try:
                    self.session.get(test_url, timeout=10, verify=False)
                except requests.exceptions.ReadTimeout:
                    if time.time() - start_time >= 4.5:
                        # Lưu lại TÊN tham số một cách chính xác
                        self._add_vulnerability("Time-Based SQLi (GET)", test_url, param_name, payload)
                        # Đã tìm thấy lỗi SQLi, không cần test thêm payload trên param này
                        return # Chuyển sang URL tiếp theo để tiết kiệm thời gian

    def _scan_post_form(self, form_details):
        target_url = form_details['action']
        inputs = form_details['inputs']
        
        for input_to_test in inputs:
            original_data = {}
            for inp in inputs:
                if inp['type'].lower() in ['submit', 'button', 'reset']: continue
                original_data[inp['name']] = inp.get('value', 'test')

            # 1. Quét XSS
            for payload in self.xss_payloads:
                data = original_data.copy()
                data[input_to_test['name']] = payload
                try:
                    res = self.session.post(target_url, data=data, timeout=5, verify=False)
                    if payload in res.text:
                        # --- CẬP NHẬT: Gửi thêm original_data ---
                        self._add_vulnerability("Stored/Reflected XSS (POST)", target_url, input_to_test['name'], payload, method="POST", data=original_data)
                        break
                except requests.RequestException:
                    pass

            # 2. Quét SQL Injection
            for payload in [p for p in self.sql_payloads if 'SLEEP' in p.upper()]:
                data = original_data.copy()
                original_value = data.get(input_to_test['name'], '')
                data[input_to_test['name']] = original_value + payload
                start_time = time.time()
                try:
                    self.session.post(target_url, data=data, timeout=10, verify=False)
                except requests.exceptions.ReadTimeout:
                    if time.time() - start_time >= 4.5:
                        # --- CẬP NHẬT: Gửi thêm original_data ---
                        self._add_vulnerability("Time-Based SQLi (POST)", target_url, input_to_test['name'], payload, method="POST", data=original_data)
                        return
    def _add_vulnerability(self, vuln_type, url, parameter, payload, method="GET", data=None):
        vulnerability = {
            "type": vuln_type,
            "url": url,
            "parameter": parameter,
            "payload": payload,
            "method": method, # Lưu lại phương thức
            "data": data,     # Lưu lại dữ liệu POST (nếu có)
        }
        if vulnerability not in self.vulnerabilities_found:
            self.vulnerabilities_found.append(vulnerability)
            self.log_updated.emit(f"[VULN] Found {vuln_type} at {url.split('?')[0]} on parameter '{parameter}'")
