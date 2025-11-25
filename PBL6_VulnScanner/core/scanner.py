import requests
import time
from urllib.parse import urlparse, urljoin, parse_qs, urlencode
from bs4 import BeautifulSoup
from PyQt5.QtCore import QObject, pyqtSignal

# Để sử dụng Selenium, bạn cần: pip install selenium
# Và tải về WebDriver tương ứng với trình duyệt của bạn (ví dụ: chromedriver)
# from selenium import webdriver
# from selenium.webdriver.common.by import By

class ScannerWorker(QObject):
    log_updated = pyqtSignal(str)
    scan_finished = pyqtSignal(list)
    progress_updated = pyqtSignal(int, int)

    def __init__(self, base_url, cookie=None): # NÂNG CẤP: Thêm tham số cookie
        super().__init__()
        
        parsed_url = urlparse(base_url)
        if not parsed_url.scheme: base_url = "http://" + base_url
        self.base_url = base_url
        
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'EthicalScanner/1.0'})

        # --- NÂNG CẤP QUAN TRỌNG NHẤT: SỬ DỤNG COOKIE ---
        self.cookie_string = cookie
        if self.cookie_string:
            self.session.headers.update({'Cookie': self.cookie_string})
            # self.log_updated.emit(f"[INFO] Using Cookie for authenticated scan.") # Gửi log ra ngoài, nhưng sẽ làm ở hàm run_scan

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
        if self.cookie_string:
            self.log_updated.emit(f"[INFO] Using Cookie for authenticated scan.")
            
        self._crawl(self.base_url)
        
        self.tasks_to_run.extend(list(self.scanned_links))
        self.tasks_to_run.extend(list(self.scanned_forms))
        
        self.log_updated.emit(f"[INFO] Crawling complete. Found {len(self.tasks_to_run)} unique items to test.")
        
        total_tasks = len(self.tasks_to_run)
        for i, task in enumerate(self.tasks_to_run):
            self.progress_updated.emit(i + 1, total_tasks)
            if isinstance(task, str):
                self.log_updated.emit(f"-> Testing GET URL: {task}")
                self._scan_get_url(task)
            elif isinstance(task, tuple):
                form_details = dict(task)
                self.log_updated.emit(f"-> Testing POST Form on: {form_details['action']}")
                self._scan_post_form(form_details)
        
        self.log_updated.emit(f"[INFO] Scan finished. Found {len(self.vulnerabilities_found)} vulnerabilities.")
        self.scan_finished.emit(self.vulnerabilities_found)

    def _crawl(self, url):
        url = url.split('?')[0].split('#')[0]
        if url in self.scanned_links or not url.startswith(self.base_url):
            return
        
        self.log_updated.emit(f"[CRAWL] Discovering on: {url}")
        self.scanned_links.add(url)
        
        try:
            res = self.session.get(url, timeout=5, verify=False)
            soup = BeautifulSoup(res.content, 'html.parser')
            
            for anchor in soup.find_all('a', href=True):
                self._crawl(urljoin(self.base_url, anchor['href']))
            
            for form in soup.find_all('form'):
                action = form.get('action')
                method = form.get('method', 'get').lower()
                form_action_url = urljoin(self.base_url, action)
                
                if method == 'post':
                    form_details = {"action": form_action_url, "method": "post", "inputs": []}
                    for input_tag in form.find_all(['input', 'textarea', 'select']):
                        if input_tag.get('name'):
                            input_details = {"name": input_tag.get('name'), "type": input_tag.get('type', 'text'), "value": input_tag.get('value', '')}
                            form_details["inputs"].append(tuple(input_details.items()))
                    form_details["inputs"] = tuple(form_details["inputs"])
                    form_tuple = tuple(form_details.items())
                    if form_tuple not in self.scanned_forms: self.scanned_forms.add(form_tuple)
        except requests.RequestException as e:
            self.log_updated.emit(f"[WARN] Failed to crawl {url}: {e}")
    
    def _scan_get_url(self, url):
        parsed_url = urlparse(url)
        original_params = parse_qs(parsed_url.query)
        if not original_params:
                return  # Bỏ qua nếu không có tham số

        for param_name in original_params.keys():
                original_value = original_params[param_name][0]

                # === 1. GIỮ NGUYÊN PHẦN TEST XSS (KHÔNG ĐỘNG VÀO) ===
                for payload in self.xss_payloads:
                        test_params = original_params.copy()
                        test_params[param_name] = [payload]
                        test_url = parsed_url._replace(query=urlencode(test_params, doseq=True)).geturl()
                        try:
                                res = self.session.get(test_url, timeout=5, verify=False)
                                if payload in res.text:
                                        self._add_vulnerability("Reflected XSS", test_url, param_name, payload)
                                        break  # Tìm thấy XSS → dừng payload XSS
                        except requests.RequestException:
                                pass

                # === 2. THÊM PHẦN TEST SQLi MẠNH HƠN (SAU XSS) ===
                self.log_updated.emit(f"[TEST] Scanning SQLi on parameter: {param_name} = {original_value}")

                for payload in self.sql_payloads:
                        # Kiểu 1: Nối payload vào sau giá trị gốc (rất quan trọng!)
                        test_val = original_value + payload
                        test_params = original_params.copy()
                        test_params[param_name] = [test_val]
                        test_url = parsed_url._replace(query=urlencode(test_params, doseq=True)).geturl()

                        if self._test_time_based(test_url):
                                self._add_vulnerability("Time-Based SQLi (GET)", test_url, param_name, payload)
                                break  # Tìm thấy SQLi → dừng payload SQLi

                        # Kiểu 2: Thay hoàn toàn giá trị (dành cho numeric hoặc không cần nối)
                        test_params[param_name] = [payload]
                        test_url = parsed_url._replace(query=urlencode(test_params, doseq=True)).geturl()

                        if self._test_time_based(test_url):
                                self._add_vulnerability("Time-Based SQLi (GET)", test_url, param_name, payload)
                                break
    def _test_time_based(self, url, data=None):
        start_time = time.time()
        try:
                if data:
                        self.session.post(url, data=data, timeout=12, verify=False)
                else:
                        self.session.get(url, timeout=12, verify=False)
        except requests.exceptions.ReadTimeout:
                elapsed = time.time() - start_time
                if elapsed >= 2.8:  # SLEEP(3) → chờ ít nhất 2.8s
                        return True
        except:
                pass
        return False
    def _scan_post_form(self, form_details):
        target_url = form_details['action']
        inputs = [dict(inp) for inp in form_details['inputs']]
        
        for input_to_test in inputs:
            original_data = {}
            for inp in inputs:
                if inp['type'].lower() in ['submit', 'button', 'reset']: continue
                original_data[inp['name']] = inp.get('value', 'test')

            # Quét XSS
            for payload in self.xss_payloads:
                data = original_data.copy(); data[input_to_test['name']] = payload
                try:
                    res = self.session.post(target_url, data=data, timeout=5, verify=False)
                    if payload in res.text:
                        self._add_vulnerability("Stored/Reflected XSS (POST)", target_url, input_to_test['name'], payload, method="POST", data=original_data)
                        break
                except requests.RequestException: pass

            # Quét SQL Injection
            for payload in self.sql_payloads:
                data = original_data.copy()
                payloads_to_try = [original_data.get(input_to_test['name'], '') + payload, payload]
                for p in payloads_to_try:
                    data[input_to_test['name']] = p
                    start_time = time.time()
                    try:
                        self.session.post(target_url, data=data, timeout=10, verify=False)
                    except requests.exceptions.ReadTimeout:
                        if time.time() - start_time >= 4.5:
                            self._add_vulnerability("Time-Based SQLi (POST)", target_url, input_to_test['name'], payload, method="POST", data=original_data)
                            return

    def _add_vulnerability(self, vuln_type, url, parameter, payload, method="GET", data=None):
        vulnerability = {
            "type": vuln_type, "url": url, "parameter": parameter, "payload": payload,
            "method": method, "data": data,
        }
        # Kiểm tra để tránh thêm trùng lặp
        for existing_vuln in self.vulnerabilities_found:
            if all(existing_vuln.get(k) == v for k, v in vulnerability.items() if k != 'payload'):
                return # Lỗi tương tự đã tồn tại
        self.vulnerabilities_found.append(vulnerability)
        self.log_updated.emit(f"[VULN] Found {vuln_type} at {url.split('?')[0]} on parameter '{parameter}'")

    def _crawl_with_selenium(self, url):
        """
        VÍ DỤ NÂNG CAO: Hàm crawl sử dụng Selenium để xử lý JavaScript.
        Để sử dụng, bạn cần cài đặt selenium và tải webdriver.
        Sau đó, bạn có thể thay thế lệnh gọi self._crawl() trong run_scan() bằng hàm này.
        """
        self.log_updated.emit("[INFO] Using Selenium crawler for JS-heavy pages...")
        
        # Cấu hình để chạy trình duyệt ở chế độ headless (không hiện cửa sổ)
        # options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        # driver = webdriver.Chrome(options=options)
        
        # try:
        #     driver.get(url)
            
        #     # Thêm cookie vào phiên của trình duyệt
        #     if self.cookie_string:
        #         # Selenium cần cookie ở dạng dictionary
        #         # Giả sử cookie là 'name=value'
        #         if '=' in self.cookie_string:
        #             name, value = self.cookie_string.split('=', 1)
        #             driver.add_cookie({'name': name, 'value': value})
        #             driver.refresh() # Tải lại trang với cookie mới
            
        #     # Chờ một chút để JavaScript có thể tải xong
        #     time.sleep(3) 

        #     # Lấy tất cả các link
        #     links = driver.find_elements(By.TAG_NAME, 'a')
        #     for link in links:
        #         href = link.get_attribute('href')
        #         if href:
        #             self._crawl(urljoin(self.base_url, href)) # Vẫn dùng crawler cũ để quét đệ quy
        # finally:
        #     driver.quit()
        pass
