import unittest

import csum

class TestCsum(unittest.TestCase):
    """ Tests for csum.py
        Using pre-computed stored hashes rather than computing them on the fly.
    """

    @classmethod
    def setUpClass(cls):
        cls.test_string="Make him an offer he can't refuse"
        cls.correct_md5='fc1cbdd4aa7539ff2d09e0c2feb394e7'
        cls.correct_sha256='39fa6e474a8adef60a11b306f5f71ab09cdabf87a5c89b30a90123f11b73c7a8'
        cls.correct_sha512='fc97f6c478cf25412cac95ad7e33b0e00a9894862febe6e7996fcdf63c0ff7beccde5ca0156df03ed4b0d710eaf2c89982ec4fbb5f58d9b52e38bac9d1e9f86f'
        cls.correct_sha512b64='@Jf2xHjPJUEsrJWtfjOw4AqYlIYv6+bnmW@N9jwP977M3lygFW3wPtSw1xDq8siZguxPu19Y2bUuOLrJ0en4bw=='

    def test_gethash(self):
        self.assertEqual(self.correct_md5, csum.getmd5(self.test_string))
        self.assertEqual(self.correct_sha256, csum.getsha256(self.test_string))
        self.assertEqual(self.correct_sha512, csum.getsha512(self.test_string))
        self.assertEqual(self.correct_sha512b64, csum.getsha512b64(self.test_string))

    def test_verify(self):
        self.assertTrue(csum.verify(self.test_string, self.correct_md5,
            cipher='md5'))
        self.assertTrue(csum.verify(self.test_string, self.correct_sha256,
            cipher='sha256'))
        self.assertTrue(csum.verify(self.test_string, self.correct_sha512,
            cipher='sha512'))
        self.assertTrue(csum.verify(self.test_string, self.correct_sha512b64,
            cipher='sha512b64'))

if __name__ == '__main__':
    unittest.main(verbosity=3)
