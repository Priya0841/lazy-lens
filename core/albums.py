"""Album creation and photo organization for PromptAlbumBuilder."""

import shutil
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

from core.matcher import AlbumSpec, PhotoMetadata, MatchResult


@dataclass
class Album:
    """Album with organized photos."""
    name: str
    path: Path
    photos: List[PhotoMetadata]
    earliest_date: datetime
    latest_date: datetime
    keywords: List[str]


class AlbumCreator:
    """Creates album folders and organizes photos."""
    
    def __init__(self, target_folder: Path, backup_mode: bool = False, dry_run: bool = False):
        """Initialize album creator.
        
        Args:
            target_folder: Root folder for albums
            backup_mode: If True, copy photos instead of moving
            dry_run: If True, simulate without modifying files
        """
        self.target_folder = target_folder
        self.backup_mode = backup_mode
        self.dry_run = dry_run
    
    def create_albums(self, match_result: MatchResult, album_specs: List[AlbumSpec]) -> List[Album]:
        """Create albums from match results.
        
        Args:
            match_result: Result of photo matching
            album_specs: Original album specifications
            
        Returns:
            List of created albums
        """
        albums = []
        
        # Create target folder if it doesn't exist
        if not self.dry_run and not self.target_folder.exists():
            self.target_folder.mkdir(parents=True, exist_ok=True)
        
        for spec in album_specs:
            photos = match_result.matched.get(spec.name, [])
            
            # Skip albums with no photos
            if not photos:
                print(f"Warning: Album '{spec.name}' matched no photos. Skipping folder creation.")
                continue
            
            # Determine album date
            album_date = self._get_album_date(photos, spec)
            
            # Create album folder
            album_path = self.create_folder(spec.name, album_date)
            
            # Organize photos into album
            organized_count = self.organize_photos(album_path, photos)
            
            # Create album object
            dates = [p.exif_date or p.file_created for p in photos]
            album = Album(
                name=spec.name,
                path=album_path,
                photos=photos,
                earliest_date=min(dates),
                latest_date=max(dates),
                keywords=spec.keywords
            )
            
            # Generate documentation
            self.generate_readme(album, spec.original_prompt)
            self.generate_summary(album, spec.original_prompt)
            
            albums.append(album)
            
            print(f"[{'DRY RUN' if self.dry_run else 'INFO'}] Created album: {album_path.name} ({organized_count} photos)")
        
        return albums
    
    def _get_album_date(self, photos: List[PhotoMetadata], spec: AlbumSpec) -> datetime:
        """Determine date for album folder naming.
        
        Args:
            photos: List of photos in album
            spec: Album specification
            
        Returns:
            Date to use for folder name
        """
        # Use date filter if present
        if spec.date_filter:
            if spec.date_filter.year and spec.date_filter.month:
                return datetime(spec.date_filter.year, spec.date_filter.month, 1)
            elif spec.date_filter.year:
                return datetime(spec.date_filter.year, 1, 1)
        
        # Otherwise use earliest photo date
        dates = [p.exif_date or p.file_created for p in photos]
        return min(dates)
    
    def create_folder(self, album_name: str, date: datetime) -> Path:
        """Create album folder with standardized naming.
        
        Args:
            album_name: Name of album
            date: Date for folder name
            
        Returns:
            Path to created folder
        """
        # Format: YYYY-MM-AlbumName
        folder_name = f"{date.year:04d}-{date.month:02d}-{album_name.replace(' ', '-')}"
        album_path = self.target_folder / folder_name
        
        if not self.dry_run:
            album_path.mkdir(parents=True, exist_ok=True)
        
        return album_path
    
    def organize_photos(self, album_path: Path, photos: List[PhotoMetadata]) -> int:
        """Organize photos into album folder.
        
        Args:
            album_path: Path to album folder
            photos: List of photos to organize
            
        Returns:
            Number of photos organized
        """
        organized_count = 0
        
        for photo in photos:
            try:
                # Determine destination path
                dest_path = album_path / photo.filename
                
                # Handle filename conflicts
                dest_path = self._resolve_conflict(dest_path)
                
                if not self.dry_run:
                    if self.backup_mode:
                        # Copy photo
                        shutil.copy2(photo.path, dest_path)
                    else:
                        # Move photo
                        shutil.move(str(photo.path), str(dest_path))
                    
                    # Preserve timestamps
                    self._preserve_timestamps(photo, dest_path)
                
                organized_count += 1
                
            except Exception as e:
                print(f"Error: Permission denied copying {photo.path} to {dest_path}: {e}")
                continue
        
        return organized_count
    
    def _resolve_conflict(self, dest_path: Path) -> Path:
        """Resolve filename conflicts by adding numeric suffix.
        
        Args:
            dest_path: Destination path
            
        Returns:
            Resolved path (may have suffix)
        """
        if not dest_path.exists():
            return dest_path
        
        # Add numeric suffix
        stem = dest_path.stem
        suffix = dest_path.suffix
        counter = 1
        
        while True:
            new_path = dest_path.parent / f"{stem}_{counter}{suffix}"
            if not new_path.exists():
                print(f"Info: File {dest_path.name} already exists. Renamed to {new_path.name}")
                return new_path
            counter += 1
    
    def _preserve_timestamps(self, photo: PhotoMetadata, dest_path: Path):
        """Preserve file timestamps.
        
        Args:
            photo: Original photo metadata
            dest_path: Destination path
        """
        import os
        
        # Get original timestamps
        stat = photo.path.stat() if photo.path.exists() else dest_path.stat()
        
        # Set timestamps on destination
        os.utime(dest_path, (stat.st_atime, stat.st_mtime))
    
    def generate_readme(self, album: Album, original_prompt: str):
        """Generate README.md for album.
        
        Args:
            album: Album object
            original_prompt: Original user prompt
        """
        if self.dry_run:
            return
        
        readme_path = album.path / "README.md"
        
        content = f"""# {album.name}

## Album Information

- **Total Photos**: {len(album.photos)}
- **Date Range**: {album.earliest_date.strftime('%Y-%m-%d')} to {album.latest_date.strftime('%Y-%m-%d')}
- **Keywords**: {', '.join(album.keywords)}

## Original Prompt

```
{original_prompt}
```

## Photos

This album contains {len(album.photos)} photos organized based on the criteria above.

---

*Generated by PromptAlbumBuilder*
"""
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def generate_summary(self, album: Album, original_prompt: str):
        """Generate summary.json for album.
        
        Args:
            album: Album object
            original_prompt: Original user prompt
        """
        if self.dry_run:
            return
        
        summary_path = album.path / "summary.json"
        
        # Build photo list
        photos_list = []
        for photo in album.photos:
            photo_date = photo.exif_date or photo.file_created
            photos_list.append({
                "filename": photo.filename,
                "date_taken": photo_date.strftime('%Y-%m-%d'),
                "size_bytes": photo.size_bytes
            })
        
        summary = {
            "album_name": album.name,
            "total_photos": len(album.photos),
            "earliest_date": album.earliest_date.strftime('%Y-%m-%d'),
            "latest_date": album.latest_date.strftime('%Y-%m-%d'),
            "keywords_used": album.keywords,
            "original_prompt": original_prompt,
            "created_at": datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
            "photos": photos_list
        }
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
