import db
import logging
import os
import oddity
import shutil
import tempfile
import unittest


class TestDB(unittest.TestCase):
    """ Test class for Database Interface """

    def setUp(self):

        self.DB_FILE = 'unittest.db'
        shutil.copyfile('test_data/test.db', self.DB_FILE)
        self.DB_URI = 'sqlite:///' + self.DB_FILE
        self.dbo = db.Database(self.DB_URI)
        self.static_identifier = 'd7f65cf5002a1dfda88a33b7a31b65eb-cd757aa3cfed6f0a117fa16f33250f74'
        self.test_identifier = 'test'
        self.test_url = '/partial/test'
        self.test_status = db.status_code['COMPLETED']
        self.wrong_status = 'stringcannotbestatus'

    def test_lookup(self):
        self.assertTrue(self.dbo.lookup(identifier=self.static_identifier))

    def test_lookup_error(self):
        self.assertRaises(oddity.DBError, self.dbo.lookup,
                          identifier='nonexistant')

    def test_insert(self):
        self.dbo.insert(identifier=self.test_identifier, status=self.test_status, url=self.test_url)
        partial = self.dbo.lookup(identifier=self.test_identifier)
        self.assertEqual(partial.identifier, self.test_identifier)
        self.assertEqual(partial.url, self.test_url)
        self.assertEqual(partial.location, None)

    def test_insert_error(self):
        # Empty Insert
        self.assertRaises(oddity.DBError, self.dbo.insert)
        # Overwriting insert
        self.assertRaises(oddity.DBError, self.dbo.insert,
                    identifier=self.static_identifier)


    def test_update(self):
        self.dbo.update(self.static_identifier, url=self.test_url)

    def test_update_error(self):
        # Blank update
        self.assertRaises(oddity.DBError, self.dbo.update, self.static_identifier)
        # Updating non-existant record
        self.assertRaises(oddity.DBError, self.dbo.update, self.test_identifier)

    def tearDown(self):
        os.remove(self.DB_FILE)

if __name__ == '__main__':
    unittest.main()
