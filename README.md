# MHWs Equipment Manager

モンスターハンターワイルズ（MHWs）の巨戟アーティア武器用のスキル強化状態を管理・トラッキングするための Streamlit アプリケーションです。
MVP版として、錬成の登録・実行・Undo/Redoとシードの進行管理をサポートしています。

## Data Persistence (Cookie & Cloud Sync)

本アプリは、ユーザー登録なしで即座に試用でき、かつデバイス間同期も可能なハイブリッド・ストレージを採用しています。

1.  **Anonymous Mode (Cookie)**:
    - `streamlit-cookies-controller` を使用し、ブラウザのCookieを直接操作して永続化します。
    - 4KBの制限を回避するため、データは `zlib` で高度に圧縮され `base64` エンコードされます。
2.  **Cloud Sync (Supabase)**:
    - ログインすることで、Google/GitHub等のアカウントに紐付いたクラウド同期が有効になります。
    - 同期はページロード時に自動で行われ、バックアップとしても機能します。

### Setup Instructions (Cloud)

Streamlit Community Cloud 等へデプロイする場合、以下の Secrets 設定が必要です：

1.  **Supabase Secrets**:
    `.streamlit/secrets.toml` またはデプロイ環境の Secrets 設定に、以下の形式で Supabase の接続情報を追加してください。
    ```toml
    [connections.supabase]
    url = "https://your-project.supabase.co"
    key = "your-anon-key"
    ```

## Project Structure
- `app.py`: メインダッシュボード（統計と Undo / Redo）
- `pages/`: 各種管理画面（所持武器、抽選、復元、鑑定護石）
- `src/`: アプリケーションロジック、データモデル、および DB 管理
- `docs/`: 常に最新の状態に保たれた仕様書（SSoT）
- `tests/`: ロジックの正当性を担保するユニットテスト群

## 技術スタック
- Python 3.10+
- Streamlit
- Pandas

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
