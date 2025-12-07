"""Basic smoke tests for PromptAlbumBuilder."""

import pytest
from pathlib import Path
from datetime import datetime

from core.config import Config, ConfigNotFoundError
from core.matcher import PromptParser, AlbumSpec, DateFilter
from core.scanner import PhotoScanner


def test_prompt_parser_basic():
    """Test basic prompt parsing functionality."""
    parser = PromptParser()
    
    prompt = "Create albums for NCC events, college fests, family trips"
    specs = parser.parse(prompt)
    
    assert len(specs) > 0
    assert any('ncc' in spec.name.lower() for spec in specs)


def test_album_name_extraction():
    """Test album name extraction from prompt."""
    parser = PromptParser()
    
    prompt = "Create albums for vacation, work, and family"
    names = parser.extract_album_names(prompt)
    
    assert len(names) == 3
    assert 'Vacation' in names
    assert 'Work' in names
    assert 'Family' in names


def test_date_extraction_month_year():
    """Test date extraction with month and year."""
    parser = PromptParser()
    
    prompt = "Create albums for March 2024"
    dates = parser.extract_dates(prompt)
    
    assert len(dates) > 0
    assert dates[0].year == 2024
    assert dates[0].month == 3


def test_date_extraction_year_only():
    """Test date extraction with year only."""
    parser = PromptParser()
    
    prompt = "Create albums for 2024"
    dates = parser.extract_dates(prompt)
    
    assert len(dates) > 0
    assert dates[0].year == 2024


def test_keyword_extraction():
    """Test keyword extraction from album name."""
    parser = PromptParser()
    
    keywords = parser.extract_keywords("NCC Events")
    
    assert 'ncc' in keywords
    assert 'events' in keywords


def test_config_missing_file():
    """Test config error when file doesn't exist."""
    config = Config("nonexistent.yaml")
    
    with pytest.raises(ConfigNotFoundError):
        config.load()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
