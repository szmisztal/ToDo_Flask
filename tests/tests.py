import os
import tempfile
import pytest
from flask import Flask
from wtforms import StringField, TextAreaField, BooleanField
from app import DatabaseUtils, TaskForm, app


@pytest.fixture
def test_db():
    db_fd, db_path = tempfile.mkstemp()
    db_utils = DatabaseUtils(db_path)
    db_utils.create_task_table()
    yield db_utils
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def test_app():
    app = Flask(__name__)
    app.config['WTF_CSRF_ENABLED'] = False
    return app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_create_task_table(test_db):
    query = "SELECT name FROM sqlite_master WHERE type='table' AND name='tasks';"
    result = test_db.execute_sql_query(query, fetch_option="fetchone")
    assert result[0] == 'tasks'

def test_add_and_get_one_task(test_db):
    test_db.add_task("Test task", "Test description")
    task = test_db.get_one_task(1)
    assert task[1] == "Test task"

def test_get_all_tasks(test_db):
    test_db.add_task("Task 1", "Description 1")
    test_db.add_task("Task 2", "Description 2")
    tasks = test_db.get_all_tasks()
    assert len(tasks) == 2

def test_update_task(test_db):
    test_db.add_task("Original task", "Original description")
    test_db.update_task(1, "Updated task", "Updated description", True)
    task = test_db.get_one_task(1)
    assert task[1] == "Updated task"

def test_delete_task(test_db):
    test_db.add_task("Task to delete")
    test_db.delete_task(1)
    task = test_db.get_one_task(1)
    assert task is None

def test_task_form_validation(test_app):
    with test_app.app_context():
        form = TaskForm(task_title = "", description = "Test description", done = False)
        assert not form.validate()
        assert "This field is required." in form.errors['task_title']

def test_task_form_fields(test_app):
    with test_app.app_context():
        form = TaskForm()
        assert form.task_title.label.text == "Title"
        assert isinstance(form.task_title, StringField)
        assert form.description.label.text == "Description"
        assert isinstance(form.description, TextAreaField)
        assert form.done.label.text == "Done"
        assert isinstance(form.done, BooleanField)

def test_app_home_page_content(client):
    response = client.get('/')
    assert response.status_code == 200

def test_app_add_task_form_submission(client):
    response = client.post('/add_task', data = {'task_title': 'Test Task', 'description': 'Test Description'})
    assert response.status_code == 302

def test_app_update_task(client, test_db):
    test_db.add_task(task_title = 'Test task')
    response = client.post(f'/update_task/1',
                           data = {'task_title': 'Updated Task', 'description': 'Updated Description'})
    assert response.status_code == 302

def test_app_delete_task(client):
    test_db.add_task(task_title = 'Test task')
    response = client.post('/delete_task/1')
    assert response.status_code == 302

def test_app_tasks_list_count(client):
    response = client.get('/tasks_list')
    assert len(response.data.decode('utf-8').split('<div class="task">')) >= 1
