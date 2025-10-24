# utils.py
import json
from pathlib import Path
import re

def _sanitize_json_text(text: str) -> str:
    """
    Fix common invalid backslash escapes by escaping any backslash that is
    not followed by a valid JSON escape char: "  \  /  b f n r t u
    This uses a regex negative lookahead to double backslashes where needed.
    """
    # Double backslash any "\" not followed by valid escape characters.
    sanitized = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', text)
    return sanitized

def load_json(path):
    """
    Load a JSON file safely. If invalid escape sequences are found,
    it automatically sanitizes and rewrites the file before returning data.
    """
    path = Path(path)
    text = path.read_text(encoding='utf8')
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        # attempt to sanitize common invalid backslash escapes and retry
        sanitized = _sanitize_json_text(text)
        try:
            obj = json.loads(sanitized)
            # write back sanitized content so future loads are clean
            path.write_text(sanitized, encoding='utf8')
            print(f"[utils] Fixed and sanitized invalid JSON escapes in {path.name}")
            return obj
        except json.JSONDecodeError as e2:
            # If still failing, show useful debugging info
            pos = e2.pos
            start = max(0, pos - 80)
            end = min(len(sanitized), pos + 80)
            context = sanitized[start:end].replace('\n', '\\n')
            raise ValueError(
                f"Failed to parse JSON file: {path}\n"
                f"Original error: {e}\nAfter sanitization: {e2}\n"
                f"Context (around char {pos}):\n{context}\n"
                "Please open the file and manually fix the invalid JSON structure."
            )

def save_json(obj, path):
    """
    Save Python objects to JSON file with pretty formatting.
    """
    with open(path, 'w', encoding='utf8') as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)