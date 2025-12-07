# Requirements Document

## Introduction

PromptAlbumBuilder is a Kiro agent workflow that automates photo album organization from natural language prompts. The system enables users to organize photos into albums by providing a single sentence describing the desired album structure, date filters, and categorization criteria. The system scans source photos, extracts metadata, matches photos to albums based on intelligent pattern matching, and generates organized album folders with comprehensive documentation and gallery previews.

## Glossary

- **PromptAlbumBuilder**: The Kiro agent workflow system that automates photo album organization
- **Source Folder**: The directory containing unorganized photos to be processed
- **Target Albums Folder**: The directory where organized album folders will be created
- **Album**: A folder containing photos matched to specific criteria (name, date, keywords)
- **EXIF Metadata**: Exchangeable Image File Format data embedded in photos containing timestamp, location, and camera information
- **Dry Run Mode**: Execution mode that simulates album creation without modifying files
- **Backup Mode**: Execution mode that copies photos instead of moving them
- **Unmatched Photos**: Photos that do not match any album criteria
- **Master Index**: An HTML gallery preview showing all created albums
- **Configuration File**: YAML file at .kiro/config.yaml containing source and target folder paths
- **Kiro Hook**: Command-line interface for triggering the album builder workflow

## Requirements

### Requirement 1

**User Story:** As a user, I want to provide a natural language prompt describing my desired album organization, so that I can quickly organize photos without manual sorting.

#### Acceptance Criteria

1. WHEN a user executes the Kiro hook command with a prompt THEN the PromptAlbumBuilder SHALL parse the prompt to extract album names, date filters, and keywords
2. WHEN the prompt contains multiple album names separated by commas or conjunctions THEN the PromptAlbumBuilder SHALL identify each distinct album name
3. WHEN the prompt contains date expressions (month names, years, date ranges) THEN the PromptAlbumBuilder SHALL extract and normalize the date filters
4. WHEN the prompt contains descriptive keywords THEN the PromptAlbumBuilder SHALL extract keywords for pattern matching
5. THE PromptAlbumBuilder SHALL accept prompts in natural language format without requiring structured syntax

### Requirement 2

**User Story:** As a user, I want the system to read configuration from a YAML file, so that I can specify source and target folders without modifying code.

#### Acceptance Criteria

1. WHEN the PromptAlbumBuilder starts THEN the system SHALL read the configuration file from .kiro/config.yaml
2. WHEN the configuration file contains source_folder THEN the PromptAlbumBuilder SHALL use this path as the photo source directory
3. WHEN the configuration file contains target_albums_folder THEN the PromptAlbumBuilder SHALL use this path as the album output directory
4. IF the configuration file is missing or unreadable THEN the PromptAlbumBuilder SHALL report a clear error message and terminate
5. IF the source_folder or target_albums_folder paths are invalid THEN the PromptAlbumBuilder SHALL report an error and terminate

### Requirement 3

**User Story:** As a user, I want to invoke the album builder through a command-line interface, so that I can integrate it into my workflow and scripts.

#### Acceptance Criteria

1. THE PromptAlbumBuilder SHALL provide a command-line interface accessible via "kiro album --prompt <text>"
2. WHEN the --dry-run flag is provided THEN the PromptAlbumBuilder SHALL simulate album creation without modifying files
3. WHEN the --backup flag is provided THEN the PromptAlbumBuilder SHALL copy photos instead of moving them
4. WHEN the --notify flag is provided THEN the PromptAlbumBuilder SHALL display notifications for completion status
5. WHEN required arguments are missing THEN the PromptAlbumBuilder SHALL display usage instructions and terminate

### Requirement 4

**User Story:** As a user, I want the system to scan my source folder and collect photo metadata, so that photos can be matched to albums intelligently.

#### Acceptance Criteria

1. WHEN the PromptAlbumBuilder scans the source folder THEN the system SHALL recursively traverse all subdirectories
2. WHEN the scanner encounters image files THEN the system SHALL extract file timestamps (creation date, modification date)
3. WHEN the scanner encounters image files THEN the system SHALL record the parent folder name
4. WHEN the scanner encounters image files THEN the system SHALL record the filename
5. WHEN image files contain EXIF metadata THEN the PromptAlbumBuilder SHALL extract date taken and location information
6. IF EXIF metadata is unreadable or missing THEN the PromptAlbumBuilder SHALL log a warning and use file timestamps
7. THE PromptAlbumBuilder SHALL support common image formats (JPEG, PNG, HEIC, RAW)

### Requirement 5

**User Story:** As a user, I want photos to be matched to albums using intelligent pattern matching, so that organization happens automatically without manual intervention.

#### Acceptance Criteria

1. WHEN matching photos to albums THEN the PromptAlbumBuilder SHALL compare filename patterns against album keywords
2. WHEN matching photos to albums THEN the PromptAlbumBuilder SHALL compare EXIF dates against date filters
3. WHEN matching photos to albums THEN the PromptAlbumBuilder SHALL compare folder names against album keywords
4. WHEN a photo matches multiple albums THEN the PromptAlbumBuilder SHALL assign the photo to the first matching album
5. WHEN a photo matches no albums THEN the PromptAlbumBuilder SHALL record it in the unmatched photos log
6. THE PromptAlbumBuilder SHALL support case-insensitive pattern matching
7. THE PromptAlbumBuilder SHALL support wildcard patterns (e.g., "NCC*", "*fest*", "*bill*")

### Requirement 6

**User Story:** As a user, I want albums to be created with standardized folder naming, so that I can easily locate and browse albums chronologically.

#### Acceptance Criteria

1. WHEN creating album folders THEN the PromptAlbumBuilder SHALL use the format "YYYY-MM-AlbumName"
2. WHEN the album has a date filter THEN the PromptAlbumBuilder SHALL use the filter date in the folder name
3. WHEN the album has no date filter THEN the PromptAlbumBuilder SHALL use the earliest photo date in the folder name
4. WHEN the target albums folder does not exist THEN the PromptAlbumBuilder SHALL create it
5. IF an album folder already exists THEN the PromptAlbumBuilder SHALL append photos to the existing folder

### Requirement 7

**User Story:** As a user, I want matched photos to be organized into their respective album folders, so that I have a clean organized photo library.

#### Acceptance Criteria

1. WHEN photos are matched to albums in backup mode THEN the PromptAlbumBuilder SHALL copy photos to album folders
2. WHEN photos are matched to albums in default mode THEN the PromptAlbumBuilder SHALL move photos to album folders
3. WHEN copying or moving photos THEN the PromptAlbumBuilder SHALL preserve original file timestamps
4. WHEN copying or moving photos THEN the PromptAlbumBuilder SHALL preserve original filenames
5. IF a photo with the same name exists in the target album THEN the PromptAlbumBuilder SHALL append a numeric suffix to avoid overwriting

### Requirement 8

**User Story:** As a user, I want each album to contain documentation files, so that I can understand the album contents and organization criteria.

#### Acceptance Criteria

1. WHEN an album is created THEN the PromptAlbumBuilder SHALL generate a README.md file in the album folder
2. WHEN an album is created THEN the PromptAlbumBuilder SHALL generate a summary.json file in the album folder
3. WHEN generating README.md THEN the file SHALL contain album name, total photos, date range, keywords used, and original prompt
4. WHEN generating summary.json THEN the file SHALL contain album_name, total_photos, earliest_date, latest_date, keywords_used, and original_prompt fields
5. THE PromptAlbumBuilder SHALL format dates in ISO 8601 format (YYYY-MM-DD) in documentation files

### Requirement 9

**User Story:** As a user, I want a log of unmatched photos and a master gallery index, so that I can review photos that weren't organized and preview all albums.

#### Acceptance Criteria

1. WHEN the album building process completes THEN the PromptAlbumBuilder SHALL generate an unmatched.log file
2. WHEN generating unmatched.log THEN the file SHALL list all photo paths that matched no album criteria
3. WHEN the album building process completes THEN the PromptAlbumBuilder SHALL generate a master index.html file
4. WHEN generating index.html THEN the file SHALL display thumbnail previews of all created albums
5. WHEN generating index.html THEN the file SHALL include album names, photo counts, and date ranges
6. THE PromptAlbumBuilder SHALL create the unmatched.log file in the logs/ directory
7. THE PromptAlbumBuilder SHALL create the index.html file in the target albums folder

### Requirement 10

**User Story:** As a user, I want comprehensive error handling and logging, so that I can troubleshoot issues and understand what went wrong.

#### Acceptance Criteria

1. WHEN the PromptAlbumBuilder encounters invalid date formats THEN the system SHALL log a warning and skip the invalid date filter
2. WHEN an album contains zero matched photos THEN the PromptAlbumBuilder SHALL log a warning and skip folder creation
3. WHEN EXIF metadata is unreadable THEN the PromptAlbumBuilder SHALL log a warning and fall back to file timestamps
4. WHEN file operations fail (copy, move, create) THEN the PromptAlbumBuilder SHALL log the error with file path and continue processing
5. THE PromptAlbumBuilder SHALL write all logs to a timestamped log file in the logs/ directory
6. THE PromptAlbumBuilder SHALL include log level indicators (INFO, WARNING, ERROR) in log messages

### Requirement 11

**User Story:** As a user, I want clear terminal output showing processing results, so that I can quickly understand what the system accomplished.

#### Acceptance Criteria

1. WHEN the album building process completes THEN the PromptAlbumBuilder SHALL display the total number of photos scanned
2. WHEN the album building process completes THEN the PromptAlbumBuilder SHALL display the number of albums created
3. WHEN the album building process completes THEN the PromptAlbumBuilder SHALL display matched photo counts per album
4. WHEN the album building process completes THEN the PromptAlbumBuilder SHALL display the total number of unmatched photos
5. WHEN running in dry-run mode THEN the PromptAlbumBuilder SHALL prefix output with "[DRY RUN]" indicators
6. THE PromptAlbumBuilder SHALL display progress indicators during scanning and matching operations

### Requirement 12

**User Story:** As a developer, I want the project structured with clear separation of concerns, so that the codebase is maintainable and extensible.

#### Acceptance Criteria

1. THE PromptAlbumBuilder SHALL organize code into core modules: scanner.py, matcher.py, albums.py, report.py, and gallery.py
2. THE PromptAlbumBuilder SHALL place the Kiro hook implementation in .kiro/hooks/album.py
3. THE PromptAlbumBuilder SHALL store configuration in .kiro/config.yaml
4. THE PromptAlbumBuilder SHALL create logs in the logs/ directory
5. THE PromptAlbumBuilder SHALL create album output in the output/Albums/ directory
6. THE PromptAlbumBuilder SHALL provide a requirements.txt file listing all Python dependencies
7. THE PromptAlbumBuilder SHALL provide a README.md file with usage instructions and examples

### Requirement 13

**User Story:** As a user, I want the system to use reliable Python libraries for image processing, so that metadata extraction and file operations are robust.

#### Acceptance Criteria

1. THE PromptAlbumBuilder SHALL use the Pillow library for image file validation
2. THE PromptAlbumBuilder SHALL use the exifread library for EXIF metadata extraction
3. THE PromptAlbumBuilder SHALL use the pathlib library for cross-platform path operations
4. THE PromptAlbumBuilder SHALL use the json library for generating summary files
5. THE PromptAlbumBuilder SHALL use the shutil library for file copy and move operations
6. THE PromptAlbumBuilder SHALL use the argparse library for command-line argument parsing

### Requirement 14

**User Story:** As a user, I want comprehensive documentation, so that I can understand how to install, configure, and use the system.

#### Acceptance Criteria

1. THE PromptAlbumBuilder SHALL provide a README.md file explaining installation steps
2. THE PromptAlbumBuilder SHALL provide documentation explaining how to run the album builder command
3. THE PromptAlbumBuilder SHALL provide documentation explaining dry-run mode usage
4. THE PromptAlbumBuilder SHALL provide documentation explaining backup mode usage
5. THE PromptAlbumBuilder SHALL provide documentation with example prompts and expected outputs
6. THE PromptAlbumBuilder SHALL provide instructions for preparing test datasets with sample photos

### Requirement 15

**User Story:** As a user, I want a sample configuration file, so that I can quickly set up the system with my own folder paths.

#### Acceptance Criteria

1. THE PromptAlbumBuilder SHALL provide a sample config.yaml file with placeholder paths
2. WHEN the sample config.yaml is provided THEN it SHALL include comments explaining each configuration option
3. WHEN the sample config.yaml is provided THEN it SHALL include example values for source_folder and target_albums_folder
