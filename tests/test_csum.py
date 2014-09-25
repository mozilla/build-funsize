import unittest

import funsize.utils.csum as csum


class TestCsum(unittest.TestCase):
    """ Tests for csum.py
        Using pre-computed stored hashes rather than computing them on the fly.
    """

    @classmethod
    def setUpClass(cls):
        cls.test_string="Make him an offer he can't refuse"
        cls.correct_md5='fc1cbdd4aa7539ff2d09e0c2feb394e7'
        cls.correct_sha512='fc97f6c478cf25412cac95ad7e33b0e00a9894862febe6e7996fcdf63c0ff7beccde5ca0156df03ed4b0d710eaf2c89982ec4fbb5f58d9b52e38bac9d1e9f86f'

    def test_gethash(self):
        self.assertEqual(self.correct_md5, csum.getmd5(self.test_string))
        self.assertEqual(self.correct_sha512, csum.getsha512(self.test_string))

    def test_verify(self):
        self.assertTrue(csum.verify(self.test_string, self.correct_md5,
                                    cipher='md5'))
        self.assertTrue(csum.verify(self.test_string, self.correct_sha512,
                                    cipher='sha512'))


if __name__ == '__main__':
    unittest.main(verbosity=3)
