# C:\AgentUr1\tools\validate_yaml.py
from __future__ import annotations
import sys, json, pathlib
from typing import Dict, Any, List
try:
    import yaml  # PyYAML
except ImportError:
    print("ERROR: PyYAML not installed. Run: poetry add pyyaml", file=sys.stderr)
    sys.exit(2)

REQUIRED_TOP_KEYS = {"server","ui","data","nodestore","rag","summarize","ollama"}

def load_yaml(path: pathlib.Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        # SafeLoad avoids code execution, catches tabs/indent issues
        cfg = yaml.safe_load(text)
    except yaml.YAMLError as e:
        print(f"YAML SYNTAX ERROR in {path}:\n{e}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(cfg, dict):
        print("ERROR: Root of YAML must be a mapping (key: value).", file=sys.stderr)
        sys.exit(1)
    return cfg

def check_keys(cfg: Dict[str, Any]) -> List[str]:
    missing = sorted(k for k in REQUIRED_TOP_KEYS if k not in cfg)
    return missing

def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/validate_yaml.py C:\\AgentUr1\\settings.yaml", file=sys.stderr)
        sys.exit(2)
    path = pathlib.Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(2)
    cfg = load_yaml(path)
    missing = check_keys(cfg)
    print("PARSED OK.")
    if missing:
        print("MISSING TOP-LEVEL KEYS:", ", ".join(missing))
        sys.exit(3)
    # Extra sanity for profiles (optional)
    if "profiles" in cfg:
        prof = cfg.get("profile", None)
        if prof and prof not in cfg["profiles"]:
            print(f"ERROR: profile='{prof}' not found in 'profiles' section.", file=sys.stderr)
            sys.exit(4)
    print(json.dumps(cfg, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

