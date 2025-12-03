import os
import json
import qrcode
import base64
from io import BytesIO
from flask import Flask, render_template, request, make_response
from flask_cors import CORS  # <--- IMPORTANTE PARA LA EXTENSIÓN
from weasyprint import HTML

app = Flask(__name__)
# Permitir que cualquier origen (tu extensión) se conecte
CORS(app)

# Función auxiliar para rutas de imagen
def get_image_url(filename):
    # En Linux/Docker usamos rutas de sistema de archivos directas
    path = os.path.join(app.root_path, 'static', filename)
    return 'file://' + path

@app.route('/')
def index():
    return "Servidor DTE Activo. Usa la extensión de Chrome."

@app.route('/generar-pdf', methods=['POST'])
def generar_pdf():
    if 'json_file' not in request.files:
        return "No se subió ningún archivo", 400
    
    file = request.files['json_file']
    
    try:
        data = json.load(file)
    except Exception as e:
        return f"Error leyendo el JSON: {e}", 400

    # 1. LOGICA QR
    try:
        ident = data.get('identificacion', {})
        ambiente = ident.get('ambiente', '01')
        codGen = ident.get('codigoGeneracion', '')
        # Intento robusto de obtener fecha
        fechaEmi = ident.get('fecEmi', '')
        if not fechaEmi and 'identificacion' in data:
             fechaEmi = data['identificacion'].get('fecEmi', '')

        qr_content = f"https://admin.factura.gob.sv/consultaPublica?ambiente={ambiente}&codGen={codGen}&fechaEmi={fechaEmi}"
        
        qr = qrcode.QRCode(box_size=3, border=0)
        qr.add_data(qr_content)
        qr.make(fit=True)
        img_qr = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img_qr.save(buffered, format="PNG")
        qr_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        qr_img_src = f"data:image/png;base64,{qr_b64}"
    except:
        qr_img_src = ""

    # 2. LOGICA FECHA SEPARADA
    fecha_emi = data.get('identificacion', {}).get('fecEmi', '')
    fecha_split = {'dia': '', 'mes': '', 'anio': ''}
    if fecha_emi and len(fecha_emi) >= 10:
        fecha_split['anio'] = fecha_emi[:4]
        fecha_split['mes'] = fecha_emi[5:7]
        fecha_split['dia'] = fecha_emi[8:10]

    # 3. IMÁGENES
    images = {
        'logo': get_image_url('logo.png'),
        'wa': get_image_url('whatsapp.png'),
        'fb': get_image_url('facebook.png'),
        'ig': get_image_url('instagram.png'),
        'web': get_image_url('web.png')
    }

    try:
        rendered_html = render_template(
            'invoice.html', 
            dte=data, 
            qr_code=qr_img_src, 
            imgs=images,
            fecha=fecha_split
        )
        
        pdf = HTML(string=rendered_html).write_pdf()

        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=factura_vert.pdf'
        return response
    except Exception as e:
        return f"Error interno del servidor: {e}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)