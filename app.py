import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
database_path = os.path.join(basedir, 'conferencesDB.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class ConferenceTopic(db.Model):
    __tablename__ = "ConferenceTopic"
    conference_id = db.Column(db.Integer, db.ForeignKey('conference.id'), primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), primary_key=True)


class Conference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    website = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    topics = db.relationship('Topic', secondary=ConferenceTopic.__tablename__, backref='Conference')


class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    conferences = db.relationship('Conference', secondary=ConferenceTopic.__tablename__, backref='Topic')


@app.route('/', methods=['GET'])
def index():
    keyword = request.args.get('keyword', '')

    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = Conference.query.join(ConferenceTopic).join(Topic)
    if keyword:
        query = query.filter(db.or_(
            Conference.name.ilike(f'%{keyword}%'),
            Conference.description.ilike(f'%{keyword}%'),
            Topic.name.ilike(f'%{keyword}%')
        ))

    filtered_conferences = query.distinct().paginate(page=page, per_page=per_page)
    return render_template('index.html', conferences=filtered_conferences)


if __name__ == '__main__':
    app.run(debug=True)
