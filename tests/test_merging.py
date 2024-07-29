import re
import sys
import unittest
from unittest.mock import patch, mock_open
import os

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), './../')))

from repo_documentation.merging import merger

class TestDocumentationGenerator(unittest.TestCase):

    def setUp(self):
        self.sample_files = [
            ('root', 'file1.md'),
            ('root/folder1', 'file2.md'),
            ('root/folder1/subfolder', 'file3.md'),
        ]
        self.sample_tree = {
            'files': ['file1.md'],
            'folder1': {
                'files': ['file2.md'],
                'subfolder': {
                    'files': ['file3.md']
                }
            }
        }

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.walk')
    @patch('repo_documentation.merging.merger.get_table_of_contents')
    @patch('repo_documentation.merging.merger.get_documentation_content')
    def test_create_documentation(self, mock_get_content, mock_get_toc, mock_walk, mock_file):
        mock_walk.return_value = [
            ('root', [], ['file1.md']),
            ('root/folder1', [], ['file2.md']),
            ('root/folder1/subfolder', [], ['file3.md'])
        ]
        mock_get_toc.return_value = "<ul><li>Sample TOC</li></ul>"
        mock_get_content.return_value = "<div>Sample Content</div>"

        merger.create_documentation('docs_folder')

        mock_file.assert_called()
        mock_get_toc.assert_called()
        mock_get_content.assert_called()

    def test_create_file_card(self):
        file_path = "folder/file.md"
        docs = "<p>Sample content</p>"
        result = merger.create_file_card(file_path, docs)
        self.assertIn('<div class="file-card"', result)
        self.assertIn('<summary id=folder-file>', result)
        self.assertIn('<span class="title">folder/file</span>', result)
        self.assertIn('<span class="actions">', result)
        self.assertIn('<button onclick="copyFileContents', result)
        self.assertIn('<button onclick="closeFileCard', result)

    def test_get_table_of_contents(self):
        result = merger.get_table_of_contents(self.sample_tree)
        self.assertIn('<ul>', result)
        self.assertIn('📁 folder1', result)
        self.assertIn('🐍 file1', result)
        self.assertIn('🐍 file2', result)
        self.assertIn('🐍 file3', result)

    def test_clean_path(self):
        path = "folder\\subfolder/file.md"
        result = merger.clean_path(path)
        self.assertEqual(result, "folder-subfolder-file")

    @patch('builtins.open', new_callable=mock_open, read_data="# Test\nContent")
    @patch('markdown.markdown', return_value="<h1>Test</h1><p>Content</p>")
    def test_get_documentation_content(self, mock_markdown, mock_file):
        result = merger.get_documentation_content(self.sample_files)
        # Assert that <div class="file-docs"> is there 3 times
        regex_match = re.findall(
            r'<div class=\"file-card\" id=\"file-file[0-9]\">', result)
        self.assertEqual(len(regex_match), 3)

    def test_to_tree(self):
        files = [
            'file1.md',
            'folder1\\file2.md',
            'folder1\\subfolder\\file3.md'
        ]
        result = merger.to_tree(files)
        self.assertEqual(result, self.sample_tree)


if __name__ == '__main__':
    unittest.main()
