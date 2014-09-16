import logging
import os
import shutil
import unittest
import time
import funsize.database.database as db
import funsize.utils.oddity as oddity
from funsize.database.models import status_code

__here__ = os.path.dirname(os.path.abspath(__file__))


class TestDB(unittest.TestCase):
    """ Test class for Database Interface """

    def setUp(self):

        self.DB_FILE = 'unittest.db'
        shutil.copyfile(os.path.join(__here__, 'test_data/test.db'), self.DB_FILE)
        self.DB_URI = 'sqlite:///' + self.DB_FILE
        self.dbo = db.Database(self.DB_URI)
        self.static_identifier = 'NiuRlVVSYqqSFYWK184RJMvf7jJ3uHXaV+ydgjb2cmG@SX60VW8d71lY6jKXNl8i13QcNnAVFppsXzNfdfwzVw=='
        self.start_timestamp = time.time()
        self.finish_timestamp = time.time() + 300
        self.test_identifier = 'test'
        self.test_status = status_code['COMPLETED']
        self.wrong_status = 'stringcannotbestatus'

    def test_lookup(self):
        self.assertTrue(self.dbo.lookup(identifier=self.static_identifier))

    def test_lookup_failure(self):
        self.assertIsNone(self.dbo.lookup(identifier='nonexistant'))

    def test_insert(self):
        self.dbo.insert(identifier=self.test_identifier, status=self.test_status, start_timestamp=self.start_timestamp)
        partial = self.dbo.lookup(identifier=self.test_identifier)
        self.assertEqual(partial.identifier, self.test_identifier)
        self.assertEqual(partial.start_timestamp, self.start_timestamp)
        self.assertEqual(partial.finish_timestamp, -1)

    def test_insert_error(self):
        # Empty Insert
        self.assertRaises(oddity.DBError, self.dbo.insert)
        # Overwriting insert
        try:
            self.dbo.insert(identifier=self.static_identifier)
        except:
            self.fail('Inserting duplicate record raised an error,'
                      'This should no happen.')


    def test_update(self):
        self.dbo.update(self.static_identifier, finish_timestamp=self.finish_timestamp)

    def test_update_error(self):
        # Blank update
        self.assertRaises(oddity.DBError, self.dbo.update, self.static_identifier)
        # Updating non-existant record
        self.assertRaises(oddity.DBError, self.dbo.update, self.test_identifier)

    def tearDown(self):
        os.remove(self.DB_FILE)

if __name__ == '__main__':
    unittest.main(verbosity=3)
