# Design Document

## Overview

PromptAlbumBuilder is a Python-based Kiro agent workflow that automates photo album organization through natural language processing. The system follows a pipeline architecture: configuration loading → prompt parsing → photo scanning → metadata extraction → pattern matching → album creation → documentation generation → gallery creation. The design emphasizes modularity, extensibility, and robust error handling to ensure reliable photo organization across diverse user scenarios.

## Architecture

The system follows a modular pipeline architecture with five core modules:

```
┌─────────────────┐
│  CLI Interface  │ (album.py)
│  (Kiro Hook)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Configuration  │ (config.yaml)
│     Loader      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Prompt Parser   │ (matcher.py)
│  Extract:       │
│  - Album names  │
│  - Dates        │
│  - Keywords     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Photo Scanner   │ (scanner.py)
│  Collect:       │
│  - Files        │
│  - Timestamps   │
│  - EXIF data    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Pattern Matcher │ (matcher.py)
│  Match photos   │
│  to albums      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Album Creator   │ (albums.py)
│  Create folders │
│  Copy/move      │
│  Generate docs  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Report & Gallery│ (report.py, gallery.py)
│  - unmatched.log│
│  - index.html   │
│  - Terminal out │
└─────────────────┘
```

**Design Rationale:**
- **Separation of Concerns**: Each module has a single responsibility
- **Testability**: Pure functions enable easy unit and property testing
- **Extensibility**: New matching strategies or output formats can be added without modifying core logic
- **Error Isolation**: Failures in one module don't cascade to others

## Components and Interfaces

### 1. Configuration Loader

**Module**: `core/config.py`

**Responsibilities**:
- Load and validate .kiro/config.yaml
- Provide configuration access to other modules

**Interface**:
```python
class Config:
    def __init__(self, config_path: str = ".kiro/config.yaml")
    def load(self) -> dict
    def get_source_folder(self) -> Path
    def get_target_folder(self) -> Path
    def validate(self) -> bool
```

**Data Flow**:
- Input: Path to config.yaml
- Output: Validated configuration dictionary
- Errors: ConfigNotFoundError, InvalidConfigError

### 2. Prompt Parser

**Module**: `core/matcher.py` (contains parsing logic)

**Responsibilities**:
- Parse natural language prompts
- Extract album names, date filters, keywords
- Normalize dates to standard format

**Interface**:
```python
class PromptParser:
    def parse(self, prompt: str) -> List[AlbumSpec]
    def extract_album_names(self, prompt: str) -> List[str]
    def extract_dates(self, prompt: str) -> List[DateFilter]
    def extract_keywords(self, prompt: str) -> List[str]

@dataclass
class AlbumSpec:
    name: str
    keywords: List[str]
    date_filter: Optional[DateFilter]

@dataclass
class DateFilter:
    year: Optional[int]
    month: Optional[int]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
```

**Parsing Strategy**:
- Split on commas and conjunctions (and, or) to identify album names
- Use regex patterns to match date expressions (month names, years, "March 2024")
- Extract keywords from album names (split on spaces, remove stop words)
- Support patterns: "YYYY", "Month YYYY", "MM/YYYY", "YYYY-MM"

### 3. Photo Scanner

**Module**: `core/scanner.py`

**Responsibilities**:
- Recursively scan source folder
- Collect photo metadata (timestamps, EXIF, paths)
- Handle various image formats

**Interface**:
```python
class PhotoScanner:
    def __init__(self, source_folder: Path)
    def scan(self) -> List[PhotoMetadata]
    def extract_exif(self, photo_path: Path) -> Optional[ExifData]
    def get_file_timestamp(self, photo_path: Path) -> datetime

@dataclass
class PhotoMetadata:
    path: Path
    filename: str
    folder_name: str
    file_created: datetime
    file_modified: datetime
    exif_date: Optional[datetime]
    exif_location: Optional[tuple]

@dataclass
class ExifData:
    date_taken: Optional[datetime]
    latitude: Optional[float]
    longitude: Optional[float]
    camera_model: Optional[str]
```

**Supported Formats**: .jpg, .jpeg, .png, .heic, .raw, .cr2, .nef

**EXIF Extraction Strategy**:
- Use exifread library for EXIF parsing
- Extract DateTimeOriginal tag for date taken
- Extract GPSInfo tags for location
- Fall back to file timestamps if EXIF unavailable

### 4. Pattern Matcher

**Module**: `core/matcher.py`

**Responsibilities**:
- Match photos to albums based on criteria
- Implement matching strategies (filename, date, folder)
- Handle unmatched photos

**Interface**:
```python
class PatternMatcher:
    def __init__(self, album_specs: List[AlbumSpec])
    def match(self, photos: List[PhotoMetadata]) -> MatchResult
    def match_filename(self, photo: PhotoMetadata, keywords: List[str]) -> bool
    def match_date(self, photo: PhotoMetadata, date_filter: DateFilter) -> bool
    def match_folder(self, photo: PhotoMetadata, keywords: List[str]) -> bool

@dataclass
class MatchResult:
    matched: Dict[str, List[PhotoMetadata]]  # album_name -> photos
    unmatched: List[PhotoMetadata]
```

**Matching Algorithm**:
1. For each photo, iterate through album specs in order
2. Check filename against keywords (case-insensitive, wildcard support)
3. Check EXIF date or file date against date filter
4. Check parent folder name against keywords
5. If any criterion matches, assign to album and break
6. If no match, add to unmatched list

**Wildcard Support**:
- `*` matches any characters
- Convert to regex: `NCC*` → `^NCC.*$`
- Case-insensitive matching

### 5. Album Creator

**Module**: `core/albums.py`

**Responsibilities**:
- Create album folders with standardized naming
- Copy or move photos to albums
- Generate README.md and summary.json
- Handle file conflicts

**Interface**:
```python
class AlbumCreator:
    def __init__(self, target_folder: Path, backup_mode: bool, dry_run: bool)
    def create_albums(self, match_result: MatchResult, album_specs: List[AlbumSpec]) -> List[Album]
    def create_folder(self, album_name: str, date: datetime) -> Path
    def organize_photos(self, album_path: Path, photos: List[PhotoMetadata]) -> int
    def generate_readme(self, album: Album, original_prompt: str) -> None
    def generate_summary(self, album: Album, original_prompt: str) -> None

@dataclass
class Album:
    name: str
    path: Path
    photos: List[PhotoMetadata]
    earliest_date: datetime
    latest_date: datetime
    keywords: List[str]
```

**Folder Naming Convention**:
- Format: `YYYY-MM-AlbumName`
- Date source: date_filter if present, else earliest photo date
- Example: `2024-03-NCC-Events`

**File Conflict Resolution**:
- If file exists, append numeric suffix: `photo.jpg` → `photo_1.jpg`
- Preserve original timestamps using `shutil.copy2()` or `os.utime()`

### 6. Report Generator

**Module**: `core/report.py`

**Responsibilities**:
- Generate unmatched.log
- Display terminal output with statistics
- Create timestamped log files

**Interface**:
```python
class ReportGenerator:
    def __init__(self, log_dir: Path)
    def generate_unmatched_log(self, unmatched: List[PhotoMetadata]) -> None
    def display_summary(self, albums: List[Album], unmatched_count: int, total_scanned: int) -> None
    def log_error(self, message: str) -> None
    def log_warning(self, message: str) -> None
    def log_info(self, message: str) -> None
```

**Terminal Output Format**:
```
[INFO] Scanning photos from: /path/to/source
[INFO] Found 150 photos
[INFO] Matching photos to albums...
[INFO] Created album: 2024-03-NCC-Events (25 photos)
[INFO] Created album: 2024-03-College-Fests (40 photos)
[INFO] Created album: 2024-03-Family-Trips (30 photos)
[INFO] Created album: 2024-03-Medical-Bills (15 photos)

Summary:
  Total photos scanned: 150
  Albums created: 4
  Photos matched: 110
  Photos unmatched: 40
  Unmatched log: logs/unmatched.log
```

### 7. Gallery Generator

**Module**: `core/gallery.py`

**Responsibilities**:
- Generate master index.html
- Create thumbnail previews
- Display album metadata

**Interface**:
```python
class GalleryGenerator:
    def __init__(self, target_folder: Path)
    def generate_index(self, albums: List[Album]) -> None
    def create_thumbnail(self, photo: PhotoMetadata, size: tuple = (200, 200)) -> Path
    def generate_html(self, albums: List[Album]) -> str
```

**Gallery Features**:
- Responsive grid layout
- Album thumbnails (first photo from each album)
- Album name, photo count, date range
- Click to open album folder
- CSS styling for clean presentation

### 8. CLI Interface (Kiro Hook)

**Module**: `.kiro/hooks/album.py`

**Responsibilities**:
- Parse command-line arguments
- Orchestrate the pipeline
- Handle flags (--dry-run, --backup, --notify)

**Interface**:
```python
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prompt', required=True)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--backup', action='store_true')
    parser.add_argument('--notify', action='store_true')
    args = parser.parse_args()
    
    # Pipeline execution
    config = Config().load()
    prompt_parser = PromptParser()
    album_specs = prompt_parser.parse(args.prompt)
    scanner = PhotoScanner(config.source_folder)
    photos = scanner.scan()
    matcher = PatternMatcher(album_specs)
    match_result = matcher.match(photos)
    creator = AlbumCreator(config.target_folder, args.backup, args.dry_run)
    albums = creator.create_albums(match_result, album_specs)
    report = ReportGenerator(Path('logs'))
    report.generate_unmatched_log(match_result.unmatched)
    report.display_summary(albums, len(match_result.unmatched), len(photos))
    gallery = GalleryGenerator(config.target_folder)
    gallery.generate_index(albums)
```

## Data Models

### Configuration Schema (config.yaml)

```yaml
# Source folder containing photos to organize
source_folder: "/path/to/photos"

# Target folder where albums will be created
target_albums_folder: "/path/to/albums"

# Optional: Supported image extensions
supported_extensions:
  - .jpg
  - .jpeg
  - .png
  - .heic
  - .raw
  - .cr2
  - .nef

# Optional: Logging configuration
logging:
  level: INFO
  log_dir: logs
```

### Album Specification

```python
@dataclass
class AlbumSpec:
    """Specification for an album extracted from user prompt"""
    name: str                          # Album name (e.g., "NCC Events")
    keywords: List[str]                # Keywords for matching (e.g., ["ncc", "events"])
    date_filter: Optional[DateFilter]  # Date constraints
    original_prompt: str               # Original user prompt
```

### Photo Metadata

```python
@dataclass
class PhotoMetadata:
    """Complete metadata for a single photo"""
    path: Path                         # Full path to photo file
    filename: str                      # Filename only
    folder_name: str                   # Parent folder name
    file_created: datetime             # File creation timestamp
    file_modified: datetime            # File modification timestamp
    exif_date: Optional[datetime]      # EXIF DateTimeOriginal
    exif_location: Optional[tuple]     # (latitude, longitude)
    size_bytes: int                    # File size
```

### Match Result

```python
@dataclass
class MatchResult:
    """Result of matching photos to albums"""
    matched: Dict[str, List[PhotoMetadata]]  # album_name -> list of photos
    unmatched: List[PhotoMetadata]           # photos that matched no album
    match_stats: Dict[str, int]              # album_name -> photo count
```

### Album Summary (summary.json)

```json
{
  "album_name": "2024-03-NCC-Events",
  "total_photos": 25,
  "earliest_date": "2024-03-01",
  "latest_date": "2024-03-15",
  "keywords_used": ["ncc", "events"],
  "original_prompt": "Create albums for NCC events, college fests, family trips, and medical bills in March 2024",
  "created_at": "2024-12-07T10:30:00Z",
  "photos": [
    {
      "filename": "NCC_parade_001.jpg",
      "date_taken": "2024-03-05",
      "size_bytes": 2048576
    }
  ]
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Prompt parsing extracts all album specifications
*For any* valid natural language prompt containing album names, dates, and keywords, the parser should extract all album specifications with correct names, normalized dates, and associated keywords.
**Validates: Requirements 1.1, 1.2, 1.3, 1.4**

### Property 2: Configuration values are correctly applied
*For any* valid configuration file with source_folder and target_albums_folder paths, the system should use these exact paths for scanning and album creation operations.
**Validates: Requirements 2.2, 2.3**

### Property 3: Dry-run mode prevents file modifications
*For any* set of photos and album specifications, when running in dry-run mode, no files should be created, moved, or modified in the filesystem.
**Validates: Requirements 3.2**

### Property 4: Backup mode preserves original files
*For any* set of photos organized in backup mode, all original files should remain in their source locations after album creation completes.
**Validates: Requirements 3.3, 7.1**

### Property 5: Scanner finds all photos recursively
*For any* directory structure containing image files at various nesting levels, the scanner should discover all image files regardless of depth.
**Validates: Requirements 4.1**

### Property 6: Scanner extracts complete metadata
*For any* image file, the scanner should extract and record the filename, parent folder name, and file timestamps (creation and modification dates).
**Validates: Requirements 4.2, 4.3, 4.4**

### Property 7: EXIF extraction succeeds for valid metadata
*For any* image file containing valid EXIF metadata, the scanner should successfully extract the date taken and location information.
**Validates: Requirements 4.5**

### Property 8: All supported formats are processed
*For any* image file in a supported format (JPEG, PNG, HEIC, RAW), the scanner should successfully process the file and extract metadata.
**Validates: Requirements 4.7**

### Property 9: Filename matching works correctly
*For any* photo filename and set of keywords, the matcher should return true if and only if the filename contains any of the keywords (case-insensitive).
**Validates: Requirements 5.1**

### Property 10: Date matching works correctly
*For any* photo with a date and a date filter, the matcher should return true if and only if the photo date falls within the filter range.
**Validates: Requirements 5.2**

### Property 11: Folder name matching works correctly
*For any* photo's parent folder name and set of keywords, the matcher should return true if and only if the folder name contains any of the keywords (case-insensitive).
**Validates: Requirements 5.3**

### Property 12: First-match precedence is enforced
*For any* photo that matches multiple album specifications, the photo should be assigned to the first matching album in the specification list.
**Validates: Requirements 5.4**

### Property 13: Unmatched photos are logged
*For any* photo that matches no album specifications, the photo path should appear in the unmatched.log file.
**Validates: Requirements 5.5**

### Property 14: Case-insensitive matching works
*For any* keyword and filename/folder name pair that differ only in case, the matcher should recognize them as matching.
**Validates: Requirements 5.6**

### Property 15: Wildcard patterns match correctly
*For any* wildcard pattern (containing *) and filename, the matcher should correctly evaluate whether the filename matches the pattern.
**Validates: Requirements 5.7**

### Property 16: Album folder naming follows convention
*For any* created album, the folder name should follow the format "YYYY-MM-AlbumName" where YYYY-MM is derived from the date filter or earliest photo date.
**Validates: Requirements 6.1, 6.2, 6.3**

### Property 17: Target directory is created if missing
*For any* target albums folder path that does not exist, the system should create the directory before creating album folders.
**Validates: Requirements 6.4**

### Property 18: Existing albums accept new photos
*For any* album folder that already exists, running the system again should add new matched photos to the existing folder without removing existing photos.
**Validates: Requirements 6.5**

### Property 19: Move mode removes source files
*For any* photo organized in default (move) mode, the original file should not exist in the source location after the operation completes.
**Validates: Requirements 7.2**

### Property 20: File timestamps are preserved
*For any* photo copied or moved to an album, the file timestamps (creation and modification dates) in the destination should match the source timestamps.
**Validates: Requirements 7.3**

### Property 21: Filenames are preserved
*For any* photo copied or moved to an album, the filename in the destination should match the original filename (unless a conflict requires a suffix).
**Validates: Requirements 7.4**

### Property 22: Filename conflicts are resolved with suffixes
*For any* photo being copied/moved to an album where a file with the same name already exists, the new file should be renamed with a numeric suffix (e.g., photo_1.jpg).
**Validates: Requirements 7.5**

### Property 23: Album documentation is generated
*For any* created album, both README.md and summary.json files should exist in the album folder.
**Validates: Requirements 8.1, 8.2**

### Property 24: Documentation contains required fields
*For any* generated README.md and summary.json, all required fields (album_name, total_photos, earliest_date, latest_date, keywords_used, original_prompt) should be present.
**Validates: Requirements 8.3, 8.4**

### Property 25: Dates use ISO 8601 format
*For any* date written to README.md or summary.json, the date should be formatted as YYYY-MM-DD.
**Validates: Requirements 8.5**

### Property 26: Unmatched log is generated
*For any* execution that completes, an unmatched.log file should exist in the logs/ directory.
**Validates: Requirements 9.1, 9.6**

### Property 27: Unmatched log contains all unmatched photos
*For any* photo that matched no album, the photo's path should appear in the unmatched.log file.
**Validates: Requirements 9.2**

### Property 28: Master index is generated
*For any* execution that completes, an index.html file should exist in the target albums folder.
**Validates: Requirements 9.3, 9.7**

### Property 29: Index contains all album metadata
*For any* created album, the index.html should include the album name, photo count, and date range.
**Validates: Requirements 9.4, 9.5**

### Property 30: File operation errors don't halt processing
*For any* file operation that fails (copy, move, create), the system should log the error and continue processing remaining photos.
**Validates: Requirements 10.4**

### Property 31: Timestamped log files are created
*For any* execution, a log file with a timestamp in its name should be created in the logs/ directory.
**Validates: Requirements 10.5**

### Property 32: Log messages include level indicators
*For any* log message written, the message should include a level indicator (INFO, WARNING, or ERROR).
**Validates: Requirements 10.6**

### Property 33: Terminal summary displays all statistics
*For any* execution that completes, the terminal output should display total photos scanned, albums created, matched photo count, and unmatched photo count.
**Validates: Requirements 11.1, 11.2, 11.3, 11.4**

### Property 34: Dry-run output is clearly marked
*For any* execution in dry-run mode, all terminal output lines should be prefixed with "[DRY RUN]".
**Validates: Requirements 11.5**



## Error Handling

### Configuration Errors

**Error Type**: Missing or invalid configuration file
- **Detection**: On startup, check if .kiro/config.yaml exists and is readable
- **Handling**: Display error message with path and exit with code 1
- **User Message**: "Configuration file not found at .kiro/config.yaml. Please create the configuration file."

**Error Type**: Invalid folder paths in configuration
- **Detection**: Validate that source_folder exists and is readable
- **Handling**: Display error message and exit with code 1
- **User Message**: "Source folder does not exist: {path}. Please check your configuration."

### Parsing Errors

**Error Type**: Invalid date format in prompt
- **Detection**: Date parsing returns None or raises exception
- **Handling**: Log warning, skip the invalid date filter, continue with other filters
- **User Message**: "Warning: Could not parse date '{date_string}' in prompt. Skipping date filter."

**Error Type**: Empty prompt or no albums extracted
- **Detection**: Parser returns empty list of album specifications
- **Handling**: Display error message and exit with code 1
- **User Message**: "No albums could be extracted from prompt. Please provide album names."

### Scanning Errors

**Error Type**: Source folder is empty
- **Detection**: Scanner returns empty list of photos
- **Handling**: Display warning and exit gracefully
- **User Message**: "No photos found in source folder: {path}"

**Error Type**: EXIF metadata unreadable
- **Detection**: exifread raises exception or returns None
- **Handling**: Log warning, fall back to file timestamps, continue processing
- **User Message**: "Warning: Could not read EXIF data from {filename}. Using file timestamps."

**Error Type**: Unsupported file format
- **Detection**: File extension not in supported list
- **Handling**: Skip file silently (not an error, just not processed)

### Matching Errors

**Error Type**: No photos match any album
- **Detection**: All photos end up in unmatched list
- **Handling**: Log warning, create unmatched.log, exit gracefully
- **User Message**: "Warning: No photos matched any album criteria. Check your prompt and photo filenames."

**Error Type**: Album has zero matched photos
- **Detection**: Album specification has empty photo list after matching
- **Handling**: Log warning, skip folder creation for that album
- **User Message**: "Warning: Album '{name}' matched no photos. Skipping folder creation."

### File Operation Errors

**Error Type**: Permission denied on file copy/move
- **Detection**: shutil.copy2() or shutil.move() raises PermissionError
- **Handling**: Log error with file path, add to error list, continue with next file
- **User Message**: "Error: Permission denied copying {source} to {dest}"

**Error Type**: Disk full during copy/move
- **Detection**: OSError with errno ENOSPC
- **Handling**: Log error, stop processing, display summary of partial completion
- **User Message**: "Error: Disk full. Processed {count} of {total} photos."

**Error Type**: File already exists (conflict)
- **Detection**: File exists at destination with same name
- **Handling**: Append numeric suffix (_1, _2, etc.), retry operation
- **User Message**: "Info: File {name} already exists. Renamed to {new_name}"

### Gallery Generation Errors

**Error Type**: Cannot create thumbnail
- **Detection**: PIL raises exception when opening/resizing image
- **Handling**: Log warning, use placeholder thumbnail, continue
- **User Message**: "Warning: Could not create thumbnail for {filename}"

**Error Type**: Cannot write HTML file
- **Detection**: File write operation fails
- **Handling**: Log error, continue (gallery is optional)
- **User Message**: "Error: Could not create gallery index.html: {error}"

### Error Recovery Strategy

1. **Fail Fast**: Configuration and critical setup errors terminate immediately
2. **Continue on Partial Failure**: Individual file errors don't stop processing
3. **Graceful Degradation**: Optional features (thumbnails, EXIF) fail silently with warnings
4. **Complete Logging**: All errors and warnings are logged to file for debugging
5. **User Feedback**: Clear error messages guide users to resolution

## Testing Strategy

### Unit Testing

**Framework**: pytest

**Test Coverage**:

1. **Configuration Loading** (`test_config.py`)
   - Test valid configuration loading
   - Test missing configuration file error
   - Test invalid YAML syntax error
   - Test missing required fields error

2. **Prompt Parsing** (`test_parser.py`)
   - Test single album extraction
   - Test multiple albums with comma separation
   - Test date extraction (various formats)
   - Test keyword extraction
   - Test empty prompt handling

3. **Photo Scanner** (`test_scanner.py`)
   - Test recursive directory traversal
   - Test metadata extraction from various formats
   - Test EXIF extraction
   - Test fallback to file timestamps
   - Test empty directory handling

4. **Pattern Matcher** (`test_matcher.py`)
   - Test filename pattern matching
   - Test date range matching
   - Test folder name matching
   - Test wildcard patterns
   - Test case-insensitive matching
   - Test first-match precedence
   - Test unmatched photo handling

5. **Album Creator** (`test_albums.py`)
   - Test folder naming convention
   - Test photo copying in backup mode
   - Test photo moving in default mode
   - Test timestamp preservation
   - Test filename conflict resolution
   - Test README generation
   - Test summary.json generation

6. **Report Generator** (`test_report.py`)
   - Test unmatched.log generation
   - Test terminal output formatting
   - Test log file creation
   - Test log level indicators

7. **Gallery Generator** (`test_gallery.py`)
   - Test index.html generation
   - Test thumbnail creation
   - Test HTML structure and content

### Property-Based Testing

**Framework**: Hypothesis (Python property-based testing library)

**Configuration**: Each property test should run a minimum of 100 iterations to ensure thorough coverage of the input space.

**Test Tagging**: Each property-based test must include a comment with the format:
```python
# Feature: prompt-album-builder, Property X: <property description>
```

**Property Tests**:

1. **Property 1: Prompt parsing extracts all album specifications**
   - Generate random prompts with known album names, dates, keywords
   - Verify parser extracts all expected elements
   - Strategy: Generate structured prompts, verify round-trip

2. **Property 2: Configuration values are correctly applied**
   - Generate random valid config dictionaries
   - Verify paths are used in scanner and album creator
   - Strategy: Mock filesystem, verify correct paths accessed

3. **Property 3: Dry-run mode prevents file modifications**
   - Generate random photo sets and album specs
   - Run in dry-run mode
   - Verify no filesystem changes occurred
   - Strategy: Snapshot filesystem before/after, assert equality

4. **Property 4: Backup mode preserves original files**
   - Generate random photo sets
   - Run in backup mode
   - Verify all originals still exist
   - Strategy: Check source files exist after operation

5. **Property 5: Scanner finds all photos recursively**
   - Generate random directory structures with photos at various depths
   - Verify all photos are found
   - Strategy: Create temp directories, count files manually vs scanner

6. **Property 6: Scanner extracts complete metadata**
   - Generate random image files
   - Verify all metadata fields are populated
   - Strategy: Check PhotoMetadata objects have non-None values

7. **Property 16: Album folder naming follows convention**
   - Generate random album specs with various dates
   - Verify folder names match YYYY-MM-AlbumName format
   - Strategy: Regex validation of folder names

8. **Property 20: File timestamps are preserved**
   - Generate files with random timestamps
   - Copy/move them
   - Verify timestamps match
   - Strategy: Compare os.stat() results before/after

9. **Property 22: Filename conflicts are resolved with suffixes**
   - Create file conflicts intentionally
   - Verify numeric suffixes are appended
   - Strategy: Pre-populate destination, verify suffix pattern

10. **Property 25: Dates use ISO 8601 format**
    - Generate random dates
    - Write to documentation
    - Verify format matches YYYY-MM-DD
    - Strategy: Regex validation of date strings

**Generator Strategies**:

- **Album Names**: Generate realistic names (2-4 words, alphanumeric)
- **Dates**: Generate valid dates within reasonable range (2000-2030)
- **Keywords**: Generate 1-5 word keywords per album
- **File Structures**: Generate trees with 1-5 levels, 1-20 files per level
- **Filenames**: Generate realistic photo names with extensions
- **Wildcards**: Generate patterns with * in various positions

### Integration Testing

**Test Scenarios**:

1. **End-to-End Happy Path**
   - Create test photo set with known filenames and dates
   - Run full pipeline with sample prompt
   - Verify albums created with correct photos
   - Verify documentation generated
   - Verify gallery created

2. **Mixed Matching Scenario**
   - Photos that match multiple criteria
   - Photos that match no criteria
   - Verify correct assignment and unmatched logging

3. **Dry-Run Mode**
   - Run full pipeline in dry-run mode
   - Verify no files created or modified
   - Verify output shows what would happen

4. **Backup Mode**
   - Run full pipeline in backup mode
   - Verify originals preserved
   - Verify copies created in albums

5. **Incremental Updates**
   - Run pipeline once
   - Add new photos to source
   - Run pipeline again
   - Verify new photos added to existing albums

### Test Data Preparation

**Creating Demo Photos**:

1. **Directory Structure**:
```
test_photos/
├── NCC_Events/
│   ├── NCC_parade_001.jpg
│   ├── NCC_parade_002.jpg
│   └── NCC_training_001.jpg
├── College_Fests/
│   ├── fest_cultural_001.jpg
│   ├── fest_tech_001.jpg
│   └── college_fest_2024.jpg
├── Family/
│   ├── family_trip_beach.jpg
│   ├── family_trip_mountains.jpg
│   └── vacation_2024.jpg
└── Bills/
    ├── medical_bill_march.jpg
    ├── bill_hospital.jpg
    └── receipt_pharmacy.jpg
```

2. **Setting Timestamps**:
```python
import os
from datetime import datetime

def set_file_date(filepath, date):
    """Set file creation and modification dates"""
    timestamp = date.timestamp()
    os.utime(filepath, (timestamp, timestamp))

# Example: Set March 2024 dates
march_dates = [
    datetime(2024, 3, 5),
    datetime(2024, 3, 10),
    datetime(2024, 3, 15),
]
```

3. **Adding EXIF Data** (optional):
```python
from PIL import Image
import piexif

def add_exif_date(image_path, date):
    """Add EXIF date to image"""
    img = Image.open(image_path)
    exif_dict = {"Exif": {piexif.ExifIFD.DateTimeOriginal: date.strftime("%Y:%m:%d %H:%M:%S")}}
    exif_bytes = piexif.dump(exif_dict)
    img.save(image_path, exif=exif_bytes)
```

4. **Test Prompt**:
```
"Create albums for NCC events, college fests, family trips, and medical bills in March 2024"
```

5. **Expected Results**:
- 4 albums created
- NCC_Events: 3 photos
- College_Fests: 3 photos
- Family_Trips: 3 photos
- Medical_Bills: 3 photos
- All dated March 2024

### Testing Commands

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=core tests/

# Run property tests only
pytest tests/ -k "property"

# Run integration tests only
pytest tests/integration/

# Run with verbose output
pytest -v tests/
```

## Implementation Notes

### Python Version
- Target: Python 3.8+
- Reason: Dataclasses, pathlib, type hints

### Dependencies
```
pillow>=10.0.0        # Image processing
exifread>=3.0.0       # EXIF extraction
pyyaml>=6.0.0         # Config parsing
hypothesis>=6.0.0     # Property-based testing
pytest>=7.0.0         # Unit testing
```

### Performance Considerations

1. **Lazy Loading**: Don't load full images into memory, only read metadata
2. **Batch Operations**: Group file operations to minimize I/O
3. **Progress Indicators**: Show progress for long-running scans
4. **Parallel Processing**: Consider multiprocessing for large photo sets (future enhancement)

### Future Enhancements

1. **Vision Model Integration**: Use AI to analyze photo content for smarter matching
2. **Duplicate Detection**: Identify and handle duplicate photos
3. **Face Recognition**: Group photos by people
4. **Cloud Storage**: Support Google Photos, iCloud, Dropbox
5. **Web UI**: Browser-based interface for prompt input and gallery viewing
6. **Undo/Rollback**: Ability to reverse album organization
7. **Smart Suggestions**: Analyze photos and suggest album names

### Security Considerations

1. **Path Traversal**: Validate all paths to prevent directory traversal attacks
2. **File Size Limits**: Reject files above reasonable size limit
3. **Malicious Files**: Validate image files before processing
4. **Permission Checks**: Verify read/write permissions before operations

## Deployment

### Installation Steps

1. Clone repository
2. Install Python 3.8+
3. Install dependencies: `pip install -r requirements.txt`
4. Create configuration: Copy sample config.yaml and edit paths
5. Test installation: Run with --dry-run flag

### Usage Examples

```bash
# Basic usage
python .kiro/hooks/album.py --prompt "Create albums for vacation photos in 2024"

# Dry run (preview without changes)
python .kiro/hooks/album.py --prompt "Organize by event type" --dry-run

# Backup mode (keep originals)
python .kiro/hooks/album.py --prompt "Sort by month" --backup

# With notifications
python .kiro/hooks/album.py --prompt "Create family albums" --notify
```

### Troubleshooting

**Issue**: No photos found
- **Solution**: Check source_folder path in config.yaml
- **Solution**: Verify photos have supported extensions

**Issue**: EXIF errors
- **Solution**: Install exifread: `pip install exifread`
- **Solution**: System will fall back to file timestamps

**Issue**: Permission denied
- **Solution**: Check folder permissions
- **Solution**: Run with appropriate user privileges

**Issue**: No albums created
- **Solution**: Check prompt contains clear album names
- **Solution**: Verify photo filenames/dates match criteria
- **Solution**: Review unmatched.log for details
