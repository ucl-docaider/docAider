import os


def read_file_content(file_path):
    with open(file_path, 'r') as file:
        return file.read()
    
def write_file_docs(root_folder, file_path, output_directory, docs) -> str:
    # Generate the output file path based on the input file path
    relative_path = os.path.relpath(file_path, root_folder)
    output_file_path = os.path.join(output_directory, relative_path)
    output_dir = os.path.dirname(output_file_path)
    os.makedirs(output_dir, exist_ok=True)
    output_file_path = os.path.join(root_folder, output_dir, file_path)
    
    # Add .md extension to the output file
    output_file_path += ".md"
    
    # Write the documentation to the output file
    with open(output_file_path, 'w') as file:
        file.write(docs)
    
    print(f"Updated documentation written to: {output_file_path}")
    return output_file_path