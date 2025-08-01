import json
import os
from typing import Dict, List, Optional
from .models import PlanogramSection, BoundingBox

class DeploymentConfig:
    """Handles deployment-specific configuration with environment variable support"""
    
    @staticmethod
    def get_config_dir() -> str:
        """Get configuration directory path"""
        return os.getenv('PLANOGRAM_CONFIG_DIR', 'config/planograms')
    
    @staticmethod
    def get_images_dir() -> str:
        """Get images directory path"""
        return os.getenv('PLANOGRAM_IMAGES_DIR', 'config/images')
    
    @staticmethod
    def get_weights_dir() -> str:
        """Get model weights directory path"""
        return os.getenv('PLANOGRAM_WEIGHTS_DIR', 'weights')
    
    @staticmethod
    def get_model_weights_file() -> str:
        """Get model weights file name"""
        return os.getenv('PLANOGRAM_MODEL_WEIGHTS', 'pick-instance-seg-v11-1.2.pt')
    
    @staticmethod
    def get_temp_dir() -> str:
        """Get temporary directory path"""
        return os.getenv('PLANOGRAM_TEMP_DIR', '/tmp' if os.name != 'nt' else os.path.join(os.path.expanduser('~'), 'temp'))
    
    @staticmethod
    def get_model_weights_path() -> str:
        """Get full path to model weights file"""
        weights_dir = DeploymentConfig.get_weights_dir()
        weights_file = DeploymentConfig.get_model_weights_file()
        
        # Handle relative paths by making them relative to the demo directory
        if not os.path.isabs(weights_dir):
            # Get the demo directory (parent of backend)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            demo_dir = os.path.dirname(current_dir)
            weights_dir = os.path.join(demo_dir, weights_dir)
        
        return os.path.join(weights_dir, weights_file)

class PlanogramConfig:
    """Manages planogram configurations and settings"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.sections: List[PlanogramSection] = []
        self.planogram_image_path: Optional[str] = None
        self.metadata: Dict = {}
        
        if config_path:
            self.load_from_file(config_path)
    
    def load_from_file(self, config_path: str) -> None:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            self.config_path = config_path
            self._parse_config(config_data)
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    def _parse_config(self, config_data: Dict) -> None:
        """Parse configuration data and create sections"""
        self.sections = []
        self.metadata = config_data.get('metadata', {})
        self.planogram_image_path = config_data.get('planogram_image_path')
        
        for section_data in config_data.get('sections', []):
            position_data = section_data['position']
            bbox = BoundingBox(
                x1=position_data['x1'],
                y1=position_data['y1'],
                x2=position_data['x2'],
                y2=position_data['y2']
            )
            
            section = PlanogramSection(
                section_id=section_data['section_id'],
                name=section_data['name'],
                expected_items=section_data['expected_items'],
                expected_count=section_data['expected_count'],
                expected_visible_count=section_data.get('expected_visible_count', section_data['expected_count']),  # Default to expected_count for backward compatibility
                position=bbox,
                priority=section_data.get('priority', 'Medium')
            )
            
            self.sections.append(section)
    
    def save_to_file(self, config_path: str) -> None:
        """Save current configuration to JSON file"""
        config_data = {
            'metadata': self.metadata,
            'planogram_image_path': self.planogram_image_path,
            'sections': [section.to_dict() for section in self.sections]
        }
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        self.config_path = config_path
    
    def add_section(self, section: PlanogramSection) -> None:
        """Add a new section to the configuration"""
        # Check for duplicate section IDs
        existing_ids = [s.section_id for s in self.sections]
        if section.section_id in existing_ids:
            raise ValueError(f"Section ID '{section.section_id}' already exists")
        
        self.sections.append(section)
    
    def remove_section(self, section_id: str) -> bool:
        """Remove a section by ID. Returns True if removed, False if not found"""
        original_count = len(self.sections)
        self.sections = [s for s in self.sections if s.section_id != section_id]
        return len(self.sections) < original_count
    
    def get_section_by_id(self, section_id: str) -> Optional[PlanogramSection]:
        """Get a section by its ID"""
        for section in self.sections:
            if section.section_id == section_id:
                return section
        return None
    
    def get_sections_for_item(self, item_class: str) -> List[PlanogramSection]:
        """Get all sections that should contain a specific item class"""
        return [
            section for section in self.sections 
            if item_class in section.expected_items
        ]
    
    def find_section_by_position(self, x: float, y: float) -> Optional[PlanogramSection]:
        """Find which section a given coordinate belongs to"""
        for section in self.sections:
            bbox = section.position
            if bbox.x1 <= x <= bbox.x2 and bbox.y1 <= y <= bbox.y2:
                return section
        return None
    
    @classmethod
    def create_sample_config(cls) -> 'PlanogramConfig':
        """Create a sample configuration for testing"""
        config = cls()
        
        # Sample metadata
        config.metadata = {
            'name': 'Sample Grocery Store Layout',
            'store_id': 'STORE_001',
            'created_date': '2024-01-01',
            'version': '1.0'
        }
        
        # Sample sections
        sections_data = [
            {
                'section_id': 'CEREALS_TOP',
                'name': 'Cereals - Top Shelf',
                'expected_items': ['cereal_box', 'granola'],
                'expected_count': 8,
                'expected_visible_count': 6,  # Accounting for occlusion
                'position': BoundingBox(0, 0, 300, 100),
                'priority': 'Medium'
            },
            {
                'section_id': 'CEREALS_MIDDLE',
                'name': 'Cereals - Middle Shelf',
                'expected_items': ['cereal_box'],
                'expected_count': 12,
                'expected_visible_count': 10,  # Accounting for occlusion
                'position': BoundingBox(0, 100, 300, 200),
                'priority': 'High'
            },
            {
                'section_id': 'SNACKS_TOP',
                'name': 'Snacks - Top Shelf',
                'expected_items': ['chips', 'cookies'],
                'expected_count': 6,
                'expected_visible_count': 5,  # Accounting for occlusion
                'position': BoundingBox(300, 0, 600, 100),
                'priority': 'Low'
            },
            {
                'section_id': 'BEVERAGES',
                'name': 'Beverages Section',
                'expected_items': ['bottle', 'can'],
                'expected_count': 15,
                'expected_visible_count': 12,  # Accounting for occlusion
                'position': BoundingBox(300, 100, 600, 200),
                'priority': 'High'
            }
        ]
        
        for section_data in sections_data:
            section = PlanogramSection(
                section_id=section_data['section_id'],
                name=section_data['name'],
                expected_items=section_data['expected_items'],
                expected_count=section_data['expected_count'],
                expected_visible_count=section_data['expected_visible_count'],
                position=section_data['position'],
                priority=section_data['priority']
            )
            config.add_section(section)
        
        return config
    
    @staticmethod
    def _create_default_store_004_config() -> None:
        """Create the default store_004.json configuration file"""
        config_dir = DeploymentConfig.get_config_dir()
        config_path = os.path.join(config_dir, "store_004.json")
        
        # Only create if it doesn't exist
        if os.path.exists(config_path):
            return
            
        default_config = {
            "metadata": {
                "name": "Store 004 Demo",
                "store_id": "STORE_004",
                "created_date": "2024-01-01",
                "version": "1.0",
                "description": "Configuration with expected visible counts considering occlusion"
            },
            "planogram_image_path": "config/images/store_003_planogram.jpg",
            "sections": [
                {
                    "section_id": "SECTION_WATER",
                    "name": "Water",
                    "expected_items": ["bottled_drinks"],
                    "expected_count": 4,
                    "expected_visible_count": 2,
                    "position": {"x1": 40, "y1": 65, "x2": 283, "y2": 385},
                    "priority": "Low"
                },
                {
                    "section_id": "SECTION_CANNED_DRINKS", 
                    "name": "Soda",
                    "expected_items": ["canned_drinks"],
                    "expected_count": 6,
                    "expected_visible_count": 2,
                    "position": {"x1": 275, "y1": 230, "x2": 452, "y2": 390},
                    "priority": "Low"
                },
                {
                    "section_id": "SECTION_LARGE_YOGURT",
                    "name": "Large Yogurt", 
                    "expected_items": ["yogurt_cups_large"],
                    "expected_count": 4,
                    "expected_visible_count": 2,
                    "position": {"x1": 451, "y1": 217, "x2": 702, "y2": 396},
                    "priority": "High"
                },
                {
                    "section_id": "SECTION_SMALL_YOGURT",
                    "name": "Small Yogurt",
                    "expected_items": ["yogurt_cups_small"],
                    "expected_count": 4,
                    "expected_visible_count": 2,
                    "position": {"x1": 697, "y1": 216, "x2": 987, "y2": 401},
                    "priority": "Medium"
                },
                {
                    "section_id": "SECTION_SALADS",
                    "name": "Salads",
                    "expected_items": ["salads_bowls"],
                    "expected_count": 6,
                    "expected_visible_count": 4,
                    "position": {"x1": 41, "y1": 403, "x2": 630, "y2": 734},
                    "priority": "High"
                },
                {
                    "section_id": "SECTION_LARGE_PLATES",
                    "name": "Large Plates", 
                    "expected_items": ["large_plates"],
                    "expected_count": 6,
                    "expected_visible_count": 3,
                    "position": {"x1": 627, "y1": 404, "x2": 1019, "y2": 739},
                    "priority": "High"
                },
                {
                    "section_id": "SECTION_WRAPS",
                    "name": "Wraps",
                    "expected_items": ["wraps"],
                    "expected_count": 4,
                    "expected_visible_count": 4,
                    "position": {"x1": 65, "y1": 760, "x2": 422, "y2": 1062},
                    "priority": "High"
                },
                {
                    "section_id": "SECTION_SANDWICHES",
                    "name": "Sandwiches",
                    "expected_items": ["sandwiches"],
                    "expected_count": 4,
                    "expected_visible_count": 2,
                    "position": {"x1": 419, "y1": 774, "x2": 636, "y2": 1068},
                    "priority": "High"
                },
                {
                    "section_id": "SECTION_SMALL_PLATES",
                    "name": "Small Plates",
                    "expected_items": ["small_plates"],
                    "expected_count": 6,
                    "expected_visible_count": 3,
                    "position": {"x1": 606, "y1": 747, "x2": 1000, "y2": 1076},
                    "priority": "High"
                }
            ]
        }
        
        try:
            os.makedirs(config_dir, exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"✅ Created default store_004.json configuration")
        except Exception as e:
            print(f"❌ Error creating default config: {e}")

    @staticmethod
    def _create_default_store_005_config() -> None:
        """Create the default store_005.json configuration file"""
        config_dir = DeploymentConfig.get_config_dir()
        config_path = os.path.join(config_dir, "store_005.json")
        
        # Only create if it doesn't exist
        if os.path.exists(config_path):
            return
            
        default_config = {
            "metadata": {
                "name": "Pick Demo v2",
                "store_id": "STORE_005",
                "created_date": "2024-01-01",
                "version": "1.0",
                "description": ""
            },
            "planogram_image_path": "config/images/store_005_planogram.jpg",
            "sections": [
                {
                    "section_id": "SECTION_WATER",
                    "name": "Water",
                    "expected_items": ["bottled_drinks"],
                    "expected_count": 4,
                    "expected_visible_count": 2,
                    "position": {"x1": 64, "y1": 67, "x2": 283, "y2": 390},
                    "priority": "Medium"
                },
                {
                    "section_id": "SECTION_CANNED_DRINKS",
                    "name": "Soda",
                    "expected_items": ["canned_drinks"],
                    "expected_count": 6,
                    "expected_visible_count": 2,
                    "position": {"x1": 283, "y1": 209, "x2": 459, "y2": 392},
                    "priority": "Medium"
                },
                {
                    "section_id": "SECTION_LARGE_YOGURT",
                    "name": "Large Yogurts",
                    "expected_items": ["yogurt_cups_large"],
                    "expected_count": 4,
                    "expected_visible_count": 2,
                    "position": {"x1": 457, "y1": 209, "x2": 697, "y2": 392},
                    "priority": "Medium"
                },
                {
                    "section_id": "SECTION_SMALL_YOGURT",
                    "name": "Small Yogurts",
                    "expected_items": ["yogurt_cups_small"],
                    "expected_count": 4,
                    "expected_visible_count": 2,
                    "position": {"x1": 696, "y1": 208, "x2": 1006, "y2": 393},
                    "priority": "Medium"
                },
                {
                    "section_id": "SECTION_SALADS",
                    "name": "Salads",
                    "expected_items": ["salads_bowls"],
                    "expected_count": 6,
                    "expected_visible_count": 4,
                    "position": {"x1": 48, "y1": 406, "x2": 640, "y2": 734},
                    "priority": "High"
                },
                {
                    "section_id": "SECTION_LARGE_PLATES",
                    "name": "Large Plates",
                    "expected_items": ["large_plates"],
                    "expected_count": 6,
                    "expected_visible_count": 3,
                    "position": {"x1": 640, "y1": 406, "x2": 1001, "y2": 736},
                    "priority": "High"
                },
                {
                    "section_id": "SECTION_WRAPS",
                    "name": "Wraps",
                    "expected_items": ["wraps"],
                    "expected_count": 6,
                    "expected_visible_count": 4,
                    "position": {"x1": 76, "y1": 764, "x2": 424, "y2": 1080},
                    "priority": "Medium"
                },
                {
                    "section_id": "SECTION_SANDWICHES",
                    "name": "Sandwiches",
                    "expected_items": ["sandwiches"],
                    "expected_count": 4,
                    "expected_visible_count": 2,
                    "position": {"x1": 424, "y1": 764, "x2": 624, "y2": 1081},
                    "priority": "High"
                },
                {
                    "section_id": "SECTION_SMALL_PLATES",
                    "name": "Small Plates",
                    "expected_items": ["small_plates"],
                    "expected_count": 6,
                    "expected_visible_count": 3,
                    "position": {"x1": 622, "y1": 764, "x2": 968, "y2": 1084},
                    "priority": "High"
                }
            ]
        }
        
        try:
            os.makedirs(config_dir, exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"✅ Created default store_005.json configuration")
        except Exception as e:
            print(f"❌ Error creating default config: {e}")

    @staticmethod
    def list_available_configs(config_dir: Optional[str] = None) -> List[str]:
        """List all available configuration files"""
        if config_dir is None:
            config_dir = DeploymentConfig.get_config_dir()
        
        if not os.path.exists(config_dir):
            # Create the directory if it doesn't exist
            os.makedirs(config_dir, exist_ok=True)
        
        # Ensure we have at least the default store_004.json and store_005.json
        PlanogramConfig._create_default_store_004_config()
        PlanogramConfig._create_default_store_005_config()
        
        try:
            config_files = []
            for filename in os.listdir(config_dir):
                if filename.endswith('.json'):
                    full_path = os.path.join(config_dir, filename)
                    # Verify the file is readable
                    try:
                        with open(full_path, 'r') as f:
                            json.load(f)
                        config_files.append(filename)
                    except Exception as e:
                        # Log error but continue
                        print(f"Warning: Invalid config file {filename}: {e}")
            
            return sorted(config_files)
            
        except Exception as e:
            print(f"Error reading config directory {config_dir}: {e}")
            return []
    
    @staticmethod
    def get_config_path(config_name: str, config_dir: Optional[str] = None) -> str:
        """Get full path for a configuration file"""
        if config_dir is None:
            config_dir = DeploymentConfig.get_config_dir()
            
        if not config_name.endswith('.json'):
            config_name += '.json'
        return os.path.join(config_dir, config_name)
    
    def validate_configuration(self) -> List[str]:
        """Validate the current configuration and return list of issues"""
        issues = []
        
        if not self.sections:
            issues.append("No sections defined in configuration")
        
        section_ids = set()
        for section in self.sections:
            # Check for duplicate IDs
            if section.section_id in section_ids:
                issues.append(f"Duplicate section ID: {section.section_id}")
            section_ids.add(section.section_id)
            
            # Check for empty expected items
            if not section.expected_items:
                issues.append(f"Section '{section.section_id}' has no expected items")
            
            # Check for invalid expected count
            if section.expected_count <= 0:
                issues.append(f"Section '{section.section_id}' has invalid expected count: {section.expected_count}")
            
            # Check for invalid bounding box
            bbox = section.position
            if bbox.x1 >= bbox.x2 or bbox.y1 >= bbox.y2:
                issues.append(f"Section '{section.section_id}' has invalid bounding box")
        
        return issues
    
    def to_dict(self) -> Dict:
        """Convert configuration to dictionary"""
        return {
            'metadata': self.metadata,
            'planogram_image_path': self.planogram_image_path,
            'sections': [section.to_dict() for section in self.sections]
        } 