from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import io
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Define the base directory for absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Process form data
        user_name = request.form['name']
        user_state = request.form['state']
        user_district = request.form['district']
        user_field = request.form['field']
        user_msme_reg = request.form['msme_reg']  # New input for MSME Registration Number
        
        # Process images
        profile_pic = request.files['profile_pic']
        signature = request.files['signature']
        
        # Generate certificate
        certificate = generate_certificate(
            user_name, 
            user_state, 
            user_district, 
            user_field,
            user_msme_reg,  # Pass the new parameter
            profile_pic, 
            signature
        )
        
        # Return as downloadable file
        return send_file(
            certificate,
            as_attachment=True,
            download_name='certificate.png',
            mimetype='image/png'
        )
    
    return render_template('form.html')

def generate_certificate(name, state, district, field, msme_reg, profile_pic, signature):
    # Load certificate template using an absolute path
    certificate_path = os.path.join(BASE_DIR, 'Certificate Main.png')
    template = Image.open(certificate_path).convert('RGBA')
    
    # Process profile picture
    profile_img = Image.open(profile_pic).resize((150, 150))
    template.paste(profile_img, (200, 350))  # Adjust position as needed
    
    # Process signature
    signature_img = Image.open(signature).resize((200, 80))
    template.paste(signature_img, (483, 1051))  # Adjust position as needed
    
    # Prepare drawing context
    draw = ImageDraw.Draw(template)
    
    # Define font sizes
    font_size1 = 60  # Name font size (for primary name)
    font_size2 = 30  # Details font size (for duplicate name and other details)

    # Absolute paths for font files
    font_bold_path = os.path.join(BASE_DIR, 'static', 'fonts', 'Anastasia-Script.ttf')
    font_regular_path = os.path.join(BASE_DIR, 'static', 'fonts', 'Lora-Regular.ttf')
    
    try:
        name_font = ImageFont.truetype(font_bold_path, font_size1)
        details_font = ImageFont.truetype(font_regular_path, font_size2)
    except Exception as e:
        print(f"Error loading fonts: {e}")
        name_font = ImageFont.load_default()
        details_font = ImageFont.load_default()
    
    # Add text elements (adjust coordinates as per your template)
    draw.text((552,663), name, font=name_font, fill='black')          # Primary name (Anastasia-Script)
    draw.text((517,834), state, font=details_font, fill='black')         # State
    draw.text((1027,835), district, font=details_font, fill='black')     # District
    draw.text((1288,874), field, font=details_font, fill='black')        # Field
    draw.text((1572,835), msme_reg, font=details_font, fill='black')      # MSME Registration Number

    # Duplicate user's name in Lora-Regular.ttf (details_font) at a new position
    draw.text((404,1133), name, font=details_font, fill='black')          # Duplicate name position
    
    # Save to a bytes buffer
    img_io = io.BytesIO()
    template.save(img_io, 'PNG')
    img_io.seek(0)
    
    return img_io

if __name__ == '__main__':
    app.run(debug=True)
