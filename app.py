"""
Streamlit UI for PromptAlbumBuilder

A web interface for organizing photos using natural language prompts.
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
from PIL import Image
import io

from core.config import Config, ConfigNotFoundError, InvalidConfigError
from core.matcher import PromptParser, PatternMatcher, AlbumSpec, DateFilter
from core.scanner import PhotoScanner
from core.albums import AlbumCreator
from core.report import ReportGenerator
from core.gallery import GalleryGenerator


# Page configuration
st.set_page_config(
    page_title="PromptAlbumBuilder",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .album-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background: #f9f9f9;
    }
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)


def load_configuration():
    """Load configuration from file."""
    try:
        config = Config(".kiro/config_test.yaml")  # Use test config by default
        config.load()
        return config
    except (ConfigNotFoundError, InvalidConfigError) as e:
        st.error(f"Configuration Error: {e}")
        return None


def apply_additional_filters(album_specs, month_filter, year_filter):
    """Apply additional month/year filters to album specifications.
    
    Args:
        album_specs: List of album specifications
        month_filter: Selected month (1-12 or None for all)
        year_filter: Selected year or None
        
    Returns:
        Updated album specifications with filters applied
    """
    if not month_filter and not year_filter:
        return album_specs
    
    # Update date filters for all specs
    for spec in album_specs:
        if not spec.date_filter:
            spec.date_filter = DateFilter()
        
        if year_filter:
            spec.date_filter.year = year_filter
        if month_filter:
            spec.date_filter.month = month_filter
    
    return album_specs


def create_thumbnail(image_path, size=(150, 150)):
    """Create thumbnail from image path.
    
    Args:
        image_path: Path to image
        size: Thumbnail size
        
    Returns:
        PIL Image object or None
    """
    try:
        img = Image.open(image_path)
        img.thumbnail(size, Image.Resampling.LANCZOS)
        return img
    except Exception as e:
        st.warning(f"Could not load thumbnail for {image_path.name}: {e}")
        return None


def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<h1 class="main-header">📸 PromptAlbumBuilder</h1>', unsafe_allow_html=True)
    st.markdown("### Organize your photos with natural language")
    
    # Sidebar - Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Load config
        config = load_configuration()
        
        if config:
            source_folder = config.get_source_folder()
            target_folder = config.get_target_folder()
            
            st.success("✅ Configuration loaded")
            st.info(f"**Source:** `{source_folder}`")
            st.info(f"**Target:** `{target_folder}`")
        else:
            st.error("❌ Configuration not loaded")
            st.stop()
        
        st.divider()
        
        # Mode selection
        st.header("🎯 Mode")
        dry_run = st.checkbox("Dry Run Mode", value=True, 
                             help="Preview matches without creating folders")
        backup_mode = st.checkbox("Backup Mode", value=True,
                                 help="Copy photos instead of moving them")
        
        st.divider()
        
        # Additional filters
        st.header("🔍 Additional Filters")
        
        # Month filter
        months = ["All"] + [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        month_selection = st.selectbox("Month", months)
        month_filter = None if month_selection == "All" else months.index(month_selection)
        
        # Year filter
        current_year = datetime.now().year
        year_options = ["All"] + list(range(current_year, current_year - 10, -1))
        year_selection = st.selectbox("Year", year_options)
        year_filter = None if year_selection == "All" else year_selection
    
    # Main content area
    st.divider()
    
    # Prompt input
    st.header("💬 Enter Your Prompt")
    prompt = st.text_area(
        "Describe how you want to organize your photos:",
        placeholder="Example: Create albums for NCC events, college fests, family trips, and medical bills",
        height=100,
        help="Use natural language to describe your album organization"
    )
    
    # Example prompts
    with st.expander("📝 Example Prompts"):
        st.markdown("""
        - `Create albums for NCC events, college fests, family trips, and medical bills in March 2024`
        - `Organize photos into vacation, work, and family albums`
        - `Sort by summer 2023, winter 2023, and spring 2024`
        - `Create albums for NCC* events and *fest* photos`
        """)
    
    # Run button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        run_button = st.button("🚀 Run Album Builder", type="primary", use_container_width=True)
    
    # Process when button is clicked
    if run_button:
        if not prompt or not prompt.strip():
            st.error("⚠️ Please enter a prompt!")
            return
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Parse prompt
            status_text.text("📝 Parsing prompt...")
            progress_bar.progress(10)
            
            parser = PromptParser()
            album_specs = parser.parse(prompt)
            
            if not album_specs:
                st.error("❌ Could not extract album names from prompt. Please try again.")
                return
            
            # Apply additional filters
            album_specs = apply_additional_filters(album_specs, month_filter, year_filter)
            
            st.success(f"✅ Found {len(album_specs)} album specifications")
            
            # Step 2: Scan photos
            status_text.text("🔍 Scanning photos...")
            progress_bar.progress(30)
            
            scanner = PhotoScanner(source_folder)
            photos = scanner.scan()
            
            if not photos:
                st.warning(f"⚠️ No photos found in {source_folder}")
                return
            
            st.success(f"✅ Found {len(photos)} photos")
            
            # Step 3: Match photos
            status_text.text("🎯 Matching photos to albums...")
            progress_bar.progress(50)
            
            matcher = PatternMatcher(album_specs)
            match_result = matcher.match(photos)
            
            # Step 4: Create albums (if not dry run)
            status_text.text("📁 Creating albums...")
            progress_bar.progress(70)
            
            creator = AlbumCreator(target_folder, backup_mode=backup_mode, dry_run=dry_run)
            albums = creator.create_albums(match_result, album_specs)
            
            # Step 5: Generate reports and gallery (if not dry run)
            if not dry_run:
                status_text.text("📊 Generating reports...")
                progress_bar.progress(90)
                
                report = ReportGenerator(Path("logs"), dry_run=False)
                report.generate_unmatched_log(match_result.unmatched)
                
                gallery = GalleryGenerator(target_folder, dry_run=False)
                gallery.generate_index(albums)
            
            progress_bar.progress(100)
            status_text.text("✅ Complete!")
            
            # Display results
            st.divider()
            st.header("📊 Results")
            
            # Statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="stat-box">
                    <h2>{len(photos)}</h2>
                    <p>Photos Scanned</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="stat-box">
                    <h2>{len(albums)}</h2>
                    <p>Albums Created</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                matched_count = sum(len(album.photos) for album in albums)
                st.markdown(f"""
                <div class="stat-box">
                    <h2>{matched_count}</h2>
                    <p>Photos Matched</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="stat-box">
                    <h2>{len(match_result.unmatched)}</h2>
                    <p>Unmatched</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Display mode indicator
            if dry_run:
                st.markdown("""
                <div class="warning-box">
                    <strong>🔍 DRY RUN MODE:</strong> No files were created. This is a preview only.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="success-box">
                    <strong>✅ Albums Created!</strong> Check: <code>{target_folder}</code>
                </div>
                """, unsafe_allow_html=True)
            
            st.divider()
            
            # Display albums
            if albums:
                st.header("📁 Albums")
                
                for album in albums:
                    with st.expander(f"📂 {album.name} ({len(album.photos)} photos)", expanded=True):
                        # Album info
                        col1, col2 = st.columns([1, 3])
                        
                        with col1:
                            st.markdown(f"""
                            **Album Name:** {album.name}  
                            **Photos:** {len(album.photos)}  
                            **Date Range:** {album.earliest_date.strftime('%Y-%m-%d')} to {album.latest_date.strftime('%Y-%m-%d')}  
                            **Keywords:** {', '.join(album.keywords)}
                            """)
                        
                        with col2:
                            # Display thumbnails
                            if album.photos:
                                st.markdown("**Photos:**")
                                
                                # Create columns for thumbnails (4 per row)
                                num_cols = 4
                                rows = [album.photos[i:i+num_cols] for i in range(0, len(album.photos), num_cols)]
                                
                                for row in rows:
                                    cols = st.columns(num_cols)
                                    for idx, photo in enumerate(row):
                                        with cols[idx]:
                                            # Try to display thumbnail
                                            thumb = create_thumbnail(photo.path)
                                            if thumb:
                                                st.image(thumb, caption=photo.filename, use_container_width=True)
                                            else:
                                                st.text(photo.filename)
            else:
                st.warning("⚠️ No albums were created. Try adjusting your prompt or filters.")
            
            # Display unmatched photos
            if match_result.unmatched:
                st.divider()
                st.header("❓ Unmatched Photos")
                st.warning(f"Found {len(match_result.unmatched)} photos that didn't match any album criteria")
                
                with st.expander("View unmatched photos"):
                    for photo in match_result.unmatched:
                        st.text(f"• {photo.filename}")
        
        except Exception as e:
            st.error(f"❌ Error: {e}")
            import traceback
            with st.expander("Error Details"):
                st.code(traceback.format_exc())
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 20px;">
        <p>Built with ❤️ using Streamlit | PromptAlbumBuilder v1.0</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
