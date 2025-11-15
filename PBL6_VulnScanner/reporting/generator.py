from datetime import datetime

def generate_report(target_url, vulnerabilities):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_filename = f"report_{url_to_filename(target_url)}_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"

    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write("="*50 + "\n")
        f.write("VULNERABILITY SCAN REPORT\n")
        f.write("="*50 + "\n\n")
        f.write(f"Target URL: {target_url}\n")
        f.write(f"Scan Time: {timestamp}\n")
        f.write(f"Vulnerabilities Found: {len(vulnerabilities)}\n\n")

        if not vulnerabilities:
            f.write("No vulnerabilities found.\n")
        else:
            for i, vuln in enumerate(vulnerabilities, 1):
                f.write("-"*40 + "\n")
                f.write(f"Vulnerability #{i}\n")
                f.write("-"*40 + "\n")
                f.write(f"Type: {vuln['type']}\n")
                f.write(f"URL: {vuln['url']}\n")
                f.write(f"Parameter: {vuln['parameter']}\n")
                f.write(f"Payload Used: {vuln['payload']}\n")
                f.write(f"Evidence: {vuln['evidence']}\n\n")
                f.write("--- Mitigation ---\n")
                f.write(get_mitigation_advice(vuln['type']))
                f.write("\n\n")

    print(f"[INFO] Report generated: {report_filename}")
    return report_filename

def get_mitigation_advice(vuln_type):
    if vuln_type == "SQL Injection":
        return ("- Use Parameterized Queries (Prepared Statements) instead of string concatenation.\n"
                "- Implement input validation to allow only expected characters.\n"
                "- Apply the Principle of Least Privilege for database users.")
    elif vuln_type == "Reflected XSS":
        return ("- Implement context-aware output encoding for all user-supplied data.\n"
                "- Use a Content Security Policy (CSP) to restrict script sources.\n"
                "- Validate user input on the server side.")
    return "No specific advice available."

def url_to_filename(url):
    return "".join(c for c in url if c.isalnum() or c in ('-', '_')).rstrip()
