import json
import os
import re
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

MEMORY_DIR = ".devhive/memory"
INDEX_FILE = f"{MEMORY_DIR}/index.json"
SEMANTIC_FILE = f"{MEMORY_DIR}/semantic.md"
EPISODIC_FILE = f"{MEMORY_DIR}/episodic.md"
ANTIPATTERNS_FILE = f"{MEMORY_DIR}/anti_patterns.md"

MEMORY_TYPES = ["semantic", "episodic", "anti_patterns"]


class MemoryEntry:
    def __init__(self, entry_id: str, entry_type: str, summary: str, tags: List[str],
                 source: str, score: float, project: str, created_at: str, line_ref: str = ""):
        self.id = entry_id
        self.type = entry_type
        self.summary = summary
        self.tags = tags
        self.source = source
        self.score = score
        self.project = project
        self.created_at = created_at
        self.line_ref = line_ref

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "summary": self.summary,
            "tags": self.tags,
            "source": self.source,
            "score": self.score,
            "project": self.project,
            "created_at": self.created_at,
            "line_ref": self.line_ref
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryEntry":
        return cls(
            entry_id=data["id"],
            entry_type=data["type"],
            summary=data["summary"],
            tags=data.get("tags", []),
            source=data.get("source", "unknown"),
            score=data.get("score", 0.5),
            project=data.get("project", ""),
            created_at=data.get("created_at", ""),
            line_ref=data.get("line_ref", "")
        )


class MemoryIndex:
    def __init__(self, memory_dir: str = MEMORY_DIR):
        self.memory_dir = Path(memory_dir)
        self.index_path = self.memory_dir / "index.json"
        self.entries: List[MemoryEntry] = []
        self._load_index()

    def _load_index(self):
        if self.index_path.exists():
            with open(self.index_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.entries = [MemoryEntry.from_dict(e) for e in data.get("entries", [])]
        else:
            self.entries = []

    def _save_index(self):
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "entries": [e.to_dict() for e in self.entries]
        }
        with open(self.index_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _generate_id(self, entry_type: str) -> str:
        prefix = entry_type[:3]
        existing = [e.id for e in self.entries if e.id.startswith(prefix)]
        counter = len(existing) + 1
        return f"{prefix}-{counter:03d}"

    def _get_file_path(self, entry_type: str) -> Path:
        type_to_file = {
            "semantic": self.memory_dir / "semantic.md",
            "episodic": self.memory_dir / "episodic.md",
            "anti_patterns": self.memory_dir / "anti_patterns.md"
        }
        return type_to_file.get(entry_type, self.memory_dir / "semantic.md")

    def add_entry(self, entry_type: str, summary: str, tags: List[str] = None,
                  source: str = "reflection", score: float = 0.7, project: str = "") -> MemoryEntry:
        if entry_type not in MEMORY_TYPES:
            raise ValueError(f"Invalid type. Must be one of: {MEMORY_TYPES}")

        entry_id = self._generate_id(entry_type)
        created_at = datetime.now().strftime("%Y-%m-%d")

        entry = MemoryEntry(
            entry_id=entry_id,
            entry_type=entry_type,
            summary=summary,
            tags=tags or [],
            source=source,
            score=score,
            project=project,
            created_at=created_at,
            line_ref=""
        )

        self.entries.append(entry)
        self._save_index()

        file_path = self._get_file_path(entry_type)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"\n<!-- id: {entry_id} -->\n")
            f.write(f"- **{entry.type.capitalize()}**: {summary}\n")

        for i, e in enumerate(self.entries):
            if e.id == entry_id:
                e.line_ref = f"{entry_type}.md:new"
                break

        self._save_index()
        return entry

    def get_by_type(self, entry_type: str) -> List[MemoryEntry]:
        return [e for e in self.entries if e.type == entry_type]

    def get_by_id(self, entry_id: str) -> Optional[MemoryEntry]:
        for e in self.entries:
            if e.id == entry_id:
                return e
        return None

    def search(self, query: str, entry_type: str = None) -> List[MemoryEntry]:
        query_lower = query.lower()
        results = []

        for e in self.entries:
            if entry_type and e.type != entry_type:
                continue

            if (query_lower in e.summary.lower() or
                query_lower in " ".join(e.tags).lower() or
                query_lower in e.source.lower()):
                results.append(e)

        return results

    def update_entry(self, entry_id: str, summary: str = None, tags: List[str] = None,
                     score: float = None) -> Optional[MemoryEntry]:
        for e in self.entries:
            if e.id == entry_id:
                if summary is not None:
                    e.summary = summary
                if tags is not None:
                    e.tags = tags
                if score is not None:
                    e.score = score

                self._save_index()

                file_path = self._get_file_path(e.type)
                if file_path.exists():
                    content = file_path.read_text(encoding="utf-8")
                    old_line = f"<!-- id: {entry_id} -->"
                    new_line = f"<!-- id: {entry_id} -->"
                    if old_line in content:
                        content = content.replace(old_line, new_line)

                    lines = content.split("\n")
                    for i, line in enumerate(lines):
                        if old_line in line:
                            pass

                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)

                return e
        return None

    def delete_entry(self, entry_id: str) -> bool:
        for i, e in enumerate(self.entries):
            if e.id == entry_id:
                del self.entries[i]
                self._save_index()
                return True
        return False

    def garbage_collect(self, threshold: float = 0.5) -> List[str]:
        deleted_ids = []
        for e in self.entries[:]:
            if e.score < threshold:
                deleted_ids.append(e.id)
                self.entries.remove(e)
        self._save_index()
        return deleted_ids

    def export_to_json(self, entry_type: str = None) -> str:
        entries = self.entries
        if entry_type:
            entries = [e for e in entries if e.type == entry_type]

        data = {
            "version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "count": len(entries),
            "entries": [e.to_dict() for e in entries]
        }
        return json.dumps(data, indent=2, ensure_ascii=False)

    def import_from_json(self, json_str: str) -> int:
        data = json.loads(json_str)
        imported = 0

        for e_data in data.get("entries", []):
            existing = self.get_by_id(e_data["id"])
            if not existing:
                entry = MemoryEntry.from_dict(e_data)
                self.entries.append(entry)
                imported += 1

        self._save_index()
        return imported

    def get_stats(self) -> Dict[str, Any]:
        by_type = {t: [] for t in MEMORY_TYPES}
        for e in self.entries:
            if e.type in by_type:
                by_type[e.type].append(e)

        return {
            "total": len(self.entries),
            "by_type": {t: len(by_type[t]) for t in MEMORY_TYPES},
            "avg_score": sum(e.score for e in self.entries) / len(self.entries) if self.entries else 0,
            "tags": list(set(tag for e in self.entries for tag in e.tags)),
            "sources": list(set(e.source for e in self.entries))
        }


class MemoryCLI:
    def __init__(self, memory_dir: str = MEMORY_DIR):
        self.index = MemoryIndex(memory_dir)

    def list_entries(self, entry_type: str = None):
        if entry_type:
            entries = self.index.get_by_type(entry_type)
        else:
            entries = self.index.entries

        if not entries:
            print("No memories found.")
            return

        print(f"\n{'ID':<12} {'TYPE':<12} {'SCORE':<6} {'SUMMARY':<50} {'TAGS'}")
        print("-" * 120)
        for e in entries:
            tags_str = ", ".join(e.tags[:3]) if e.tags else "-"
            summary = e.summary[:47] + "..." if len(e.summary) > 50 else e.summary
            print(f"{e.id:<12} {e.type:<12} {e.score:.2f}   {summary:<50} [{tags_str}]")

    def show_entry(self, entry_id: str):
        entry = self.index.get_by_id(entry_id)
        if not entry:
            print(f"Entry '{entry_id}' not found.")
            return

        print(f"\n{'='*60}")
        print(f"ID:       {entry.id}")
        print(f"Type:     {entry.type}")
        print(f"Score:    {entry.score}")
        print(f"Tags:     {', '.join(entry.tags) if entry.tags else 'None'}")
        print(f"Source:   {entry.source}")
        print(f"Project:  {entry.project}")
        print(f"Created:  {entry.created_at}")
        print(f"{'='*60}")
        print(f"\nSummary:\n{entry.summary}")

    def search_entries(self, query: str, entry_type: str = None):
        results = self.index.search(query, entry_type)
        if not results:
            print(f"No results found for: '{query}'")
            return

        print(f"\nFound {len(results)} result(s) for: '{query}'")
        print(f"{'ID':<12} {'TYPE':<12} {'SCORE':<6} {'SUMMARY'}")
        print("-" * 100)
        for e in results:
            summary = e.summary[:60] + "..." if len(e.summary) > 60 else e.summary
            print(f"{e.id:<12} {e.type:<12} {e.score:.2f}   {summary}")

    def edit_entry(self, entry_id: str, summary: str = None, tags: str = None, score: float = None):
        tag_list = [t.strip() for t in tags.split(",")] if tags else None
        entry = self.index.update_entry(entry_id, summary, tag_list, score)
        if entry:
            print(f"Updated entry: {entry_id}")
        else:
            print(f"Entry '{entry_id}' not found.")

    def delete_entry(self, entry_id: str):
        if self.index.delete_entry(entry_id):
            print(f"Deleted entry: {entry_id}")
        else:
            print(f"Entry '{entry_id}' not found.")

    def export_memory(self, entry_type: str = None, output_file: str = None):
        json_data = self.index.export_to_json(entry_type)
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(json_data)
            print(f"Exported to: {output_file}")
        else:
            print(json_data)

    def import_memory(self, input_file: str):
        with open(input_file, "r", encoding="utf-8") as f:
            json_data = f.read()
        count = self.index.import_from_json(json_data)
        print(f"Imported {count} entries.")

    def show_stats(self):
        stats = self.index.get_stats()
        print("\n" + "=" * 40)
        print("MEMORY STATISTICS")
        print("=" * 40)
        print(f"Total Entries:  {stats['total']}")
        print(f"  - Semantic:   {stats['by_type'].get('semantic', 0)}")
        print(f"  - Episodic:    {stats['by_type'].get('episodic', 0)}")
        print(f"  - Anti-patterns: {stats['by_type'].get('anti_patterns', 0)}")
        print(f"Average Score:  {stats['avg_score']:.2f}")
        print(f"Unique Tags:     {len(stats['tags'])}")
        print(f"Sources:         {', '.join(stats['sources'][:5]) if stats['sources'] else 'None'}")
        print("=" * 40)

    def garbage_collect(self, threshold: float = 0.5):
        deleted = self.index.garbage_collect(threshold)
        if deleted:
            print(f"Deleted {len(deleted)} entries: {', '.join(deleted)}")
        else:
            print(f"No entries below threshold {threshold}")


def get_memory_cli() -> MemoryCLI:
    return MemoryCLI()


def ensure_memory_dir():
    Path(MEMORY_DIR).mkdir(parents=True, exist_ok=True)