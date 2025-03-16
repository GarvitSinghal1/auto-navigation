import qrcode
import os
import argparse
from PIL import Image, ImageDraw, ImageFont

def generate_qr_code(data, output_file, size=10, border=4, add_text=True):
    """
    Generate a QR code with optional text label
    
    Args:
        data: The data to encode in the QR code
        output_file: Output file path (PNG)
        size: QR code size (1-40, higher means more data capacity)
        border: Border size in modules
        add_text: Whether to add text label below QR code
    """
    # Create QR code instance
    qr = qrcode.QRCode(
        version=size,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
        box_size=10,  # Size of each box in pixels
        border=border  # Border size in boxes
    )
    
    # Add data
    qr.add_data(data)
    qr.make(fit=True)
    
    # Create an image from the QR Code
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Add text label if requested
    if add_text:
        # Convert to PIL image with mode 'RGB'
        img = img.convert('RGB')
        
        # Get image size
        img_width, img_height = img.size
        
        # Create a new image with extra space for text
        text_height = 30
        new_img = Image.new('RGB', (img_width, img_height + text_height), color='white')
        new_img.paste(img, (0, 0))
        
        # Add text
        draw = ImageDraw.Draw(new_img)
        try:
            # Try to use a TrueType font if available
            font = ImageFont.truetype("arial.ttf", 20)
        except IOError:
            # Fall back to default font
            font = ImageFont.load_default()
        
        # Center text below QR code
        text_width = len(data) * 10  # Approximate width based on text length
        text_x = (img_width - text_width) // 2
        text_y = img_height + 5
        
        draw.text((text_x, text_y), data, fill="black", font=font)
        img = new_img
    
    # Save the image
    img.save(output_file)
    print(f"QR code saved to {output_file}")
    
    # Display file size
    file_size = os.path.getsize(output_file) / 1024  # Size in KB
    print(f"File size: {file_size:.2f} KB")
    
    return output_file

def main():
    parser = argparse.ArgumentParser(description='Generate QR code for robot tracking')
    parser.add_argument('--data', type=str, default='ROBOT_TARGET', 
                        help='Data to encode in QR code')
    parser.add_argument('--output', type=str, default='robot_target.png',
                        help='Output file name')
    parser.add_argument('--size', type=int, default=5,
                        help='QR code size (1-40), higher values allow more data')
    parser.add_argument('--border', type=int, default=4,
                        help='Border size in modules')
    parser.add_argument('--no-text', action='store_true',
                        help='Do not add text label below QR code')
    
    args = parser.parse_args()
    
    generate_qr_code(
        data=args.data,
        output_file=args.output,
        size=args.size,
        border=args.border,
        add_text=not args.no_text
    )

if __name__ == "__main__":
    main() 