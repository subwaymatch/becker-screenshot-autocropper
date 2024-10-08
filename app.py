from flask import Flask, request, render_template, redirect, send_file
from peewee import *
from uuid_extensions import uuid7str
from process_screenshot import get_file_checksum, autocrop_screenshot
import datetime
import pathlib
import os

app = Flask(__name__)
app.config.from_pyfile('config.py')

pg_db = PostgresqlDatabase(
    app.config['DATABASE_NAME'],
    user=app.config['DATABASE_USER'],
    password=app.config['DATABASE_PASSWORD'],
    host=app.config['DATABASE_HOST'],
)

class BaseModel(Model):
    class Meta:
        database = pg_db

class Screenshot(BaseModel):
    screenshot_id = CharField(primary_key=True, unique=True)
    original_filename = CharField()
    exam_section = CharField()
    question_id = CharField()
    is_correct = BooleanField()
    is_answered = BooleanField()
    created_at = DateTimeField(default=datetime.datetime.now)
    new_filename = CharField()
    file_checksum = CharField()

def create_tables():
    with pg_db:
        pg_db.create_tables([Screenshot])

def create_directories():
    pathlib.Path('./screenshot-uploads/input-images').mkdir(parents=True, exist_ok=True)
    pathlib.Path('./screenshot-uploads/output-images').mkdir(parents=True, exist_ok=True)

@app.route("/")
def home():
    return redirect("/list")

@app.get('/list')
def get_list():
    items = Screenshot.select() \
        .order_by(Screenshot.created_at.desc()) \
        .dicts()
    return render_template('list.jinja', items=items)


@app.get('/random')
def get_random_list():
    items = Screenshot.select() \
        .order_by(fn.Random()).limit(10) \
        .dicts()
    return render_template('list.jinja', items=items)


@app.route('/screenshot/<string:filename>')
def get_screenshot(filename=None):
    output_image_path = os.path.join('screenshot-uploads/output-images', filename)

    if pathlib.Path(output_image_path).is_file():
        return send_file(output_image_path)
    else:
        return send_file('static/images/question-placeholder.png')


@app.get('/upload-screenshot')
def upload_screenshot_get():
    return render_template(
        'upload-screenshot.jinja',
    )

@app.post('/upload-screenshot')
def upload_screenshot_post():
    f = request.files['image_file']

    try:
        screenshot_id = uuid7str()
        file_checksum = get_file_checksum(f)

        # check if the checksum already exists
        does_checksum_alreay_exists = Screenshot.select().where(Screenshot.file_checksum == file_checksum).count()

        if does_checksum_alreay_exists:
            return {
                'success': False,
                'message': f'The checksum {file_checksum} already exists in the database',
            }

        input_image_save_path = f'./screenshot-uploads/input-images/{f.filename}'
        f.save(input_image_save_path)

        result = autocrop_screenshot(f)

        Screenshot.create(
            screenshot_id = screenshot_id,
            original_filename = result['original_filename'],
            exam_section = result['exam_section'],
            question_id = result['question_id'],
            is_answered = result['is_answered'],
            is_correct = result['is_correct'],
            new_filename = result['new_filename'],
            file_checksum = file_checksum
        )

        output_image_save_path = os.path.join('screenshot-uploads', 'output-images', result['new_filename'])
        result['cropped_image'].save(output_image_save_path)

        return {
            'success': True,
            'original_filename': result['original_filename'],
            'screenshot_id': screenshot_id,
            'original_filename': result['original_filename'],
            'exam_section': result['exam_section'],
            'question_id': result['question_id'],
            'is_answered': result['is_answered'],
            'is_correct': result['is_correct'],
            'new_filename': result['new_filename'],
            'file_checksum': file_checksum
        }
    except Exception as err:
        raise
        # return {
        #     'success': False,
        #     'message': repr(err)
        # }

@app.get('/delete-screenshot/<string:screenshot_id>')
def delete_screenshot(screenshot_id):
    record = Screenshot.get(Screenshot.screenshot_id == screenshot_id)
    
    pathlib.Path(
        os.path.join(
            './screenshot-uploads/input-images',
            record.original_filename

        )
    ).unlink()

    pathlib.Path(
        os.path.join(
            './screenshot-uploads/output-images',
            record.new_filename
        )
    ).unlink()
    
    record.delete_instance()

    return redirect('/')


if __name__ == '__main__':
    create_tables()
    create_directories()
    app.run(debug=True)