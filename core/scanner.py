"""Photo scanning and metadata extraction for PromptAlbumBuilder."""

import os
import exifread
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

from core.matcher import PhotoMetadata


@dataclass
class ExifData:
    """EXIF metadata extracted from photo."""
    date_taken: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    camera_model: Optional[str] = None


class PhotoScanner:
    """Scans directories for photos and extracts metadata."""
    
    def __init__(self, source_folder: Path, supported_extensions: Optional[List[str]] = None):
        """Initialize photo scanner.
        
        Args:
            source_folder: Root folder to scan for photos
            supported_extensions: List of supported file extensions
        """
        self.source_folder = source_folder
        self.supported_extensions = supported_extensions or [
            '.jpg', '.jpeg', '.png', '.heic', '.raw', '.cr2', '.nef'
        ]
        # Normalize extensions to lowercase
        self.supported_extensions = [ext.lower() for ext in self.supported_extensions]
    
    def scan(self) -> List[PhotoMetadata]:
        """Scan source folder recursively for photos.
        
        Returns:
            List of photo metadata
        """
        photos = []
        
        # Recursively walk through directory
        for root, dirs, files in os.walk(self.source_folder):
            for filename in files:
                # Check if file has supported extension
                file_ext = Path(filename).suffix.lower()
                if file_ext in self.supported_extensions:
                    file_path = Path(root) / filename
                    
                    try:
                        metadata = self._extract_metadata(file_path)
                        photos.append(metadata)
                    except Exception as e:
                        # Log error but continue processing
                        print(f"Warning: Could not process {file_path}: {e}")
                        continue
        
        return photos
    
    def _extract_metadata(self, photo_path: Path) -> PhotoMetadata:
        """Extract metadata from a single photo.
        
        Args:
            photo_path: Path to photo file
            
        Returns:
            Photo metadata
        """
        # Get file stats
        stat = photo_path.stat()
        file_created = datetime.fromtimestamp(stat.st_ctime)
        file_modified = datetime.fromtimestamp(stat.st_mtime)
        size_bytes = stat.st_size
        
        # Get folder name (parent directory)
        folder_name = photo_path.parent.name
        
        # Extract EXIF data
        exif_data = self.extract_exif(photo_path)
        
        metadata = PhotoMetadata(
            path=photo_path,
            filename=photo_path.name,
            folder_name=folder_name,
            file_created=file_created,
            file_modified=file_modified,
            exif_date=exif_data.date_taken if exif_data else None,
            exif_location=(exif_data.latitude, exif_data.longitude) if exif_data and exif_data.latitude else None,
            size_bytes=size_bytes
        )
        
        return metadata
    
    def extract_exif(self, photo_path: Path) -> Optional[ExifData]:
        """Extract EXIF metadata from photo.
        
        Args:
            photo_path: Path to photo file
            
        Returns:
            EXIF data or None if extraction fails
        """
        try:
            with open(photo_path, 'rb') as f:
                tags = exifread.process_file(f, details=False)
            
            if not tags:
                return None
            
            exif_data = ExifData()
            
            # Extract date taken
            date_tag = tags.get('EXIF DateTimeOriginal') or tags.get('Image DateTime')
            if date_tag:
                try:
                    # EXIF date format: "YYYY:MM:DD HH:MM:SS"
                    date_str = str(date_tag)
                    exif_data.date_taken = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                except ValueError:
                    pass
            
            # Extract GPS coordinates
            gps_lat = tags.get('GPS GPSLatitude')
            gps_lat_ref = tags.get('GPS GPSLatitudeRef')
            gps_lon = tags.get('GPS GPSLongitude')
            gps_lon_ref = tags.get('GPS GPSLongitudeRef')
            
            if gps_lat and gps_lon:
                try:
                    lat = self._convert_gps_to_decimal(gps_lat, gps_lat_ref)
                    lon = self._convert_gps_to_decimal(gps_lon, gps_lon_ref)
                    exif_data.latitude = lat
                    exif_data.longitude = lon
                except Exception:
                    pass
            
            # Extract camera model
            camera_tag = tags.get('Image Model')
            if camera_tag:
                exif_data.camera_model = str(camera_tag)
            
            return exif_data
            
        except Exception as e:
            # Return None if EXIF extraction fails
            print(f"Warning: Could not read EXIF data from {photo_path.name}. Using file timestamps.")
            return None
    
    def _convert_gps_to_decimal(self, gps_coord, gps_ref) -> float:
        """Convert GPS coordinates from EXIF format to decimal degrees.
        
        Args:
            gps_coord: GPS coordinate in EXIF format
            gps_ref: GPS reference (N/S/E/W)
            
        Returns:
            Decimal degree coordinate
        """
        # GPS coordinates are stored as [degrees, minutes, seconds]
        degrees = float(gps_coord.values[0].num) / float(gps_coord.values[0].den)
        minutes = float(gps_coord.values[1].num) / float(gps_coord.values[1].den)
        seconds = float(gps_coord.values[2].num) / float(gps_coord.values[2].den)
        
        decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
        
        # Apply reference (negative for S and W)
        if str(gps_ref) in ['S', 'W']:
            decimal = -decimal
        
        return decimal
    
    def get_file_timestamp(self, photo_path: Path) -> datetime:
        """Get file creation timestamp.
        
        Args:
            photo_path: Path to photo file
            
        Returns:
            File creation datetime
        """
        stat = photo_path.stat()
        return datetime.fromtimestamp(stat.st_ctime)
