# doc_api_endpoint

This is a simple API endpoint that takes document YAML files as source data to return as JSON objects. This serves as an API server that can be used to provide audit data programmatically.

This project is an extension of the [yaml_docx_filler project](https://github.com/NicholasChua/yaml_docx_filler), and references the same document YAML format. 

While the project intentionally only provides read-only access to the data, it is possible to extend it to create/update/delete functionality as well.

## Requirements

- Python 3.12
- API Testing Tool (e.g. Postman, Insomnia, or curl)

## Usage

```bash
fastapi dev endpoint.py
```

```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/v1/documents/' \
  -H 'accept: application/json'
```

## YAML Source

You can use the example YAML files in the 'yml' directory to test the API endpoint. If you have your own YAML files, you can place them in the 'yml' directory as well.

## Other

The functionality here will eventually be merged with yaml_docx_filler. This repository exists to document only the API endpoint functionality of the project.
