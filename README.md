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

### 初回セットアップ
1. リポジトリをクローンします。
2. 仮想環境を作成し、依存関係をインストールします。
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 起動方法 (自動)
以下のいずれかの方法で簡単に起動できます：

- **PowerShell**: `./start.ps1` を実行（仮想環境の有効化も自動で行われます）
- **コマンドプロンプト**: `start.bat` を実行
- **VS Code**: ワークスペースを開くと自動的にタスクが実行されます（`.vscode/tasks.json` により設定済み）
- **Antigravityエージェント**: `/dev` セッション開始時に自動的にアプリの状態を確認・起動します

### 起動方法 (手動)
```powershell
. .venv\Scripts\activate
streamlit run app.py
```
