import sqlite3
from flask import Flask, request, g
from flask_restful import Api, Resource, reqparse

app = Flask(__name__)
api = Api(app)
app.config['DATABASE'] = 'notepad.db'  # SQLite database file

# Helper functions for database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Create the database schema if it doesn't exist
def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL
            )
        ''')
        db.commit()

init_db()


class NotesResource(Resource):
    def get(self):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id, title, content FROM notes')
        notes = [{'note_id': row[0], 'title': row[1], 'content': row[2]} for row in cursor.fetchall()]

        return notes

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str, required=True, help='Note title is required')
        parser.add_argument('content', type=str, required=True, help='Note content is required')
        args = parser.parse_args()

        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO notes (title, content) VALUES (?, ?)', (args['title'], args['content']))
        db.commit()
        note_id = cursor.lastrowid

        return {'note_id': note_id, 'title': args['title'], 'content': args['content']}, 201


class NoteResource(Resource):
    def note_exists(self, note_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id FROM notes WHERE id = ?', (note_id,))
        row = cursor.fetchone()

        return row is not None


    def get(self, note_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT title, content FROM notes WHERE id = ?', (note_id,))
        row = cursor.fetchone()

        if row:
            return {'note_id': note_id, 'title': row[0], 'content': row[1]}
        else:
            return {'message': 'Note not found'}, 404

    def put(self, note_id):
        if self.note_exists(note_id):
            parser = reqparse.RequestParser()
            parser.add_argument('title', type=str, required=True, help='Note title is required')
            parser.add_argument('content', type=str, required=True, help='Note content is required')
            args = parser.parse_args()

            db = get_db()
            cursor = db.cursor()
            cursor.execute('UPDATE notes SET title = ?, content = ? WHERE id = ?', (args['title'], args['content'], note_id))
            db.commit()

            return {'note_id': note_id, 'title': args['title'], 'content': args['content']}
        else:
            return {'message': 'Note not found'}, 404


    def delete(self, note_id):
        db = get_db()
        cursor = db.cursor()

        # Check if the note exists
        if self.note_exists(note_id):
            # Note exists, delete it
            cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
            db.commit()

            return {'message': 'Note deleted'}
        else:
            # Note not found
            return {'message': 'Note not found'}, 404


api.add_resource(NotesResource, '/notes')
api.add_resource(NoteResource, '/notes/<int:note_id>')


if __name__ == '__main__':
    app.run(debug=True)
