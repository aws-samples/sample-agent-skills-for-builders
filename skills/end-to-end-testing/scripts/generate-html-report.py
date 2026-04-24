#!/usr/bin/env python3
"""
HTML Test Report Generator

Automatically generates an interactive HTML report from test artifacts in a timestamped directory.

Usage:
    python generate-html-report.py <test-reports-directory>

Example:
    python generate-html-report.py test-reports/2025-11-13_143022

The script will:
1. Parse test-summary-report.md for executive summary and statistics
2. Parse all test-case-reports/*.md for test case details
3. Parse all defect-reports/*.md for defect information
4. Scan screenshots/ directory for all images
5. Scan logs/ directory for all log files
6. Generate Test_Report_Viewer.html with all data populated
"""

import os
import sys
import re
import glob
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


class TestReport:
    """Container for test report data"""

    def __init__(self):
        self.title = "Test Execution Report"
        self.test_version = "Unknown"
        self.executive_summary = ""
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.blocked_tests = 0
        self.not_run_tests = 0
        self.test_cases = []
        self.defects = []
        self.screenshots = []
        self.logs = []
        self.environment_info = {}
        self.module_coverage = []


class TestCase:
    """Test case data structure"""

    def __init__(self):
        self.id = ""
        self.title = ""
        self.status = ""  # Pass, Fail, Blocked, Not Run
        self.module = ""
        self.priority = ""
        self.steps = []
        self.expected = ""
        self.actual = ""
        self.execution_time = ""
        self.screenshots = []  # List of screenshot paths related to this test case
        self.api_error_logs = []  # List of API error log file paths


class Defect:
    """Defect data structure"""

    def __init__(self):
        self.id = ""
        self.summary = ""
        self.severity = ""
        self.priority = ""
        self.status = ""
        self.module = ""
        self.description = ""
        self.file_path = ""


def parse_markdown_file(file_path: str) -> Dict[str, str]:
    """Parse markdown file and extract sections"""

    if not os.path.exists(file_path):
        return {}

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    sections = {}

    # Extract YAML frontmatter if present
    frontmatter_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        for line in frontmatter.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                sections[key.strip()] = value.strip()

    return {'content': content, 'sections': sections}


def parse_test_summary(file_path: str) -> Tuple[str, Dict]:
    """Parse test-summary-report.md"""

    data = parse_markdown_file(file_path)
    content = data.get('content', '')

    # Extract executive summary (Section 1)
    exec_summary_match = re.search(
        r'##\s*(?:1\.|Executive Summary)(.*?)(?=##|\Z)',
        content,
        re.DOTALL
    )
    executive_summary = exec_summary_match.group(1).strip() if exec_summary_match else ""

    # Extract statistics
    stats = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'blocked': 0
    }

    # Look for statistics table or numbers
    stats_patterns = [
        r'Total.*?:?\s*(\d+)',
        r'Passed.*?:?\s*(\d+)',
        r'Failed.*?:?\s*(\d+)',
        r'Blocked.*?:?\s*(\d+)'
    ]

    for i, pattern in enumerate(stats_patterns):
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            key = ['total', 'passed', 'failed', 'blocked'][i]
            stats[key] = int(match.group(1))

    return executive_summary, stats


def parse_test_case(file_path: str) -> TestCase:
    """Parse individual test case report"""

    tc = TestCase()
    data = parse_markdown_file(file_path)
    content = data.get('content', '')

    # Extract test case ID from filename
    filename = os.path.basename(file_path)
    tc_id_match = re.match(r'(TC-\d+)', filename)
    if tc_id_match:
        tc.id = tc_id_match.group(1)

    # Extract title
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        tc.title = title_match.group(1).strip()

    # Extract status
    status_match = re.search(r'\*\*Status\*\*:?\s*(.+?)(?:\n|$)', content)
    if status_match:
        tc.status = status_match.group(1).strip()

    # Extract module
    module_match = re.search(r'\*\*Module\*\*:?\s*(.+?)(?:\n|$)', content)
    if module_match:
        tc.module = module_match.group(1).strip()

    # Extract priority
    priority_match = re.search(r'\*\*Priority\*\*:?\s*(.+?)(?:\n|$)', content)
    if priority_match:
        tc.priority = priority_match.group(1).strip()

    return tc


def parse_defect(file_path: str) -> Defect:
    """Parse defect report"""

    defect = Defect()
    data = parse_markdown_file(file_path)
    content = data.get('content', '')

    # Extract defect ID from filename
    filename = os.path.basename(file_path)
    defect_id_match = re.match(r'(DEFECT-\d+)', filename)
    if defect_id_match:
        defect.id = defect_id_match.group(1)

    defect.file_path = os.path.basename(file_path)

    # Extract summary/title
    title_match = re.search(r'^#\s+(?:🐞\s+)?(?:Defect Report:?\s+)?(.+)$', content, re.MULTILINE)
    if title_match:
        defect.summary = title_match.group(1).strip()

    # Extract severity
    severity_match = re.search(r'\*\*Severity\*\*:?\s*(.+?)(?:\n|$|\|)', content)
    if severity_match:
        defect.severity = severity_match.group(1).strip()

    # Extract priority
    priority_match = re.search(r'\*\*Priority\*\*:?\s*(.+?)(?:\n|$|\|)', content)
    if priority_match:
        defect.priority = priority_match.group(1).strip()

    # Extract status
    status_match = re.search(r'\*\*Status\*\*:?\s*(.+?)(?:\n|$|\|)', content)
    if status_match:
        defect.status = status_match.group(1).strip()

    # Extract module
    module_match = re.search(r'\*\*Module\*\*:?\s*(.+?)(?:\n|$|\|)', content)
    if module_match:
        defect.module = module_match.group(1).strip()

    return defect


def collect_screenshots(directory: str) -> List[str]:
    """Collect all screenshot files"""

    screenshots = []
    screenshot_dir = os.path.join(directory, 'screenshots')

    if os.path.exists(screenshot_dir):
        for ext in ['*.png', '*.jpg', '*.jpeg']:
            screenshots.extend(glob.glob(os.path.join(screenshot_dir, ext)))

    # Sort by filename (numerical if numbered)
    def sort_key(path):
        basename = os.path.basename(path)
        num_match = re.match(r'(\d+)', basename)
        if num_match:
            return (int(num_match.group(1)), basename)
        return (float('inf'), basename)

    screenshots.sort(key=sort_key)

    # Return relative paths
    return [os.path.join('screenshots', os.path.basename(s)) for s in screenshots]


def collect_logs(directory: str) -> List[Tuple[str, int]]:
    """Collect all log files with their sizes"""

    logs = []
    log_dir = os.path.join(directory, 'logs')

    if os.path.exists(log_dir):
        for ext in ['*.log', '*.txt', '*.json']:
            for log_file in glob.glob(os.path.join(log_dir, ext)):
                size = os.path.getsize(log_file)
                rel_path = os.path.join('logs', os.path.basename(log_file))
                logs.append((rel_path, size))

    logs.sort()
    return logs


def link_screenshots_to_testcases(test_cases: List[TestCase], screenshots: List[str]) -> None:
    """
    Link screenshots to test cases based on filename patterns.

    Patterns recognized:
    - Numbered with TC prefix: 05_TC-003_payment_error.png -> TC-003
    - tc followed by numbers: 04_tc11_package_list.png -> TC-011 (or TC-11)
    - Simple TC-ID pattern: TC-001_login.png -> TC-001
    """

    for screenshot in screenshots:
        basename = os.path.basename(screenshot)

        # Pattern 1: Look for TC-XXX or TC-XX in filename
        tc_match = re.search(r'TC-?(\d+)', basename, re.IGNORECASE)
        if tc_match:
            tc_num = tc_match.group(1).zfill(3)  # Pad to 3 digits: 1 -> 001
            tc_id = f"TC-{tc_num}"

            # Find matching test case
            for tc in test_cases:
                if tc.id == tc_id or tc.id.replace('-', '').upper() == tc_id.replace('-', '').upper():
                    tc.screenshots.append(screenshot)
                    break

        # Pattern 2: Look for _tcXX pattern (e.g., 04_tc11_package_list.png)
        tc_match_lower = re.search(r'_tc(\d+)_', basename, re.IGNORECASE)
        if tc_match_lower:
            tc_num = tc_match_lower.group(1).zfill(3)
            tc_id = f"TC-{tc_num}"

            for tc in test_cases:
                # Flexible matching
                if tc.id == tc_id or tc.id.replace('-', '').replace('.', '').upper() == f"TC{tc_num}":
                    if screenshot not in tc.screenshots:  # Avoid duplicates
                        tc.screenshots.append(screenshot)
                    break


def link_api_logs_to_testcases(test_cases: List[TestCase], logs: List[Tuple[str, int]]) -> None:
    """
    Link API error log files to test cases based on filename patterns.

    Expected pattern: api_error_TC-XXX_description.json
    """

    for log_path, _ in logs:
        basename = os.path.basename(log_path)

        # Only process API error logs
        if not basename.startswith('api_error_'):
            continue

        # Extract TC-XXX pattern
        tc_match = re.search(r'TC-?(\d+)', basename, re.IGNORECASE)
        if tc_match:
            tc_num = tc_match.group(1).zfill(3)
            tc_id = f"TC-{tc_num}"

            # Find matching test case
            for tc in test_cases:
                if tc.id == tc_id or tc.id.replace('-', '').upper() == tc_id.replace('-', '').upper():
                    tc.api_error_logs.append(log_path)
                    break


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""

    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def generate_test_case_html(tc: TestCase) -> str:
    """Generate HTML for a single test case with inline screenshots and API logs"""

    status_class = 'pass' if tc.status.lower() == 'pass' else 'blocked'
    status_emoji = '✅ PASS' if tc.status.lower() == 'pass' else '⚠️ BLOCKED'

    html = f'''
                <div class="test-case">
                    <div class="test-case-header" onclick="toggleTestCase(this)">
                        <div class="test-case-title">
                            <span class="toggle-icon"></span>
                            <span>{tc.id}: {tc.title}</span>
                        </div>
                        <span class="status-badge {status_class}">{status_emoji}</span>
                    </div>
                    <div class="test-case-body">
                        <div class="info-grid">'''

    # Add info items
    if tc.module:
        html += f'''
                            <div class="info-item">
                                <div class="label">Module</div>
                                <div class="value">{tc.module}</div>
                            </div>'''

    if tc.priority:
        html += f'''
                            <div class="info-item">
                                <div class="label">Priority</div>
                                <div class="value">{tc.priority}</div>
                            </div>'''

    if tc.execution_time:
        html += f'''
                            <div class="info-item">
                                <div class="label">Execution Time</div>
                                <div class="value">{tc.execution_time}</div>
                            </div>'''

    html += '''
                        </div>'''

    # Add test description/summary placeholder
    html += f'''
                        <p><strong>Test Case:</strong> {tc.title}</p>'''

    # Add API error logs if present (for failed/blocked tests)
    if tc.api_error_logs:
        html += '''
                        <!-- API Error Log Section -->
                        <div class="api-error-log">
                            <h4>API Error Details</h4>'''

        for log_file in tc.api_error_logs:
            html += f'''
                            <div class="api-log-viewer">
                                <div class="api-log-section">
                                    <div class="api-log-label">LOG FILE:</div>
                                    <p>See <a href="{log_file}" target="_blank" style="color: #856404; text-decoration: underline;">{os.path.basename(log_file)}</a> for complete API request/response details</p>
                                </div>
                            </div>'''

        html += '''
                        </div>'''

    # Add inline screenshots if present
    if tc.screenshots:
        html += '''
                        <!-- Inline Screenshots Section -->
                        <div class="test-screenshots">
                            <h4>📸 Test Execution Screenshots</h4>
                            <div class="inline-screenshot-grid">'''

        for screenshot in tc.screenshots:
            basename = os.path.basename(screenshot)
            # Extract number prefix if present
            num_match = re.match(r'(\d+)[_\-]', basename)
            caption = f"{num_match.group(1)}: {basename}" if num_match else basename

            html += f'''
                                <div class="inline-screenshot" onclick="openModal('{screenshot}')">
                                    <img src="{screenshot}" alt="{basename}" onerror="this.parentElement.innerHTML='<div style=\\'padding:20px;text-align:center;color:#999;\\'>{basename}<br>Image not found</div>'">
                                    <div class="caption">{caption}</div>
                                </div>'''

        html += '''
                            </div>
                        </div>'''

    html += '''
                    </div>
                </div>'''

    return html


def generate_html_report(report: TestReport, output_path: str, template_path: str):
    """Generate HTML report from template"""

    # Read the template
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Update title
    html = re.sub(
        r'<title>.*?</title>',
        f'<title>{report.title}</title>',
        html
    )

    # Update header title
    html = re.sub(
        r'<div class="header">.*?<h1>(.*?)</h1>',
        f'<div class="header">\n            <h1>{report.title}</h1>',
        html,
        flags=re.DOTALL
    )

    # Update statistics
    html = re.sub(
        r'<div class="stat-card total">.*?<div class="number">(\d+)</div>',
        f'<div class="stat-card total">\n                    <div class="number">{report.total_tests}</div>',
        html,
        flags=re.DOTALL
    )

    html = re.sub(
        r'<div class="stat-card passed">.*?<div class="number">(\d+)</div>',
        f'<div class="stat-card passed">\n                    <div class="number">{report.passed_tests}</div>',
        html,
        flags=re.DOTALL
    )

    html = re.sub(
        r'<div class="stat-card failed">.*?<div class="number">(\d+)</div>',
        f'<div class="stat-card failed">\n                    <div class="number">{report.failed_tests}</div>',
        html,
        flags=re.DOTALL
    )

    html = re.sub(
        r'<div class="stat-card blocked">.*?<div class="number">(\d+)</div>',
        f'<div class="stat-card blocked">\n                    <div class="number">{report.blocked_tests}</div>',
        html,
        flags=re.DOTALL
    )

    # Update executive summary
    if report.executive_summary:
        summary_html = report.executive_summary.replace('\n', '<br>\n                ')
        html = re.sub(
            r'<div id="summary" class="tab-content active">.*?<p>(.*?)</p>',
            f'<div id="summary" class="tab-content active">\n                <h2>Executive Summary</h2>\n                <p>{summary_html}</p>',
            html,
            flags=re.DOTALL
        )

    # Generate screenshots HTML
    if report.screenshots:
        screenshots_html = '\n'.join([
            f'''                    <div class="screenshot-card" onclick="openModal('{screenshot}')">
                        <img src="{screenshot}" alt="{os.path.basename(screenshot)}">
                        <p>{os.path.basename(screenshot)}</p>
                    </div>'''
            for screenshot in report.screenshots
        ])

        # Replace the screenshots section
        html = re.sub(
            r'(<div id="screenshots" class="tab-content">.*?<div class="screenshot-grid">)(.*?)(</div>\s*</div>)',
            f'\\1\n{screenshots_html}\n                \\3',
            html,
            flags=re.DOTALL
        )

    # Generate logs HTML
    if report.logs:
        logs_html = '\n'.join([
            f'''                    <div class="log-entry">
                        <strong>{os.path.basename(log_path)}</strong> - {format_file_size(size)}
                        <a href="{log_path}" target="_blank" style="margin-left: 10px; color: #667eea;">View/Download</a>
                    </div>'''
            for log_path, size in report.logs
        ])

        # Replace the logs section
        html = re.sub(
            r'(<div id="logs" class="tab-content">)(.*?)(</div>\s*<!-- Modal -->)',
            f'\\1\n                <h2>Test Execution Logs</h2>\n{logs_html}\n            \\3',
            html,
            flags=re.DOTALL
        )

    # Generate test case cards for passed tests
    passed_tests = [tc for tc in report.test_cases if tc.status.lower() == 'pass']
    if passed_tests:
        passed_html = '\n'.join([generate_test_case_html(tc) for tc in passed_tests])

        # Replace the passed tests section (keep the alert, replace test cases)
        html = re.sub(
            r'(<div id="passed" class="tab-content">.*?</div>\s*)(.*?)(\s*</div>\s*<!-- Blocked Tests Tab -->)',
            f'\\1\n{passed_html}\n            \\3',
            html,
            flags=re.DOTALL
        )

    # Generate test case cards for blocked/failed tests
    blocked_tests = [tc for tc in report.test_cases if tc.status.lower() in ['blocked', 'fail', 'failed']]
    if blocked_tests:
        blocked_html = '\n'.join([generate_test_case_html(tc) for tc in blocked_tests])

        # Replace the blocked tests section (keep the alert, replace test cases)
        html = re.sub(
            r'(<div id="blocked" class="tab-content">.*?</div>\s*)(.*?)(\s*</div>\s*<!-- Defects Tab -->)',
            f'\\1\n{blocked_html}\n            \\3',
            html,
            flags=re.DOTALL
        )

    # Write the generated HTML
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ HTML report generated successfully: {output_path}")
    print(f"   Generated {len(passed_tests)} passed test case(s)")
    print(f"   Generated {len(blocked_tests)} blocked/failed test case(s)")


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate-html-report.py <test-reports-directory>")
        print("\nExample:")
        print("  python generate-html-report.py test-reports/2025-11-13_143022")
        sys.exit(1)

    test_dir = sys.argv[1]

    if not os.path.exists(test_dir):
        print(f"❌ Error: Directory not found: {test_dir}")
        sys.exit(1)

    print(f"📊 Generating HTML report from: {test_dir}")
    print()

    # Initialize report
    report = TestReport()

    # Parse test summary report
    summary_file = os.path.join(test_dir, 'test-summary-report.md')
    if os.path.exists(summary_file):
        print("📄 Parsing test summary report...")
        report.executive_summary, stats = parse_test_summary(summary_file)
        report.total_tests = stats['total']
        report.passed_tests = stats['passed']
        report.failed_tests = stats['failed']
        report.blocked_tests = stats['blocked']
    else:
        print(f"⚠️  Warning: test-summary-report.md not found")

    # Parse test case reports
    test_case_dir = os.path.join(test_dir, 'test-case-reports')
    if os.path.exists(test_case_dir):
        print("📝 Parsing test case reports...")
        for tc_file in glob.glob(os.path.join(test_case_dir, '*.md')):
            tc = parse_test_case(tc_file)
            report.test_cases.append(tc)
        print(f"   Found {len(report.test_cases)} test case(s)")
    else:
        print(f"⚠️  Warning: test-case-reports/ directory not found")

    # Parse defect reports
    defect_dir = os.path.join(test_dir, 'defect-reports')
    if os.path.exists(defect_dir):
        print("🐞 Parsing defect reports...")
        for defect_file in glob.glob(os.path.join(defect_dir, '*.md')):
            defect = parse_defect(defect_file)
            report.defects.append(defect)
        print(f"   Found {len(report.defects)} defect(s)")
    else:
        print(f"ℹ️  No defect-reports/ directory (no defects found)")

    # Collect screenshots
    print("📸 Collecting screenshots...")
    report.screenshots = collect_screenshots(test_dir)
    print(f"   Found {len(report.screenshots)} screenshot(s)")

    # Collect logs
    print("📋 Collecting log files...")
    report.logs = collect_logs(test_dir)
    print(f"   Found {len(report.logs)} log file(s)")

    # Link screenshots and API logs to test cases
    print("🔗 Linking screenshots and logs to test cases...")
    link_screenshots_to_testcases(report.test_cases, report.screenshots)
    link_api_logs_to_testcases(report.test_cases, report.logs)

    # Print linking summary
    for tc in report.test_cases:
        if tc.screenshots or tc.api_error_logs:
            print(f"   {tc.id}: {len(tc.screenshots)} screenshot(s), {len(tc.api_error_logs)} API log(s)")

    # Generate HTML
    print()
    print("🔨 Generating HTML report...")

    # Find the template
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(
        os.path.dirname(script_dir),
        'assets',
        'templates',
        'Test_Report_Viewer.html'
    )

    if not os.path.exists(template_path):
        print(f"❌ Error: Template not found: {template_path}")
        sys.exit(1)

    output_path = os.path.join(test_dir, 'Test_Report_Viewer.html')

    generate_html_report(report, output_path, template_path)

    print()
    print("=" * 60)
    print("✅ Report generation complete!")
    print(f"📂 Output: {output_path}")
    print()
    print("To view the report, open the HTML file in your web browser:")
    print(f"   file://{os.path.abspath(output_path)}")
    print("=" * 60)


if __name__ == '__main__':
    main()
