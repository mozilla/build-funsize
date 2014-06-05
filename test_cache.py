import logging
import os
import shutil
import tempfile
import unittest

import cache
import oddity

class TestCache(unittest.TestCase):
    """ Tests for the Cache """

    def setUp(self):
        self.cache_uri = tempfile.mkdtemp()
        self.cache_object = cache.Cache(self.cache_uri)
        _, self.test_file = tempfile.mkstemp()
        self.test_string = 'This is a test string\n'
        _, self.output_file = tempfile.mkstemp()
        with open(self.test_file, 'wb') as f:
            f.write(self.test_string)

    def test_cache(self):
        """ Full test of a successful insert, lookup retrieval """
        # This doesn't sound right, but this is the best I can think of

        identifier = self.cache_object.save(self.test_file, isfile=True)
        logging.info('Identifier: %s' % identifier)
        self.assertTrue(self.cache_object.find(identifier))
        self.cache_object.retrieve(identifier, output_file=self.output_file)
        with open(self.output_file, 'rb') as f:
            self.assertEqual(self.test_string, f.read())

    def test_find(self):
        """ Check the find method works """
        self.assertFalse(self.cache_object.find('nonexistantid'))

    def test_retrieve(self):
        self.assertRaises(oddity.CacheMissError, self.cache_object.retrieve,
                'nonexistantid', output_file=False)

    @unittest.skip('Skipping test till we figure out what should go in it')
    def test_save(self):
        # TODO: Test all errors are raised correctly
        pass

    def tearDown(self):
        shutil.rmtree(self.cache_uri)
        os.remove(self.test_file)

if __name__ == '__main__':
    unittest.main(verbosity=3)
