from pdf2image import convert_from_path
from PIL import Image
import numpy as np
import os

def find_content_boundaries(image):
    # Convert image to numpy array
    img_array = np.array(image)
    
    # Convert to grayscale if image is RGB
    if len(img_array.shape) == 3:
        img_array = np.mean(img_array, axis=2)
    
    threshold = 250  # Threshold for considering a pixel as content
    
    # Find the last non-white row (bottom boundary)
    rows_with_content = np.where(np.min(img_array, axis=1) < threshold)[0]
    # Find the last non-white column (right boundary)
    cols_with_content = np.where(np.min(img_array, axis=0) < threshold)[0]
    
    if len(rows_with_content) == 0 or len(cols_with_content) == 0:
        return image.height, image.width
    
    # Add padding to both bottom and right
    padding = 20  # Adjust this value as needed
    last_content_row = rows_with_content[-1]
    last_content_col = cols_with_content[-1]
    
    bottom_boundary = min(last_content_row + padding, image.height)
    right_boundary = min(last_content_col + padding, image.width)
    
    return bottom_boundary, right_boundary

def process_shipping_label(input_path, output_path):
    # Convert PDF to images
    pages = convert_from_path(input_path, dpi=300)
    
    processed_images = []
    
    for page in pages:
        # Find both bottom and right boundaries
        bottom_boundary, right_boundary = find_content_boundaries(page)
        
        # Crop the image from all sides
        cropped_image = page.crop((0, 0, right_boundary, bottom_boundary))
        
        # Convert to RGB mode if necessary
        if cropped_image.mode != 'RGB':
            cropped_image = cropped_image.convert('RGB')
            
        processed_images.append(cropped_image)
    
    # Save the first image as PDF
    if processed_images:
        processed_images[0].save(
            output_path,
            "PDF",
            resolution=300.0,
            save_all=True,
            append_images=processed_images[1:]
        )

# Example usage
if __name__ == "__main__":
    input_pdf = "input_label.pdf"
    output_pdf = "trimmed_labels.pdf"
    process_shipping_label(input_pdf, output_pdf) 