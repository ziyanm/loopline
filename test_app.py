import unittest
import json
from app import app, get_db

class NotepadAppTests(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

        # Clear the database before each test
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute('DELETE FROM notes')
            db.commit()

    def test_create_note(self):
        response = self.app.post('/notes', data=json.dumps({'title': 'Test Note', 'content': 'This is a test note.'}), content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('note_id', data)

    def test_list_notes(self):
        # Create two test notes
        self.app.post('/notes', data=json.dumps({'title': 'Test Note 1', 'content': 'This is test note 1.'}), content_type='application/json')
        self.app.post('/notes', data=json.dumps({'title': 'Test Note 2', 'content': 'This is test note 2.'}), content_type='application/json')

        response = self.app.get('/notes')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 2)

    def test_get_note(self):
        response_create = self.app.post('/notes', data=json.dumps({'title': 'Test Note', 'content': 'This is a test note.'}), content_type='application/json')
        data_create = json.loads(response_create.data)
        note_id = data_create['note_id']

        response_get = self.app.get(f'/notes/{note_id}')
        data_get = json.loads(response_get.data)
        self.assertEqual(response_get.status_code, 200)
        self.assertEqual(data_get['title'], 'Test Note')

    def test_get_nonexistent_note(self):
        response = self.app.get('/notes/2')
        self.assertEqual(response.status_code, 404)

    def test_edit_note(self):
        response_create = self.app.post('/notes', data=json.dumps({'title': 'Test Note', 'content': 'This is a test note.'}), content_type='application/json')
        data_create = json.loads(response_create.data)
        note_id = data_create['note_id']

        response = self.app.put(f'/notes/{note_id}', data=json.dumps({'title': 'Updated Note', 'content': 'This is the updated content.'}), content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['title'], 'Updated Note')

    def test_edit_nonexistent_note(self):
        response = self.app.put('/notes/2', data=json.dumps({'title': 'Updated Note', 'content': 'This is the updated content.'}), content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_delete_note(self):
        response_create = self.app.post('/notes', data=json.dumps({'title': 'Test Note', 'content': 'This is a test note.'}), content_type='application/json')
        data_create = json.loads(response_create.data)
        note_id = data_create['note_id']

        response = self.app.delete(f'/notes/{note_id}')
        self.assertEqual(response.status_code, 200)

    def test_delete_nonexistent_note(self):
        response = self.app.delete('/notes/2')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
