#!/usr/bin/env python3
"""
nexus-tech/test_aggregator_stress.py
QA Stress-test suite for the Nexus Tech & Gaming Aggregator Daemon.
Verifies graceful fallbacks and exception safety for timeouts, rate-limits, and empty payloads.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import requests

# Set working directory to allow local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import aggregator_daemon


class TestAggregatorStress(unittest.TestCase):

    def setUp(self):
        # Change directory to the script's directory so file paths align
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

    @patch('requests.get')
    def test_timeout_handling(self, mock_get):
        """Verify that timeouts trigger fallbacks for all endpoints without crashing."""
        mock_get.side_effect = requests.exceptions.Timeout("API request timed out")
        
        # Test TechCrunch
        tc = aggregator_daemon.fetch_techcrunch_feed()
        self.assertTrue(len(tc) > 0)
        self.assertEqual(tc[0]['title'], "Quantum Interlinks Go Live in Sub-2nm Computing Core Centers")
        
        # Test SEC
        sec = aggregator_daemon.fetch_sec_feed()
        self.assertTrue(len(sec) > 0)
        self.assertIn("Berkshire Hathaway", sec[0]['title'])
        
        # Test Steam
        steam = aggregator_daemon.fetch_steam_feed()
        self.assertTrue(len(steam) > 0)
        self.assertIn("Cyberpunk 2078", steam[0]['title'])
        
        # Test Reddit
        reddit = aggregator_daemon.fetch_reddit_feed()
        self.assertTrue(len(reddit) > 0)
        self.assertIn("GTA VI", reddit[0]['title'])
        
        # Test Wccftech
        wccf = aggregator_daemon.fetch_wccftech_feed()
        self.assertTrue(len(wccf) > 0)
        self.assertIn("Next-Gen Console Showcase", wccf[0]['title'])
        
        # Test YouTube
        yt = aggregator_daemon.fetch_youtube_feed()
        self.assertTrue(len(yt) > 0)
        self.assertIn("Elden Ring", yt[0]['title'])

    @patch('requests.get')
    def test_rate_limiting_handling_429_and_403(self, mock_get):
        """Verify that 429 and 403 status codes trigger fallbacks correctly."""
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        mock_resp.content = b"Too Many Requests"
        mock_get.return_value = mock_resp
        
        tc = aggregator_daemon.fetch_techcrunch_feed()
        self.assertTrue(len(tc) > 0)
        self.assertEqual(tc[0]['title'], "Quantum Interlinks Go Live in Sub-2nm Computing Core Centers")
        
        mock_resp.status_code = 403
        mock_resp.content = b"Forbidden"
        sec = aggregator_daemon.fetch_sec_feed()
        self.assertTrue(len(sec) > 0)
        self.assertIn("Berkshire Hathaway", sec[0]['title'])

    @patch('requests.get')
    def test_empty_payload_handling(self, mock_get):
        """Verify that empty feed payloads (empty lists or tags) fall back gracefully."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        
        # 1. TechCrunch: Empty XML
        mock_resp.content = b"<rss><channel></channel></rss>"
        mock_get.return_value = mock_resp
        tc = aggregator_daemon.fetch_techcrunch_feed()
        self.assertTrue(len(tc) > 0)
        
        # 2. SEC: Empty Atom XML
        mock_resp.content = b"<feed></feed>"
        mock_get.return_value = mock_resp
        sec = aggregator_daemon.fetch_sec_feed()
        self.assertTrue(len(sec) > 0)
        
        # 3. Steam: Empty JSON
        mock_resp.json.return_value = {}
        mock_get.return_value = mock_resp
        steam = aggregator_daemon.fetch_steam_feed()
        self.assertTrue(len(steam) > 0)
        
        # 4. Reddit: Empty children
        mock_resp.json.return_value = {"data": {"children": []}}
        mock_get.return_value = mock_resp
        reddit = aggregator_daemon.fetch_reddit_feed()
        self.assertTrue(len(reddit) > 0)
        
        # 5. YouTube: Empty XML
        mock_resp.content = b"<feed></feed>"
        mock_get.return_value = mock_resp
        yt = aggregator_daemon.fetch_youtube_feed()
        self.assertTrue(len(yt) > 0)

    @patch('requests.get')
    def test_empty_tags_in_xml(self, mock_get):
        """Verify that XML feeds containing elements with empty text fields do not cause crashes."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        
        # TechCrunch with empty title/link/description text
        mock_resp.content = b"""<rss version="2.0">
            <channel>
                <item>
                    <title></title>
                    <link></link>
                    <description></description>
                    <pubDate></pubDate>
                </item>
            </channel>
        </rss>"""
        mock_get.return_value = mock_resp
        tc = aggregator_daemon.fetch_techcrunch_feed()
        self.assertTrue(len(tc) > 0)
        self.assertIsNotNone(tc[0]['title'])
        self.assertIsNotNone(tc[0]['link'])
        self.assertIsNotNone(tc[0]['summary'])
        
        # SEC EDGAR with empty titles and missing links
        mock_resp.content = b"""<feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <title></title>
                <link href="" />
                <summary></summary>
            </entry>
        </feed>"""
        mock_get.return_value = mock_resp
        sec = aggregator_daemon.fetch_sec_feed()
        self.assertTrue(len(sec) > 0)
        self.assertIsNotNone(sec[0]['title'])
        self.assertIsNotNone(sec[0]['link'])

    @patch('requests.get')
    def test_full_pipeline_success(self, mock_get):
        """Ensure that even if all network operations fail, the main compiler pipeline completes successfully."""
        mock_get.side_effect = requests.exceptions.Timeout("All network calls timed out")
        
        # Verify execution does not raise exceptions
        try:
            # Redirect stdout to suppress print logs in test output
            import io
            from contextlib import redirect_stdout
            f = io.StringIO()
            with redirect_stdout(f):
                aggregator_daemon.main()
        except Exception as e:
            self.fail(f"aggregator_daemon.main() failed with an exception under stress mock conditions: {e}")


if __name__ == '__main__':
    unittest.main()
