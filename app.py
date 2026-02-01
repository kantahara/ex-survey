from flask import Flask, render_template, request, redirect, url_for, session
from models import db, User, Survey, Question, Choice, Answer
from sqlalchemy import func
import os

app = Flask(__name__)

# 設定
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'survey.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'my_secret_key_12345' # セッション管理に必要

# データベースとアプリを紐付け
db.init_app(app)

# --- 1. トップページ ---
@app.route('/')
def index():
    surveys = Survey.query.all()
    current_user = None
    if 'user_id' in session:
        current_user = User.query.get(session['user_id'])
    return render_template('index.html', surveys=surveys, user=current_user)

# --- 2. ユーザ登録 ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        
        # 既存チェック（簡易）
        exists = User.query.filter_by(email=email).first()
        if exists:
            return "そのメールアドレスは既に登録されています。<a href='/register'>戻る</a>"

        new_user = User(name=name, email=email)
        db.session.add(new_user)
        db.session.commit()
        
        # 登録後そのままログイン状態にする
        session['user_id'] = new_user.id
        return redirect(url_for('index'))
    return render_template('register.html')

# --- 3. ログイン（ID入力式） ---
@app.route('/login', methods=['POST'])
def login():
    user_id = request.form['user_id']
    user = User.query.get(user_id)
    if user:
        session['user_id'] = user.id
    return redirect(url_for('index'))

# --- 4. ログアウト ---
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

# --- 5. アンケート新規作成 ---
@app.route('/create_survey', methods=['GET', 'POST'])
def create_survey():
    if 'user_id' not in session:
        return redirect(url_for('register'))
    
    if request.method == 'POST':
        title = request.form['title']
        new_survey = Survey(title=title, user_id=session['user_id'])
        db.session.add(new_survey)
        db.session.commit()
        # 作成したら質問追加画面へ
        return redirect(url_for('add_question', survey_id=new_survey.id))
    return render_template('create_survey.html')

# --- 6. 質問・選択肢の追加 ---
@app.route('/survey/<int:survey_id>/add_question', methods=['GET', 'POST'])
def add_question(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    
    if request.method == 'POST':
        q_text = request.form['question_text']
        choices_str = request.form['choices'] # カンマ区切りの文字列
        
        # 質問を保存
        new_q = Question(text=q_text, survey_id=survey.id)
        db.session.add(new_q)
        db.session.commit()
        
        # 選択肢を保存
        choice_list = choices_str.split(',')
        for c_text in choice_list:
            if c_text.strip():
                new_c = Choice(text=c_text.strip(), question_id=new_q.id)
                db.session.add(new_c)
        db.session.commit()
        return redirect(url_for('add_question', survey_id=survey.id))
        
    return render_template('add_question.html', survey=survey)

# --- 7. アンケート回答 ---
@app.route('/survey/<int:survey_id>/answer', methods=['GET', 'POST'])
def answer_survey(survey_id):
    if 'user_id' not in session:
        return redirect(url_for('register')) # 未ログインなら登録画面へ
        
    survey = Survey.query.get_or_404(survey_id)
    
    if request.method == 'POST':
        # フォームの全データを確認
        for key, value in request.form.items():
            # name="q_1" のような形式を探す
            if key.startswith('q_'):
                q_id = int(key.split('_')[1])
                c_id = int(value)
                
                new_answer = Answer(
                    user_id=session['user_id'],
                    question_id=q_id,
                    choice_id=c_id
                )
                db.session.add(new_answer)
        db.session.commit()
        return redirect(url_for('survey_result', survey_id=survey.id))
        
    return render_template('answer.html', survey=survey)

# --- 8. 集計結果 ---
@app.route('/survey/<int:survey_id>/result')
def survey_result(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    results = {}
    
    for q in survey.questions:
        # SQLで集計: SELECT choice_id, COUNT(*) ... GROUP BY choice_id
        q_counts = db.session.query(Answer.choice_id, func.count(Answer.id))\
            .filter_by(question_id=q.id)\
            .group_by(Answer.choice_id).all()
        
        # 辞書に変換 {choice_id: count}
        count_map = {r[0]: r[1] for r in q_counts}
        
        results[q.id] = []
        for c in q.choices:
            results[q.id].append({
                'text': c.text,
                'count': count_map.get(c.id, 0)
            })
            
    return render_template('result.html', survey=survey, results=results)

if __name__ == '__main__':
    app.run(debug=True)