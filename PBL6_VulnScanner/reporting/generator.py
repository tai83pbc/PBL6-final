import os
from datetime import datetime
import html as html_module

def generate_report(target_url, vulnerabilities, exploited_data=None):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_url = "".join(c for c in target_url if c.isalnum())[:20]
    filename = f"Report_{clean_url}_{timestamp}.html"
    
    css = """
    body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #f0f2f5; padding: 30px; }
    .container { max-width: 1200px; margin: auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 5px 20px rgba(0,0,0,0.1); }
    h1 { color: #1a73e8; text-align: center; border-bottom: 2px solid #e8eaed; padding-bottom: 20px; }
    h2 { color: #d93025; border-left: 6px solid #d93025; padding-left: 15px; margin-top: 40px; }
    h3 { color: #188038; background: #e6f4ea; padding: 12px; border-radius: 8px; margin-top: 30px; }
    
    /* Style cho bảng tổng quan */
    .summary-table { width: 100%; border-collapse: collapse; margin-bottom: 40px; }
    .summary-table th { background: #5f6368; color: white; }
    .summary-table td, .summary-table th { border: 1px solid #dadce0; padding: 12px; text-align: left; }
    .summary-table tr:nth-child(even) { background: #f8f9fa; }

    /* Style cho bảng dữ liệu Records */
    .data-table { width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 0.85em; display: block; overflow-x: auto; }
    .data-table th { background: #1a73e8; color: white; white-space: nowrap; }
    .data-table td, .data-table th { border: 1px solid #dadce0; padding: 10px; text-align: left; }
    .data-table tr:hover { background: #f1f3f4; }
    
    .badge { padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; background: #e8f0fe; color: #1967d2; }
    """

    report_html = f"""<!DOCTYPE html><html><head><title>Full Vulnerability & Data Report</title><style>{css}</style></head><body>
    <div class='container'>
        <h1>Security Analysis & Data Exfiltration Report</h1>
        <p><strong>Target Site:</strong> <code style='color:#d93025'>{target_url}</code></p>
        <p><strong>Generated on:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    """

    # --- PHẦN 1: BẢNG TỔNG QUAN CẤU TRÚC (DB -> TABLES) ---
    if exploited_data:
        report_html += "<h2>📊 Part 1: Database Structure Overview</h2>"
        report_html += "<table class='summary-table'><thead><tr><th>Database Name</th><th>Included Tables</th><th>Total Records Extracted</th></tr></thead><tbody>"
        
        for db_name, tables in exploited_data.items():
            table_list = ", ".join([f"<code>{t}</code>" for t in tables.keys()])
            total_records = sum([len(content['records']) for content in tables.values()])
            report_html += f"<tr><td><strong>{db_name}</strong></td><td>{table_list}</td><td><span class='badge'>{total_records} rows</span></td></tr>"
        
        report_html += "</tbody></table>"

        # --- PHẦN 2: CHI TIẾT RECORDS TRONG TỪNG TABLE ---
        report_html += "<h2>🗄️ Part 2: Detailed Data Records</h2>"
        for db_name, tables in exploited_data.items():
            report_html += f"<div style='border: 2px solid #1a73e8; padding: 20px; margin-bottom: 30px; border-radius: 10px;'>"
            report_html += f"<h3 style='margin-top:0'>Database: {db_name}</h3>"
            
            for table_name, content in tables.items():
                record_count = len(content['records'])
                report_html += f"<p style='font-weight:bold; color:#5f6368;'>Table: <span style='color:#1a73e8'>{table_name}</span> ({record_count} records)</p>"
                
                if record_count == 0:
                    report_html += "<p><em>No data found for this table.</em></p>"
                    continue

                report_html += "<table class='data-table'><thead><tr>"
                for h in content['headers']:
                    report_html += f"<th>{html_module.escape(h)}</th>"
                report_html += "</tr></thead><tbody>"
                
                # In toàn bộ Records (giới hạn 100 dòng để tránh treo trình duyệt nếu dữ liệu quá lớn)
                for row in content['records'][:100]:
                    report_html += "<tr>"
                    for cell in row:
                        report_html += f"<td>{html_module.escape(str(cell))}</td>"
                    report_html += "</tr>"
                
                report_html += "</tbody></table>"
                if record_count > 100:
                    report_html += f"<p style='color:#70757a'><em>... {record_count - 100} more records omitted for brevity.</em></p>"
            report_html += "</div>"

    # --- PHẦN 3: DANH SÁCH LỖI HỔNG ---
    report_html += "<h2>⚠️ Part 3: Vulnerabilities Detected</h2>"
    for i, v in enumerate(vulnerabilities, 1):
        report_html += f"""
        <div style='background:#fff; border:1px solid #dadce0; padding:15px; border-radius:8px; margin-bottom:15px;'>
            <strong>#{i} {v['type']}</strong><br>
            <small>URL: {v['url']}</small><br>
            <small>Parameter: <code>{v['parameter']}</code></small>
        </div>
        """

    report_html += "</div><p style='text-align:center; color:#70757a; font-size:0.8em;'>End of Report</p></body></html>"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report_html)
    return filename
