import zipfile
import os

def extract_zip(file_path, extract_to):
    """
    Extract a zip file to a target directory.
    
    :param file_path: Path to the zip file.
    :param extract_to: Directory where files should be extracted.
    :raises: Exception if extraction fails.
    """
    if not zipfile.is_zipfile(file_path):
        raise ValueError(f"{file_path} is not a valid zip file.")

    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
