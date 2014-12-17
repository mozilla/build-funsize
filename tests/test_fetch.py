import os
import tempfile
import unittest

import funsize.utils.fetch as fetch
import funsize.utils.oddity as oddity

TEST_URL = 'https://ftp.mozilla.org/pub/mozilla.org/firefox/releases/29.0/KEY'
TEST_MD5 = 'ab3ef84fb7437659c5fd34a793cad0f2'
WRONG_MD5 = '2f0dac397a43df5c9567347bf48fe3ba'
TEST_SHA512 = '6f445230407ae4e4c73a73d345de8b349e975f08adcdfafc713e9ba05e40a38f8dd287055ddbbcc59aef21a814f7b1a0488492e2be116242bbbdbee62f5ab997'
WRONG_SHA512 = '799ba5f26eebdbbb242611eb2e2948840a1b7f418a12fea95ccbbdd550782dd8f83a04e50ab9e317cfafdcda80f579e943b8ed543d37a37c4e4ea704032544f6'


class TestFetch(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_url = TEST_URL
        cls.test_md5 = TEST_MD5
        cls.wrong_md5 = WRONG_MD5
        cls.test_sha512 = TEST_SHA512
        cls.wrong_sha512 = WRONG_SHA512

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        _, self.temp_filepath = tempfile.mkstemp()
        _, self.existing_temp_file = tempfile.mkstemp()
        with open(self.existing_temp_file, 'w') as f:
            f.write('Already something in this file\n')

    def test_correct_download(self):
        self.assertEqual(
            None, fetch.downloadmar(self.test_url,
                                    self.test_sha512, cipher='sha512',
                                    output_file=self.temp_filepath))

    def test_incorrect_download(self):
        self.assertRaises(oddity.DownloadError, fetch.downloadmar,
                          self.test_url, self.wrong_sha512, cipher='sha512',
                          output_file=self.temp_filepath)

    def test_file_save(self):
        fetch.downloadmar(self.test_url, self.test_sha512, cipher='sha512',
                          output_file=self.temp_filepath)
        self.assertTrue(os.path.exists(self.temp_filepath))

    def test_existing_file_save(self):
        fetch.downloadmar(self.test_url, self.test_sha512, cipher='sha512',
                          output_file=self.temp_filepath)
        self.assertTrue(os.path.exists(self.temp_filepath))

    def tearDown(self):
        os.remove(self.existing_temp_file)
        os.remove(self.temp_filepath)
        os.rmdir(self.temp_dir)

    @classmethod
    def tearDownClass(cls):
        pass

if __name__ == '__main__':
    unittest.main(verbosity=3)
