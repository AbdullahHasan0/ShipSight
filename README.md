# ShipSight

**Convert your running projects into shareable proof (visuals + narrative) automatically.**

ShipSight is a CLI tool that analyzes your codebase, captures screenshots of your running application, and generates professional documentation (README, LinkedIn posts, code snapshots) - all automatically.

## Features

### 🎯 Multi-Framework Support
- **Node.js**: Next.js, Vite, React, Vue, and more
- **Python**: FastAPI, Flask, Django
- **Flutter**: Web, Mobile, Desktop
- **Docker**: Docker Compose projects

### 📸 Automated Capture
- **Screenshots**: High-resolution 2x captures of your running app
- **Route Discovery**: Automatically finds and captures all routes
- **Code Snapshots**: Beautiful code visualizations via Carbon

### 🤖 AI-Powered Documentation
- **README Generation**: Professional project documentation
- **LinkedIn Posts**: Shareable social media content
- **Tech Stack Analysis**: Automatic framework and dependency detection

### 🚀 Execution Modes
- **Full Mode**: Runs your app, captures screenshots, generates docs
- **Static Mode**: Code-only analysis (no execution required)
- **Fallback**: Automatic static mode on startup failures

### 🛡️ Smart Detection
- **Framework Auto-Detection**: Identifies FastAPI, Flask, Django, Next.js, Vite, Flutter
- **CLI Tool Recognition**: Distinguishes between web apps, CLI tools, and libraries
- **Project DNA**: Detects project type (Mobile, Web, CLI, Backend) to tailor AI content
- **Smart Provider Detection**: Auto-switches AI provider if API keys are found in environment variables
- **Port Discovery**: Automatically finds the correct port for your app

## Installation

### Prerequisites
- Python 3.11+
- Node.js (for Node.js projects)
- Flutter SDK (for Flutter projects, optional)

### Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/shipsight.git
cd shipsight

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Install Playwright browsers (for screenshots)
playwright install chromium
```

### Configure API Keys

ShipSight uses AI providers for documentation generation. You can configure API keys in two ways:

#### Option 1: Environment Variables (.env file) - Recommended

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API key(s)
# Choose at least one provider:
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

#### Option 2: CLI Command

```bash
# Option 1: OpenAI
shipsight auth --openai YOUR_OPENAI_API_KEY

# Option 2: Anthropic
shipsight auth --anthropic YOUR_ANTHROPIC_API_KEY

# Option 3: Groq (free tier available)
shipsight auth --groq YOUR_GROQ_API_KEY
```

**Note**: Environment variables (.env) take precedence over CLI configuration.

#### Smart Provider Detection

ShipSight automatically detects which provider to use based on your API keys. 
- If you add `OPENAI_API_KEY`, it auto-switches to OpenAI (uses GPT-4).
- If you add `ANTHROPIC_API_KEY`, it auto-switches to Anthropic (uses Claude 3).
- **Default**: Without keys, it defaults to local Ollama.

## Examples

Here are real examples of ShipSight output:

### Next.js Application Screenshot

ShipSight automatically captures your running application:

![Next.js App Screenshot](examples/nextjs_screenshot.png)
*Captured from a Next.js application with multiple routes*

### Code Visualizations

Beautiful, syntax-highlighted code snapshots with vibrant themes:

**TypeScript Code:**

![TypeScript Code Visual](examples/code_visual_typescript.png)
*Database configuration with Drizzle ORM - Monokai theme*

**Dart/Flutter Code:**

![Dart Code Visual](examples/code_visual_dart.png)
*Flutter ViewModel with state management - Colorful syntax highlighting*

### Generated Documentation

ShipSight generates professional READMEs and LinkedIn posts automatically. Check the `shipsight_output/` directory after running to see:
- `README.generated.md` - Professional project documentation
- `linkedin.post.md` - Shareable social media content
- `code_visuals/` - Beautiful code snapshots
- `screenshots/` - High-resolution app captures

## Usage

### Basic Usage

```bash
# Analyze a project (auto-detects framework)
shipsight run /path/to/your/project

# Use static mode (no execution, code-only analysis)
shipsight run /path/to/your/project --static
```

### Examples

#### FastAPI Project
```bash
shipsight run ./my-fastapi-app
# Detects: FastAPI
# Runs: uvicorn main:app --port 8000
# Captures: Screenshots at http://localhost:8000
```

#### Flask Project
```bash
shipsight run ./my-flask-app
# Detects: Flask
# Runs: python main.py or flask run
# Captures: Screenshots at http://localhost:5000
```

#### Next.js Project
```bash
shipsight run ./my-nextjs-app
# Detects: Next.js
# Runs: npm run dev
# Captures: Screenshots at http://localhost:3000
```

#### Flutter Web Project
```bash
shipsight run ./my-flutter-app
# Detects: Flutter
# Runs: flutter run -d web-server --web-port 8080
# Captures: Screenshots at http://localhost:8080
```

#### Flutter Mobile (Static Mode)
```bash
shipsight run ./my-flutter-mobile-app --static
# Analyzes Dart code without execution
# Generates README from code structure
```

### Custom Configuration

Create a `shipsight.yml` in your project root:

```yaml
run:
  strategy: local  # or 'docker' or 'static'
  port: 8000
  command: uvicorn main:app --port 8000

capture:
  routes:
    - /
    - /api/docs
    - /dashboard

output:
  path: shipsight_output

ai:
  provider: openai  # or 'anthropic' or 'groq'
  model: gpt-4o-mini
```

## Output

ShipSight generates the following in `shipsight_output/`:

```
shipsight_output/
├── README.generated.md      # Professional project README
├── linkedin.post.md         # Shareable LinkedIn post
├── metadata.json            # Project analysis data
├── screenshots/             # High-res app screenshots
│   ├── index.png
│   └── ...
└── code_snapshots/          # Beautiful code visualizations
    ├── main.py.png
    └── ...
```

## Advanced Features

### Automatic Static Fallback

If your project fails to start, ShipSight automatically offers static mode:

```
Project process terminated prematurely (Exit Code: 1).
Execution Engine failed to start project.
Last 15 lines of project_startup.log:
[error details]

Would you like to try running in Static Mode (analysis only)? [Y/n]:
```

### CLI Tool Detection

ShipSight intelligently detects CLI tools and libraries (via `console_scripts` in `pyproject.toml`) and won't try to run them as web services.

### Enhanced Intelligence for Complex Projects

- Analyzes up to 100 files for comprehensive understanding
- Prioritizes architectural code (features, services, API layers)
- Generates detailed documentation for multi-module projects

## Supported Project Types

| Type | Detection | Execution | Static Mode |
|------|-----------|-----------|-------------|
| FastAPI | `requirements.txt` with `fastapi` | ✅ uvicorn | ✅ |
| Flask | `requirements.txt` with `flask` | ✅ python/flask run | ✅ |
| Django | `requirements.txt` with `django` | ✅ manage.py runserver | ✅ |
| Next.js | `package.json` with `next` | ✅ npm run dev | ✅ |
| Vite | `package.json` with `vite` | ✅ npm run dev | ✅ |
| Flutter Web | `pubspec.yaml` | ✅ flutter run -d web-server | ✅ |
| Flutter Mobile | `pubspec.yaml` | ❌ | ✅ |
| CLI Tools | `console_scripts` in pyproject.toml | ❌ | ✅ |
| Docker | `docker-compose.yml` | ✅ docker-compose up | ✅ |

## Troubleshooting

### "No run command specified or detected"

**Cause**: Old `shipsight.yml` from before framework detection improvements.

**Solution**: Delete `shipsight.yml` and run again:
```bash
rm shipsight.yml  # or del shipsight.yml on Windows
shipsight run .
```

### "flutter is not recognized"

**Cause**: Flutter SDK not installed or not in PATH.

**Solution**: Use static mode:
```bash
shipsight run . --static
```

### API Token Limits (Groq 413 Error)

**Cause**: Large codebase exceeds Groq's free tier token limit.

**Solution**: Use OpenAI or Anthropic:
```bash
shipsight auth --openai YOUR_KEY
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Roadmap & Future Work

### 🌐 Framework Support
- [ ] **Ruby on Rails** - Full Rails application support
- [ ] **Go** - Gin, Echo, Fiber framework detection
- [ ] **Rust** - Actix, Rocket web framework support
- [ ] **PHP** - Laravel, Symfony detection
- [ ] **Java/Kotlin** - Spring Boot support
- [ ] **Swift** - Vapor framework for server-side Swift
- [ ] **C#/.NET** - ASP.NET Core support

### ✨ Features
- [ ] **Manual Screenshot Mode** - Upload your own screenshots for mobile apps
- [ ] **Video Recording** - Capture user flows and interactions as video
- [ ] **Multi-Page Analysis** - Automatically discover and capture all routes
- [ ] **Dark/Light Mode Detection** - Capture both themes automatically
- [ ] **Responsive Screenshots** - Mobile, tablet, desktop viewports
- [ ] **Interactive Demos** - Generate interactive HTML demos
- [ ] **Changelog Generation** - Auto-generate changelogs from git history
- [ ] **Architecture Diagrams** - Auto-generate system architecture diagrams

### 🔗 Integrations
- [ ] **CI/CD Pipelines** - GitHub Actions, GitLab CI, CircleCI integration
- [ ] **Cloud Deployment Guides** - AWS, GCP, Azure, Vercel, Netlify
- [ ] **Package Registries** - Auto-publish to npm, PyPI, crates.io
- [ ] **Documentation Platforms** - Sync to GitBook, ReadTheDocs, Docusaurus
- [ ] **Social Media** - Auto-post to Twitter, LinkedIn, Dev.to
- [ ] **Portfolio Sites** - Export to portfolio builders

### ⚡ Quality & Performance
- [ ] **Parallel Screenshot Capture** - Faster multi-route capture
- [ ] **Smart Caching** - Cache unchanged code snapshots
- [ ] **Incremental Analysis** - Only re-analyze changed files
- [ ] **Custom Themes** - User-defined code visualization themes
- [ ] **Multi-Language READMEs** - Generate docs in multiple languages
- [ ] **SEO Optimization** - Generate SEO-friendly documentation

### 📚 Documentation & Developer Experience
- [ ] **Interactive Tutorial** - Built-in walkthrough for new users
- [ ] **VS Code Extension** - Run ShipSight from within VS Code
- [ ] **Web Dashboard** - Visual interface for configuration
- [ ] **Template Library** - Pre-built templates for different project types
- [ ] **Plugin System** - Allow custom analyzers and generators

### 🎨 Code Visualization Enhancements
- [ ] **More Themes** - GitHub, Solarized, Atom, Material themes
- [ ] **Custom Fonts** - Support for JetBrains Mono, Cascadia Code
- [ ] **Annotations** - Highlight specific lines with comments
- [ ] **Diff Visualization** - Show before/after code changes
- [ ] **Dependency Graphs** - Visualize project dependencies

### 🤖 AI Enhancements
- [ ] **Local LLM Support** - Better Ollama integration
- [ ] **Custom Prompts** - User-defined documentation styles
- [ ] **Multi-Model Consensus** - Use multiple AI models for better quality
- [ ] **Code Review** - AI-powered code quality analysis
- [ ] **Security Scanning** - Identify potential vulnerabilities

---

**Want to contribute?** Check out our [Contributing Guide](CONTRIBUTING.md) or pick an item from the roadmap!

---

**Built with ❤️ to help developers ship faster and showcase their work.**
