import datetime


class Document():
    """
    Represents a document with source file path, generated docs path, and other attributes.

    Args:
        source_file_path (str): The path of the source file.
        generated_docs_path (str): The path where the generated docs will be stored.
    """

    @staticmethod
    def from_dict(data: dict):
        doc = Document(None, None)
        doc.source_file_path = data['source_file_path']
        doc.source_file_hash = data['source_file_hash']
        doc.generated_docs_path = data['generated_docs_path']
        doc.generated_docs_hash = data['generated_docs_hash']
        doc.modified_on = data['modified_on']
        return doc

    def __init__(self, source_file_path, generated_docs_path):
        self.source_file_path = source_file_path
        self.source_file_hash = self.__get_file_content_hash(
            source_file_path) if source_file_path else None
        self.generated_docs_path = generated_docs_path
        self.generated_docs_hash = self.__get_file_content_hash(
            generated_docs_path) if generated_docs_path else None
        self.modified_on = self.__timestamp()

    def __get_file_content_hash(self, file_path):
        return hash(self.__read_file_content(file_path))

    def __timestamp(self):
        return datetime.datetime.now().isoformat()

    def __read_file_content(self, file_path):
        with open(file_path, 'r') as file:
            return file.read()

    def update_path(self, path):
        self.generated_docs_path = path
        self.generated_docs_hash = self.__get_file_content_hash(path)
        self.modified_on = self.__timestamp()
        print(f'Cache updated for {self.source_file_path} at {self.modified_on}')
