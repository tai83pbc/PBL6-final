import streamlit as st
import sys
import os

# Thêm đường dẫn gốc của dự án vào sys.path để import các module khác
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.scanner import VulnerabilityScanner
from reporting.generator import generate_report

def main():
    st.set_page_config(page_title="Ethical Vulnerability Scanner", layout="wide")
    
    st.title("Ethical Web Vulnerability Scanner")
    st.write("This tool is for educational purposes only. Only scan websites you have permission to test.")

    # Thay đổi ô nhập liệu để nhận URL gốc
    base_url = st.text_input("Enter the Base URL to scan (e.g., http://localhost:8003/)", "")

    if st.button("Start Scan"):
        if not base_url:
            st.error("Please enter a Base URL to scan.")
        else:
            try:
                # Khởi tạo scanner với URL gốc
                scanner = VulnerabilityScanner(base_url)
                
                status_text = st.empty()
                
                with st.spinner("Scanning in progress... This may take a while."):
                    status_text.info("Phase 1: Crawling the website to discover all links...")
                    vulnerabilities = scanner.run_scanner() # Chạy quy trình quét mới
                
                st.success("Scan Complete!")

                if vulnerabilities:
                    st.subheader(f"Found {len(vulnerabilities)} potential vulnerabilities:")
                    for vuln in vulnerabilities:
                        with st.expander(f"🔴 {vuln['type']} at {vuln['url']}"):
                            st.json(vuln)
                    
                    report_content = ""
                    report_filename = generate_report(base_url, vulnerabilities)
                    with open(report_filename, 'r', encoding='utf-8') as f:
                        report_content = f.read()
                    
                    st.download_button(
                        label="Download Full Report",
                        data=report_content,
                        file_name=report_filename,
                        mime="text/plain"
                    )
                else:
                    st.info("No vulnerabilities were found with the current payloads.")

            except Exception as e:
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
