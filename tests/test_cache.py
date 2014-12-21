import os
import shutil
import tempfile
import unittest

import funsize.cache as cache


# FIXME: the test suite doesn't work without mocking S3
@unittest.SkipTest
class TestCache(unittest.TestCase):
    """ Tests for the Cache """

    def setUp(self):
        self.cache_uri = tempfile.mkdtemp()
        self.cache_object = cache.Cache(self.cache_uri)
        _, self.test_file = tempfile.mkstemp()
        self.test_string = 'This is a test string\n'
        _, self.output_file = tempfile.mkstemp()
        self.key = 'thisisatestkey'
        self.category = 'complete'
        with open(self.test_file, 'wb') as f:
            f.write(self.test_string)

    def test_cache(self):
        """ Full test of a successful insert, lookup retrieval """
        # This doesn't sound right as a unittest, but this is the best I can
        # think of

        self.cache_object.save(self.test_file, self.key, self.category,
                               isfile=True)
        self.assertTrue(self.cache_object.find(self.key, self.category))
        self.cache_object.retrieve(self.key, self.category,
                                   output_file=self.output_file)
        with open(self.output_file, 'rb') as f:
            self.assertEqual(self.test_string, f.read())

    def test_find(self):
        """ Check the find method works """
        self.assertFalse(self.cache_object.find('nonexistantid', self.category))

    @unittest.skip('Skipping test till we figure out what should go in it')
    def test_save(self):
        # TODO: Test all errors are raised correctly
        pass

    def tearDown(self):
        shutil.rmtree(self.cache_uri)
        os.remove(self.test_file)

if __name__ == '__main__':
    unittest.main(verbosity=3)
