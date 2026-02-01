from app import app, db

# アプリケーションコンテキスト内で実行
with app.app_context():
    db.create_all()
    print("=========================================")
    print(" データベース (survey.db) を作成しました！")
    print("=========================================")