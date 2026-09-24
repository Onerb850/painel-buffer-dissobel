import os
import json
import threading
import time
from flask import Flask, send_from_directory, jsonify, request
import drive_sync
import process_data
import generate_dashboard

app = Flask(__name__, static_folder='.')

_sync_lock = threading.Lock()
_last_auto_sync = 0
AUTO_SYNC_INTERVAL = 300  # Intervalo de 5 minutos entre verificações automáticas no Drive

def trigger_auto_sync(force=False):
    global _last_auto_sync
    now = time.time()
    if not force and (now - _last_auto_sync < AUTO_SYNC_INTERVAL):
        return
    
    def _worker():
        global _last_auto_sync
        if not _sync_lock.acquire(blocking=False):
            return
        try:
            _last_auto_sync = time.time()
            print("[Auto-Sync] Verificando arquivos mais recentes no Google Drive...")
            res = drive_sync.sync_from_drive()
            if res.get('success'):
                print("[Auto-Sync] Painel atualizado com sucesso a partir do Google Drive!")
            else:
                print(f"[Auto-Sync] Nota: {res.get('error')}")
        except Exception as e:
            print(f"[Auto-Sync] Erro: {e}")
        finally:
            _sync_lock.release()

    t = threading.Thread(target=_worker, daemon=True)
    t.start()

def check_local_update():
    """Garante que qualquer alteração direta em BUFFER.csv seja refletida no dash imediatamente."""
    try:
        if os.path.exists('BUFFER.csv') and os.path.exists('data.json'):
            b_mtime = os.path.getmtime('BUFFER.csv')
            d_mtime = os.path.getmtime('data.json')
            if b_mtime > d_mtime:
                process_data.run_process()
                generate_dashboard.run_generate()
    except Exception as e:
        pass

# Dispara sincronização inicial em segundo plano apenas se data.json não existir
if not os.path.exists('data.json'):
    trigger_auto_sync(force=True)

@app.route('/')
def index():
    check_local_update()
    trigger_auto_sync(force=False)
    if os.path.exists('dashboard.html'):
        return send_from_directory('.', 'dashboard.html')
    elif os.path.exists('index.html'):
        return send_from_directory('.', 'index.html')
    return "Dashboard ainda não gerado. Execute process_data.py e generate_dashboard.py", 404

@app.route('/dashboard.html')
def dashboard_html():
    check_local_update()
    trigger_auto_sync(force=False)
    return send_from_directory('.', 'dashboard.html')

@app.route('/data.json')
def get_data_json():
    check_local_update()
    if os.path.exists('data.json'):
        return send_from_directory('.', 'data.json', mimetype='application/json')
    return jsonify({"error": "data.json não encontrado"}), 404

@app.route('/api/status', methods=['GET'])
def api_status():
    check_local_update()
    trigger_auto_sync(force=False)
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
    executa o cálculo e regenera o dashboard de forma segura (sem colisão de concorrência).
    """
    acquired = _sync_lock.acquire(timeout=45)
    if not acquired:
        return jsonify({
            "success": False,
            "error": "Uma sincronização já está sendo processada no servidor. Aguarde alguns segundos.",
            "timestamp": time.strftime('%d/%m/%Y %H:%M:%S')
        }), 429

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
    finally:
        _sync_lock.release()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"Servidor do Dashboard rodando em http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
