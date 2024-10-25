import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import serial.tools.list_ports  # For cross-platform device listing

app = Flask(__name__)

# Define the folder to save uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed extensions for device communication (dummy example)
ALLOWED_EXTENSIONS = {'txt', 'log'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def list_connected_devices():
    """List all available serial ports"""
    ports = serial.tools.list_ports.comports()
    devices = [{"port": port.device, "description": port.description} for port in ports]
    return devices

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Device selection route
@app.route('/device', methods=['POST'])
def select_device():
    selected_device = request.form.get('device')
    devices = list_connected_devices()
    # Find selected device in the list of connected devices
    device_info = next((d for d in devices if d['port'] == selected_device), None)
    
    if device_info:
        print(f"Connected to '{device_info['port']}'")
        return jsonify({'message': f"Connected to '{device_info['port']}'"})
    else:
        return jsonify({'error': 'Device not found'}), 404

# Get available devices route
@app.route('/list_devices', methods=['GET'])
def list_devices():
    devices = list_connected_devices()
    return jsonify(devices)

# GeoTIFF upload and display route
@app.route('/upload_geotiff', methods=['POST'])
def upload_geotiff():
    if 'geotiff' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['geotiff']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return jsonify({'message': 'GeoTIFF uploaded successfully', 'file_path': file_path})
    
    return jsonify({'error': 'Invalid file type'})

# Handle GeoJSON export
@app.route('/export_geojson', methods=['POST'])
def export_geojson():
    geojson_data = request.json.get('geojson')
    with open(os.path.join(app.config['UPLOAD_FOLDER'], 'shapes.geojson'), 'w') as f:
        f.write(geojson_data)
    return jsonify({'message': 'GeoJSON exported successfully'})

if __name__ == '__main__':
    app.run(debug=True)
