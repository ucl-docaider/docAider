import sys
import os
import unittest

from unittest.mock import Mock, patch
from autogen import AssistantAgent, UserProxyAgent

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), './../')))

from autogen_utils import utils as autogen_utils

class TestAutogenUtils(unittest.TestCase):
    def setUp(self):
        self.user = Mock(spec=UserProxyAgent)
        self.assistant = Mock(spec=AssistantAgent)
        self.output_dir = '/tmp/test_output'
        self.root_folder = '/test/root'

    @patch('autogen_utils.utils.initiate_chat')
    def test_get_documentation(self, mock_initiate_chat):
        file_path = '/test/file.py'
        file_content = 'print("Hello, World!")'
        additional_docs = 'Some additional docs'

        self.assistant.last_message.return_value = {'content': '\nTest docs\n'}

        result = autogen_utils.get_documentation(
            file_path=file_path,
            file_content=file_content,
            additional_docs=additional_docs,
            user=self.user,
            assistant=self.assistant,
            output_dir=self.output_dir,
            root_folder=self.root_folder,
            save_debug=True
        )
        self.assertEqual(result, 'Test docs')

    @patch('autogen_utils.utils.initiate_chat')
    def test_get_updated_documentation(self, mock_initiate_chat):
        file_path = '/test/file.py'
        old_file_docs = 'Old docs'
        old_file_content = 'Old content'
        new_file_content = 'New content'
        diff = 'Some diff'
        additional_docs = 'Additional docs'
        changes = 'Some changes'

        self.assistant.last_message.return_value = {'content': 'Updated docs'}

        result = autogen_utils.get_updated_documentation(
            file_path=file_path,
            old_file_docs=old_file_docs,
            old_file_content=old_file_content,
            new_file_content=new_file_content,
            diff=diff,
            additional_docs=additional_docs,
            changes=changes,
            user=self.user,
            assistant=self.assistant,
            output_dir=self.output_dir,
            save_debug=True
        )
        self.assertEqual(result, 'Updated docs')

    @patch('autogen_utils.utils.initiate_chat')
    def test_get_updated_parent_documentation(self, mock_initiate_chat):
        file_path = '/test/parent.py'
        updated_functions = {'func1': 'Updated content'}
        additional_docs = 'Additional docs'
        new_content = 'New parent content'
        functions = 'func1, func2'
        parent_content = 'Old parent content'
        old_parent_docs = 'Old parent docs'

        self.assistant.last_message.return_value = {
            'content': 'Updated parent docs'}

        result = autogen_utils.get_updated_parent_documentation(
            file_path, updated_functions, additional_docs, new_content, functions,
            parent_content, old_parent_docs, self.user, self.assistant, self.output_dir, save_debug=True
        )

        self.assertEqual(result, 'Updated parent docs')

    @patch('autogen_utils.utils.initiate_chat')
    def test_get_updated_commit_documentation(self, mock_initiate_chat):
        file_path = '/test/file.py'
        comment = 'Update documentation'
        file_content = 'Current file content'
        old_file_docs = 'Old file docs'

        self.assistant.last_message.return_value = {
            'content': 'Updated commit docs'}

        result = autogen_utils.get_updated_commit_documentation(
            file_path, comment, file_content, old_file_docs,
            self.user, self.assistant, self.output_dir, save_debug=True
        )

        self.assertEqual(result, 'Updated commit docs')


if __name__ == '__main__':
    unittest.main()
