import os
import argparse
from pathlib import Path
from typing import List, Optional, Dict
from kiutils.footprint import Footprint, Model
from kiutils.items.common import Coordinate

def debug_model(model: Model):
    """Print all attributes of a model object"""
    print("\nModel debug info:")
    print(f"Model path: {model.path}")
    print("Available attributes:")
    for attr in dir(model):
        if not attr.startswith('_'):  # Skip internal attributes
            try:
                value = getattr(model, attr)
                print(f"  {attr}: {value}")
            except Exception as e:
                print(f"  {attr}: Error accessing - {str(e)}")

def sync_models(footprint: Footprint) -> bool:
    """Synchronize 3D model configurations in a footprint.
    
    Returns True if modifications were made, False otherwise."""
    if not footprint.models:
        print("  No model sections found in file")
        return False

    # Find third party and project models
    third_party_model = None
    project_model = None

    for model in footprint.models:
        if '${KICAD_3RD_PARTY}' in model.path:
            third_party_model = model
        elif '${KIPRJMOD}' in model.path:
            project_model = model

    if not third_party_model:
        print("  No KICAD_3RD_PARTY model found in file")
        return False

    # If no project model exists, create one based on the third party model
    if not project_model:
        # Create new model with same base filename but different path
        model_filename = os.path.basename(third_party_model.path)
        new_path = "${KIPRJMOD}/3d-models/" + model_filename
        
        project_model = Model()
        project_model.path = new_path
        project_model.pos = Coordinate(X=third_party_model.pos.X, 
                                   Y=third_party_model.pos.Y,
                                   Z=third_party_model.pos.Z)
        project_model.scale = Coordinate(X=third_party_model.scale.X,
                                     Y=third_party_model.scale.Y, 
                                     Z=third_party_model.scale.Z)
        project_model.rotate = Coordinate(X=third_party_model.rotate.X,
                                      Y=third_party_model.rotate.Y,
                                      Z=third_party_model.rotate.Z)
        project_model.hide = third_party_model.hide
        project_model.opacity = third_party_model.opacity
        
        footprint.models.append(project_model)
        print(f"  Added project model: {new_path}")
        return True

    # If both models exist, sync the project model's properties with third party model
    else:
        modified = False
        
        # Check and update each property
        if project_model.pos != third_party_model.pos:
            project_model.pos = Coordinate(X=third_party_model.pos.X,
                                       Y=third_party_model.pos.Y,
                                       Z=third_party_model.pos.Z)
            modified = True
            print("  Updated Coordinate")
            
        if project_model.scale != third_party_model.scale:
            project_model.scale = Coordinate(X=third_party_model.scale.X,
                                         Y=third_party_model.scale.Y,
                                         Z=third_party_model.scale.Z)
            modified = True
            print("  Updated scale")
            
        if project_model.rotate != third_party_model.rotate:
            project_model.rotate = Coordinate(X=third_party_model.rotate.X,
                                          Y=third_party_model.rotate.Y,
                                          Z=third_party_model.rotate.Z)
            modified = True
            print("  Updated rotation")
            
        if project_model.hide != third_party_model.hide:
            project_model.hide = third_party_model.hide
            modified = True
            print("  Updated visibility")
            
        if project_model.opacity != third_party_model.opacity:
            project_model.opacity = third_party_model.opacity
            modified = True
            print("  Updated opacity")

        return modified

    return False

def process_footprint_file(filepath: str, dry_run: bool = False) -> bool:
    """Process a single footprint file."""
    try:
        print(f"\nProcessing: {filepath}")
        
        # Load the footprint file
        footprint = Footprint().from_file(filepath)
        
        # Attempt to sync the models
        was_modified = sync_models(footprint)
        
        if was_modified:
            if not dry_run:
                # Save the modified footprint
                footprint.to_file(filepath)
                print("✅ File modified successfully")
            else:
                print("🔍 Would modify file")
            return True
        else:
            print("✓ No changes needed")
            return False
            
    except Exception as e:
        print(f"❌ Error processing file: {str(e)}")
        return False

def find_footprint_files(directory: str) -> List[str]:
    """Find all .kicad_mod files in the given directory."""
    footprint_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.kicad_mod'):
                footprint_files.append(os.path.join(root, file))
    return footprint_files

def main():
    parser = argparse.ArgumentParser(
        description='Synchronize KiCAD 3D model configurations between KICAD_3RD_PARTY and KIPRJMOD.'
    )
    parser.add_argument(
        '--directory', '-d',
        default='.',
        help='Directory to search for .kicad_mod files (default: current directory)'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Show what would be modified without making changes'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed processing information'
    )
    args = parser.parse_args()
    
    base_dir = os.getenv('GITHUB_WORKSPACE', args.directory)
    
    print(f"🔍 Searching for .kicad_mod files in: {base_dir}")
    footprint_files = find_footprint_files(base_dir)
    
    if not footprint_files:
        print("❌ No .kicad_mod files found!")
        return
    
    print(f"📦 Found {len(footprint_files)} .kicad_mod files")
    
    modified_files = 0
    for filepath in footprint_files:
        if process_footprint_file(filepath, args.dry_run):
            modified_files += 1
    
    print("\n📊 Summary:")
    print(f"Total files processed: {len(footprint_files)}")
    print(f"Files {'would be ' if args.dry_run else ''}modified: {modified_files}")
    
    if modified_files > 0 and not args.dry_run:
        exit(1)
    exit(0)

if __name__ == '__main__':
    main()
