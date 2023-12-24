from flask import Flask, render_template, request, flash, redirect, url_for
from forms import TaskForm
from db_utils import DatabaseUtils
from secrets import key

app = Flask(__name__)
app.config["SECRET_KEY"] = key
db = DatabaseUtils("tasks.db")

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/add_task", methods = ["GET", "POST"])
def add_task():
    form = TaskForm()
    if request.method == "GET":
        return render_template("task_form.html", form = form)
    elif request.method == "POST":
        task_title = form.task_title.data
        description = form.description.data
        if description:
            db.add_task(task_title, description)
        else:
            db.add_task(task_title)
        flash("Task was added successfully")
        return redirect(url_for("home"))

@app.route("/tasks_list", methods = ["GET"])
def tasks_list():
    tasks = db.get_all_tasks()
    return render_template("tasks_list.html", tasks = tasks)

@app.route("/task/<int:task_id>", methods = ["GET"])
def task_details(task_id):
    task = db.get_one_task(task_id)
    if task[4] == 1:
        done_status = "Yes"
    else:
        done_status = "No"
    return render_template("task_details.html", task = task, done_status = done_status, task_id = task[0])

@app.route("/update_task/<int:task_id>", methods = ["GET", "POST"])
def task_update(task_id):
    task = db.get_one_task(task_id)
    if task is None:
        return "Task not found", 404
    form = TaskForm(
        task_title = task[1],
        description = task[3],
        done = task[4]
    )
    if request.method == "GET":
        return render_template("task_form.html", form = form, task = task)
    elif request.method == "POST":
        task_title = form.task_title.data
        description = form.description.data
        done = form.done.data
        db.update_task(task_id, task_title, description, done)
        flash("Task was updated successfully")
        return redirect(url_for("tasks_list"))

@app.route("/delete_task/<int:task_id>", methods = ["GET", "POST"])
def task_delete(task_id):
    task = db.get_one_task(task_id)
    if task is None:
        return "Task not found", 404
    if request.method == "GET":
        return render_template("task_delete.html", task = task, task_id = task[0])
    elif request.method == "POST":
        db.delete_task(task[0])
        flash("Task was deleted successfully")
        return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug = False)
