import os
import json
from flask import Flask, send_from_directory, jsonify, request
import drive_sync
import process_data
import generate_dashboard

app = Flask(__name__, static_folder='.')

@app.route('/')
def index():
    if os.path.exists('dashboard.html'):
        return send_from_directory('.', 'dashboard.html')
    elif os.path.exists('index.html'):
        return send_from_directory('.', 'index.html')
    return "Dashboard ainda não gerado. Execute process_data.py e generate_dashboard.py", 404

@app.route('/dashboard.html')
def dashboard_html():
    return send_from_directory('.', 'dashboard.html')

@app.route('/data.json')
def get_data_json():
    if os.path.exists('data.json'):
        return send_from_directory('.', 'data.json', mimetype='application/json')
    return jsonify({"error": "data.json não encontrado"}), 404

@app.route('/api/status', methods=['GET'])
def api_status():
    last_sync = {}
    if os.path.exists('last_sync.json'):
        try:
            with open('last_sync.json', 'r', encoding='utf-8') as f:
                last_sync = json.load(f)
        except:
            pass

    summary = {}
    if os.path.exists('data.json'):
        try:
            with open('data.json', 'r', encoding='utf-8') as f:
                d = json.load(f)
                summary = d.get('summary', {})
        except:
            pass

    return jsonify({
        "status": "online",
        "last_sync": last_sync,
        "summary": summary
    })

@app.route('/api/sync', methods=['POST'])
def api_sync():
    """
    Dispara a sincronização com o Google Drive, baixa as planilhas mais recentes,
    executa o cálculo e regenera o dashboard.
    """
    try:
        result = drive_sync.sync_from_drive()
        if result.get('success'):
            return jsonify({
                "success": True,
                "message": "Dados atualizados com sucesso do Google Drive!",
                "timestamp": result.get('timestamp'),
                "summary": result.get('summary')
            })
        else:
            return jsonify({
                "success": False,
                "error": result.get('error', 'Falha ao sincronizar com o Google Drive.'),
                "timestamp": result.get('timestamp')
            }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Erro interno durante sincronização: {str(e)}"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"Servidor do Dashboard rodando em http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
