import os
from PIL import Image
from pathlib import Path

def optimize_icons(directory, size=(64, 64)):
    icon_dir = Path(directory)
    if not icon_dir.exists():
        print(f"Directory {directory} not found.")
        return

    print(f"Optimizing icons in {directory} to {size}...")
    
    for icon_path in icon_dir.glob("*"):
        if icon_path.suffix.lower() in [".png", ".jpg", ".jpeg"]:
            try:
                with Image.open(icon_path) as img:
                    # Convert to RGBA for PNG compatibility if needed
                    if img.mode != 'RGBA' and icon_path.suffix.lower() == '.png':
                        img = img.convert('RGBA')
                    
                    # Resize using Lanczos for high quality
                    img.thumbnail(size, Image.Resampling.LANCZOS)
                    
                    # Save back
                    img.save(icon_path)
                    print(f"Optimized: {icon_path.name} ({img.size})")
            except Exception as e:
                print(f"Failed to optimize {icon_path.name}: {e}")

if __name__ == "__main__":
    optimize_icons("assets/icons")
