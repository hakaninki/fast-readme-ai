> 🤖 This README was generated automatically using **fast-readme-ai** — the AI documentation generator built in this repository.
 ![AI Generated README](https://img.shields.io/badge/README-AI%20Generated-blue)

# fast-readme-ai

[![Python](https://img.shields.io/badge/language-Python-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview
fast-readme-ai is an intelligent tool designed to automatically generate comprehensive and professional `README.md` files for software projects. It analyzes project directories, detects technology stacks, extracts key file information, and leverages the Google Gemini API to produce high-quality documentation, including architecture diagrams.

## Features
*   **Automated Project Analysis**: Scans project directories to understand structure and content.
*   **Technology Stack Detection**: Identifies programming languages, frameworks, and databases used.
*   **Key File Content Extraction**: Summarizes important files like `main.py`, `package.json`, and `requirements.txt`.
*   **AI-Powered README Generation**: Utilizes the Google Gemini API to write detailed and context-aware READMEs.
*   **Mermaid Diagram Generation**: Automatically creates visual architecture diagrams based on the detected project structure.
*   **FastAPI Backend**: Provides a robust and scalable API for README generation.
*   **Streamlit Demo**: Offers an interactive web interface for easy project input and README output.
*   **Git Repository Cloning**: Can analyze projects directly from GitHub URLs.

## Tech Stack

| Layer          | Technology                                  |
| :------------- | :------------------------------------------ |
| **Languages**  | Python                                      |
| **Frameworks** | FastAPI, Streamlit                          |
| **AI/ML**      | Google Generative AI (Gemini)               |
| **Utilities**  | GitPython, python-dotenv, Pydantic, httpx   |
| **Server**     | Uvicorn                                     |

## Project Structure

```
.
├── analyzer/
│   ├── __init__.py
│   ├── directory_tree.py
│   ├── file_reader.py
│   ├── repo_cloner.py
│   └── stack_detector.py
├── backend/
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── readme.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── gemini_service.py
│   ├── __init__.py
│   ├── config.py
│   └── main.py
├── demo/
│   └── streamlit_app.py
├── examples/
│   ├── sample_project/
│   │   ├── src/
│   │   │   └── app.py
│   │   ├── package.json
│   │   └── requirements.txt
│   └── sample_output_README.md
├── generator/
│   ├── __init__.py
│   ├── mermaid_builder.py
│   ├── prompt_builder.py
│   └── readme_writer.py
├── tests/
│   ├── __init__.py
│   ├── test_analyzer.py
│   ├── test_api.py
│   └── test_generator.py
├── .env.example
├── .gitignore
├── Makefile
├── README.md
└── requirements.txt
```

## Getting Started

### Prerequisites
Before you begin, ensure you have the following installed:
*   **Python 3.8+**
*   **Git**

### Installation
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/fast-readme-ai.git
    cd fast-readme-ai
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Environment Setup
1.  **Create a `.env` file:**
    Copy the `.env.example` file to `.env` in the project root:
    ```bash
    cp .env.example .env
    ```
2.  **Configure API Key:**
    Open the newly created `.env` file and add your Google Gemini API key:
    ```
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    ```
    You can obtain a Gemini API key from the [Google AI Studio](https://aistudio.google.com/app/apikey).

## Usage

### Running the FastAPI Backend
To start the API server:
```bash
uvicorn backend.main:app --reload
```
The API will be accessible at `http://127.0.0.1:8000`.

### Running the Streamlit Demo
To launch the interactive demo application:
```bash
streamlit run demo/streamlit_app.py
```
This will open the Streamlit app in your web browser, typically at `http://localhost:8501`. You can then input a local project path or a GitHub URL to generate a README.

## API Reference

The FastAPI backend exposes the following endpoints:

| Method | Path               | Description                                       |
| :----- | :----------------- | :------------------------------------------------ |
| `GET`  | `/`                | Returns basic API information (name, version).    |
| `POST` | `/generate-readme` | Generates a README.md for a given project path or URL. |

**Example Request (Python using `httpx`):**

```python
import httpx

async def generate_readme_example():
    payload = {
        "project_path": "./examples/sample_project", # Or a GitHub URL like "https://github.com/octocat/Spoon-Knife"
        "output_path": "./generated_readme.md"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post("http://127.0.0.1:8000/generate-readme", json=payload)
        response.raise_for_status()
        print(response.json())

# To run: asyncio.run(generate_readme_example())
```

## Architecture

```mermaid
graph TD
    A[User/Client (Streamlit/HTTP)] --> B[FastAPI Backend]
    B --> C[Analyzer Module]
    C --> D[Generator Module]
    D --> E[Google Gemini API]
    E --> D
    D --> F[Generated README]
    B --> A
```

## Contributing
Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
