import sys
import unittest
from unittest.mock import patch
import os

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), './../')))

from code2flow.code2flow import ast_utils

FunctionChangeType = ast_utils.FunctionChangeType
FunctionChange = ast_utils.FunctionChange
filter_changes = ast_utils.filter_changes
get_function_changes = ast_utils.get_function_changes
_get_all_functions_from_content = ast_utils._get_all_functions_from_content
_get_all_functions_from_file = ast_utils._get_all_functions_from_file
_get_similarity = ast_utils._get_similarity


class TestFunctionChangeAnalyzer(unittest.TestCase):

    def setUp(self):
        self.sample_changes = [
            FunctionChange('func1', FunctionChangeType.EQUAL, 1.0),
            FunctionChange('func2', FunctionChangeType.UPDATED, 0.8),
            FunctionChange('func3', FunctionChangeType.REMOVED, 0),
            FunctionChange('func4', FunctionChangeType.ADDED, 0),
            FunctionChange('func5', FunctionChangeType.RENAMED, 0.9),
        ]

    def test_function_change_str(self):
        self.assertEqual(
            str(self.sample_changes[0]), "Function func1 has no changes.")
        self.assertEqual(str(
            self.sample_changes[1]), "Function func2 has been updated with similarity of 80.0%.")
        self.assertEqual(
            str(self.sample_changes[2]), "Function func3 has been removed.")
        self.assertEqual(
            str(self.sample_changes[3]), "Function func4 has been added.")
        self.assertEqual(str(
            self.sample_changes[4]), "Function func5 has been renamed with similarity of 90.0%")

    def test_filter_changes(self):
        filtered = filter_changes(self.sample_changes)
        self.assertEqual(filtered, ['func2'])

    @patch('code2flow.code2flow.ast_utils._get_all_functions_from_content')
    def test_get_function_changes(self, mock_get_functions):
        old_functions = {'func1': 'def func1():\n    pass',
                         'func2': 'def func2():\n    return 1'}
        new_functions = {'func1': 'def func1():\n    pass',
                         'func2': 'def func2():\n    return 2', 'func3': 'def func3():\n    pass'}
        mock_get_functions.side_effect = [old_functions, new_functions]

        changes = get_function_changes('test.py', 'old_content', 'new_content')

        self.assertEqual(len(changes), 3)
        self.assertEqual(changes[0].name, 'func1')
        self.assertEqual(changes[0].type, FunctionChangeType.EQUAL)
        self.assertEqual(changes[1].name, 'func2')
        self.assertEqual(changes[1].type, FunctionChangeType.UPDATED)
        self.assertEqual(changes[2].name, 'func3')
        self.assertEqual(changes[2].type, FunctionChangeType.ADDED)

    @patch('code2flow.code2flow.ast_utils.generate_graph')
    @patch('code2flow.code2flow.ast_utils.get_call_graph')
    def test_get_all_functions_from_file(self, mock_get_call_graph, mock_generate_graph):
        mock_get_call_graph.return_value = {
            'func1': {'name': 'func1', 'content': 'def func1():\n    pass'},
            'func2': {'name': 'func2', 'content': 'def func2():\n    return 1'},
            'EXTERNAL::print': {'name': 'EXTERNAL::print', 'content': ''}
        }

        result = _get_all_functions_from_file('test.py')

        self.assertEqual(len(result), 2)
        self.assertIn('func1', result)
        self.assertIn('func2', result)
        self.assertNotIn('EXTERNAL::print', result)

    def test_get_similarity(self):
        a = "def func():\n    return 1"
        b = "def func():\n    return 2"
        similarity = _get_similarity(a, b)
        self.assertGreater(similarity, 0.8)
        self.assertLess(similarity, 1.0)

    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('code2flow.code2flow.ast_utils._get_all_functions_from_file')
    def test_get_all_functions_from_content(self, mock_get_functions, mock_open):
        mock_get_functions.return_value = {
            'func1': 'content1', 'func2': 'content2'}

        result = _get_all_functions_from_content('test.py', 'file content')

        mock_open.assert_called_once_with('./tmp/test.py', 'w')
        mock_open().write.assert_called_once_with('file content')
        self.assertEqual(result, {'func1': 'content1', 'func2': 'content2'})


if __name__ == '__main__':
    unittest.main()
