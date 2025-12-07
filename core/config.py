"""Configuration loader for PromptAlbumBuilder."""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigNotFoundError(Exception):
    """Raised when configuration file is not found."""
    pass


class InvalidConfigError(Exception):
    """Raised when configuration is invalid."""
    pass


class Config:
    """Loads and validates configuration from YAML file."""
    
    def __init__(self, config_path: str = ".kiro/config.yaml"):
        """Initialize configuration loader.
        
        Args:
            config_path: Path to configuration YAML file
        """
        self.config_path = Path(config_path)
        self._config: Optional[Dict[str, Any]] = None
    
    def load(self) -> Dict[str, Any]:
        """Load configuration from YAML file.
        
        Returns:
            Configuration dictionary
            
        Raises:
            ConfigNotFoundError: If config file doesn't exist
            InvalidConfigError: If config is invalid
        """
        if not self.config_path.exists():
            raise ConfigNotFoundError(
                f"Configuration file not found at {self.config_path}. "
                "Please create the configuration file."
            )
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise InvalidConfigError(f"Invalid YAML syntax in config file: {e}")
        except Exception as e:
            raise InvalidConfigError(f"Error reading config file: {e}")
        
        if not self._config:
            raise InvalidConfigError("Configuration file is empty")
        
        # Validate configuration
        if not self.validate():
            raise InvalidConfigError("Configuration validation failed")
        
        return self._config
    
    def get_source_folder(self) -> Path:
        """Get source folder path from configuration.
        
        Returns:
            Path to source folder
            
        Raises:
            InvalidConfigError: If source_folder not configured or invalid
        """
        if not self._config:
            self.load()
        
        if 'source_folder' not in self._config:
            raise InvalidConfigError("source_folder not specified in configuration")
        
        source_path = Path(self._config['source_folder'])
        
        if not source_path.exists():
            raise InvalidConfigError(
                f"Source folder does not exist: {source_path}. "
                "Please check your configuration."
            )
        
        if not source_path.is_dir():
            raise InvalidConfigError(
                f"Source folder is not a directory: {source_path}"
            )
        
        return source_path
    
    def get_target_folder(self) -> Path:
        """Get target albums folder path from configuration.
        
        Returns:
            Path to target albums folder
            
        Raises:
            InvalidConfigError: If target_albums_folder not configured
        """
        if not self._config:
            self.load()
        
        if 'target_albums_folder' not in self._config:
            raise InvalidConfigError(
                "target_albums_folder not specified in configuration"
            )
        
        return Path(self._config['target_albums_folder'])
    
    def validate(self) -> bool:
        """Validate configuration has required fields.
        
        Returns:
            True if valid, False otherwise
        """
        if not self._config:
            return False
        
        required_fields = ['source_folder', 'target_albums_folder']
        
        for field in required_fields:
            if field not in self._config:
                return False
            if not self._config[field]:
                return False
        
        return True
    
    def get_supported_extensions(self) -> list:
        """Get list of supported image extensions.
        
        Returns:
            List of supported extensions (with leading dot)
        """
        if not self._config:
            self.load()
        
        default_extensions = ['.jpg', '.jpeg', '.png', '.heic', '.raw', '.cr2', '.nef']
        
        if 'supported_extensions' in self._config:
            return self._config['supported_extensions']
        
        return default_extensions
    
    def get_log_level(self) -> str:
        """Get logging level from configuration.
        
        Returns:
            Log level string (default: INFO)
        """
        if not self._config:
            self.load()
        
        if 'logging' in self._config and 'level' in self._config['logging']:
            return self._config['logging']['level']
        
        return 'INFO'
    
    def get_log_dir(self) -> Path:
        """Get log directory from configuration.
        
        Returns:
            Path to log directory (default: logs)
        """
        if not self._config:
            self.load()
        
        if 'logging' in self._config and 'log_dir' in self._config['logging']:
            return Path(self._config['logging']['log_dir'])
        
        return Path('logs')
