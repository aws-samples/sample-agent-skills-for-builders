#!/usr/bin/env python3
"""
Generate HTML security scan report with modern tabbed interface.
Usage: python generate-html-report.py <scan_dir>
"""

import sys
import os
import base64
from pathlib import Path

def read_file(filepath):
    """Read file content, return empty string if not exists."""
    try:
        return Path(filepath).read_text(encoding='utf-8')
    except Exception:
        return ''

def read_binary(filepath):
    """Read binary file and return base64 encoded string."""
    try:
        with open(filepath, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception:
        return ''

def escape_html(text):
    """Escape HTML special characters."""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def get_image_mime(filepath):
    """Get image MIME type from extension."""
    ext = Path(filepath).suffix.lower()
    return {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.svg': 'image/svg+xml', '.gif': 'image/gif'}.get(ext, 'image/png')

def extract_project_name(summary_md):
    """Extract project name from SUMMARY.md content."""
    import re
    # 查找 | 项目名称 | xxx | 格式
    match = re.search(r'\|\s*项目名称\s*\|\s*([^|]+)\s*\|', summary_md)
    if match:
        return match.group(1).strip()
    return None

def generate_html(scan_dir):
    """Generate the complete HTML report."""
    scan_path = Path(scan_dir)
    scan_name = scan_path.name

    # Read all content files
    summary_md = read_file(scan_path / 'SUMMARY.md')

    # Extract project name from SUMMARY.md
    project_name = extract_project_name(summary_md) or scan_name
    cdk_synth = read_file(scan_path / 'result' / 'cdk-synth.txt')
    viperlight = read_file(scan_path / 'result' / 'viperlight.txt')
    license_md = read_file(scan_path / 'result' / 'license.md')
    trivy_md = read_file(scan_path / 'result' / 'trivy.md')
    ash_md = read_file(scan_path / 'result' / 'ash' / 'ash.md')
    ash_html = read_file(scan_path / 'result' / 'ash' / 'ash.html')
    ash_yaml = read_file(scan_path / 'result' / 'ash' / 'ash.yaml')
    deploy_log = read_file(scan_path / '07-deploy' / 'output.txt')

    # Read architecture image
    arch_img = ''
    arch_mime = 'image/png'
    for ext in ['.png', '.jpg', '.jpeg', '.svg']:
        arch_path = scan_path / 'result' / f'architecture{ext}'
        if arch_path.exists():
            arch_img = read_binary(arch_path)
            arch_mime = get_image_mime(arch_path)
            break

    # Generate HTML
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Scan Report - {scan_name}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.0/marked.min.js"></script>
    <style>
        :root {{
            --bg-primary: #ffffff;
            --bg-secondary: #f6f8fa;
            --bg-tertiary: #eef1f4;
            --border-color: #d0d7de;
            --text-primary: #1f2328;
            --text-secondary: #656d76;
            --accent-blue: #0969da;
            --accent-green: #1a7f37;
            --accent-yellow: #9a6700;
            --accent-red: #cf222e;
            --accent-purple: #8250df;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
        }}

        .header {{
            background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
            border-bottom: 1px solid var(--border-color);
            padding: 24px 32px;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(10px);
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        }}

        .header h1 {{
            font-size: 24px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .header h1::before {{
            content: '🛡️';
            font-size: 28px;
        }}

        .header .scan-id {{
            font-size: 14px;
            color: var(--text-secondary);
            margin-top: 4px;
            font-family: 'SF Mono', Consolas, monospace;
        }}

        .tabs-container {{
            display: flex;
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border-color);
            padding: 0 16px;
            overflow-x: auto;
            scrollbar-width: thin;
        }}

        .tabs-container::-webkit-scrollbar {{
            height: 6px;
        }}

        .tabs-container::-webkit-scrollbar-thumb {{
            background: var(--border-color);
            border-radius: 3px;
        }}

        .tab-btn {{
            padding: 12px 20px;
            background: transparent;
            border: none;
            color: var(--text-secondary);
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            white-space: nowrap;
            position: relative;
            transition: all 0.2s ease;
        }}

        .tab-btn:hover {{
            color: var(--text-primary);
            background: var(--bg-tertiary);
        }}

        .tab-btn.active {{
            color: var(--accent-blue);
        }}

        .tab-btn.active::after {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: var(--accent-blue);
            border-radius: 2px 2px 0 0;
        }}

        .tab-btn .icon {{
            margin-right: 8px;
        }}

        .sub-tabs {{
            display: flex;
            background: var(--bg-tertiary);
            border-bottom: 1px solid var(--border-color);
            padding: 0 16px;
        }}

        .sub-tab-btn {{
            padding: 8px 16px;
            background: transparent;
            border: none;
            color: var(--text-secondary);
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
            transition: all 0.2s ease;
            border-radius: 6px 6px 0 0;
        }}

        .sub-tab-btn:hover {{
            color: var(--text-primary);
        }}

        .sub-tab-btn.active {{
            color: var(--accent-purple);
            background: var(--bg-secondary);
        }}

        .content {{
            padding: 24px 32px;
            max-width: 1400px;
            margin: 0 auto;
        }}

        .tab-content {{
            display: none;
            animation: fadeIn 0.3s ease;
        }}

        .tab-content.active {{
            display: block;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        /* Markdown Styles */
        .markdown-body {{
            color: var(--text-primary);
        }}

        .markdown-body h1 {{
            font-size: 28px;
            font-weight: 600;
            margin: 0 0 16px 0;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border-color);
        }}

        .markdown-body h2 {{
            font-size: 22px;
            font-weight: 600;
            margin: 32px 0 16px 0;
            padding-bottom: 8px;
            border-bottom: 1px solid var(--border-color);
        }}

        .markdown-body h3 {{
            font-size: 18px;
            font-weight: 600;
            margin: 24px 0 12px 0;
        }}

        .markdown-body p {{
            margin: 12px 0;
        }}

        .markdown-body table {{
            width: 100%;
            border-collapse: collapse;
            margin: 16px 0;
            font-size: 14px;
        }}

        .markdown-body th {{
            background: var(--bg-tertiary);
            padding: 12px 16px;
            text-align: left;
            font-weight: 600;
            border: 1px solid var(--border-color);
        }}

        .markdown-body td {{
            padding: 10px 16px;
            border: 1px solid var(--border-color);
        }}

        .markdown-body tr:hover td {{
            background: var(--bg-secondary);
        }}

        .markdown-body code {{
            background: var(--bg-tertiary);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'SF Mono', Consolas, monospace;
            font-size: 13px;
        }}

        .markdown-body pre {{
            background: var(--bg-tertiary);
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 16px 0;
        }}

        .markdown-body pre code {{
            background: transparent;
            padding: 0;
        }}

        .markdown-body ul, .markdown-body ol {{
            margin: 12px 0;
            padding-left: 24px;
        }}

        .markdown-body li {{
            margin: 6px 0;
        }}

        .markdown-body hr {{
            border: none;
            border-top: 1px solid var(--border-color);
            margin: 24px 0;
        }}

        .markdown-body blockquote {{
            border-left: 4px solid var(--accent-blue);
            padding-left: 16px;
            margin: 16px 0;
            color: var(--text-secondary);
        }}

        .markdown-body a {{
            color: var(--accent-blue);
            text-decoration: none;
        }}

        .markdown-body a:hover {{
            text-decoration: underline;
        }}

        /* Code Block */
        .code-block {{
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            overflow: hidden;
        }}

        .code-header {{
            background: var(--bg-secondary);
            padding: 8px 16px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .code-header span {{
            font-size: 13px;
            color: var(--text-secondary);
            font-family: 'SF Mono', Consolas, monospace;
        }}

        .code-content {{
            padding: 16px;
            overflow-x: auto;
            max-height: 70vh;
            overflow-y: auto;
        }}

        .code-content pre {{
            margin: 0;
            font-family: 'SF Mono', Consolas, monospace;
            font-size: 13px;
            line-height: 1.5;
            white-space: pre;
        }}

        /* Image Container */
        .image-container {{
            text-align: center;
            padding: 24px;
            background: var(--bg-secondary);
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }}

        .image-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 4px;
        }}

        .image-container .caption {{
            margin-top: 12px;
            color: var(--text-secondary);
            font-size: 14px;
        }}

        /* ASH HTML iframe */
        .ash-html-frame {{
            width: 100%;
            height: 80vh;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            background: #fff;
        }}

        /* Status badges */
        .status-pass {{ color: var(--accent-green); }}
        .status-fail {{ color: var(--accent-red); }}
        .status-warn {{ color: var(--accent-yellow); }}

        /* Footer */
        .footer {{
            text-align: center;
            padding: 24px;
            color: var(--text-secondary);
            font-size: 13px;
            border-top: 1px solid var(--border-color);
            margin-top: 48px;
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            .header {{ padding: 16px; }}
            .content {{ padding: 16px; }}
            .tab-btn {{ padding: 10px 14px; font-size: 13px; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Security Scan Report</h1>
        <div class="scan-id">{project_name}</div>
    </div>

    <div class="tabs-container">
        <button class="tab-btn active" data-tab="summary"><span class="icon">📋</span>Summary</button>
        <button class="tab-btn" data-tab="architecture"><span class="icon">🏗️</span>Architecture</button>
        <button class="tab-btn" data-tab="cdk-synth"><span class="icon">☁️</span>CDK Synth</button>
        <button class="tab-btn" data-tab="viperlight"><span class="icon">🔍</span>Viperlight</button>
        <button class="tab-btn" data-tab="license"><span class="icon">📜</span>License</button>
        <button class="tab-btn" data-tab="trivy"><span class="icon">🐳</span>Trivy</button>
        <button class="tab-btn" data-tab="ash"><span class="icon">🛡️</span>ASH</button>
        <button class="tab-btn" data-tab="deploy"><span class="icon">🚀</span>Deploy</button>
    </div>

    <div id="ash-subtabs" class="sub-tabs" style="display: none;">
        <button class="sub-tab-btn active" data-subtab="ash-md">ash.md</button>
        <button class="sub-tab-btn" data-subtab="ash-html">ash.html</button>
        <button class="sub-tab-btn" data-subtab="ash-yaml">ash.yaml</button>
    </div>

    <div class="content">
        <!-- Summary Tab -->
        <div id="tab-summary" class="tab-content active">
            <div class="markdown-body" id="summary-content"></div>
        </div>

        <!-- Architecture Tab -->
        <div id="tab-architecture" class="tab-content">
            <div class="image-container">
                {f'<img src="data:{arch_mime};base64,{arch_img}" alt="Architecture Diagram">' if arch_img else '<p>No architecture diagram found.</p>'}
                <div class="caption">Project Architecture Diagram</div>
            </div>
        </div>

        <!-- CDK Synth Tab -->
        <div id="tab-cdk-synth" class="tab-content">
            <div class="code-block">
                <div class="code-header">
                    <span>cdk-synth.txt</span>
                    <span>CloudFormation Template</span>
                </div>
                <div class="code-content">
                    <pre><code class="language-yaml">{escape_html(cdk_synth) if cdk_synth else 'No CDK synth output found.'}</code></pre>
                </div>
            </div>
        </div>

        <!-- Viperlight Tab -->
        <div id="tab-viperlight" class="tab-content">
            <div class="code-block">
                <div class="code-header">
                    <span>viperlight.txt</span>
                    <span>Security Scan Results</span>
                </div>
                <div class="code-content">
                    <pre><code>{escape_html(viperlight) if viperlight else 'No Viperlight output found.'}</code></pre>
                </div>
            </div>
        </div>

        <!-- License Tab -->
        <div id="tab-license" class="tab-content">
            <div class="markdown-body" id="license-content"></div>
        </div>

        <!-- Trivy Tab -->
        <div id="tab-trivy" class="tab-content">
            <div class="markdown-body" id="trivy-content"></div>
        </div>

        <!-- ASH Tab -->
        <div id="tab-ash" class="tab-content">
            <div id="subtab-ash-md" class="sub-tab-content active">
                <div class="markdown-body" id="ash-md-content"></div>
            </div>
            <div id="subtab-ash-html" class="sub-tab-content" style="display: none;">
                <iframe class="ash-html-frame" srcdoc="{escape_html(ash_html).replace(chr(34), '&quot;')}" sandbox="allow-same-origin"></iframe>
            </div>
            <div id="subtab-ash-yaml" class="sub-tab-content" style="display: none;">
                <div class="code-block">
                    <div class="code-header">
                        <span>ash.yaml</span>
                        <span>ASH Configuration</span>
                    </div>
                    <div class="code-content">
                        <pre><code class="language-yaml">{escape_html(ash_yaml) if ash_yaml else 'No ASH config found.'}</code></pre>
                    </div>
                </div>
            </div>
        </div>

        <!-- Deploy Tab -->
        <div id="tab-deploy" class="tab-content">
            <div class="code-block">
                <div class="code-header">
                    <span>deploy-output.txt</span>
                    <span>Deployment Log</span>
                </div>
                <div class="code-content">
                    <pre><code>{escape_html(deploy_log) if deploy_log else 'No deployment log found.'}</code></pre>
                </div>
            </div>
        </div>
    </div>

    <div class="footer">
        Generated by Security Scan Power | {scan_name}
    </div>

    <script>
        // Markdown content
        const markdownContent = {{
            summary: {repr(summary_md)},
            license: {repr(license_md)},
            trivy: {repr(trivy_md)},
            ashMd: {repr(ash_md)}
        }};

        // Render markdown
        function renderMarkdown(elementId, content) {{
            const element = document.getElementById(elementId);
            if (element && content) {{
                element.innerHTML = marked.parse(content);
                element.querySelectorAll('pre code').forEach((block) => {{
                    hljs.highlightElement(block);
                }});
            }}
        }}

        // Initialize markdown rendering
        document.addEventListener('DOMContentLoaded', function() {{
            marked.setOptions({{
                breaks: true,
                gfm: true
            }});

            renderMarkdown('summary-content', markdownContent.summary);
            renderMarkdown('license-content', markdownContent.license);
            renderMarkdown('trivy-content', markdownContent.trivy);
            renderMarkdown('ash-md-content', markdownContent.ashMd);

            // Highlight code blocks
            document.querySelectorAll('pre code').forEach((block) => {{
                hljs.highlightElement(block);
            }});
        }});

        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {{
            btn.addEventListener('click', function() {{
                const tabId = this.dataset.tab;

                // Update active tab button
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');

                // Update active tab content
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                document.getElementById('tab-' + tabId).classList.add('active');

                // Show/hide ASH subtabs
                const ashSubtabs = document.getElementById('ash-subtabs');
                ashSubtabs.style.display = tabId === 'ash' ? 'flex' : 'none';
            }});
        }});

        // ASH sub-tab switching
        document.querySelectorAll('.sub-tab-btn').forEach(btn => {{
            btn.addEventListener('click', function() {{
                const subtabId = this.dataset.subtab;

                // Update active sub-tab button
                document.querySelectorAll('.sub-tab-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');

                // Update active sub-tab content
                document.querySelectorAll('.sub-tab-content').forEach(c => c.style.display = 'none');
                document.getElementById('subtab-' + subtabId).style.display = 'block';
            }});
        }});
    </script>
</body>
</html>'''

    return html

def main():
    if len(sys.argv) < 2:
        print('Usage: python generate-html-report.py <scan_dir>')
        sys.exit(1)

    scan_dir = sys.argv[1]

    # Input validation: path length limit
    if len(scan_dir) > 4096:
        print('Error: Path too long (max 4096 characters)')
        sys.exit(1)

    if not Path(scan_dir).exists():
        print(f'Error: Directory not found: {scan_dir}')
        sys.exit(1)

    html = generate_html(scan_dir)

    output_path = Path(scan_dir) / 'report.html'
    output_path.write_text(html, encoding='utf-8')

    print(f'✅ HTML report generated: {output_path}')

if __name__ == '__main__':
    main()
