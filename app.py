from flask import Flask, render_template, send_from_directory, request, redirect, url_for
import socket
import os
import qrcode

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), "shared")
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # Max 100 MB

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Get local IP address
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

# Generate QR code for the IP address
def generate_qr_code(ip):
    url = f"http://{ip}:6789"
    qr = qrcode.make(url)
    qr_path = os.path.join("static", "ip_qr.png")
    qr.save(qr_path)

@app.route('/', methods=['GET', 'POST'])
def index():
    ip = get_ip()
    generate_qr_code(ip)

    if request.method == 'POST':
        uploaded_file = request.files.get('file')
        if uploaded_file and uploaded_file.filename:
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            uploaded_file.save(save_path)
        return redirect(url_for('index'))

    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', files=files, ip=ip)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6789)
