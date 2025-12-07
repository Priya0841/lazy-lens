# PromptAlbumBuilder

A Kiro agent workflow that automates photo album organization from natural language prompts. Simply describe how you want your photos organized, and PromptAlbumBuilder will scan your photos, extract metadata, match them to albums, and create organized folders with documentation.

## Features

- **Natural Language Prompts**: Organize photos by describing your desired albums in plain English
- **Intelligent Matching**: Matches photos based on filenames, dates, folder names, and EXIF metadata
- **Flexible Modes**: Dry-run mode for preview, backup mode to preserve originals
- **Comprehensive Documentation**: Auto-generates README and JSON summaries for each album
- **Gallery Preview**: Creates an HTML index with thumbnails of all albums
- **Robust Error Handling**: Continues processing even when individual files fail

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone or download this project** to your local machine

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your paths**:
   - Open `.kiro/config.yaml`
   - Update `source_folder` to point to your unorganized photos
   - Update `target_albums_folder` to point to where you want albums created
   
   Example configuration:
   ```yaml
   source_folder: "C:/Users/YourName/Pictures/Unsorted"
   target_albums_folder: "C:/Users/YourName/Pictures/Albums"
   ```

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Paths
Edit `.kiro/config_test.yaml`:
```yaml
source_folder: "demo_photos/input"
target_albums_folder: "demo_photos/output"
```

### 3. Launch Web UI (Recommended) 🎨

```bash
streamlit run app.py
```

Opens automatically at **http://localhost:8501**

**Web UI Features:**
- 📝 Visual prompt input with examples
- 🔍 Month/year filter dropdowns
- 🖼️ Live thumbnail previews (4 per row)
- 📊 Real-time statistics dashboard
- 🎯 Dry-run mode for safe testing
- 💾 Backup mode to preserve originals

### 4. Or Use Command Line

```bash
python .kiro/hooks/album.py --prompt "Your album organization description"
```

### Command-Line Options

- `--prompt <text>` (required): Natural language description of how to organize photos
- `--dry-run`: Preview what would happen without modifying files
- `--backup`: Copy photos instead of moving them (preserves originals)
- `--notify`: Display notifications when processing completes

### Example Prompts

**Example 1: Organize by event and date**
```bash
kiro album --prompt "Create albums for NCC events, college fests, family trips, and medical bills in March 2024"
```

**Example 2: Organize by keywords**
```bash
kiro album --prompt "Organize photos into vacation, work, and family albums"
```

**Example 3: Organize with date ranges**
```bash
kiro album --prompt "Create albums for summer 2023, winter 2023, and spring 2024"
```

**Example 4: Organize with wildcards**
```bash
kiro album --prompt "Create albums for NCC* events, *fest* photos, and *bill* documents"
```

### Dry-Run Mode (Preview)

Test your prompt without modifying files:

```bash
kiro album --prompt "Your prompt here" --dry-run
```

This will show you:
- Which photos would be matched to which albums
- How many photos would be in each album
- Which photos wouldn't match any album

### Backup Mode (Preserve Originals)

Copy photos instead of moving them:

```bash
kiro album --prompt "Your prompt here" --backup
```

Use this when you want to keep your original photo organization intact.

## How It Works

1. **Configuration Loading**: Reads source and target folders from `.kiro/config.yaml`
2. **Prompt Parsing**: Extracts album names, date filters, and keywords from your prompt
3. **Photo Scanning**: Recursively scans source folder and extracts metadata (timestamps, EXIF data)
4. **Pattern Matching**: Matches photos to albums based on:
   - Filename patterns (case-insensitive)
   - Date ranges (from EXIF or file timestamps)
   - Folder names
   - Wildcard patterns
5. **Album Creation**: Creates folders with standardized naming (YYYY-MM-AlbumName)
6. **Documentation**: Generates README.md and summary.json for each album
7. **Gallery**: Creates master index.html with thumbnails and album metadata
8. **Reporting**: Logs unmatched photos and displays summary statistics

## Output Structure

After running PromptAlbumBuilder, your target folder will look like:

```
Albums/
├── 2024-03-NCC-Events/
│   ├── README.md
│   ├── summary.json
│   ├── photo1.jpg
│   └── photo2.jpg
├── 2024-03-College-Fests/
│   ├── README.md
│   ├── summary.json
│   └── ...
├── index.html (master gallery)
└── ...

logs/
├── unmatched.log
└── 2024-12-07_10-30-00.log
```

## Album Folder Naming

Albums are named using the format: `YYYY-MM-AlbumName`

- **YYYY-MM**: Derived from date filter in prompt, or earliest photo date
- **AlbumName**: Extracted from your prompt

Examples:
- `2024-03-NCC-Events`
- `2023-07-Summer-Vacation`
- `2024-01-Family-Trips`

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- HEIC (.heic)
- RAW formats (.raw, .cr2, .nef)

## Troubleshooting

### "Configuration file not found"

Make sure `.kiro/config.yaml` exists and contains valid paths.

### "Source folder does not exist"

Check that the `source_folder` path in `.kiro/config.yaml` is correct and accessible.

### "No photos found"

Verify that:
- Your source folder contains image files
- The image files have supported extensions
- You have read permissions for the source folder

### "No photos matched any album criteria"

Try:
- Using more general keywords in your prompt
- Checking that your photo filenames or folder names contain relevant keywords
- Using wildcard patterns (e.g., `*event*`)

### EXIF warnings

If you see warnings about EXIF data, the system will automatically fall back to file timestamps. This is normal for photos without EXIF metadata.

## Testing

### Run Unit Tests

```bash
pytest
```

### Run Property-Based Tests

```bash
pytest -v -k property
```

### Prepare Test Dataset

To create a test dataset for experimentation:

```bash
python scripts/prepare_test_data.py
```

This will create sample photos with appropriate filenames and metadata for testing.

## Project Structure

```
PromptAlbumBuilder/
├── core/                    # Core modules
│   ├── config.py           # Configuration loader
│   ├── matcher.py          # Prompt parser and pattern matcher
│   ├── scanner.py          # Photo scanner and metadata extractor
│   ├── albums.py           # Album creator
│   ├── report.py           # Report generator
│   └── gallery.py          # Gallery generator
├── .kiro/
│   ├── hooks/
│   │   └── album.py        # CLI interface (Kiro hook)
│   └── config.yaml         # Configuration file
├── logs/                    # Log files
├── output/
│   └── Albums/             # Created albums
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Advanced Usage

### Custom Date Formats

The system recognizes various date formats:
- Years: `2024`, `2023`
- Month-Year: `March 2024`, `Mar 2024`
- ISO format: `2024-03`, `2024-03-15`

### Wildcard Patterns

Use `*` for flexible matching:
- `NCC*` matches "NCC_event", "NCC_parade", etc.
- `*fest*` matches "techfest", "culturefest", etc.
- `*bill*` matches "medical_bill", "electricity_bill", etc.

### First-Match Precedence

When a photo matches multiple albums, it's assigned to the first matching album in your prompt. Order your albums from most specific to most general.

Example:
```bash
kiro album --prompt "Create albums for NCC parade, NCC events, and general events"
```

A photo named "NCC_parade_2024.jpg" will go to "NCC parade" (not "NCC events").

## Contributing

This project follows the spec-driven development methodology. See `.kiro/specs/prompt-album-builder/` for requirements, design, and implementation tasks.

## License

MIT License - feel free to use and modify as needed.
