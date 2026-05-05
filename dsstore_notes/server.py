"""MCP server: update_recent_note, bound to the post-write breadcrumb."""
import tempfile
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from dsstore_notes.store import write_note, delete_note, read_note

mcp = FastMCP("dsstore-notes")


BREADCRUMB = Path(tempfile.gettempdir()) / 'claude_dsstore_breadcrumb'


@mcp.tool()
def update_recent_note(note: str) -> str:
    """Update the ambient note for the file you most recently modified.

    The target file path is read from a breadcrumb dropped by the PostToolUse
    hook — do not pass a file path. The note is stored as a 'llMD' record in
    that file's directory's .DS_Store and will auto-inject next time the file
    is read.

    OVERWRITES, does not append. If a note already exists and parts are still
    relevant, include them in your new note text — anything you omit is lost.
    Empty string deletes the note.
    """
    bc = BREADCRUMB
    if not bc.exists():
        return "No breadcrumb found — there's no recent write to attach a note to."

    target = Path(bc.read_text().strip())
    if not target.exists():
        return f"Breadcrumb pointed to {target}, which no longer exists."

    if not note.strip():
        ok = delete_note(target)
        return f"Deleted ambient note for {target.name}." if ok else f"No note existed for {target.name}."

    write_note(target, note)
    return f"Saved ambient note for {target.name}."


@mcp.tool()
def read_ambient_note(file_path: str) -> str:
    """Read the ambient note for an arbitrary file (or '(none)' if there isn't one)."""
    note = read_note(Path(file_path))
    return note or "(none)"


def main():
    mcp.run()


if __name__ == '__main__':
    main()
