import os
from pathlib import Path
from typing import Dict, List

class IntelligenceEngine:
    def __init__(self, project_path: Path):
        self.project_path = project_path

    def analyze_stack(self) -> Dict:
        """Analyze project files to understand the architecture."""
        analysis = {
            "name": self.project_path.name,
            "description": self.get_project_intent(),
            "frameworks": [],
            "file_counts": {}
        }
        
        for root, dirs, files in os.walk(self.project_path):
            if any(p in root for p in [".git", "node_modules", ".venv", "__pycache__", "shipsight_output", "dist", ".next"]):
                continue
                
            for file in files:
                ext = Path(file).suffix
                if ext:
                    analysis["file_counts"][ext] = analysis["file_counts"].get(ext, 0) + 1
                
                # Detect frameworks
                if file == "package.json":
                    analysis["frameworks"].append("node")
                elif file in ["pyproject.toml", "requirements.txt"]:
                    analysis["frameworks"].append("python")
                elif file == "docker-compose.yml":
                    analysis["frameworks"].append("docker")
                elif "next.config" in file:
                    analysis["frameworks"].append("nextjs")
                elif "vite.config" in file:
                    analysis["frameworks"].append("vite")
                elif file == "pubspec.yaml":
                    analysis["frameworks"].append("flutter")

        analysis["frameworks"] = list(set(analysis["frameworks"]))
        return analysis

    def get_project_intent(self) -> str:
        """Try to find what the project actually DOES."""
        # 1. Check package.json
        pkg_path = self.project_path / "package.json"
        if pkg_path.exists():
            try:
                import json
                with open(pkg_path, "r") as f:
                    data = json.load(f)
                    desc = data.get("description")
                    if desc: return desc
            except: pass

        # 2. Check README.md
        for readme_name in ["README.md", "readme.md", "Readme.md"]:
            readme_path = self.project_path / readme_name
            if readme_path.exists():
                try:
                    with open(readme_path, "r", encoding="utf-8") as f:
                        content = f.read(1000)
                        # Just return the first few sentences
                        return content[:500].strip()
                except: pass
        
        return "Unknown Purpose"

    def get_hero_code(self) -> Dict[str, str]:
        """Identify and extract the most 'impressive' code snippets, avoiding config."""
        heroes = {}
        # Priority directories - expanded for complex architectures
        priority_dirs = ["features", "services", "api", "src", "app", "lib", "components", "pages", "core", "integrations", "models"]
        
        found_files = []
        for root, dirs, files in os.walk(self.project_path):
            # Strict ignore
            if any(p in root for p in [".git", "node_modules", ".venv", "__pycache__", "dist", ".next"]):
                continue
            
            for file in files:
                # Skip config files
                if any(c in file.lower() for c in ["config", "setup", "test", "spec", "d.ts", "init"]):
                    continue
                
                if file.endswith((".py", ".js", ".ts", ".go", ".rs", ".tsx", ".dart")):
                    path = Path(root) / file
                    # Score based on directory and filename importance
                    score = 1
                    rel_path = os.path.relpath(root, self.project_path)
                    
                    if any(p in rel_path.lower() for p in priority_dirs):
                        score += 10 # Massive boost for architectural code
                    
                    if "api" in file.lower() or "service" in file.lower():
                        score += 5
                        
                    found_files.append((path, score))

        # Sort by score and take top
        found_files.sort(key=lambda x: x[1], reverse=True)
        
        # Take up to 5 heroes for better context in complex projects
        for path, score in found_files:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    # Filter for substantial code
                    code_lines = [l for l in lines if l.strip() and not l.strip().startswith(("#", "//", "import", "from"))]
                    
                    if len(code_lines) > 15: # Significant implementation
                        heroes[path.name] = "".join(lines[:70]) # First 70 lines
                        if len(heroes) >= 5: break
            except: continue
            
        return heroes

    def get_summary_context(self, analysis: Dict, heroes: Dict = None) -> str:
        """Format analysis into a context string with deep documentation insights."""
        frameworks_str = ", ".join(analysis["frameworks"])
        
        # 1. Base Context
        context = f"PROJECT NAME: {analysis['name']}\n"
        context += f"TECH STACK: {frameworks_str}\n"
        
        # 2. Extract Intent from Docs (Prioritizing Design.md)
        doc_gist = ""
        unique_concepts = set()
        for doc_name in ["Design.md", "DESIGN.md", "README.md", "readme.md"]:
            doc_path = self.project_path / doc_name
            if doc_path.exists():
                content = doc_path.read_text(errors="ignore")
                doc_gist += f"\n--- {doc_name} ---\n{content[:500]}...\n"
                
                # Semantic Extraction
                if "Design Philosophy" in content:
                    phil = content.split("Design Philosophy")[1].split("\n")[1:3]
                    unique_concepts.add(f"PHILOSOPHY: {' '.join(phil).strip()}")
                if "Goal" in content or "Purpose" in content:
                    key = "Goal" if "Goal" in content else "Purpose"
                    goal = content.split(key)[1].split("\n")[1:3]
                    unique_concepts.add(f"CORE GOAL: {' '.join(goal).strip()}")

        context += f"PROJECT INTENT/PURPOSE (Deducted): {analysis['description']}\n"
        context += f"DOCUMENTATION GIST: {doc_gist}\n"
        if unique_concepts:
            context += f"UNIQUE CONCEPTS IDENTIFIED: {list(unique_concepts)}\n"

        # 3. Code Samples
        if heroes:
            context += f"ARCHITECTURAL COMPONENTS FOUND: {list(heroes.keys())}"
        
        # 4. Deep Structure
        context += f"\nPROJECT STRUCTURE SAMPLE:\n{self.get_deep_structure()}"
        return context

    def get_deep_structure(self, max_files: int = 100) -> str:
        """Recursively list representative files to give LLM a sense of the architecture."""
        structure = []
        count = 0
        for root, dirs, files in os.walk(self.project_path):
            if any(p in root for p in [".git", "node_modules", ".venv", "__pycache__", "shipsight_output", "dist", ".next"]):
                continue
            
            rel_path = os.path.relpath(root, self.project_path)
            if rel_path == ".": rel_path = ""
            
            # Show directories to give a sense of hierarchy
            if rel_path:
                structure.append(f"DIR: {rel_path}")
            
            for file in files:
                if count >= max_files: break
                if file.endswith((".py", ".ts", ".tsx", ".js", ".go", ".rs", ".java", ".cpp", ".yml", ".json", ".dart")):
                    # Filter out common junk
                    if any(j in file.lower() for j in ["lock", "min.js", "map", "license"]):
                        continue
                    structure.append(os.path.join(rel_path, file))
                    count += 1
            if count >= max_files: break
            
        return "\n".join(structure)
