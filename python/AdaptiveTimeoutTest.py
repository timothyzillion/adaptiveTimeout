import unittest
import AdaptiveTimeout

class AdaptiveTimeoutTest(unittest.TestCase):
    def test_basicMeanTest(self):
        at = AdaptiveTimeout.AdaptiveTimeout(5)
        at.update(5)
        self.assertEqual(at.mean, 5)
        at.update(5)
        self.assertEqual(at.mean, 5)
        print at.sigma
        at.update(10)
        self.assertAlmostEqual(at.mean, 20.0/3.0)


if __name__ == 'main':
    unittest.main()
