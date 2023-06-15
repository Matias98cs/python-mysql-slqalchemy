from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

load_dotenv()
user = os.environ["MYSQL_USER"]
password = os.environ["MYSQL_PASSWORD"]
hots = os.environ["MYSQL_HOST"]
database = os.environ["MYSQL_DATABASE"]

app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"mysql+pymysql://{user}:{password}@{hots}/{database}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

ma = Marshmallow(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(70), unique=True)
    description = db.Column(db.String(255))

    def __init__(self, title, description):
        self.title = title
        self.description = description


with app.app_context():
    db.create_all()


class TaskSchema(ma.Schema):
    class Meta:
        fields = ("id", "title", "description")


task_shema = TaskSchema()
tasks_shema = TaskSchema(many=True)


@app.route("/task", methods=["POST"])
def create_task():
    title = request.json["title"]
    description = request.json["description"]
    new_task = Task(title, description)
    db.session.add(new_task)
    db.session.commit()
    return task_shema.jsonify(new_task)
    # return f"received task {request.json}"


@app.route("/tasks", methods=["GET"])
def get_tasks():
    all_tasks = Task.query.all()
    result = tasks_shema.dump(all_tasks)
    return jsonify(result)


@app.route("/task/<id>", methods=["GET"])
def get_task(id):
    task = Task.query.get(id)
    return task_shema.jsonify(task)


@app.route("/task/<id>", methods=["PUT"])
def update_task(id):
    task = Task.query.get(id)
    title = request.json["title"]
    description = request.json["description"]

    task.title = title
    task.description = description

    db.session.commit()
    return task_shema.jsonify(task)


@app.route("/task/<id>", methods=["DELETE"])
def delete_task(id):
    task = Task.query.get(id)
    db.session.delete(task)
    db.session.commit()
    return task_shema.jsonify(task)


@app.route("/")
def index():
    return f"Hola!!"


if __name__ == "__main__":
    app.run(debug=True)
