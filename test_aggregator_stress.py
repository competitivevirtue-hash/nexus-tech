#!/usr/bin/env python3
"""
nexus-tech/test_aggregator_stress.py
QA Stress-test suite for the Nexus Tech & Gaming Aggregator Daemon.
Verifies that the daemon behaves cleanly under exceptions, returning empty lists and exiting properly.
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
        """Verify that timeouts return empty lists rather than raising crashes or returning fallbacks."""
        mock_get.side_effect = requests.exceptions.Timeout("API request timed out")
        
        # Test TechCrunch
        tc = aggregator_daemon.fetch_techcrunch_feed()
        self.assertEqual(len(tc), 0)
        
        # Test SEC
        sec = aggregator_daemon.fetch_sec_feed()
        self.assertEqual(len(sec), 0)
        
        # Test Steam
        steam = aggregator_daemon.fetch_steam_feed()
        self.assertEqual(len(steam), 0)
        
        # Test Reddit
        reddit = aggregator_daemon.fetch_reddit_feed()
        self.assertEqual(len(reddit), 0)
        
        # Test Wccftech
        wccf = aggregator_daemon.fetch_wccftech_feed()
        self.assertEqual(len(wccf), 0)

    @patch('requests.get')
    def test_rate_limiting_handling_429_and_403(self, mock_get):
        """Verify that 429 and 403 status codes result in empty lists."""
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        mock_resp.content = b"Too Many Requests"
        mock_get.return_value = mock_resp
        
        tc = aggregator_daemon.fetch_techcrunch_feed()
        self.assertEqual(len(tc), 0)
        
        mock_resp.status_code = 403
        mock_resp.content = b"Forbidden"
        sec = aggregator_daemon.fetch_sec_feed()
        self.assertEqual(len(sec), 0)

    @patch('requests.get')
    def test_empty_payload_handling(self, mock_get):
        """Verify that empty feed payloads result in empty lists gracefully."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        
        # 1. TechCrunch: Empty XML
        mock_resp.content = b"<rss><channel></channel></rss>"
        mock_get.return_value = mock_resp
        tc = aggregator_daemon.fetch_techcrunch_feed()
        self.assertEqual(len(tc), 0)
        
        # 2. SEC: Empty Atom XML
        mock_resp.content = b"<feed></feed>"
        mock_get.return_value = mock_resp
        sec = aggregator_daemon.fetch_sec_feed()
        self.assertEqual(len(sec), 0)
        
        # 3. Steam: Empty JSON
        mock_resp.json.return_value = {}
        mock_get.return_value = mock_resp
        steam = aggregator_daemon.fetch_steam_feed()
        self.assertEqual(len(steam), 0)
        
        # 4. Reddit: Empty children
        mock_resp.json.return_value = {"data": {"children": []}}
        mock_get.return_value = mock_resp
        reddit = aggregator_daemon.fetch_reddit_feed()
        self.assertEqual(len(reddit), 0)

    @patch('requests.get')
    def test_empty_tags_in_xml(self, mock_get):
        """Verify that XML feeds containing elements with empty text fields are skipped and return empty lists."""
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
        self.assertEqual(len(tc), 0)
        
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
        self.assertEqual(len(sec), 0)

    @patch('requests.get')
    def test_full_pipeline_failure_exit(self, mock_get):
        """Ensure that if all network operations fail, the main compiler pipeline aborts with SystemExit."""
        mock_get.side_effect = requests.exceptions.Timeout("All network calls timed out")
        
        # Verify main() raises SystemExit due to empty feeds guard
        import io
        from contextlib import redirect_stdout
        f = io.StringIO()
        with redirect_stdout(f):
            with self.assertRaises(SystemExit) as cm:
                aggregator_daemon.main()
            self.assertEqual(cm.exception.code, 1)


if __name__ == '__main__':
    unittest.main()
