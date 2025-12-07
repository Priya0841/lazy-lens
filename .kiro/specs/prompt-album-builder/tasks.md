# Implementation Plan

- [x] 1. Set up project structure and configuration





  - Create directory structure: core/, logs/, output/Albums/, .kiro/hooks/
  - Create requirements.txt with dependencies (pillow, exifread, pyyaml, hypothesis, pytest)
  - Create sample .kiro/config.yaml with placeholder paths and comments
  - Create project README.md with installation and usage instructions
  - _Requirements: 12.1, 12.2, 12.3, 12.6, 12.7, 13.1-13.6, 14.1-14.6, 15.1-15.3_

- [x] 2. Implement configuration loader


  - Create core/config.py with Config class
  - Implement YAML loading and validation
  - Implement path validation for source_folder and target_albums_folder
  - Add error handling for missing/invalid configuration
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ]* 2.1 Write property test for configuration loading
  - **Property 2: Configuration values are correctly applied**
  - **Validates: Requirements 2.2, 2.3**

- [x] 3. Implement prompt parser


  - Create core/matcher.py with PromptParser class
  - Implement album name extraction (split on commas and conjunctions)
  - Implement date extraction with regex patterns (month names, years, YYYY-MM format)
  - Implement keyword extraction from album names
  - Create AlbumSpec and DateFilter dataclasses
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [ ]* 3.1 Write property test for prompt parsing
  - **Property 1: Prompt parsing extracts all album specifications**
  - **Validates: Requirements 1.1, 1.2, 1.3, 1.4**

- [x] 4. Implement photo scanner


  - Create core/scanner.py with PhotoScanner class
  - Implement recursive directory traversal
  - Implement file metadata extraction (timestamps, filename, folder name)
  - Implement EXIF extraction using exifread library
  - Add fallback to file timestamps when EXIF unavailable
  - Create PhotoMetadata and ExifData dataclasses
  - Support common image formats (.jpg, .jpeg, .png, .heic, .raw, .cr2, .nef)
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

- [ ]* 4.1 Write property test for recursive scanning
  - **Property 5: Scanner finds all photos recursively**
  - **Validates: Requirements 4.1**

- [ ]* 4.2 Write property test for metadata extraction
  - **Property 6: Scanner extracts complete metadata**
  - **Validates: Requirements 4.2, 4.3, 4.4**

- [ ]* 4.3 Write property test for EXIF extraction
  - **Property 7: EXIF extraction succeeds for valid metadata**
  - **Validates: Requirements 4.5**

- [ ]* 4.4 Write property test for format support
  - **Property 8: All supported formats are processed**
  - **Validates: Requirements 4.7**

- [x] 5. Implement pattern matcher

  - Add PatternMatcher class to core/matcher.py
  - Implement filename pattern matching with case-insensitive comparison
  - Implement date range matching against EXIF/file dates
  - Implement folder name pattern matching
  - Implement wildcard pattern support (convert * to regex)
  - Implement first-match precedence logic
  - Track unmatched photos
  - Create MatchResult dataclass
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

- [ ]* 5.1 Write property test for filename matching
  - **Property 9: Filename matching works correctly**
  - **Validates: Requirements 5.1**

- [ ]* 5.2 Write property test for date matching
  - **Property 10: Date matching works correctly**
  - **Validates: Requirements 5.2**

- [ ]* 5.3 Write property test for folder matching
  - **Property 11: Folder name matching works correctly**
  - **Validates: Requirements 5.3**

- [ ]* 5.4 Write property test for first-match precedence
  - **Property 12: First-match precedence is enforced**
  - **Validates: Requirements 5.4**

- [ ]* 5.5 Write property test for unmatched logging
  - **Property 13: Unmatched photos are logged**
  - **Validates: Requirements 5.5**

- [ ]* 5.6 Write property test for case-insensitive matching
  - **Property 14: Case-insensitive matching works**
  - **Validates: Requirements 5.6**

- [ ]* 5.7 Write property test for wildcard patterns
  - **Property 15: Wildcard patterns match correctly**
  - **Validates: Requirements 5.7**

- [x] 6. Implement album creator


  - Create core/albums.py with AlbumCreator class
  - Implement standardized folder naming (YYYY-MM-AlbumName)
  - Implement date selection logic (filter date or earliest photo date)
  - Implement photo copying for backup mode using shutil.copy2()
  - Implement photo moving for default mode using shutil.move()
  - Implement timestamp preservation
  - Implement filename conflict resolution with numeric suffixes
  - Create target directory if it doesn't exist
  - Create Album dataclass
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ]* 6.1 Write property test for folder naming convention
  - **Property 16: Album folder naming follows convention**
  - **Validates: Requirements 6.1, 6.2, 6.3**

- [ ]* 6.2 Write property test for directory creation
  - **Property 17: Target directory is created if missing**
  - **Validates: Requirements 6.4**

- [ ]* 6.3 Write property test for existing album handling
  - **Property 18: Existing albums accept new photos**
  - **Validates: Requirements 6.5**

- [ ]* 6.4 Write property test for move mode
  - **Property 19: Move mode removes source files**
  - **Validates: Requirements 7.2**

- [ ]* 6.5 Write property test for timestamp preservation
  - **Property 20: File timestamps are preserved**
  - **Validates: Requirements 7.3**

- [ ]* 6.6 Write property test for filename preservation
  - **Property 21: Filenames are preserved**
  - **Validates: Requirements 7.4**

- [ ]* 6.7 Write property test for conflict resolution
  - **Property 22: Filename conflicts are resolved with suffixes**
  - **Validates: Requirements 7.5**

- [x] 7. Implement documentation generation

  - Add README generation to AlbumCreator
  - Add summary.json generation to AlbumCreator
  - Include all required fields: album_name, total_photos, earliest_date, latest_date, keywords_used, original_prompt
  - Format dates in ISO 8601 format (YYYY-MM-DD)
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ]* 7.1 Write property test for documentation generation
  - **Property 23: Album documentation is generated**
  - **Validates: Requirements 8.1, 8.2**

- [ ]* 7.2 Write property test for documentation content
  - **Property 24: Documentation contains required fields**
  - **Validates: Requirements 8.3, 8.4**

- [ ]* 7.3 Write property test for date formatting
  - **Property 25: Dates use ISO 8601 format**
  - **Validates: Requirements 8.5**

- [x] 8. Implement report generator


  - Create core/report.py with ReportGenerator class
  - Implement unmatched.log generation in logs/ directory
  - Implement terminal summary output with statistics
  - Implement timestamped log file creation
  - Implement log level indicators (INFO, WARNING, ERROR)
  - Add dry-run mode output prefix "[DRY RUN]"
  - _Requirements: 9.1, 9.2, 9.6, 10.1, 10.2, 10.4, 10.5, 10.6, 11.1, 11.2, 11.3, 11.4, 11.5_

- [ ]* 8.1 Write property test for unmatched log generation
  - **Property 26: Unmatched log is generated**
  - **Property 27: Unmatched log contains all unmatched photos**
  - **Validates: Requirements 9.1, 9.2, 9.6**

- [ ]* 8.2 Write property test for log file creation
  - **Property 31: Timestamped log files are created**
  - **Validates: Requirements 10.5**

- [ ]* 8.3 Write property test for log formatting
  - **Property 32: Log messages include level indicators**
  - **Validates: Requirements 10.6**

- [ ]* 8.4 Write property test for terminal summary
  - **Property 33: Terminal summary displays all statistics**
  - **Validates: Requirements 11.1, 11.2, 11.3, 11.4**

- [ ]* 8.5 Write property test for dry-run output
  - **Property 34: Dry-run output is clearly marked**
  - **Validates: Requirements 11.5**

- [x] 9. Implement gallery generator


  - Create core/gallery.py with GalleryGenerator class
  - Implement index.html generation in target albums folder
  - Implement thumbnail creation using Pillow (200x200 size)
  - Generate HTML with responsive grid layout
  - Include album metadata (name, photo count, date range)
  - Add CSS styling for clean presentation
  - _Requirements: 9.3, 9.4, 9.5, 9.7_

- [ ]* 9.1 Write property test for index generation
  - **Property 28: Master index is generated**
  - **Validates: Requirements 9.3, 9.7**

- [ ]* 9.2 Write property test for index content
  - **Property 29: Index contains all album metadata**
  - **Validates: Requirements 9.4, 9.5**



- [ ] 10. Implement CLI interface (Kiro hook)
  - Create .kiro/hooks/album.py with main() function
  - Implement argument parsing with argparse (--prompt, --dry-run, --backup, --notify)
  - Orchestrate the full pipeline: config → parse → scan → match → create → report → gallery
  - Add error handling for missing arguments
  - Implement dry-run mode flag propagation
  - Implement backup mode flag propagation
  - Add usage instructions for missing arguments
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ]* 10.1 Write property test for dry-run mode
  - **Property 3: Dry-run mode prevents file modifications**
  - **Validates: Requirements 3.2**

- [ ]* 10.2 Write property test for backup mode
  - **Property 4: Backup mode preserves original files**


  - **Validates: Requirements 3.3, 7.1**

- [ ] 11. Add comprehensive error handling
  - Add configuration error handling (missing file, invalid paths)
  - Add parsing error handling (invalid dates, empty prompts)
  - Add scanning error handling (empty folder, EXIF errors)
  - Add matching error handling (no matches, empty albums)
  - Add file operation error handling (permissions, disk full, conflicts)
  - Add gallery error handling (thumbnail creation, HTML write)
  - Implement error recovery strategy (continue on partial failure)
  - _Requirements: 2.4, 2.5, 10.1, 10.2, 10.3, 10.4_


- [ ]* 11.1 Write property test for error recovery
  - **Property 30: File operation errors don't halt processing**
  - **Validates: Requirements 10.4**

- [x] 12. Create test dataset preparation script

  - Create scripts/prepare_test_data.py
  - Implement function to create test directory structure
  - Implement function to set file timestamps
  - Implement function to add EXIF data to images
  - Create sample test photos with appropriate filenames
  - Document test prompt and expected results
  - _Requirements: 14.6_

- [x] 13. Write comprehensive documentation

  - Update README.md with complete installation steps
  - Add usage examples for all command-line flags
  - Add troubleshooting section
  - Document test dataset preparation
  - Add example prompts and expected outputs
  - Document configuration options
  - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_

- [x] 14. Final checkpoint - Ensure all tests pass



  - Ensure all tests pass, ask the user if questions arise.
