import tempfile
import unittest
from pathlib import Path
from research_agents import AGENTS,init_db,latest,parse_feed
class ResearchTests(unittest.TestCase):
    def test_roster(self):
        self.assertGreaterEqual(len(AGENTS),10)
        self.assertEqual(len({a["id"] for a in AGENTS}),len(AGENTS))
    def test_rss(self):
        xml=b'<rss><channel><item><title>Market study</title><link>https://example.org/study</link></item></channel></rss>'
        items=parse_feed(xml,"Test")
        self.assertEqual(len(items),1)
        self.assertEqual(items[0]["title"],"Market study")
    def test_http_rejected(self):
        xml=b'<rss><channel><item><title>Bad</title><link>http://example.org/</link></item></channel></rss>'
        self.assertEqual(parse_feed(xml,"Test"),[])
    def test_db(self):
        with tempfile.TemporaryDirectory() as d:
            path=str(Path(d)/"research.sqlite3")
            init_db(path)
            self.assertEqual(latest(path),[])
if __name__=="__main__": unittest.main()
