import os
import app as flaskr
import unittest
import tempfile


class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.testing = True
        self.app = flaskr.app.test_client()
        with flaskr.app.app_context():
            flaskr.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(flaskr.app.config['DATABASE'])

    def test_messages(self):
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here',
            category='A category'
        ), follow_redirects=True)
        assert b'No entries here so far' not in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'<strong>HTML</strong> allowed here' in rv.data
        assert b'A category' in rv.data

    def test_add_entry(self):
        # Test adding a new entry
        rv = self.app.post('/add', data=dict(
            title='Test Entry',
            text='This entry is for testing purposes. Surprise',
            category='Test Category (for testing!)'
        ), follow_redirects=True)
        assert b'Test Entry' in rv.data
        assert b'This entry is for testing purposes. Surprise' in rv.data
        assert b'Test Category (for testing!)' in rv.data


def test_filter_entries(self):
    # Test filtering entries by category
    self.app.post('/add', data=dict(
        title='Filtered Entry',
        text='This is a filtered entry',
        category='Filtered Category'
    ))
    rv = self.app.post('/filter', data=dict(
        category='Filtered Category'
    ), follow_redirects=True)
    assert b'Filtered Entry' in rv.data
    assert b'This is a filtered entry' in rv.data
    assert b'Filtered Category' in rv.data


def test_delete_entry(self):
    # Test deleting an entry
    rv = self.app.post('/add', data=dict(
        title='Entry to delete',
        text='This entry will be deleted',
        category='Deletion Category'
    ), follow_redirects=True)
    entry_id = flaskr.get_db().execute('SELECT id FROM entries WHERE title = "Entry to delete"')
    rv = self.app.post('/delete', data=dict(
        entry_id=entry_id
    ), follow_redirects=True)
    assert b'Entry to delete' not in rv.data
    assert b'This entry will be deleted' not in rv.data
    assert b'Deletion Category' not in rv.data


if __name__ == '__main__':
    unittest.main()
