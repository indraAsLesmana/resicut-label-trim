from pdf2image import convert_from_path
from PIL import Image
import numpy as np
import os

# A6 dimensions in pixels at 300 DPI
A6_WIDTH = int(4.1 * 300)  # 1230 pixels
A6_HEIGHT = int(5.8 * 300)  # 1740 pixels

# Target dimensions for each label (half of A6 height)
TARGET_WIDTH = A6_WIDTH
TARGET_HEIGHT = A6_HEIGHT // 2  # Half of A6 height

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
    
    # Get first and last content positions
    first_row = rows_with_content[0]
    last_row = rows_with_content[-1]
    first_col = cols_with_content[0]
    last_col = cols_with_content[-1]
    
    # Add padding
    padding = 20
    top = max(0, first_row - padding)
    bottom = min(last_row + padding, image.height)
    left = max(0, first_col - padding)
    right = min(last_col + padding, image.width)
    
    return top, bottom, left, right

def resize_to_target(image):
    """Resize image to fit within target dimensions while maintaining aspect ratio"""
    aspect = image.width / image.height
    target_aspect = TARGET_WIDTH / TARGET_HEIGHT
    
    if aspect > target_aspect:
        # Width is the limiting factor
        new_width = TARGET_WIDTH
        new_height = int(TARGET_WIDTH / aspect)
    else:
        # Height is the limiting factor
        new_height = TARGET_HEIGHT
        new_width = int(TARGET_HEIGHT * aspect)
    
    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

def process_shipping_label(input_path, output_path):
    # Convert PDF to images
    pages = convert_from_path(input_path, dpi=300)
    
    processed_images = []
    current_page = Image.new('RGB', (A6_WIDTH, A6_HEIGHT), 'white')
    y_offset = 0
    label_count = 0
    
    for page in pages:
        # Find content boundaries
        top, bottom, left, right = find_content_boundaries(page)
        
        # Crop the image
        cropped_image = page.crop((left, top, right, bottom))
        
        # Resize to fit target dimensions
        resized_image = resize_to_target(cropped_image)
        
        # Calculate centering position
        x_center = (A6_WIDTH - resized_image.width) // 2
        
        # If this is the first label on the page or there's space
        if label_count % 2 == 0:
            y_offset = 0
            if label_count > 0:
                processed_images.append(current_page)
            current_page = Image.new('RGB', (A6_WIDTH, A6_HEIGHT), 'white')
        else:
            y_offset = TARGET_HEIGHT
        
        # Paste the image onto the current page
        current_page.paste(resized_image, (x_center, y_offset))
        label_count += 1
    
    # Add the last page if it has any content
    if label_count % 2 != 0 or label_count == 0:
        processed_images.append(current_page)
    
    # Save as PDF
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