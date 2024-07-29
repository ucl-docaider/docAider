import sys
import os
import json
import unittest
from unittest.mock import patch, mock_open, MagicMock

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), './../')))

from repo_documentation import utils
import repo_documentation.git_utils as git_utils

class TestUtils(unittest.TestCase):
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_prompt_debug(self, mock_file, mock_makedirs):
        utils.save_prompt_debug('output_dir', 'test.py',
                                'Prompt message', utils.Mode.CREATE)
        mock_makedirs.assert_called()
        mock_file.assert_called()

    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_response_debug(self, mock_file, mock_makedirs):
        utils.save_response_debug(
            'output_dir', 'test.py', 'Response message', utils.Mode.UPDATE)
        mock_makedirs.assert_called()
        mock_file.assert_called()

    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_write_file_docs(self, mock_file, mock_makedirs):
        path = utils.write_file_docs(
            'output_dir', 'root_folder', 'test.py', 'Docs content')
        mock_makedirs.assert_called()
        mock_file.assert_called()
        self.assertTrue(path.endswith('test.py.md'))

    def test_get_additional_docs_path(self):
        graph = {
            'func1': {'file_name': 'test.py', 'name': 'func1', 'content': 'def func1(): pass'},
            'func2': {'file_name': 'test.py', 'name': 'func2', 'content': 'def func2(): pass'},
            'EXTERNAL::print': {'file_name': 'EXTERNAL', 'name': 'print', 'content': ''}
        }
        bfs_explore = {'func1': ['func2'], 'func2': []}
        docs = utils.get_additional_docs_path('test.py', graph, bfs_explore)
        # Mock 
        docs += f'\nFunction/Class func2:\ndef func2(): pass\n'
        docs += f'\nFunction/Class func1:\ndef func1(): pass\n'
        
        self.assertIn('func1', docs)
        self.assertIn('func2', docs)
        self.assertNotIn('EXTERNAL::print', docs)

    def test_get_unified_diff(self):
        old_content = "Line 1\nLine 2\nLine 3"
        new_content = "Line 1\nLine 2 modified\nLine 3"
        diff = git_utils.get_unified_diff(old_content, new_content)
        self.assertIn('-Line 2', diff)
        self.assertIn('+Line 2 modified', diff)


if __name__ == '__main__':
    unittest.main()
