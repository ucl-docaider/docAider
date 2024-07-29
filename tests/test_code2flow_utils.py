import os
import sys
import unittest
from unittest.mock import patch

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), './../')))

from code2flow.code2flow import utils

class TestCallGraphUtils(unittest.TestCase):
    def setUp(self):
        self.sample_graph = {
            'func1': {'file_name': 'file1.py', 'callers': [], 'callees': ['func2', 'func3']},
            'func2': {'file_name': 'file1.py', 'callers': ['func1'], 'callees': ['func4']},
            'func3': {'file_name': 'file2.py', 'callers': ['func1'], 'callees': []},
            'func4': {'file_name': 'file2.py', 'callers': ['func2'], 'callees': []},
            'EXTERNAL::dict': {'file_name': 'EXTERNAL', 'callers': [], 'callees': []}
        }

    @patch('code2flow.code2flow.utils.__load_json')
    def test_get_cache(self, mock_load_json):
        mock_load_json.return_value = {'cache': 'data'}
        result = utils.get_cache('output')
        self.assertEqual(result, {'cache': 'data'})
        mock_load_json.assert_called_once_with('output/cache.json')

    @patch('code2flow.code2flow.utils.__load_json')
    def test_get_call_graph(self, mock_load_json):
        mock_load_json.return_value = self.sample_graph
        result = utils.get_call_graph('output')
        self.assertEqual(result, self.sample_graph)
        mock_load_json.assert_called_once_with('output/call_graph.json')

    def test_get_file_to_functions(self):
        expected = {
            'file1.py': ['func1', 'func2'],
            'file2.py': ['func3', 'func4'],
            'EXTERNAL': ['EXTERNAL::dict']
        }
        result = utils.get_file_to_functions(self.sample_graph)
        self.assertEqual(result, expected)

    def test_explore_call_graph(self):
        expected = {
            'func1': {'func2': {'func4': {}}, 'func3': {}},
            'func2': {'func4': {}},
            'func3': {},
            'func4': {}
        }
        result = utils.explore_call_graph(self.sample_graph, depth=3)
        self.assertEqual(result, expected)

    def test_get_parent_dependencies(self):
        matched_functions = ['func3', 'func4']
        expected = {'file1.py': ['func1', 'func2']}
        result = utils.get_parent_dependencies(self.sample_graph, matched_functions, 'file2.py')
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()