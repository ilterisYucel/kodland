import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, render_template, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import JSON

load_dotenv()


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Quiz(db.Model):
    __tablename__ = "quiz"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(JSON)
    result = db.Column(JSON)

    def __init__(self, content, result):
        self.content = content
        self.result = result

    def toDict(self):
        return {"id": self.id, "content": self.content, "result": self.result}

    def __repr__(self):
        return f"<Quiz {self.id}>"


class Score(db.Model):
    __tablename__ = "score"

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer)
    result = db.Column(db.Integer)

    def __init__(self, quiz_id, result):
        self.quiz_id = quiz_id
        self.result = result

    def toDict(self):
        return {"id": self.id, "result": self.result, "quiz_id": self.quiz_id}

    def __repr__(self):
        return f"<Score {self.id}>"


@app.get("/healthcheck")
def healthcheck():
    return f"Hello, system time is {datetime.now()}"


@app.get("/api/quizzes/<quiz>")
def get_quiz(quiz):
    try:
        data = Quiz.query.get(quiz)
        if not data:
            return Response(f"Quiz {quiz} not found.", status=404)
        return jsonify(data.toDict())
    except Exception:
        return Response("Server Fault.", status=500)


@app.post("/api/quizzes")
def post_quiz():
    try:
        data = request.get_json(force=True)
        if "content" not in data or "result" not in data:
            return Response("Bad Request.", status=400)
        quiz = Quiz(content=data["content"], result=data["result"])
        db.session.add(quiz)
        db.session.commit()
        return jsonify(data)
    except Exception:
        return Response("Server Fault.", status=500)


@app.get("/api/scores/<score>")
def get_score(score):
    try:
        data = Score.query.get(score)
        if not data:
            return Response(f"Score {score} not found.", status=404)
        return jsonify(data.toDict())
    except Exception:
        return Response("Server Fault.", status=500)


@app.post("/api/scores")
def post_score():
    try:
        data = request.get_json(force=True)
        if "quiz_id" not in data or "result" not in data:
            return Response("Bad Request.", status=400)
        score = Score(result=data["result"], quiz_id=data["quiz_id"])
        db.session.add(score)
        db.session.commit()
        return jsonify(data)
    except Exception as e:
        print(e)
        return Response("Server Fault.", status=500)


@app.get("/api/scores/max")
def get_max_score():
    try:
        data = Score.query.all()
        if not data or not len(data):
            return Response("Scores not found.", status=404)
        parsed_data = [d.toDict() for d in data]
        max_score = max(parsed_data, key=lambda x: x["result"])
        return jsonify(max_score)
    except Exception:
        return Response("Server Fault.", status=500)


@app.get("/quizzes/<quiz>")
def render_quiz(quiz):
    try:
        data = Quiz.query.get(quiz)
        if not data:
            return Response(f"Quiz {quiz} not found.", status=404)
        return render_template("quiz.html", quiz=data.toDict())
    except Exception as e:
        print(e)
        return Response("Server Fault.", status=500)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
