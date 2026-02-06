# ShipSight 🚢

**Convert your running projects into shareable proof (visuals + narrative) automatically.**

ShipSight is a zero-config CLI toolkit that analyzes your codebase, captures high-resolution screenshots of your running application, and generates professional documentation—READMEs, LinkedIn posts, and beautiful code snapshots—ready for public showcase.

## 🚀 Quick Start (Zero Setup)

The easiest way to run ShipSight is using our runner scripts which handle virtual environments and dependencies automatically.

### Windows
```powershell
.\shipsight.ps1 run "C:\path\to\your\project"
```

### Linux / macOS
```bash
./shipsight.sh run "/path/to/your/project"
```

---

## ✨ Key Features

### 🧽 Context Hygiene (Loki-Aware)
ShipSight automatically cleanses your project context before sending it to the AI. It strictly ignores `.git`, `node_modules`, `.venv`, `.skills`, `tools`, and other non-essential directories to prevent hallucinations and ensure the AI focuses on **your actual code**.

### 🤖 Creator-Voice Narrative
Unlike generic AI generators, ShipSight writes from the **builder's perspective**. 
- **Authentic Tone**: No hyperbolic "revolutionary" or "groundbreaking" fluff.
- **Problem/Solution Focus**: Explains *why* you built it and *how* it works.
- **80/20 Code Focus**: 80% on features/logic, 20% on the backend stack.

### 📸 Automated Visual Proof
- **High-Res Screenshots**: 2x resolution captures of discovered routes.
- **Route Discovery**: Automatically finds active routes in your web app.
- **Carbon Visuals**: Beautiful, themeable code snapshots for your core logic.

### 📉 Token Hygiene
Smart signature extraction for large files. If a file is over 100 lines, ShipSight extracts class/function signatures only, giving the AI the architecture without the token bloat.

## 🎯 Supported Stacks

| Stack | Frameworks | Default Command |
|-------|------------|-----------------|
| **Node.js** | Next.js, Vite, React, Vue | `npm run dev` |
| **Python** | FastAPI, Flask, Django | `uvicorn` / `python main.py` |
| **Flutter** | Web, Mobile, Desktop | `flutter run -d web-server` |
| **Docker** | Compose Projects | `docker-compose up -d` |
| **CLI/Lib** | Libraries & CLI Tools | Static Analysis Only |

---

## 🛠️ Configuration

### 1. Configure API Keys
ShipSight supports OpenAI, Anthropic, and Groq. 

**Option A: .env File (Recommended)**
```bash
cp .env.example .env
# Add your OPENAI_API_KEY, ANTHROPIC_API_KEY, or GROQ_API_KEY
```

**Option B: CLI Auth**
```bash
shipsight auth --openai YOUR_KEY
```

**Smart Detection**: ShipSight auto-switches to the best available provider based on your keys (GPT-4o mini / Claude 3.5 Sonnet).

### 2. Custom Project Config (Optional)
Create a `shipsight.yml` in your project root for granular control:

```yaml
run:
  port: 3000
  strategy: local # local, docker, or static
capture:
  routes: ["/", "/dashboard", "/pricing"]
ai:
  model: gpt-4o-mini
```

---

## 📂 Output Structure

After a successful run, everything is saved to `shipsight_output/`:
- `README.generated.md`: Professional project documentation.
- `linkedin.post.md`: Authentic, shareable social media content.
- `screenshots/`: High-resolution app captures.
- `code_visuals/`: Beautiful code snapshots of your "Hero" files.
- `metadata.json`: Full technical analysis of your project.

---

## 🛠️ Manual Installation (Advanced)

If you prefer not to use the runner scripts:
1. `python -m venv .venv`
2. `source .venv/bin/activate` (or `.venv\Scripts\activate`)
3. `pip install -e .`
4. `playwright install chromium`

---

## 🤝 Contributing

We love contributions! Check out our [Contributing Guide](CONTRIBUTING.md) to get started.

## 📄 License

MIT © ShipSight Team

---
**Built with ❤️ for builders who want to show, not just tell.**
