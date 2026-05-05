"""Per-file ambient notes stored in .DS_Store under custom record code 'llMD'."""
from pathlib import Path
from typing import Optional

from ds_store import DSStore
from ds_store.store import DSStoreEntry

NOTE_CODE = b'llMD'


def read_note(file_path: Path) -> Optional[str]:
    ds = file_path.parent / '.DS_Store'
    if not ds.exists():
        return None
    try:
        with DSStore.open(str(ds), 'r') as d:
            for entry in d:
                if entry.filename == file_path.name and entry.code == NOTE_CODE:
                    val = entry.value
                    if isinstance(val, bytes):
                        return val.decode('utf-8', errors='replace')
                    return str(val)
    except Exception:
        return None
    return None


def write_note(file_path: Path, note: str) -> None:
    ds = file_path.parent / '.DS_Store'
    mode = 'r+' if ds.exists() else 'w+'
    with DSStore.open(str(ds), mode) as d:
        try:
            d.delete(file_path.name, NOTE_CODE)
        except KeyError:
            pass
        entry = DSStoreEntry(file_path.name, NOTE_CODE.decode('ascii'), 'ustr', note)
        d.insert(entry)


def delete_note(file_path: Path) -> bool:
    ds = file_path.parent / '.DS_Store'
    if not ds.exists():
        return False
    try:
        with DSStore.open(str(ds), 'r+') as d:
            d.delete(file_path.name, NOTE_CODE)
        return True
    except Exception:
        return False
