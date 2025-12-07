"""Gallery generation for PromptAlbumBuilder."""

from pathlib import Path
from typing import List
from PIL import Image

from core.albums import Album


class GalleryGenerator:
    """Generates HTML gallery index for albums."""
    
    def __init__(self, target_folder: Path, dry_run: bool = False):
        """Initialize gallery generator.
        
        Args:
            target_folder: Root folder for albums
            dry_run: If True, simulate without creating files
        """
        self.target_folder = target_folder
        self.dry_run = dry_run
    
    def generate_index(self, albums: List[Album]):
        """Generate master index.html for all albums.
        
        Args:
            albums: List of albums to include in gallery
        """
        if self.dry_run:
            return
        
        html = self.generate_html(albums)
        
        index_path = self.target_folder / "index.html"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"[INFO] Gallery index created: {index_path}")
    
    def create_thumbnail(self, photo_path: Path, size: tuple = (200, 200)) -> Path:
        """Create thumbnail for photo.
        
        Args:
            photo_path: Path to original photo
            size: Thumbnail size (width, height)
            
        Returns:
            Path to thumbnail file
        """
        try:
            # Open image
            img = Image.open(photo_path)
            
            # Create thumbnail
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Save thumbnail
            thumb_path = photo_path.parent / f"thumb_{photo_path.name}"
            img.save(thumb_path)
            
            return thumb_path
            
        except Exception as e:
            print(f"Warning: Could not create thumbnail for {photo_path.name}: {e}")
            return photo_path  # Return original if thumbnail creation fails
    
    def generate_html(self, albums: List[Album]) -> str:
        """Generate HTML content for gallery index.
        
        Args:
            albums: List of albums
            
        Returns:
            HTML string
        """
        # Build album cards
        album_cards = []
        for album in albums:
            # Get first photo for thumbnail
            if album.photos:
                first_photo = album.photos[0]
                # Use relative path for thumbnail
                thumb_rel = f"{album.path.name}/{first_photo.filename}"
            else:
                thumb_rel = ""
            
            card_html = f"""
            <div class="album-card">
                <div class="album-thumbnail">
                    {f'<img src="{thumb_rel}" alt="{album.name}">' if thumb_rel else '<div class="no-image">No Photos</div>'}
                </div>
                <div class="album-info">
                    <h3>{album.name}</h3>
                    <p class="photo-count">{len(album.photos)} photos</p>
                    <p class="date-range">{album.earliest_date.strftime('%Y-%m-%d')} to {album.latest_date.strftime('%Y-%m-%d')}</p>
                    <p class="keywords">{', '.join(album.keywords)}</p>
                    <a href="{album.path.name}/README.md" class="view-link">View Album →</a>
                </div>
            </div>
            """
            album_cards.append(card_html)
        
        albums_html = '\n'.join(album_cards)
        
        # Complete HTML document
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Photo Albums - PromptAlbumBuilder</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            color: white;
            margin-bottom: 50px;
        }}
        
        h1 {{
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        
        .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .gallery {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 30px;
            margin-top: 40px;
        }}
        
        .album-card {{
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .album-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }}
        
        .album-thumbnail {{
            width: 100%;
            height: 200px;
            overflow: hidden;
            background: #f0f0f0;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .album-thumbnail img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        
        .no-image {{
            color: #999;
            font-size: 1.1em;
        }}
        
        .album-info {{
            padding: 20px;
        }}
        
        .album-info h3 {{
            font-size: 1.5em;
            margin-bottom: 10px;
            color: #333;
        }}
        
        .photo-count {{
            color: #667eea;
            font-weight: 600;
            margin-bottom: 5px;
        }}
        
        .date-range {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
        }}
        
        .keywords {{
            color: #999;
            font-size: 0.85em;
            font-style: italic;
            margin-bottom: 15px;
        }}
        
        .view-link {{
            display: inline-block;
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
            transition: color 0.3s ease;
        }}
        
        .view-link:hover {{
            color: #764ba2;
        }}
        
        .stats {{
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 20px;
            color: white;
            text-align: center;
            margin-bottom: 30px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin-top: 15px;
        }}
        
        .stat-item {{
            padding: 10px;
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            display: block;
        }}
        
        .stat-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📸 Photo Albums</h1>
            <p class="subtitle">Organized by PromptAlbumBuilder</p>
        </header>
        
        <div class="stats">
            <h2>Collection Statistics</h2>
            <div class="stats-grid">
                <div class="stat-item">
                    <span class="stat-number">{len(albums)}</span>
                    <span class="stat-label">Albums</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{sum(len(a.photos) for a in albums)}</span>
                    <span class="stat-label">Total Photos</span>
                </div>
            </div>
        </div>
        
        <div class="gallery">
            {albums_html}
        </div>
    </div>
</body>
</html>
"""
        
        return html
