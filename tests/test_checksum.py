import unittest

import funsize.utils.checksum as checksum


class TestChecksum(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_string = "Make him an offer he can't refuse"
        cls.correct_sha512 = 'fc97f6c478cf25412cac95ad7e33b0e00a9894862febe6e' \
            '7996fcdf63c0ff7beccde5ca0156df03ed4b0d710eaf2c89982ec4fbb5f58d9b' \
            '52e38bac9d1e9f86f'

    def test_gethash(self):
        self.assertEqual(self.correct_sha512,
                         checksum.get_hash("sha512", self.test_string))

    def test_verify(self):
        self.assertTrue(checksum.verify(self.test_string, self.correct_sha512))
