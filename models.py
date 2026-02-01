from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# データベース操作用オブジェクトの作成
db = SQLAlchemy()

# 1. ユーザ情報
class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

# 2. アンケート情報
class Survey(db.Model):
    __tablename__ = 'Survey'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    
    # リレーション: SurveyからQuestionを参照できるようにする
    questions = db.relationship('Question', backref='survey', lazy=True)
    # 作成者の名前を取得しやすくする
    user = db.relationship('User', backref='surveys')

# 3. 質問
class Question(db.Model):
    __tablename__ = 'Question'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    survey_id = db.Column(db.Integer, db.ForeignKey('Survey.id'))
    
    # リレーション: QuestionからChoiceを参照できるようにする
    choices = db.relationship('Choice', backref='question', lazy=True)

# 4. 選択肢
class Choice(db.Model):
    __tablename__ = 'Choice'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('Question.id'))

# 5. 回答
class Answer(db.Model):
    __tablename__ = 'Answer'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('Question.id'))
    choice_id = db.Column(db.Integer, db.ForeignKey('Choice.id'))