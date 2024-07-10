from cache.document import Document

"""
A simple cache to map project file paths to their respective documentation.
"""


class DocsCache():
    @staticmethod
    def from_dict(data: dict):
        cache = DocsCache()
        for key, value in data.items():
            cache.__cache[key] = Document.from_dict(value)
        return cache

    def __init__(self):
        self.__cache = {}

    def __str__(self) -> str:
        return str(self.__cache)

    def add(self, source_path, source_content, gen_docs_path):
        self.__cache[source_path] = Document(
            source_path, source_content, gen_docs_path)

    def get(self, key: str) -> Document:
        return self.__cache.get(key, None)

    def update_docs(self, path, content, gen_docs_path):
        assert path in self.__cache, f"{path} not found in cache"
        self.get(path).update(path, content, gen_docs_path)

    def remove(self, key: str):
        if key in self.__cache:
            del self.__cache[key]

    def clear(self):
        self.__cache.clear()

    def size(self) -> int:
        return len(self.__cache)

    def to_dict(self) -> dict:
        result = {}
        for key, value in self.__cache.items():
            result[key] = value.__dict__
        return result
