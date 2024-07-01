from typing import Tuple, Dict, Any
from fastapi import HTTPException, APIRouter
import os
import glob
from concurrent.futures import ThreadPoolExecutor

# Internal imports
from documentHandler import read_yaml_file


def load_document(input_file: str) -> Tuple[str, Dict[str, Any]]:
    """
    Load a document from a YAML file and return the content as a tuple.
    This function reads the YAML file, transforms the data structure, and returns the content.

    Args:
        input_file: The file path of the YAML file to load.

    Returns:
        A tuple containing the document name and its content.
    """
    document_content = read_yaml_file(input_file)
    if document_content is None:
        return None  # Skip improperly formatted YAML files
    document_name = os.path.basename(input_file).split(".")[
        0
    ]  # Extract the document name from the file path
    return document_name, document_content


def populate_loaded_documents(directory: str) -> dict:
    """
    Load all .yml documents in the specified directory and return them as a dictionary.

    Args:
        directory: The directory containing the YAML documents.

    Returns:
        A dictionary containing the loaded documents.
    """
    document_names = [file for file in glob.glob(f"{directory}/*.yml")]
    loaded_documents = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(load_document, document_names)
        for result in results:
            if result is not None:  # Skip None results indicating an error
                document_name, content = result
                loaded_documents[document_name] = content
    return loaded_documents


def check_document_loaded(document_name: str, loaded_documents: dict):
    """
    Check if the document is already loaded and return it.
    If not found, raise an HTTPException.

    Args:
        document_name: The name of the document to retrieve.
        loaded_documents: The dictionary containing loaded documents.

    Returns:
        The content of the loaded document.

    Raises:
        HTTPException: If the document is not found in loaded_documents.
    """
    if document_name in loaded_documents:
        return loaded_documents[document_name]
    else:
        raise HTTPException(
            status_code=404, detail=f"Document {document_name}.yml not found"
        )


# Create an APIRouter instance
router = APIRouter()

# Load all YAML files in /yml directory
loaded_documents = populate_loaded_documents("yml")


# Define the API routes
@router.get("/")
async def get_document_list():
    """
    Retrieve the list of documents that have been loaded.

    Returns:
    - 200 OK | A list of the names of the documents that have been loaded.
    """
    return list(loaded_documents.keys())


@router.get("/{document}")
async def get_document_content(document: str):
    """
    Retrieve the content of a document.

    Parameters:
    - document: The name of the document to retrieve.

    Returns:
    - 200 OK | The content of the document if it is already loaded.

    Raises:
    - 404 Not Found | HTTPException with status code 404 if the document is not found.
    """
    document_content = check_document_loaded(document, loaded_documents)
    return document_content


@router.get("/{document}/sections")
async def get_document_content_sections(document: str):
    """
    Retrieve the sections of a document. This should be standardized across all documents, so this function is meant as a helper to list the sections.

    Parameters:
    - document: The name of the document to retrieve sections from.

    Returns:
    - 200 OK | The sections of the document if it is already loaded.

    Raises:
    - 404 Not Found | HTTPException with status code 404 if the document is not found.
    """
    document_content = check_document_loaded(document, loaded_documents)
    # Get the keys of the document content (sections)
    sections = list(document_content.keys())
    # Inject "metadata" as the 7th element in the sections list
    sections.insert(6, "metadata")
    # Inject "document_control" as the 11th element in the sections list (after inserting "metadata")
    sections.insert(10, "document_control")
    return sections


@router.get("/{document}/metadata")
async def get_document_content_metadata(document: str):
    """
    Retrieve the header and footer items (metadata) of a document.

    Parameters:
    - document: The name of the document to retrieve metadata from.

    Returns:
    - 200 OK | The metadata of the document if it is already loaded.

    Raises:
    - 404 Not Found | HTTPException with status code 404 if the document is not found.
    """
    content = check_document_loaded(document, loaded_documents)
    metadata = {
        "document_type": content["type"],
        "document_no": content["document_no"],
        "effective_date": content["effective_date"],
        "document_rev": content["document_rev"],
        "title": content["title"],
        "document_code": content["document_code"],
    }
    return metadata


# Return the document control (content of the revision_history, prepared_by, reviewed_approved_by) in the {document}.yml file
@router.get("/{document}/document_control")
async def get_document_document_control(document: str):
    """
    Retrieve the document control items (revision history, prepared by, reviewed and approved by) of a document.

    Parameters:
    - document: The name of the document to retrieve document control items from.

    Returns:
    - 200 OK | The document control items of the document if it is already loaded.

    Raises:
    - 404 Not Found | HTTPException with status code 404 if the document is not found.
    """
    content = check_document_loaded(document, loaded_documents)
    document_control = {
        "revision_history": content["revision_history"],
        "prepared_by": content["prepared_by"],
        "reviewed_approved_by": content["reviewed_approved_by"],
    }
    return document_control


# Get the content of a specific section in the example.yml file
@router.get("/{document}/{section}")
async def get_document_content_section(document: str, section: str):
    """
    Retrieve the content of a specific section in a document.

    Parameters:
    - document: The name of the document to retrieve the section from.
    - section: The name of the section to retrieve.

    Returns:
    - 200 OK | The content of the specified section if it exists in the document.

    Raises:
    - 404 Not Found | HTTPException with status code 404 if the document or section is not found.
    """
    content = check_document_loaded(document, loaded_documents)
    if section not in content:
        raise HTTPException(
            status_code=404,
            detail=f"Section '{section}' doesn't exist in {document}.yml",
        )
    return content[section]
