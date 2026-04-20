# Bookmark Manager

A local desktop bookmark manager built with Python and Qt

## Features
- Tag-based organization
- Ranked search
- Duplicate handling with merge/overwrite options
- Editable bookmarks
- Automatic orphan tag cleanup
- Keyboard shortcuts and menu-driven UI

## Tech Stack
- Python 3.14
- Qt (PySide6)
- SQLite

## Usage
Run the application:
```
python -m bookmark_manager
```

## Notes
- Bookmarks are uniquely identified by URL
- Tags are input using space separation
- Search supports `#tag` syntax
- Data is stored locally (no external sync)
