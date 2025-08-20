"""
Image processing utilities for optimization and cleanup.
"""

import os
from typing import List, Optional
from PIL import Image
from typing import List, Optional

class ImageProcessor:
    """
    Provides utilities for image optimization and cleanup.
    """

    @staticmethod
    def optimize_image(image_path: str, quality: int = 85, output_format: Optional[str] = None) -> str:
        """
        Optimizes an image by reducing its quality or converting its format.

        Args:
            image_path (str): The path to the input image.
            quality (int): The quality level for JPEG optimization (0-100).
                           Ignored for PNG.
            output_format (str, optional): The desired output format (e.g., "JPEG", "PNG").
                                           If None, keeps original format.

        Returns:
            str: The path to the optimized image. If no optimization is needed, returns original path.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at: {image_path}")

        img = Image.open(image_path)
        original_format = img.format
        
        # Determine output path and format
        base_name, _ = os.path.splitext(image_path)
        
        final_output_format = output_format if output_format else original_format
        if not final_output_format:
            raise ValueError("Could not determine output format for image optimization.")

        output_path = f"{base_name}_optimized.{final_output_format.lower()}"

        # Save with optimization
        if final_output_format in ["JPEG", "JPG"]:
            img.save(output_path, quality=quality, optimize=True)
        elif final_output_format == "PNG":
            # PNG optimization is lossless, so quality parameter is not directly applicable
            # We can still save to re-compress if needed, but it might not reduce size significantly
            img.save(output_path, optimize=True)
        else:
            img.save(output_path) # Save without specific optimization for other formats

        return output_path

    @staticmethod
    def cleanup_images(image_paths: List[str]):
        """
        Deletes a list of image files from the file system.

        Args:
            image_paths (List[str]): A list of paths to the image files to delete.
        """
        for path in image_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
                    print(f"Cleaned up: {path}")
                else:
                    print(f"Warning: File not found for cleanup: {path}")
            except Exception as e:
                print(f"Error cleaning up {path}: {e}")
