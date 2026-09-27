import unittest
from core.compute_bcs import poll_pct, comp_points, drop_high_low, infer_ballots

class TestBCSMath(unittest.TestCase):
    def test_poll_pct(self): self.assertAlmostEqual(poll_pct(1500,60),1.0)
    def test_comp_points(self):
        self.assertEqual(comp_points(1),1.0)
        self.assertEqual(comp_points(25),0.04)
        self.assertEqual(comp_points(26),0.0)
        self.assertEqual(comp_points(None),0.0)
    def test_drop_high_low_six(self):
        self.assertAlmostEqual(drop_high_low([1,.8,.6,.4,.2,0]),.5)
    def test_no_drop_before_six(self):
        self.assertAlmostEqual(drop_high_low([1,.5,0]),.5)
    def test_infer_ballots(self):
        self.assertEqual(infer_ballots({"teams":[{"points":1524}]}),61)
        self.assertEqual(infer_ballots({"ballots":62,"teams":[]}),62)

if __name__=="__main__": unittest.main()
