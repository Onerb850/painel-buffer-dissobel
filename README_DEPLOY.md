# Guia de Deploy Online: Dashboard BUFFER + Google Drive

Este guia mostra passo a passo como colocar o Dashboard online na nuvem gratuitamente (no **Render.com**), com sincronização direta da sua pasta do **Google Drive**.

---

## 📁 1. Configurar o Google Drive (MUITO IMPORTANTE)

Para que o servidor online consiga ler as planilhas da sua pasta do Drive ao clicar no botão "Sincronizar":

1. Abra o [Google Drive](https://drive.google.com).
2. Vá até a pasta `TRABALHO - DISSOBEL > BUFFER`.
3. Clique com o botão direito sobre a pasta **BUFFER** (ou clique na setinha ao lado do nome da pasta no topo) e escolha **Compartilhar** > **Compartilhar**.
4. Em **Acesso geral**, mude de "Restrito" para:
   👉 **"Qualquer pessoa com o link"** (função: **Leitor**).
5. Clique em **Concluído**.

> **Como atualizar no dia a dia:**  
> Sempre que quiser atualizar os dados, basta arrastar o novo `BUFFER.csv` e `01.11.csv` para dentro dessa pasta no Google Drive (substituindo os anteriores).

---

## 🚀 2. Como Fazer o Deploy Online Gratuito (Render.com)

O **Render** oferece hospedagem web gratuita para aplicações Python.

### Passo 2.1: Enviar o código para o GitHub
1. Crie um repositório no seu GitHub (pode ser Privado ou Público), por exemplo: `buffer-dashboard`.
2. Suba todos os arquivos desta pasta (`BUFFER`) para esse repositório:
   ```bash
   git init
   git add .
   git commit -m "Deploy Buffer Dashboard com Google Drive Sync"
   git branch -M main
   git remote add origin https://github.com/SEU_USUARIO/buffer-dashboard.git
   git push -u origin main
   ```

### Passo 2.2: Criar o Serviço no Render
1. Acesse **[dashboard.render.com](https://dashboard.render.com)** e faça login com seu GitHub.
2. Clique no botão azul **New +** e selecione **Web Service**.
3. Escolha o repositório que você acabou de criar (`buffer-dashboard`).
4. Preencha as configurações (o Render detectará a maioria automaticamente graças ao `render.yaml`):
   * **Name:** `buffer-dissobel` (ou o nome que preferir)
   * **Region:** Ohio (US East) ou Frankfurt
   * **Branch:** `main`
   * **Runtime:** `Python 3`
   * **Build Command:** `pip install -r requirements.txt && python process_data.py && python generate_dashboard.py`
   * **Start Command:** `gunicorn app:app`
   * **Instance Type:** `Free`
5. Clique em **Create Web Service**.

Em 2 a 3 minutos, o Render gerará um link público seguro com HTTPS, por exemplo:  
👉 **`https://buffer-dissobel.onrender.com`**

---

## 🔄 3. Como Funciona a Atualização no Painel Online

1. Quando você ou alguém da equipe abrir o link gerado:
2. No canto superior direito do painel, há o botão:  
   **`[ 🔄 Sincronizar Drive ]`**
3. Ao clicar:
   * O botão entra no modo *"Sincronizando..."* com ícone giratório.
   * O servidor na nuvem se conecta à pasta do Google Drive, baixa o `BUFFER.csv` e o `01.11.csv` mais recentes.
   * O script processa todos os números, pesos e paletes.
   * A tela recarrega automaticamente com uma mensagem de confirmação:  
     `✅ Dados atualizados com sucesso do Google Drive!`

---

## 💻 4. Rodando Localmente com o Servidor Flask

Se você quiser rodar localmente no seu computador com a mesma inteligência do botão:

```powershell
python app.py
```
E acesse no navegador:  
👉 **`http://localhost:5000`**
