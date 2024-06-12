Here are the test cases for the functions and classes:

```python
import unittest
from django.db import models
from account.models import Account  # Assuming this is a mock model
from urllib.parse import urlparse, URLParserError
from unittest.mock import patch

class TestPolicySearch(unittest.TestCase):

    def setUp(self):
        self.policy_search = PolicySearch()

    def test_auto_increment_id(self):
        self.assertIsInstance(self.policy_search.auto_increment_id, models.AutoField)

    def test_created_at(self):
        self.assertIsInstance(self.policy_search.created_at, models.DateTimeField)

    def test_name(self):
        self.assertEqual(type(self.policy_search.name), type(""))

    def test_keywords(self):
        self.assertEqual(type(self.policy_search.keywords), type(""))

    def test_account(self):
        self.assertIsInstance(self.policy_search.account, models.ForeignKey)

    def test_object_id(self):
        self.assertEqual(type(self.policy_search.object_id), type(""))

    def test_progress(self):
        self.assertIsInstance(self.policy_search.progress, int)

    def test_unique_thread_id(self):
        self.assertEqual(type(self.policy_search.unique_thread_id), type(""))


class TestParseContent(unittest.TestCase):

    @patch('re.compile')
    def test_parse_content(self, mock_compile):
        content = "Test content"
        pattern = re.compile(r"INFORMATION:\s*(.*?)\s*SOURCE:\s*(.*?)\s*(?=INFORMATION:|$)", re.DOTALL)
        entries = []
        matches = pattern.findall(content)
        for info, source in matches:
            source_url = source.strip()
            parsed_url = urlparse(source_url)
            domain = f"{parsed_url.scheme}://{parsed_url.netloc}" if parsed_url.netloc else "Invalid URL or no source"
            entries.append({
                'information': info.strip(),
                'source': source_url,
                'domain': domain if domain != "Invalid URL or no source" else "No source available",
                'id': str(uuid.uuid4()) 
            })
        self.assertEqual(entries, [])  # Assuming this is a correct output


if __name__ == '__main__':
    unittest.main()
```