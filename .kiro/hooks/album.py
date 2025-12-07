"""CLI interface for PromptAlbumBuilder (Kiro Hook)."""

import sys
import argparse
from pathlib import Path

# Add parent directory to path to import core modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.config import Config, ConfigNotFoundError, InvalidConfigError
from core.matcher import PromptParser, PatternMatcher
from core.scanner import PhotoScanner
from core.albums import AlbumCreator
from core.report import ReportGenerator
from core.gallery import GalleryGenerator


def main():
    """Main entry point for PromptAlbumBuilder CLI."""
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='PromptAlbumBuilder - Organize photos from natural language prompts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python .kiro/hooks/album.py --prompt "Create albums for NCC events, college fests in March 2024"
  python .kiro/hooks/album.py --prompt "Organize vacation photos" --dry-run
  python .kiro/hooks/album.py --prompt "Sort by event type" --backup
        """
    )
    
    parser.add_argument(
        '--prompt',
        required=True,
        help='Natural language prompt describing album organization'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview what would happen without modifying files'
    )
    
    parser.add_argument(
        '--backup',
        action='store_true',
        help='Copy photos instead of moving them (preserves originals)'
    )
    
    parser.add_argument(
        '--notify',
        action='store_true',
        help='Display notifications for completion status'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.prompt or not args.prompt.strip():
        print("Error: Prompt cannot be empty")
        parser.print_help()
        sys.exit(1)
    
    try:
        # Step 1: Load configuration
        print("[INFO] Loading configuration...")
        config = Config()
        config.load()
        
        source_folder = config.get_source_folder()
        target_folder = config.get_target_folder()
        supported_extensions = config.get_supported_extensions()
        log_dir = config.get_log_dir()
        
        print(f"[INFO] Source folder: {source_folder}")
        print(f"[INFO] Target folder: {target_folder}")
        
        if args.dry_run:
            print("[DRY RUN] Running in dry-run mode - no files will be modified")
        
        if args.backup:
            print("[INFO] Running in backup mode - photos will be copied, not moved")
        
        # Step 2: Parse prompt
        print(f"[INFO] Parsing prompt: {args.prompt}")
        prompt_parser = PromptParser()
        album_specs = prompt_parser.parse(args.prompt)
        
        if not album_specs:
            print("Error: No albums could be extracted from prompt. Please provide album names.")
            sys.exit(1)
        
        print(f"[INFO] Found {len(album_specs)} album specifications:")
        for spec in album_specs:
            print(f"  - {spec.name} (keywords: {', '.join(spec.keywords)})")
        
        # Step 3: Scan photos
        print(f"[INFO] Scanning photos from: {source_folder}")
        scanner = PhotoScanner(source_folder, supported_extensions)
        photos = scanner.scan()
        
        if not photos:
            print(f"Warning: No photos found in source folder: {source_folder}")
            sys.exit(0)
        
        print(f"[INFO] Found {len(photos)} photos")
        
        # Step 4: Match photos to albums
        print("[INFO] Matching photos to albums...")
        matcher = PatternMatcher(album_specs)
        match_result = matcher.match(photos)
        
        # Display match results
        for album_name, matched_photos in match_result.matched.items():
            if matched_photos:
                print(f"[INFO] {album_name}: {len(matched_photos)} photos")
        
        if match_result.unmatched:
            print(f"[WARNING] {len(match_result.unmatched)} photos did not match any album")
        
        # Step 5: Create albums
        print("[INFO] Creating albums...")
        creator = AlbumCreator(target_folder, backup_mode=args.backup, dry_run=args.dry_run)
        albums = creator.create_albums(match_result, album_specs)
        
        # Step 6: Generate reports
        print("[INFO] Generating reports...")
        report = ReportGenerator(log_dir, dry_run=args.dry_run)
        report.generate_unmatched_log(match_result.unmatched)
        
        # Step 7: Generate gallery
        if not args.dry_run:
            print("[INFO] Generating gallery...")
            gallery = GalleryGenerator(target_folder, dry_run=args.dry_run)
            gallery.generate_index(albums)
        
        # Step 8: Display summary
        report.display_summary(albums, len(match_result.unmatched), len(photos))
        
        # Notifications
        if args.notify:
            print("[INFO] Processing complete!")
        
        print("[INFO] PromptAlbumBuilder completed successfully")
        
    except ConfigNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    except InvalidConfigError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n[INFO] Operation cancelled by user")
        sys.exit(0)
    
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
