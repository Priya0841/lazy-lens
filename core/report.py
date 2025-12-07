"""Report generation and logging for PromptAlbumBuilder."""

from datetime import datetime
from pathlib import Path
from typing import List

from core.matcher import PhotoMetadata
from core.albums import Album


class ReportGenerator:
    """Generates reports and logs for album building process."""
    
    def __init__(self, log_dir: Path, dry_run: bool = False):
        """Initialize report generator.
        
        Args:
            log_dir: Directory for log files
            dry_run: If True, prefix output with [DRY RUN]
        """
        self.log_dir = log_dir
        self.dry_run = dry_run
        self.log_file = None
        
        # Create log directory if it doesn't exist
        if not dry_run:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            
            # Create timestamped log file
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            self.log_file = self.log_dir / f"{timestamp}.log"
    
    def generate_unmatched_log(self, unmatched: List[PhotoMetadata]):
        """Generate log file for unmatched photos.
        
        Args:
            unmatched: List of unmatched photos
        """
        if self.dry_run:
            return
        
        unmatched_log = self.log_dir / "unmatched.log"
        
        with open(unmatched_log, 'w', encoding='utf-8') as f:
            f.write(f"# Unmatched Photos Log\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Total unmatched: {len(unmatched)}\n\n")
            
            for photo in unmatched:
                f.write(f"{photo.path}\n")
        
        self.log_info(f"Unmatched log created: {unmatched_log}")
    
    def display_summary(self, albums: List[Album], unmatched_count: int, total_scanned: int):
        """Display terminal summary of processing results.
        
        Args:
            albums: List of created albums
            unmatched_count: Number of unmatched photos
            total_scanned: Total number of photos scanned
        """
        prefix = "[DRY RUN] " if self.dry_run else ""
        
        print(f"\n{prefix}Summary:")
        print(f"  Total photos scanned: {total_scanned}")
        print(f"  Albums created: {len(albums)}")
        
        matched_count = sum(len(album.photos) for album in albums)
        print(f"  Photos matched: {matched_count}")
        print(f"  Photos unmatched: {unmatched_count}")
        
        if not self.dry_run:
            print(f"  Unmatched log: logs/unmatched.log")
        
        print()
    
    def log_error(self, message: str):
        """Log error message.
        
        Args:
            message: Error message
        """
        self._log("ERROR", message)
    
    def log_warning(self, message: str):
        """Log warning message.
        
        Args:
            message: Warning message
        """
        self._log("WARNING", message)
    
    def log_info(self, message: str):
        """Log info message.
        
        Args:
            message: Info message
        """
        self._log("INFO", message)
    
    def _log(self, level: str, message: str):
        """Write log message to file and console.
        
        Args:
            level: Log level (INFO, WARNING, ERROR)
            message: Log message
        """
        prefix = "[DRY RUN] " if self.dry_run else ""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] [{level}] {message}"
        
        # Print to console
        print(f"{prefix}{log_line}")
        
        # Write to log file
        if self.log_file and not self.dry_run:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_line + '\n')
