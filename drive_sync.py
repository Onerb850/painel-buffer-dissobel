import os
import shutil
import datetime
import gdown
from concurrent.futures import ThreadPoolExecutor
import process_data
import generate_dashboard

FOLDER_URL = os.environ.get(
    'GDRIVE_FOLDER_URL', 
    'https://drive.google.com/drive/folders/1PASq_9Ctw405jREodldP4MITOayxsrdr'
)

# IDs diretos oficiais dos arquivos do Google Drive
BUFFER_FILE_ID = os.environ.get('GDRIVE_BUFFER_FILE_ID', '1Vo-hO9AAtTz1Cmp9vo4F8TfUM_fwlRAR')
PROD_FILE_ID = os.environ.get('GDRIVE_PROD_FILE_ID', '19ITdc1_sK0WFqap_ehQo_FH9JWOMpa9h')

LAST_SYNC_FILE = 'last_sync.json'

def sync_from_drive():
    """
    Baixa os arquivos BUFFER.csv e 01.11.csv do Google Drive e reprocessa o dashboard.
    """
    tz_brasilia = datetime.timezone(datetime.timedelta(hours=-3))
    sync_time = datetime.datetime.now(tz_brasilia).strftime('%d/%m/%Y %H:%M:%S')
    downloaded_files = []


    # 1. Tentar download direto por File ID se configurado
    if BUFFER_FILE_ID:
        try:
            # Baixa o BUFFER.csv para um arquivo temporário primeiro (evita arquivo corrompido/travado)
            temp_buf = 'BUFFER_downloading.csv'
            gdown.download(id=BUFFER_FILE_ID, output=temp_buf, quiet=True)
            if os.path.exists(temp_buf) and os.path.getsize(temp_buf) > 1000:
                if os.path.exists('BUFFER.csv'):
                    try: os.remove('BUFFER.csv')
                    except: pass
                shutil.move(temp_buf, 'BUFFER.csv')
                downloaded_files.append('BUFFER.csv')

            # Verifica se 01.11.csv precisa ser baixado (se não existir ou se foi atualizado no Drive)
            needs_prod = not os.path.exists('01.11.csv') or os.path.getsize('01.11.csv') < 10000
            if not needs_prod and PROD_FILE_ID:
                try:
                    import requests
                    import email.utils
                    prod_url = f'https://drive.google.com/uc?id={PROD_FILE_ID}'
                    r = requests.head(prod_url, allow_redirects=True, timeout=4)
                    if 'Last-Modified' in r.headers:
                        drive_mtime = email.utils.parsedate_to_datetime(r.headers['Last-Modified']).timestamp()
                        local_mtime = os.path.getmtime('01.11.csv')
                        if drive_mtime > local_mtime + 5:
                            print(f"[Drive Sync] Nova versão do 01.11.csv detectada no Drive! Baixando...")
                            needs_prod = True
                except Exception:
                    pass

            if needs_prod and PROD_FILE_ID:
                temp_prod = '01.11_downloading.csv'
                gdown.download(id=PROD_FILE_ID, output=temp_prod, quiet=True)
                if os.path.exists(temp_prod) and os.path.getsize(temp_prod) > 10000:
                    if os.path.exists('01.11.csv'):
                        try: os.remove('01.11.csv')
                        except: pass
                    shutil.move(temp_prod, '01.11.csv')
                    downloaded_files.append('01.11.csv')
        except Exception as e:
            return {
                'success': False,
                'error': f"Erro ao baixar do Drive: {str(e)}",
                'timestamp': sync_time
            }

    # 2. Tentar download da pasta compartilhada
    if not downloaded_files:
        temp_dir = 'drive_download_temp'
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
            os.makedirs(temp_dir, exist_ok=True)

            files = gdown.download_folder(url=FOLDER_URL, output=temp_dir, quiet=True)
            
            # Localizar e mover BUFFER.csv e 01.11.csv (ou 03.01.11.csv)
            found_buffer = False
            found_prod = False

            for root, _, filenames in os.walk(temp_dir):
                for f in filenames:
                    f_upper = f.upper()
                    full_src = os.path.join(root, f)
                    if 'BUFFER' in f_upper and f_upper.endswith('.CSV'):
                        shutil.copy2(full_src, 'BUFFER.csv')
                        found_buffer = True
                        downloaded_files.append('BUFFER.csv')
                    elif ('01.11' in f_upper or '03.01.11' in f_upper) and f_upper.endswith('.CSV'):
                        shutil.copy2(full_src, '01.11.csv')
                        found_prod = True
                        downloaded_files.append('01.11.csv')

            shutil.rmtree(temp_dir, ignore_errors=True)

            if not found_buffer and not found_prod:
                return {
                    'success': False,
                    'error': "A pasta do Drive foi acessada, mas os arquivos BUFFER.csv e 01.11.csv não foram encontrados dentro dela.",
                    'timestamp': sync_time
                }
        except Exception as e:
            err_msg = str(e)
            if '404' in err_msg or 'permission' in err_msg.lower():
                return {
                    'success': False,
                    'error': "Acesso negado (404). A pasta no Google Drive precisa estar com o compartilhamento definido como 'Qualquer pessoa com o link pode ler'.",
                    'timestamp': sync_time
                }
            return {
                'success': False,
                'error': f"Falha na sincronização com o Google Drive: {err_msg}",
                'timestamp': sync_time
            }

    # 3. Reprocessar dados e regenerar o dashboard
    try:
        data = process_data.run_process()
        generate_dashboard.run_generate()
        
        # Salvar status do sync
        sync_info = {
            'success': True,
            'timestamp': sync_time,
            'summary': data.get('summary', {}),
            'files': downloaded_files
        }
        
        import json
        with open(LAST_SYNC_FILE, 'w', encoding='utf-8') as sf:
            json.dump(sync_info, sf, ensure_ascii=False, indent=2)

        return sync_info
    except Exception as e:
        return {
            'success': False,
            'error': f"Erro ao processar dados após download: {str(e)}",
            'timestamp': sync_time
        }

if __name__ == '__main__':
    res = sync_from_drive()
    print("Resultado Sync:", res)
