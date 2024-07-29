import os
import sys
import unittest
from unittest.mock import patch
from datetime import datetime

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), './../')))

from cache.document import Document, sha256_hash
from cache import docs_cache

class TestDocsCache(unittest.TestCase):
    def setUp(self):
        self.cache = docs_cache.DocsCache()

    def test_add_and_get(self):
        self.cache.add("path/to/file.py", "content", "path/to/docs.md")
        doc = self.cache.get("path/to/file.py")
        self.assertIsInstance(doc, Document)
        self.assertEqual(doc.source_file_path, "path/to/file.py")
        self.assertEqual(doc.generated_docs_path, "path/to/docs.md")

    def test_update_docs_new(self):
        self.cache.update_docs("path/to/file.py", "content", "path/to/docs.md")
        doc = self.cache.get("path/to/file.py")
        self.assertIsInstance(doc, Document)
        self.assertEqual(doc.source_file_path, "path/to/file.py")

    def test_update_docs_existing(self):
        self.cache.add("path/to/file.py", "old_content", "path/to/old_docs.md")
        self.cache.update_docs(
            "path/to/file.py", "new_content", "path/to/new_docs.md")
        doc = self.cache.get("path/to/file.py")
        self.assertEqual(doc.generated_docs_path, "path/to/new_docs.md")
        self.assertEqual(doc.source_file_hash, sha256_hash("new_content"))

    def test_remove(self):
        self.cache.add("path/to/file.py", "content", "path/to/docs.md")
        self.cache.remove("path/to/file.py")
        self.assertIsNone(self.cache.get("path/to/file.py"))

    def test_clear(self):
        self.cache.add("path1.py", "content1", "docs1.md")
        self.cache.add("path2.py", "content2", "docs2.md")
        self.cache.clear()
        self.assertEqual(self.cache.size(), 0)

    def test_size(self):
        self.cache.add("path1.py", "content1", "docs1.md")
        self.cache.add("path2.py", "content2", "docs2.md")
        self.assertEqual(self.cache.size(), 2)

    def test_to_dict(self):
        self.cache.add("path.py", "content", "docs.md")
        cache_dict = self.cache.to_dict()
        self.assertIsInstance(cache_dict, dict)
        self.assertIn("path.py", cache_dict)
        self.assertIsInstance(cache_dict["path.py"], dict)

    def test_from_dict(self):
        test_dict = {
            "path.py": {
                "source_file_path": "path.py",
                "source_file_hash": "hash",
                "generated_docs_path": "docs.md",
                "modified_on": "2023-01-01T00:00:00"
            }
        }
        cache = docs_cache.DocsCache.from_dict(test_dict)
        self.assertIsInstance(cache, docs_cache.DocsCache)
        doc = cache.get("path.py")
        self.assertIsInstance(doc, Document)
        self.assertEqual(doc.source_file_path, "path.py")

    @patch('cache.document.datetime')
    def test_document_update(self, mock_datetime):
        mock_datetime.datetime.now.return_value = datetime(2023, 1, 1, 0, 0, 0)
        doc = Document("old_path.py", "old_content", "old_docs.md")
        doc.update("new_path.py", "new_content", "new_docs.md")
        self.assertEqual(doc.source_file_path, "new_path.py")
        self.assertEqual(doc.source_file_hash, sha256_hash("new_content"))
        self.assertEqual(doc.generated_docs_path, "new_docs.md")
        self.assertEqual(doc.modified_on, "2023-01-01T00:00:00")


if __name__ == '__main__':
    unittest.main()
