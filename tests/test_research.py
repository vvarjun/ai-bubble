import unittest
import numpy as np
import pandas as pd
from src.research import downside_study


class TestDownsideStudy(unittest.TestCase):
    def test_known_difference_and_reproducibility(self):
        market = np.linspace(-.05, .05, 100)
        data = pd.DataFrame({"market": market, "asset": market - .01})
        result = downside_study(data, "market", ["asset"], iterations=100)
        self.assertAlmostEqual(result["excess"], -.01)
        self.assertAlmostEqual(result["ci_low"], -.01)
        self.assertEqual(result["stress_days"], 10)
        self.assertEqual(result["ci_high"], downside_study(data, "market", ["asset"], iterations=100)["ci_high"])

    def test_rejects_small_sample_and_invalid_basket(self):
        data = pd.DataFrame({"market": [1.] * 10, "asset": [1.] * 10})
        with self.assertRaises(ValueError):
            downside_study(data, "market", ["asset"])
        with self.assertRaises(ValueError):
            downside_study(data, "market", ["market"])

class TestFactorsAndScenario(unittest.TestCase):
    def test_heldout_factor_fit_and_scenario(self):
        from src.research import factor_adjusted_comovement, revenue_shock
        rng = np.random.default_rng(2)
        factor = rng.normal(size=100)
        residual = rng.normal(size=100)
        frame = pd.DataFrame({'factor': factor, 'a': 2 * factor + residual, 'b': 3 * factor + residual}, index=pd.date_range('2020-01-01', periods=100))
        result = factor_adjusted_comovement(frame, ['factor'], ['a', 'b'])
        self.assertEqual(result['train_n'], 70)
        self.assertEqual(result['test_n'], 30)
        self.assertGreater(result['residual_mean'], .99)
        self.assertAlmostEqual(revenue_shock(.25, .20, .15)['second_loss'], .0075)
        with self.assertRaises(ValueError):
            revenue_shock(1.1, .2, .3)

    def test_rejects_constant_factor(self):
        from src.research import factor_adjusted_comovement
        frame = pd.DataFrame({'factor': [1.] * 100, 'a': range(100), 'b': range(100)})
        with self.assertRaises(ValueError):
            factor_adjusted_comovement(frame, ['factor'], ['a', 'b'])

class TestTokenStress(unittest.TestCase):
    def test_fixed_budget_caps_usage(self):
        from src.research import token_price_stress
        result = token_price_stress(1000, 5, 1, .2, 0)
        self.assertAlmostEqual(result['actual_tokens'], 500)
        self.assertAlmostEqual(result['spend'], 5000)
        self.assertTrue(result['budget_binding'])

    def test_planned_cut_can_bind_instead(self):
        from src.research import token_price_stress
        result = token_price_stress(1000, 5, 1, .6, 0)
        self.assertAlmostEqual(result['actual_tokens'], 400)
        self.assertAlmostEqual(result['spend'], 4000)
        self.assertFalse(result['budget_binding'])

    def test_invalid_inputs(self):
        from src.research import token_price_stress
        with self.assertRaises(ValueError):
            token_price_stress(0, 5, 1, .2, 0)
        with self.assertRaises(ValueError):
            token_price_stress(1000, 5, 1, 1.1, 0)
