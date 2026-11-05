import unittest
import pandas as pd
from src.analytics import daily_returns,rolling_contagion,drawdown
class TestAnalytics(unittest.TestCase):
 def test_returns(self):
  p=pd.DataFrame({'a':[100,110,99]});self.assertAlmostEqual(daily_returns(p).iloc[0,0],.1)
 def test_contagion(self):
  r=pd.DataFrame({'a':[.1,.2,-.1,.3], 'b':[.2,.4,-.2,.6]});self.assertAlmostEqual(rolling_contagion(r,3).iloc[-1],1.)
 def test_drawdown(self):
  self.assertAlmostEqual(drawdown(pd.DataFrame({'a':[10,12,9]})).iloc[-1,0],-.25)
if __name__=='__main__':unittest.main()

class TestInputAndEdgeCases(unittest.TestCase):
 def test_prepare_sorts_dates(self):
  from src.analytics import prepare_prices
  frame = pd.DataFrame({'Date': ['2024-01-05', '2024-01-01', '2024-01-04', '2024-01-03', '2024-01-02'], 'a': [5, 1, 4, 3, 2], 'b': [6, 2, 5, 4, 3]})
  self.assertTrue(prepare_prices(frame).index.is_monotonic_increasing)
 def test_prepare_rejects_missing_and_duplicate_dates(self):
  from src.analytics import prepare_prices
  frame = pd.DataFrame({'Date': ['2024-01-01'] * 5, 'a': [1] * 5, 'b': [2] * 5})
  with self.assertRaises(ValueError): prepare_prices(frame)
  frame['Date'] = pd.date_range('2024-01-01', periods=5)
  frame.loc[0, 'a'] = None
  with self.assertRaises(ValueError): prepare_prices(frame)
 def test_window_longer_than_returns(self):
  r = pd.DataFrame({'a': [1, 2], 'b': [2, 3]})
  self.assertEqual(len(rolling_contagion(r, 5)), 2)
  self.assertTrue(rolling_contagion(r, 5).isna().all())
 def test_demo_is_reproducible(self):
  from src.analytics import demo_prices
  pd.testing.assert_frame_equal(demo_prices(), demo_prices())
