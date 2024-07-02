import datetime


import datetime


class Document():
    """
    Represents a document with source file path, generated docs path, and other attributes.

    Args:
        source_file_path (str): The path of the source file.
        generated_docs_path (str): The path where the generated docs will be stored.
    """

    def __init__(self, source_file_path, generated_docs_path):
        self.source_file_path = source_file_path
        self.source_file_hash = self.get_hash(
            source_file_path) if source_file_path else None
        self.generated_docs_path = generated_docs_path
        self.generated_docs_hash = self.get_hash(
            generated_docs_path) if generated_docs_path else None
        self.created_on = self.__timestamp()

    def get_hash(self, value):
        return hash(value)

    def __timestamp(self):
        return datetime.datetime.now().isoformat()
