"""
This Python module provides functions to read and transform YAML content for a document template.
The module includes type definitions for the YAML content structure and functions to read YAML files and return the content.

This is the assumed structure of the document template:
- Document Header and Footer Items
    - Header
        - Document Type
        - Document Number
        - Document Revision Number
        - Document Effective Date
        - Document Title
    - Footer
        - Document Code
- Document Control Items
    - Revision History
    - Document Review and Approval
        - Prepared By
        - Reviewed and Approved By
- Document Body Items
    - Purpose           (1.0)
    - Scope             (2.0)
    - Responsibility    (3.0)
    - Definition        (4.0)
    - Procedure         (5.0)
    - Reference         (6.0)
    - Attachment        (7.0)
"""

from typing import TypedDict, List, Dict, Any
import yaml


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
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            example_content = yaml.safe_load(file)
    except yaml.YAMLError:
        print(f"Error reading the YAML file {input_file}.")
        return None

    # Transform the data structure to remove trailing newline characters from all string elements
    example_content = transform_data(example_content)

    return example_content
