from typing import TypedDict, List, Dict, Any
from fastapi.responses import RedirectResponse
import yaml
from fastapi import FastAPI, HTTPException
import os
import glob
from concurrent.futures import ThreadPoolExecutor


# Imported types from my yaml_docx_filler project
# Define the types for the YAML content based on the assumed structure of the document template
class HeaderFooterItems(TypedDict):
    """
    Represents the structure of the header and footer items in a document.

    Fields:
    - document_type (str): The type of the document.
    - document_no (str): The document number.
    - document_code (str): The code identifying the document.
    - effective_date (str): The date the document becomes effective.
    - document_rev (str): The revision number of the document.
    - title (str): The title of the document.
    """

    document_type: str
    document_no: str
    document_code: str
    effective_date: str
    document_rev: str
    title: str


class RevisionHistoryItem(TypedDict):
    """
    Represents the structure of a revision history item in a document.

    Fields:
    - revision (str): The revision number.
    - date (str): The date of the revision.
    - description (str): The description of the changes made in the revision.
    """

    revision: str
    date: str
    description: str


class PreparedByItem(TypedDict, total=False):
    """
    Represents the structure of the Prepared By section in a document.

    Fields:
    - name (str): The name of the individual.
    - role (str): The role of the individual.
    - date (str | None): The date of preparation. Optional field as it may not be present in all documents.
    """

    name: str
    role: str
    date: str | None


class ReviewedApprovedByItem(TypedDict, total=False):
    """
    Represents the structure of the Reviewed and Approved By section in a document.

    Fields:
    - name (str): The name of the individual.
    - role (str): The role of the individual.
    - date (str | None): The date of review or approval. Optional field as it may not be present in all documents.
    """

    name: str
    role: str
    date: str | None


class ProcedureSection(TypedDict, total=False):
    """
    Represents the structure of the Procedure section (5.0) in a document.
    This is the part of the document that is most likely to vary significantly between documents,
    thus it is left flexible with optional fields, and custom handling may be required.
    Minimally, it can be expected to be a mixed list of lists and dictionaries.

    Fields:
    - title (str): The title of the procedure section.
    - content [List[str] | List[Dict[str, Any]] | Dict[str, Any]] | None: The content of the procedure section.
    """

    title: str
    content: List[str] | List[Dict[str, Any]] | Dict[str, Any] | None


class DocumentType(TypedDict):
    """
    Represents the structure of a standard document, including header/footer, document control items and content sections.

    Fields:
    - document_type (str): The type of the document.
    - document_no (str): The document number.
    - effective_date (str): The date the document becomes effective.
    - document_rev (str): The revision number of the document.
    - title (str): The title of the document.
    - document_code (str): The code identifying the document.
    - revision_history (List[RevisionHistoryItem]): A list of revision history items.
    - prepared_by (List[PreparedByItem]): A list of individuals who prepared the document.
    - reviewed_approved_by (List[ReviewedApprovedByItem]): A list of individuals who reviewed and approved the document.
    - purpose (List[str]): The purpose of the document.
    - scope (List[str]): The scope of the document.
    - responsibility (List[str]): The responsibilities outlined in the document.
    - definition (List[str]): Definitions of terms used in the document.
    - reference (List[str]): References to other documents.
    - attachment (List[str]): Attachments to the document.
    - procedure (List[ProcedureSection]): The procedural content of the document.
    """

    document_type: str
    document_no: str
    effective_date: str
    document_rev: str
    title: str
    document_code: str
    revision_history: List[RevisionHistoryItem]
    prepared_by: List[PreparedByItem]
    reviewed_approved_by: List[ReviewedApprovedByItem]
    purpose: List[str]
    scope: List[str]
    responsibility: List[str]
    definition: List[str]
    reference: List[str]
    attachment: List[str]
    procedure: List[ProcedureSection]


# Imported functions from my yaml_docx_filler project
def transform_data(
    data: DocumentType | Dict[str, Any] | List[Any]
) -> DocumentType | Dict[str, Any] | List[Any]:
    """
    Helper function that recursively enters an unknown-amount nested dictionary or list and applies transformations to all string elements.
    This function can be flexibly edited to apply other transformations to the data structure as needed.
    In this example, we remove trailing newline characters from all string elements.
    Usage: transform_data(data)

    Args:
        data: The input data structure which can be a dictionary, list, string, or any other type.

    Returns:
        data: The transformed data structure with modifications applied to all string elements.
    """
    if isinstance(data, dict):
        return {
            transform_data(key): transform_data(value) for key, value in data.items()
        }
    elif isinstance(data, list):
        return [transform_data(element) for element in data]
    elif isinstance(data, str):
        # Edit the transformation here as needed
        return data.rstrip("\n")
    else:
        print("There are no string elements in the data structure to transform.")
        return data


def read_yaml_file(input_file: str) -> DocumentType | Dict:
    """
    Used to read a YAML file and return the content as a dictionary
    Usage: content = read_yaml_file('text.yml')

    Inputs:
    input_file: The file path of the YAML file to be read

    Returns:
    example_content: The content of the YAML file as a dictionary
    """
    with open(input_file, "r", encoding="utf-8") as file:
        example_content = yaml.safe_load(file)

    # Transform the data structure to remove trailing newline characters from all string elements
    example_content = transform_data(example_content)

    return example_content


def load_document(input_file: str) -> Dict[str, Any]:
    """
    Load a document from a YAML file and return the content as a dictionary.
    This function reads the YAML file, transforms the data structure, and returns the content.

    Args:
        input_file: The file path of the YAML file to load.

    Returns:
        A tuple containing the document name and its content as a dictionary.
    """
    document_content = read_yaml_file(input_file)
    document_name = os.path.basename(input_file).split(".")[
        0
    ]  # Extract the document name from the file path
    return document_name, document_content


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


# Create a FastAPI instance
app = FastAPI()

# Load all YAML files in /yml directory
document_names = [file for file in glob.glob("yml/*.yml")]

# Create a dictionary to store all loaded documents and content in the format {document_name: content}
loaded_documents = {}

# Use ThreadPoolExecutor to read multiple documents in parallel and update loaded_documents
with ThreadPoolExecutor(max_workers=5) as executor:
    results = executor.map(load_document, document_names)
    for document_name, content in results:
        loaded_documents[document_name] = content


@app.get("/v1")
async def get_api_info():
    """
    Send the user to the API documentation page. RTFM!

    Returns:
    - 200 OK | Information about the API.
    """
    return RedirectResponse(url="/redoc")


@app.get("/v1/documents")
async def get_document_list():
    """
    Retrieve the list of documents that have been loaded.

    Returns:
    - 200 OK | A list of the names of the documents that have been loaded.
    """
    return list(loaded_documents.keys())


@app.get("/v1/{document}")
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


@app.get("/v1/{document}/sections")
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


@app.get("/v1/{document}/metadata")
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
@app.get("/v1/{document}/document_control")
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
@app.get("/v1/{document}/{section}")
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


# @app.get("/")
# async def root():
#     return {"message": "Hello World"}


def main():
    # Warn user that you do not run this file directly
    print("This is the fastapi endpoint file. Do not run this file directly.")
    print("Instead, use the command below to start this endpoint:")
    print(f"fastapi dev {os.path.basename(__file__)}")


if __name__ == "__main__":
    main()
