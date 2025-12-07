"""Test dataset preparation script for PromptAlbumBuilder.

This script creates a sample photo collection with appropriate filenames,
folder structure, and timestamps for testing the album builder.
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
from PIL import Image
import random


def create_test_directory_structure(base_path: Path):
    """Create test directory structure.
    
    Args:
        base_path: Base path for test photos
    """
    directories = [
        'NCC_Events',
        'College_Fests',
        'Family',
        'Bills'
    ]
    
    for dir_name in directories:
        dir_path = base_path / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Created test directory structure at: {base_path}")


def create_sample_image(filepath: Path, color: tuple = (100, 150, 200)):
    """Create a sample colored image.
    
    Args:
        filepath: Path where image will be saved
        color: RGB color tuple
    """
    # Create a simple colored image
    img = Image.new('RGB', (800, 600), color=color)
    
    # Add some variation
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    
    # Draw some shapes for variety
    for _ in range(10):
        x1 = random.randint(0, 700)
        y1 = random.randint(0, 500)
        x2 = x1 + random.randint(50, 100)
        y2 = y1 + random.randint(50, 100)
        shape_color = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )
        draw.rectangle([x1, y1, x2, y2], fill=shape_color)
    
    # Save image
    img.save(filepath, 'JPEG')


def set_file_date(filepath: Path, date: datetime):
    """Set file creation and modification dates.
    
    Args:
        filepath: Path to file
        date: Date to set
    """
    timestamp = date.timestamp()
    os.utime(filepath, (timestamp, timestamp))


def prepare_test_dataset(base_path: str = "test_photos"):
    """Prepare complete test dataset.
    
    Args:
        base_path: Base directory for test photos
    """
    base = Path(base_path)
    
    # Create directory structure
    create_test_directory_structure(base)
    
    # Define test photos with filenames and dates
    test_photos = {
        'NCC_Events': [
            ('NCC_parade_001.jpg', datetime(2024, 3, 5), (200, 100, 100)),
            ('NCC_parade_002.jpg', datetime(2024, 3, 5), (200, 100, 100)),
            ('NCC_training_001.jpg', datetime(2024, 3, 10), (200, 100, 100)),
        ],
        'College_Fests': [
            ('fest_cultural_001.jpg', datetime(2024, 3, 8), (100, 200, 100)),
            ('fest_tech_001.jpg', datetime(2024, 3, 12), (100, 200, 100)),
            ('college_fest_2024.jpg', datetime(2024, 3, 15), (100, 200, 100)),
        ],
        'Family': [
            ('family_trip_beach.jpg', datetime(2024, 3, 20), (100, 100, 200)),
            ('family_trip_mountains.jpg', datetime(2024, 3, 22), (100, 100, 200)),
            ('vacation_2024.jpg', datetime(2024, 3, 25), (100, 100, 200)),
        ],
        'Bills': [
            ('medical_bill_march.jpg', datetime(2024, 3, 3), (150, 150, 150)),
            ('bill_hospital.jpg', datetime(2024, 3, 7), (150, 150, 150)),
            ('receipt_pharmacy.jpg', datetime(2024, 3, 14), (150, 150, 150)),
        ]
    }
    
    # Create photos
    print("\nCreating test photos...")
    for folder, photos in test_photos.items():
        folder_path = base / folder
        print(f"\n{folder}:")
        
        for filename, date, color in photos:
            filepath = folder_path / filename
            
            # Create image
            create_sample_image(filepath, color)
            
            # Set timestamp
            set_file_date(filepath, date)
            
            print(f"  ✓ {filename} (date: {date.strftime('%Y-%m-%d')})")
    
    print(f"\n✅ Test dataset created successfully at: {base.absolute()}")
    print("\nTest prompt to use:")
    print('  "Create albums for NCC events, college fests, family trips, and medical bills in March 2024"')
    print("\nExpected results:")
    print("  - 4 albums created")
    print("  - NCC Events: 3 photos")
    print("  - College Fests: 3 photos")
    print("  - Family Trips: 3 photos")
    print("  - Medical Bills: 3 photos")
    print("  - All dated March 2024")
    print("\nTo test:")
    print(f'  1. Update .kiro/config.yaml with source_folder: "{base.absolute()}"')
    print('  2. Run: python .kiro/hooks/album.py --prompt "Create albums for NCC events, college fests, family trips, and medical bills in March 2024" --dry-run')


if __name__ == '__main__':
    import sys
    
    # Allow custom base path
    base_path = sys.argv[1] if len(sys.argv) > 1 else "test_photos"
    
    print("=" * 60)
    print("PromptAlbumBuilder - Test Dataset Preparation")
    print("=" * 60)
    
    prepare_test_dataset(base_path)
