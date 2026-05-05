"""PreToolUse hook for Read: inject the file's ambient note into context."""
import json
import sys
from pathlib import Path

from dsstore_notes.store import read_note


def main():
    try:
        inp = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    fp = inp.get('tool_input', {}).get('file_path', '')
    if not fp:
        sys.exit(0)

    p = Path(fp)
    note = read_note(p)
    if not note:
        sys.exit(0)

    msg = (
        f"╭─ ambient note for {p.name} ─╮\n"
        f"{note}\n"
        f"╰─ (from {p.parent}/.DS_Store, code llMD) ─╯"
    )

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": msg
        }
    }))


if __name__ == '__main__':
    main()
