import flask
import os
import shutil
import tempfile
import unittest
import mock

class TestAPI_GET(unittest.TestCase):
    """ Test the flask APIs call and return all the right things
        TODO: Concretize the 'return' format.
    """

    def setUpClass(cls):

    import api

    def setUp(self):

        self.app = api.app.test_client()

        #_, self.test_db = tempfile.mkstemp()
        #shutil.copyfile('test_data/test.db', self.test_db)
        # Use the temp database. How do we do this?

    def test_db_lookup(self):
        with mock.patch('api.db.lookup') as m:
            m.return_value = mock.MagicMock(status=0)
            mock_partial = m.return_value
            mock_partial.status=api.db.status_code['COMPLETED'] #Mock the return value
            rv = self.app.get('/partial/test')
            m.assert_called_once_with(identfier=u'test')

    def test_completed
        with mock.patch('api.db.lookup') as m:
            m.return_value = mock.MagicMock(status=0)
            mock_partial = m.return_value
            mock_partial.status=api.db.status_code['COMPLETED'] #Mock the return value
            rv = self.app.get('/partial/test')
            m.assert_called_once_with(identfier=u'test')

        #mock_lookup = mock.MagicMock()
        #mock_lookup.status = api.db.status_code['COMPLETED']
        #api.db.lookup = mock_lookup

    def tearDown(self):
        #os.remove(self.test_db)
        pass

if __name__ == '__main__':
    unittest.main()
