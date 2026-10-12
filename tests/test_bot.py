import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from bot import load_configs, prepare_messages, publish_once, read_state, channel_footer

VLESS = 'vless://uuid@a.example:443?security=reality&encryption=none#name'
TROJAN = 'trojan://pw@b.example:443?security=tls#server'


class BotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)
        self.configs_path = self.path / 'configs.txt'
        self.state_path = self.path / 'state.json'
        self.configs_path.write_text('\n'.join([VLESS, TROJAN,
                                                'vless://id@c.example:443',
                                                'vless://id@d.example:443',
                                                'vless://id@e.example:443']) + '\n', encoding='utf-8')

    def publish(self, now=1200, client=None, **kwargs):
        return publish_once(configs_path=self.configs_path, state_path=self.state_path,
                            channel='@example', token='fake', now=now,
                            client=client or MagicMock(), **kwargs)

    def test_dry_run_does_not_write_state(self):
        result = self.publish(dry_run=True)
        self.assertEqual((result['status'], result['count']), ('preview', 1))
        self.assertFalse(self.state_path.exists())

    def test_one_post_and_wait_at_least_11_minutes(self):
        client = MagicMock()
        self.assertEqual(self.publish(client=client)['count'], 1)
        self.assertEqual(self.publish(now=1200+659, client=client)['status'], 'skipped_wait')
        self.assertEqual(self.publish(now=1200+660, client=client)['count'], 1)
        self.assertEqual(client.send_message.call_count, 2)
        self.assertEqual(read_state(self.state_path)['cursor'], 2)

    def test_cron_hour_boundary_does_not_send_at_five_minutes(self):
        client = MagicMock()
        self.publish(now=55*60, client=client)
        self.assertEqual(self.publish(now=60*60, client=client)['status'], 'skipped_wait')
        self.assertEqual(self.publish(now=71*60, client=client)['count'], 1)
        self.assertEqual(client.send_message.call_count, 2)

    def test_one_link_per_post_without_inline_button(self):
        infos, _ = load_configs(self.configs_path)
        one = prepare_messages(infos[:1], [101], '@example')[0]
        self.assertEqual(one['parse_mode'], 'HTML')
        self.assertIn('<pre>', one['text'])
        self.assertIn('&amp;', one['text'])
        self.assertIn('#V2Ray', one['text'])
        self.assertIn('#کانفیگ_رایگان', one['text'])
        self.assertIn('https://t.me/example', one['text'])
        self.assertNotIn('reply_markup', one)
        self.assertNotIn(TROJAN, one['text'])

    def test_long_link_works_without_256_char_button(self):
        link = 'vless://uuid@a.example:443?x=' + 'a' * 400
        self.configs_path.write_text(link, encoding='utf-8')
        infos, _ = load_configs(self.configs_path)
        msg = prepare_messages(infos, [101], '@example')[0]
        self.assertIn(link, msg['text'])
        self.assertNotIn('reply_markup', msg)

    def test_invalid_channel_handle_not_used_in_link(self):
        self.assertNotIn('https://', channel_footer('-100111000'))

    def test_failed_send_does_not_advance_state(self):
        client = MagicMock()
        client.send_message.side_effect = RuntimeError('simulated failure')
        with self.assertRaises(RuntimeError):
            self.publish(client=client)
        self.assertFalse(self.state_path.exists())

    def test_missing_token(self):
        with self.assertRaisesRegex(ValueError, 'BOT_TOKEN'):
            publish_once(configs_path=self.configs_path, state_path=self.state_path,
                         channel='@example', token=None, now=1200)

    def test_refresh_configs_without_code_change(self):
        client = MagicMock()
        for i in range(5):
            self.publish(now=1200+660*i, client=client)
        latest = 'vless://id@fresh.example:443?security=tls#new'
        with self.configs_path.open('a', encoding='utf-8') as f:
            f.write(latest + '\n')
        self.publish(now=1200+660*5, client=client)
        self.assertIn(latest, client.send_message.call_args[0][0]['text'])

    def test_no_repeats_until_all_posted(self):
        links = [f'vless://id@node{i}.example:443' for i in range(100)]
        self.configs_path.write_text('\n'.join(links), encoding='utf-8')
        client = MagicMock()
        for i in range(100):
            self.publish(now=660*(i+1), client=client)
        self.assertEqual(len(read_state(self.state_path)['posted_ids']), 100)
        self.assertEqual(client.send_message.call_count, 100)
        self.publish(now=660*101, client=client)
        self.assertEqual(len(read_state(self.state_path)['posted_ids']), 1)
        self.assertEqual(client.send_message.call_count, 101)

    def test_old_state_migrates_without_losing_history(self):
        old_id = hashlib.sha256(VLESS.encode()).hexdigest()[:24]
        old = {"cursor": 1, "last_slot": 111, "slot_sent": 3, "posted_ids": [old_id]}
        self.state_path.write_text(json.dumps(old), encoding='utf-8')
        self.assertEqual(read_state(self.state_path)['last_sent_at'], None)
        client = MagicMock()
        self.publish(now=90000, client=client)
        self.assertIn(TROJAN, client.send_message.call_args[0][0]['text'])

    def test_corrupt_state_fails_closed(self):
        self.state_path.write_text('{bad json', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Invalid state'):
            self.publish()

    def test_invalid_config_raises(self):
        self.configs_path.write_text('not a link\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'No structurally valid'):
            self.publish()


if __name__ == '__main__':
    unittest.main()
