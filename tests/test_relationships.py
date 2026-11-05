import unittest
from pathlib import Path
import pandas as pd


class TestRelationshipInventory(unittest.TestCase):
    def test_evidence_has_unique_ids_and_sources(self):
        path = Path(__file__).resolve().parents[1] / 'data/research/relationships.csv'
        data = pd.read_csv(path)
        self.assertTrue(data['id'].is_unique)
        self.assertTrue(data['source_url'].str.startswith('https://').all())
        self.assertTrue(pd.to_datetime(data['disclosure_date'], errors='coerce').notna().all())
        self.assertTrue(data[['from_entity', 'to_entity', 'relationship_type', 'status']].notna().all().all())

    def test_historical_and_amended_microsoft_commitment_are_distinct(self):
        data = pd.read_csv(Path(__file__).resolve().parents[1] / 'data/research/relationships.csv').set_index('id')
        self.assertEqual(data.loc['R005', 'status'], 'superseded_historical')
        self.assertEqual(data.loc['R007', 'amount_usd'], 44_900_000_000)
        self.assertEqual(data.loc['R012', 'status'], 'conditional')
