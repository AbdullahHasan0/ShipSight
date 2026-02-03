import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

class Carbonizer:
    def __init__(self, output_dir: Path, theme: str = "monokai"):
        self.output_dir = (output_dir / "code_visuals")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.theme = theme  # monokai, dracula, nord, one-dark

    def _detect_language(self, filename: str) -> str:
        """Detect programming language from filename."""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.jsx': 'javascript',
            '.go': 'go',
            '.rs': 'rust',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.rb': 'ruby',
            '.php': 'php',
            '.dart': 'dart',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.md': 'markdown',
            '.sh': 'bash',
        }
        for ext, lang in ext_map.items():
            if filename.endswith(ext):
                return lang
        return 'plaintext'

    async def carbonize(self, code: str, filename: str):
        """Render code as a beautiful image with syntax highlighting using Highlight.js."""
        language = self._detect_language(filename)
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/{self.theme}.min.css">
            <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&display=swap');
                
                body {{
                    margin: 0;
                    padding: 60px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    font-family: 'Fira Code', 'Courier New', monospace;
                }}
                .window {{
                    background: #1e1e1e;
                    border-radius: 16px;
                    box-shadow: 
                        0 30px 90px rgba(0, 0, 0, 0.4),
                        0 0 0 1px rgba(255, 255, 255, 0.1);
                    overflow: hidden;
                    width: fit-content;
                    max-width: 900px;
                    min-width: 600px;
                }}
                .titlebar {{
                    background: linear-gradient(180deg, #3c3c3c 0%, #2d2d2d 100%);
                    padding: 14px 20px;
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    border-bottom: 1px solid #1a1a1a;
                }}
                .dots {{
                    display: flex;
                    gap: 8px;
                }}
                .dot {{
                    width: 13px;
                    height: 13px;
                    border-radius: 50%;
                    box-shadow: inset 0 1px 2px rgba(0,0,0,0.3);
                }}
                .red {{ 
                    background: linear-gradient(135deg, #ff6057 0%, #ff4136 100%);
                    border: 0.5px solid #d93025;
                }}
                .yellow {{ 
                    background: linear-gradient(135deg, #ffbd2e 0%, #ffaa00 100%);
                    border: 0.5px solid #e69500;
                }}
                .green {{ 
                    background: linear-gradient(135deg, #28ca42 0%, #20a034 100%);
                    border: 0.5px solid #1a8029;
                }}
                .filename {{
                    color: #a0a0a0;
                    font-size: 13px;
                    font-weight: 500;
                    flex-grow: 1;
                    text-align: center;
                    letter-spacing: 0.3px;
                }}
                .code-container {{
                    padding: 28px 32px;
                    background: #1e1e1e;
                    overflow-x: auto;
                }}
                pre {{
                    margin: 0;
                    font-family: 'Fira Code', 'Courier New', monospace;
                    font-size: 15px;
                    line-height: 1.6;
                    font-weight: 400;
                }}
                code {{
                    font-family: 'Fira Code', 'Courier New', monospace;
                    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
                }}
                /* Enhanced syntax highlighting colors */
                .hljs {{
                    background: transparent !important;
                    padding: 0 !important;
                }}
                .hljs-keyword,
                .hljs-selector-tag,
                .hljs-literal,
                .hljs-section,
                .hljs-link {{
                    font-weight: 600;
                }}
                .hljs-string,
                .hljs-title,
                .hljs-name,
                .hljs-type,
                .hljs-attribute,
                .hljs-symbol,
                .hljs-bullet,
                .hljs-addition,
                .hljs-variable,
                .hljs-template-tag,
                .hljs-template-variable {{
                    font-weight: 500;
                }}
            </style>
        </head>
        <body>
            <div class="window">
                <div class="titlebar">
                    <div class="dots">
                        <div class="dot red"></div>
                        <div class="dot yellow"></div>
                        <div class="dot green"></div>
                    </div>
                    <div class="filename">{filename}</div>
                </div>
                <div class="code-container">
                    <pre><code class="language-{language}">{code.replace('<', '&lt;').replace('>', '&gt;')}</code></pre>
                </div>
            </div>
            <script>
                hljs.highlightAll();
            </script>
        </body>
        </html>
        """
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport={'width': 1400, 'height': 1000})
            await page.set_content(html_template)
            
            # Wait for Highlight.js to load and syntax highlighting to apply
            await page.wait_for_timeout(500)
            
            # Screenshot the entire window
            window = await page.query_selector('.window')
            if window:
                await window.screenshot(path=str(self.output_dir / filename), scale='device')
            
            await browser.close()
