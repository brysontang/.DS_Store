"""PostToolUse hook for Edit|Write|MultiEdit: drop breadcrumb + remind agent."""
import json
import sys
import tempfile
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

    p = Path(fp).resolve()

    breadcrumb = Path(tempfile.gettempdir()) / 'claude_dsstore_breadcrumb'
    breadcrumb.write_text(str(p))

    existing = read_note(p)

    if existing:
        body = (
            f"current ambient note:\n  {existing}\n\n"
            f"If your edits invalidated any of it, call update_recent_note with the "
            f"FULL replacement text — it OVERWRITES, not appends. Carry forward anything "
            f"still relevant, drop what's now obvious from the code itself, add what's "
            f"newly non-obvious. Empty string deletes."
        )
    else:
        body = (
            "no ambient note yet. If you learned something worth remembering about this "
            "file (intent, gotchas, why it's shaped this way, decisions a future reader "
            "would not derive from the code), call update_recent_note with the note text. "
            "It will overwrite on subsequent calls — keep notes terse."
        )

    msg = f"You just modified {p.name} — {body}"

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": msg
        }
    }))


if __name__ == '__main__':
    main()
