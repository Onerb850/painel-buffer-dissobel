import os
import shutil
import datetime
import gdown
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
    sync_time = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    downloaded_files = []

    # 1. Tentar download direto por File ID se configurado
    if BUFFER_FILE_ID and PROD_FILE_ID:
        try:
            gdown.download(id=BUFFER_FILE_ID, output='BUFFER.csv', quiet=True)
            gdown.download(id=PROD_FILE_ID, output='01.11.csv', quiet=True)
            downloaded_files = ['BUFFER.csv', '01.11.csv']
        except Exception as e:
            return {
                'success': False,
                'error': f"Erro ao baixar por File ID: {str(e)}",
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
