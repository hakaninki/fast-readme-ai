> 🤖 This README was generated automatically using **fast-readme-ai** — the AI documentation generator built in this repository.
![AI Generated README](https://img.shields.io/badge/README-AI%20Generated-blue)

# fast-readme-ai

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

## Overview

fast-readme-ai is an AI-powered tool designed to automatically generate comprehensive `README.md` files for software projects. It analyzes a given repository's structure and key files, detects its technology stack, and leverages the Google Gemini API to produce detailed, professional documentation, including architecture diagrams. This project aims to streamline the documentation process for developers.

## Features

*   Automated repository analysis (directory structure, file contents).
*   Intelligent technology stack detection (languages, frameworks, databases).
*   AI-driven README content generation using Google Gemini.
*   Automatic generation of Mermaid.js architecture diagrams.
*   FastAPI backend for robust API endpoints.
*   Streamlit-based demo application for interactive usage.
*   Support for cloning remote Git repositories.

## Tech Stack

| Layer            | Technology                               |
| :--------------- | :--------------------------------------- |
| **Languages**    | Python, JavaScript                       |
| **Frameworks**   | FastAPI, Next.js, React                  |
| **Databases**    | PostgreSQL, Redis                        |
| **AI/ML**        | Google Gemini                            |
| **Package Mgrs** | pip, npm                                 |
| **Other**        | SQLAlchemy, Uvicorn, Streamlit, GitPython|

## Project Structure

```
0457947f-eb66-4f9a-a43b-1931cbbfbe35/
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

To get a local copy up and running, follow these simple steps.

### Prerequisites

*   Python 3.8+
*   Git

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-org/fast-readme-ai.git # Replace with actual repo URL
    cd fast-readme-ai
    ```
2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: `venv\Scripts\activate`
    ```
3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set up environment variables:**
    ```bash
    cp .env.example .env
    ```
    Open the newly created `.env` file and add your Google Gemini API key:
    ```
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    ```
    You can obtain a Gemini API key from the [Google AI Studio](https://aistudio.google.com/app/apikey).

## Usage

### Running the FastAPI Backend

Start the API server:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be accessible at `http://localhost:8000`.

### Running the Streamlit Demo

In a separate terminal, launch the interactive Streamlit application:

```bash
streamlit run demo/streamlit_app.py
```

The Streamlit app will open in your web browser, typically at `http://localhost:8501`. From there, you can input a repository URL or local path to generate a README.

## API Reference

The FastAPI backend exposes the following endpoints:

| Method | Path         | Description                                                                                             |
| :----- | :----------- | :------------------------------------------------------------------------------------------------------ |
| `GET`  | `/`          | Returns basic API information, including the tool's name and version.                                   |
| `GET`  | `/health`    | Checks the health status of the API, indicating if it's running correctly.                              |
| `POST` | `/generate`  | Initiates the README generation process. Expects a JSON payload containing details about the project (e.g., a GitHub repository URL or a local project path). |

## Architecture

```mermaid
graph TD
    A[User/Client] --> B(FastAPI Backend)
    B --> C{Analyzer Module}
    B --> D{Generator Module}

    C --> C1[Repo Cloner]
    C --> C2[File Reader]
    C --> C3[Stack Detector]

    D --> D1[Prompt Builder]
    D --> D2[Mermaid Builder]
    D --> D3[README Writer]

    C1 --> E[Input Repository]
    C2 --> E
    C3 --> E

    D1 --> F[Google Gemini API]
    D1 --> G[Analysis Data]
    D2 --> G
    D3 --> H[Generated README.md]
    D3 --> I[Mermaid Diagram Code]

    E --&gt; G
    F --&gt; D1
    G --&gt; D1
    G --&gt; D2
    D2 --&gt; I
    D1 --&gt; D3
    I --&gt; D3
```

## Contributing

Contributions are welcome! Please feel free to open issues for bug reports or feature requests, or submit pull requests with improvements. Ensure your code adheres to the project's style guidelines and includes appropriate tests.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
