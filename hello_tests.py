import os
import hello
import unittest
import tempfile


class HelloTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, hello.app.config['DATABASE'] = tempfile.mkstemp()
        hello.app.config['TESTING'] = True
        self.app = hello.app.test_client()
        hello.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(hello.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        assert 'No entries by now' in str(rv.data)

    def login(self, user, pw):
        return self.app.post('/login', data=dict(
            username=user,
            password=pw), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_auth(self):
        rv = self.login('qd', 'default')
        assert 'You where logged in' in str(rv.data)
        rv = self.logout()
        assert 'You where logged out' in str(rv.data)
        rv = self.login('adminx', 'default')
        assert 'Invalid username/password'
        rv = self.login('qd', 'lolpass')
        assert 'Invalid username/password'

    def test_messages(self):
        self.login('qd', 'default')
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here'),
            follow_redirects=True)
        assert 'No entries by now' not in str(rv.data)
        assert '&lt;Hello&gt;' in str(rv.data)
        assert '<strong>HTML</strong> allowed here' in str(rv.data)

if __name__ == '__main__':
    unittest.main()
