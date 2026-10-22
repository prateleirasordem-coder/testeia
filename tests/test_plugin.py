import io
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from testeia import AIPlugin, DemoProvider, RemoteProvider
from testeia.__main__ import main


class PluginTests(unittest.TestCase):
    def test_demo_is_explicit_and_trims_input(self):
        self.assertEqual(AIPlugin(DemoProvider()).run(' oi '),
                         '[DEMONSTRAÇÃO — sem IA real] Recebido: oi')

    def test_invalid_prompts_do_not_call_provider(self):
        provider = unittest.mock.Mock()
        for prompt in (' ', 'x' * 20001):
            with self.assertRaises(ValueError):
                AIPlugin(provider).run(prompt)
        provider.generate.assert_not_called()

    def test_configuration(self):
        for endpoint in ('', 'http://example.com', 'https://user:key@example.com',
                         'https://example.com?key=secret'):
            with self.assertRaises(ValueError):
                RemoteProvider(endpoint, 'model', 'secret')

    @patch('testeia.plugin.build_opener')
    def test_remote_contract(self, opener):
        response = opener.return_value.open.return_value.__enter__.return_value
        response.read.return_value = b'{"choices":[{"message":{"content":"Resposta"}}]}'
        provider = RemoteProvider('https://example.com/chat', 'model', 'secret')
        self.assertEqual(provider.generate('oi'), 'Resposta')
        request = opener.return_value.open.call_args.args[0]
        self.assertEqual(request.get_header('Authorization'), 'Bearer secret')
        self.assertIn(b'"role": "user"', request.data)
        self.assertEqual(opener.return_value.open.call_args.kwargs['timeout'], 30)

    @patch('testeia.plugin.build_opener')
    def test_invalid_response(self, opener):
        response = opener.return_value.open.return_value.__enter__.return_value
        for raw in (b'{}', b'bad json', b'x' * 1048577,
                    b'{"choices":[{"message":{"content":null}}]}'):
            response.read.return_value = raw
            with self.assertRaises(RuntimeError):
                RemoteProvider('https://example.com/chat', 'm', 'secret').generate('oi')

    @patch('testeia.plugin.build_opener')
    def test_errors_do_not_expose_provider_details(self, opener):
        for error in (HTTPError('https://example.com', 401, 'secret', {}, None),
                      URLError('secret'), TimeoutError('secret')):
            opener.return_value.open.side_effect = error
            with self.assertRaises(RuntimeError) as caught:
                RemoteProvider('https://example.com/chat', 'm', 'secret').generate('oi')
            self.assertNotIn('secret', str(caught.exception))

    @patch('sys.argv', ['testeia', ' '])
    @patch('sys.stderr', new_callable=io.StringIO)
    def test_cli_failure_exit(self, stderr):
        self.assertEqual(main(), 1)
        self.assertIn('Erro:', stderr.getvalue())


if __name__ == '__main__':
    unittest.main()
