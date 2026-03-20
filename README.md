# MHWs Equipment Manager

モンスターハンターワイルズ（MHWs）の巨戟アーティア武器用のスキル強化状態を管理・トラッキングするための Streamlit アプリケーションです。
MVP版として、錬成の登録・実行・Undo/Redoとシードの進行管理をサポートしています。

## ディレクトリ構成
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

1. リポジトリをクローンし、仮想環境を作成します。
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
