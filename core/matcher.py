"""Prompt parsing and pattern matching for PromptAlbumBuilder."""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path


@dataclass
class DateFilter:
    """Date filter specification."""
    year: Optional[int] = None
    month: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


@dataclass
class AlbumSpec:
    """Album specification extracted from prompt."""
    name: str
    keywords: List[str]
    date_filter: Optional[DateFilter] = None
    original_prompt: str = ""


@dataclass
class PhotoMetadata:
    """Complete metadata for a single photo."""
    path: Path
    filename: str
    folder_name: str
    file_created: datetime
    file_modified: datetime
    exif_date: Optional[datetime] = None
    exif_location: Optional[tuple] = None
    size_bytes: int = 0


@dataclass
class MatchResult:
    """Result of matching photos to albums."""
    matched: Dict[str, List[PhotoMetadata]]
    unmatched: List[PhotoMetadata]
    match_stats: Dict[str, int]


class PromptParser:
    """Parses natural language prompts to extract album specifications."""
    
    # Month names for date extraction
    MONTH_NAMES = {
        'january': 1, 'jan': 1,
        'february': 2, 'feb': 2,
        'march': 3, 'mar': 3,
        'april': 4, 'apr': 4,
        'may': 5,
        'june': 6, 'jun': 6,
        'july': 7, 'jul': 7,
        'august': 8, 'aug': 8,
        'september': 9, 'sep': 9, 'sept': 9,
        'october': 10, 'oct': 10,
        'november': 11, 'nov': 11,
        'december': 12, 'dec': 12
    }
    
    # Stop words to exclude from keywords
    STOP_WORDS = {
        'a', 'an', 'and', 'or', 'the', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'create', 'albums', 'album', 'photos',
        'organize', 'sort', 'group'
    }
    
    def parse(self, prompt: str) -> List[AlbumSpec]:
        """Parse prompt to extract album specifications.
        
        Args:
            prompt: Natural language prompt
            
        Returns:
            List of album specifications
        """
        album_names = self.extract_album_names(prompt)
        dates = self.extract_dates(prompt)
        
        # Create album specs
        album_specs = []
        for name in album_names:
            keywords = self.extract_keywords(name)
            # Use first date filter if available (can be enhanced to match dates to specific albums)
            date_filter = dates[0] if dates else None
            
            album_spec = AlbumSpec(
                name=name,
                keywords=keywords,
                date_filter=date_filter,
                original_prompt=prompt
            )
            album_specs.append(album_spec)
        
        return album_specs
    
    def extract_album_names(self, prompt: str) -> List[str]:
        """Extract album names from prompt.
        
        Args:
            prompt: Natural language prompt
            
        Returns:
            List of album names
        """
        # Remove common phrases
        text = prompt.lower()
        text = re.sub(r'create albums? for', '', text)
        text = re.sub(r'organize (photos? )?into', '', text)
        text = re.sub(r'sort (photos? )?by', '', text)
        
        # Remove date expressions to avoid confusion
        text = re.sub(r'\b\d{4}\b', '', text)  # Remove years
        text = re.sub(r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)\b', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\d{4}-\d{2}', '', text)  # Remove YYYY-MM
        
        # Split on commas and conjunctions
        text = re.sub(r'\s+and\s+', ',', text)
        text = re.sub(r'\s+or\s+', ',', text)
        
        # Split and clean
        parts = [p.strip() for p in text.split(',')]
        
        # Filter out empty strings and clean up
        album_names = []
        for part in parts:
            if part and len(part) > 0:
                # Capitalize first letter of each word
                name = ' '.join(word.capitalize() for word in part.split())
                if name:
                    album_names.append(name)
        
        return album_names
    
    def extract_dates(self, prompt: str) -> List[DateFilter]:
        """Extract date filters from prompt.
        
        Args:
            prompt: Natural language prompt
            
        Returns:
            List of date filters
        """
        date_filters = []
        text = prompt.lower()
        
        # Pattern 1: "Month YYYY" (e.g., "March 2024")
        pattern1 = r'\b(' + '|'.join(self.MONTH_NAMES.keys()) + r')\s+(\d{4})\b'
        for match in re.finditer(pattern1, text, re.IGNORECASE):
            month_name = match.group(1).lower()
            year = int(match.group(2))
            month = self.MONTH_NAMES[month_name]
            
            date_filter = DateFilter(year=year, month=month)
            date_filters.append(date_filter)
        
        # Pattern 2: "YYYY-MM" (e.g., "2024-03")
        pattern2 = r'\b(\d{4})-(\d{2})\b'
        for match in re.finditer(pattern2, text):
            year = int(match.group(1))
            month = int(match.group(2))
            
            if 1 <= month <= 12:
                date_filter = DateFilter(year=year, month=month)
                date_filters.append(date_filter)
        
        # Pattern 3: Just year (e.g., "2024")
        if not date_filters:  # Only if no month-year found
            pattern3 = r'\b(\d{4})\b'
            for match in re.finditer(pattern3, text):
                year = int(match.group(1))
                if 2000 <= year <= 2100:  # Reasonable year range
                    date_filter = DateFilter(year=year)
                    date_filters.append(date_filter)
        
        return date_filters
    
    def extract_keywords(self, album_name: str) -> List[str]:
        """Extract keywords from album name.
        
        Args:
            album_name: Album name
            
        Returns:
            List of keywords
        """
        # Convert to lowercase and split
        words = album_name.lower().split()
        
        # Filter out stop words
        keywords = [w for w in words if w not in self.STOP_WORDS]
        
        # Also include the full album name as a keyword
        if album_name.lower() not in keywords:
            keywords.insert(0, album_name.lower())
        
        return keywords


class PatternMatcher:
    """Matches photos to albums based on criteria."""
    
    def __init__(self, album_specs: List[AlbumSpec]):
        """Initialize pattern matcher.
        
        Args:
            album_specs: List of album specifications
        """
        self.album_specs = album_specs
    
    def match(self, photos: List[PhotoMetadata]) -> MatchResult:
        """Match photos to albums.
        
        Args:
            photos: List of photo metadata
            
        Returns:
            Match result with matched and unmatched photos
        """
        matched: Dict[str, List[PhotoMetadata]] = {
            spec.name: [] for spec in self.album_specs
        }
        unmatched: List[PhotoMetadata] = []
        
        for photo in photos:
            matched_album = None
            
            # Try to match against each album spec (first match wins)
            for spec in self.album_specs:
                if self._matches_spec(photo, spec):
                    matched_album = spec.name
                    break
            
            if matched_album:
                matched[matched_album].append(photo)
            else:
                unmatched.append(photo)
        
        # Calculate stats
        match_stats = {name: len(photos) for name, photos in matched.items()}
        
        return MatchResult(
            matched=matched,
            unmatched=unmatched,
            match_stats=match_stats
        )
    
    def _matches_spec(self, photo: PhotoMetadata, spec: AlbumSpec) -> bool:
        """Check if photo matches album specification.
        
        Args:
            photo: Photo metadata
            spec: Album specification
            
        Returns:
            True if photo matches spec
        """
        # Check if keywords match (filename or folder)
        keyword_match = (
            self.match_filename(photo, spec.keywords) or 
            self.match_folder(photo, spec.keywords)
        )
        
        # If there's a date filter, check both keyword and date
        if spec.date_filter:
            date_match = self.match_date(photo, spec.date_filter)
            # Match if EITHER keywords match OR date matches (more flexible)
            # But prefer both matching
            if keyword_match and date_match:
                return True
            # If only keywords match (but date doesn't), still match
            # This allows organizing by keyword even if date is different
            if keyword_match:
                return True
            return False
        
        # No date filter, just check keywords
        return keyword_match
    
    def match_filename(self, photo: PhotoMetadata, keywords: List[str]) -> bool:
        """Check if filename matches keywords.
        
        Args:
            photo: Photo metadata
            keywords: List of keywords to match
            
        Returns:
            True if filename matches any keyword
        """
        filename_lower = photo.filename.lower()
        
        for keyword in keywords:
            # Convert wildcard pattern to regex
            if '*' in keyword:
                pattern = keyword.replace('*', '.*')
                pattern = f'^{pattern}'
                if re.search(pattern, filename_lower, re.IGNORECASE):
                    return True
            else:
                # Simple substring match (case-insensitive)
                if keyword.lower() in filename_lower:
                    return True
        
        return False
    
    def match_date(self, photo: PhotoMetadata, date_filter: DateFilter) -> bool:
        """Check if photo date matches date filter.
        
        Args:
            photo: Photo metadata
            date_filter: Date filter specification
            
        Returns:
            True if photo date matches filter
        """
        # Use EXIF date if available, otherwise file date
        photo_date = photo.exif_date if photo.exif_date else photo.file_created
        
        if not photo_date:
            return False
        
        # Check year
        if date_filter.year and photo_date.year != date_filter.year:
            return False
        
        # Check month
        if date_filter.month and photo_date.month != date_filter.month:
            return False
        
        # Check date range
        if date_filter.start_date and photo_date < date_filter.start_date:
            return False
        
        if date_filter.end_date and photo_date > date_filter.end_date:
            return False
        
        return True
    
    def match_folder(self, photo: PhotoMetadata, keywords: List[str]) -> bool:
        """Check if folder name matches keywords.
        
        Args:
            photo: Photo metadata
            keywords: List of keywords to match
            
        Returns:
            True if folder name matches any keyword
        """
        folder_lower = photo.folder_name.lower()
        
        for keyword in keywords:
            # Convert wildcard pattern to regex
            if '*' in keyword:
                pattern = keyword.replace('*', '.*')
                pattern = f'^{pattern}'
                if re.search(pattern, folder_lower, re.IGNORECASE):
                    return True
            else:
                # Simple substring match (case-insensitive)
                if keyword.lower() in folder_lower:
                    return True
        
        return False
