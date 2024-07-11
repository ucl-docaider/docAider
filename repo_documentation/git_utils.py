import difflib
import os


def get_latest_commit_sha(repo, branch):
    """
    Get the SHA of the latest commit on the specified branch.
    Raises exception if the specified branch is not found in the repository.
    """
    if branch not in repo.heads:
        raise Exception(
            f'Branch {branch} not found in the repository.')
    branch_ref = repo.heads[branch]
    latest_commit = branch_ref.commit
    return latest_commit.hexsha


def get_previous_non_doc_commit(commit):
    """
    Gets the previous non-documentation commit from the given commit.
    """
    while commit:
        if "Update documentation" not in commit.message:
            return commit.parents[0]
        if commit.parents:
            commit = commit.parents[0]
        else:
            break
    return None


def get_diffs(commit, parent):
    """
    Find all the Python file diffs between the commit and its parent.
    """
    diffs = commit.diff(parent, R=True)
    python_diffs = []
    for diff in diffs:
        file_path = diff.a_path
        if file_path.endswith('.py'):
            python_diffs.append(diff)
    return python_diffs


def get_file__commit_content(root_folder, file_path, commit):
    """
    Get the content of a file at a specific commit.

    Args:
        file_path (str): The path of the file.
        commit (Commit): The specific commit to retrieve the file content from.

    Returns the content of the file at the specified commit. 
    If the file does not exist, an empty string is returned.
    """
    try:
        relative_path = os.path.relpath(file_path, root_folder)
        blob = commit.tree

        # Split the path and traverse the tree
        for part in relative_path.split(os.path.sep):
            blob = blob[part]

        # If it's a blob, return its content
        if blob.type == 'blob':
            return blob.data_stream.read().decode('utf-8')
        else:
            # If it's not a blob (e.g., it's a tree), return an empty string
            return ''
    except KeyError:
        return ''


def get_unified_diff(old_content, new_content):
    """
    Generate a unified diff between the old and new file contents.
    """
    diff = difflib.unified_diff(
        old_content.splitlines(), new_content.splitlines())
    return "\n".join(diff)
