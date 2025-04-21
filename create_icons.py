#!/usr/bin/env python3
"""
Icon generator for Py-Fusion application.

This script creates application icons in various formats and sizes
required for different operating systems.
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_base_icon(size=1024):
    """Create a base icon with the letters 'PF' for Py-Fusion.

    Args:
        size: Size of the icon in pixels (square)

    Returns:
        PIL.Image: The generated icon image
    """
    # Create a new image with a transparent background
    img = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw a rounded rectangle as background
    bg_color = (52, 152, 219)  # Nice blue color
    margin = size // 10
    draw.rounded_rectangle(
        [(margin, margin), (size - margin, size - margin)],
        radius=size // 10,
        fill=bg_color
    )

    # Add text "PF" (Py-Fusion)
    try:
        # Try to use a nice font if available
        font = ImageFont.truetype("Arial Bold", size // 2)
    except IOError:
        # Fallback to default font
        font = ImageFont.load_default()

    text = "PF"
    text_color = (255, 255, 255)  # White text

    # Calculate text position to center it
    try:
        # For newer Pillow versions
        left, top, right, bottom = font.getbbox(text)
        text_width, text_height = right - left, bottom - top
    except AttributeError:
        # For older Pillow versions
        if hasattr(draw, 'textsize'):
            text_width, text_height = draw.textsize(text, font=font)
        else:
            text_width, text_height = font.getsize(text)

    position = ((size - text_width) // 2, (size - text_height) // 2)

    # Draw the text
    draw.text(position, text, font=font, fill=text_color)

    return img

def save_png_icons(base_img, output_dir):
    """Save PNG icons in various sizes.

    Args:
        base_img: Base image to resize
        output_dir: Directory to save icons to
    """
    sizes = [16, 32, 48, 64, 128, 256, 512, 1024]

    for size in sizes:
        resized = base_img.resize((size, size), Image.LANCZOS)
        resized.save(os.path.join(output_dir, f"py_fusion_{size}.png"))

    # Save a copy of the 1024px version as the main icon
    base_img.save(os.path.join(output_dir, "py_fusion.png"))

def create_ico_file(output_dir):
    """Create Windows .ico file from the PNG icons.

    Args:
        output_dir: Directory containing the PNG icons
    """
    try:
        from PIL import Image

        # Load images of different sizes
        sizes = [16, 32, 48, 64, 128, 256]
        images = []

        for size in sizes:
            img_path = os.path.join(output_dir, f"py_fusion_{size}.png")
            if os.path.exists(img_path):
                img = Image.open(img_path)
                images.append(img)

        # Save as ICO
        if images:
            images[0].save(
                os.path.join(output_dir, "py_fusion.ico"),
                format='ICO',
                sizes=[(img.width, img.height) for img in images]
            )
            print("Created Windows .ico file")
    except Exception as e:
        print(f"Error creating .ico file: {e}")

def create_icns_file(output_dir):
    """Create macOS .icns file from the PNG icons.

    This requires the macOS 'iconutil' command-line tool.

    Args:
        output_dir: Directory containing the PNG icons
    """
    try:
        import subprocess
        import tempfile
        import shutil

        # Create a temporary iconset directory
        iconset_dir = os.path.join(tempfile.gettempdir(), "py_fusion.iconset")
        os.makedirs(iconset_dir, exist_ok=True)

        # Copy and rename PNG files to the format required by iconutil
        size_mapping = {
            16: "16x16",
            32: "32x32",
            64: "64x64",
            128: "128x128",
            256: "256x256",
            512: "512x512",
            1024: "1024x1024"
        }

        for size, name in size_mapping.items():
            src = os.path.join(output_dir, f"py_fusion_{size}.png")
            if os.path.exists(src):
                # Regular resolution
                dst = os.path.join(iconset_dir, f"icon_{name}.png")
                shutil.copy2(src, dst)

                # High resolution (2x) - use the next size up if available
                if size * 2 in size_mapping:
                    src_2x = os.path.join(output_dir, f"py_fusion_{size*2}.png")
                    if os.path.exists(src_2x):
                        dst_2x = os.path.join(iconset_dir, f"icon_{name}@2x.png")
                        shutil.copy2(src_2x, dst_2x)

        # Run iconutil to create .icns file
        icns_path = os.path.join(output_dir, "py_fusion.icns")
        subprocess.run(["iconutil", "-c", "icns", iconset_dir, "-o", icns_path], check=True)

        # Clean up
        shutil.rmtree(iconset_dir)
        print("Created macOS .icns file")
    except Exception as e:
        print(f"Error creating .icns file: {e}")
        print("Note: .icns creation requires macOS with the 'iconutil' command")

def main():
    """Main function to create all icon files."""
    # Create output directory
    output_dir = os.path.join("py_fusion_gui", "resources", "icons")
    os.makedirs(output_dir, exist_ok=True)

    # Create base icon
    base_img = create_base_icon(1024)

    # Save PNG icons
    save_png_icons(base_img, output_dir)
    print(f"Created PNG icons in {output_dir}")

    # Create .ico file for Windows
    create_ico_file(output_dir)

    # Create .icns file for macOS
    create_icns_file(output_dir)

    print("Icon generation complete!")

if __name__ == "__main__":
    main()
