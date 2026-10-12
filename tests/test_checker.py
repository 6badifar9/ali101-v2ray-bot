import base64
import json
import unittest
from unittest.mock import patch

from checker import parse_config, select_configs, test_config, tcp_reachable


class CheckerTests(unittest.TestCase):
    def test_vless(self):
        info = parse_config('vless://11111111-1111-1111-1111-111111111111@example.org:443?security=reality#test')
        self.assertEqual((info.protocol, info.host, info.port), ('VLESS', 'example.org', 443))

    def test_trojan(self):
        info = parse_config('trojan://password@example.com:8443?security=tls')
        self.assertEqual(info.port, 8443)

    def test_vmess_base64(self):
        vmess = {'v': '2', 'ps': 'test', 'add': 'example.net', 'port': '443', 'id': 'uuid'}
        payload = base64.urlsafe_b64encode(json.dumps(vmess).encode()).decode().rstrip('=')
        self.assertEqual(parse_config('vmess://' + payload).host, 'example.net')

    def test_bad_links(self):
        invalid = ['random', 'http://example.com', 'vless://@example.org:443',
                   'vless://id@example.com:70000', 'vmess://!',
                   'trojan://pass@example.com:0', 'vless://id@example.com:443\nextra']
        for raw in invalid:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                parse_config(raw)
            self.assertFalse(test_config(raw))

    def test_dedup_and_stats(self):
        link = 'vless://id@example.com:443'
        valid, stats = select_configs(['#comment', '', link, link, 'bad', 'trojan://pass@other.test:443'])
        self.assertEqual(len(valid), 2)
        self.assertEqual(stats, {'invalid': 1, 'duplicates': 1, 'unreachable': 0})

    def test_optional_port_check(self):
        with patch('checker.tcp_reachable', return_value=False):
            valid, stats = select_configs(['vless://id@node.test:443'], check_tcp=True)
        self.assertEqual(valid, [])
        self.assertEqual(stats['unreachable'], 1)


if __name__ == '__main__':
    unittest.main()
