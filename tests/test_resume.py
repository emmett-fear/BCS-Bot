import unittest
from core.resume import rate

class TestResume(unittest.TestCase):
    def test_head_to_head_matters(self):
        r=rate([{"winner":"A","loser":"B","winner_site":"neutral","loser_site":"neutral"}])
        self.assertLess(r["A"]["rank"],r["B"]["rank"])
    def test_road_win_beats_home_win_all_else_equal(self):
        games=[
          {"winner":"A","loser":"X","winner_site":"road","loser_site":"home"},
          {"winner":"B","loser":"Y","winner_site":"home","loser_site":"road"},
          {"winner":"X","loser":"Z","winner_site":"neutral","loser_site":"neutral"},
          {"winner":"Y","loser":"Z","winner_site":"neutral","loser_site":"neutral"}]
        r=rate(games); self.assertGreater(r["A"]["score"],r["B"]["score"])

if __name__=="__main__":unittest.main()
