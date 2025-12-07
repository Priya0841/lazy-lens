"""Integration test for PromptAlbumBuilder end-to-end workflow."""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from PIL import Image

from core.config import Config
from core.matcher import PromptParser, PatternMatcher
from core.scanner import PhotoScanner
from core.albums import AlbumCreator
from core.report import ReportGenerator
from core.gallery import GalleryGenerator


def create_test_photo(path: Path, color=(100, 100, 100)):
    """Create a simple test photo."""
    img = Image.new('RGB', (100, 100), color=color)
    img.save(path, 'JPEG')


def test_end_to_end_workflow():
    """Test complete workflow from prompt to album creation."""
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as tmpdir:
        source_dir = Path(tmpdir) / "source"
        target_dir = Path(tmpdir) / "target"
        source_dir.mkdir()
        target_dir.mkdir()
        
        # Create test photos
        test_photos = [
            ("ncc_event_1.jpg", (200, 100, 100)),
            ("ncc_event_2.jpg", (200, 100, 100)),
            ("fest_photo.jpg", (100, 200, 100)),
            ("family_trip.jpg", (100, 100, 200)),
        ]
        
        for filename, color in test_photos:
            photo_path = source_dir / filename
            create_test_photo(photo_path, color)
        
        # Step 1: Parse prompt
        parser = PromptParser()
        prompt = "Create albums for NCC events, college fests, family trips"
        album_specs = parser.parse(prompt)
        
        assert len(album_specs) == 3
        
        # Step 2: Scan photos
        scanner = PhotoScanner(source_dir)
        photos = scanner.scan()
        
        assert len(photos) == 4
        
        # Step 3: Match photos
        matcher = PatternMatcher(album_specs)
        match_result = matcher.match(photos)
        
        # Verify matching worked
        assert len(match_result.matched) == 3
        
        # Step 4: Create albums (dry run)
        creator = AlbumCreator(target_dir, backup_mode=True, dry_run=True)
        albums = creator.create_albums(match_result, album_specs)
        
        # In dry run, albums are created but no files
        assert len(albums) > 0
        
        print("✅ End-to-end workflow test passed!")


def test_prompt_parsing_variations():
    """Test various prompt formats."""
    parser = PromptParser()
    
    test_cases = [
        ("Create albums for vacation and work", 2),
        ("Organize photos into family, friends, events", 3),
        ("Sort by NCC events, college fests in March 2024", 2),
    ]
    
    for prompt, expected_count in test_cases:
        specs = parser.parse(prompt)
        assert len(specs) >= expected_count, f"Failed for prompt: {prompt}"
    
    print("✅ Prompt parsing variations test passed!")


def test_date_parsing_variations():
    """Test various date formats."""
    parser = PromptParser()
    
    test_cases = [
        ("Photos from March 2024", 2024, 3),
        ("Images from 2023", 2023, None),
        ("Pictures from 2024-03", 2024, 3),
    ]
    
    for prompt, expected_year, expected_month in test_cases:
        dates = parser.extract_dates(prompt)
        if dates:
            assert dates[0].year == expected_year
            if expected_month:
                assert dates[0].month == expected_month
    
    print("✅ Date parsing variations test passed!")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
