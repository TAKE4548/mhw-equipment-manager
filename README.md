# MHWs Equipment Manager

モンスターハンターワイルズ（MHWs）の巨戟アーティア武器用のスキル強化状態を管理・トラッキングするための Streamlit アプリケーションです。
MVP版として、錬成の登録・実行・Undo/Redoとシードの進行管理をサポートしています。

## Data Persistence (Google Sheets)

This application uses Google Sheets for data persistence on Streamlit Community Cloud.

### Setup Instructions

1.  **Create a Google Sheet**: Create a new spreadsheet in your Google Drive.
2.  **Add Headers**: Add the following headers to the first row (A1 to F1):
    `id`, `weapon_type`, `element`, `series_skill`, `group_skill`, `remaining_count`
3.  **Enable APIs**: In the Google Cloud Console, ensure that both **Google Drive API** and **Google Sheets API** are enabled for your project. (Both are required for the `streamlit-gsheets-connection` library).
4.  **Share the Sheet**: 
    -   Create a **Service Account** in the [Google Cloud Console](https://console.cloud.google.com/).
    -   Generate a **JSON Key** for the service account.
    -   Copy the `client_email` from the JSON.
    -   Click "Share" on your Google Sheet and invite that email as an **Editor**.
4.  **Configure the App (Local)**:
    -   Create a folder `.streamlit` in the project root.
    -   Create a file `secrets.toml` inside it.
    -   Pass the JSON key content into `secrets.toml` as follows:
      ```toml
      [connections.gsheets]
      type = "service_account"
      project_id = "..."
      private_key_id = "..."
      private_key = "..."
      client_email = "..."
      client_id = "..."
      auth_uri = "https://accounts.google.com/o/oauth2/auth"
      token_uri = "https://oauth2.googleapis.com/token"
      auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
      client_x509_cert_url = "..."
      ```
5.  **Configure the App (Cloud)**:
    -   Copy the same TOML content into the "Secrets" section of your Streamlit Community Cloud dashboard.
6.  **Paste the URL**:
    -   Copy the URL of your spreadsheet and paste it into the **Settings** sidebar of the app.

## Project Structure
- `app.py`: メインダッシュボード（アクティブな強化一覧と実行）
- `pages/1_register.py`: 新規スキル強化の登録画面
- `src/`: アプリケーションロジックとコンポーネント（履歴管理、DB管理）
- `docs/`: 仕様書および設計ドキュメント群

## 技術スタック
- Python 3.10+
- Streamlit
- Pandas
- SQLite3

## ローカルでの実行方法

1. リポジリをクローンし、仮想環境を作成します。
```bash
python -m venv .venv
source .venv/Scripts/activate # Windowsの場合は .venv\Scripts\activate
```

2. 依存関係をインストールします。
```bash
pip install -r requirements.txt
```

3. Streamlitアプリを起動します。
```bash
streamlit run app.py
```
