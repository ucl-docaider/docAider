import datetime
import hashlib

class Document():
    """
    Represents a document with source file path, generated docs path, and other attributes.

    Args:
        source_file_path (str): The path of the source file.
        generated_docs_path (str): The path where the generated docs will be stored.
    """

    @staticmethod
    def from_dict(data: dict):
        doc = Document(None, None, None)
        doc.source_file_path = data['source_file_path']
        doc.source_file_hash = data['source_file_hash']
        doc.generated_docs_path = data['generated_docs_path']
        doc.modified_on = data['modified_on']
        return doc

    def __init__(self, source_file_path, source_file_content, generated_docs_path):
        self.source_file_path = source_file_path
        self.source_file_hash = sha256_hash(source_file_content) if source_file_content else ''
        self.generated_docs_path = generated_docs_path
        self.modified_on = self.__timestamp()

    def __timestamp(self):
        return datetime.datetime.now().isoformat()
    
    def update(self, path, content, generated_docs_path):
        self.source_file_path = path
        self.source_file_hash = sha256_hash(content)
        self.generated_docs_path = generated_docs_path
        self.modified_on = self.__timestamp()
        print(f'Cache updated for {self.source_file_path} at {self.modified_on}')

def sha256_hash(content : str):
    return hashlib.sha256(content.encode('utf-8')).hexdigest()