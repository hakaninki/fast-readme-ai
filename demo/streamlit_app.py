"""Streamlit demo UI for fast-readme-ai.

Provides an interactive web interface for generating README.md files
by calling the FastAPI backend.
"""

import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title="fast-readme-ai",
    page_icon="⚡",
    layout="wide",
)

st.title("⚡ fast-readme-ai")
st.markdown("**Generate professional README.md files instantly with AI**")

st.divider()

col1, col2 = st.columns([2, 1])

with col1:
    source = st.text_input(
        "📁 Project path or GitHub URL",
        placeholder="e.g. /path/to/project or https://github.com/user/repo",
    )

with col2:
    project_name = st.text_input(
        "📝 Project name (optional)",
        placeholder="Auto-detected if empty",
    )

model = st.selectbox(
    "🤖 Gemini Model",
    options=["gemini-2.5-flash", "gemini-2.5-pro"],
    index=0,
)

API_URL = "http://localhost:8000/generate"

if st.button("🚀 Generate README", type="primary", use_container_width=True):
    if not source:
        st.error("Please enter a project path or GitHub URL.")
    else:
        with st.spinner("Analyzing project and generating README..."):
            try:
                payload = {
                    "source": source,
                    "model": model,
                }
                if project_name:
                    payload["project_name"] = project_name

                response = requests.post(API_URL, json=payload, timeout=120)

                if response.status_code == 200:
                    data = response.json()

                    if data.get("success"):
                        st.success(
                            f"✅ README generated for **{data['project_name']}**"
                        )

                        # Detected stack
                        st.subheader("🔍 Detected Stack")
                        stack = data.get("stack", {})
                        stack_rows = []
                        for category, items in stack.items():
                            if items:
                                stack_rows.append({
                                    "Category": category.replace("_", " ").title(),
                                    "Detected": ", ".join(items),
                                })
                        if stack_rows:
                            st.table(pd.DataFrame(stack_rows))
                        else:
                            st.info("No specific stack items detected.")

                        # Download button
                        st.download_button(
                            label="📥 Download README.md",
                            data=data["readme_content"],
                            file_name="README.md",
                            mime="text/markdown",
                            use_container_width=True,
                        )

                        # README content
                        st.subheader("📄 Generated README")
                        st.code(data["readme_content"], language="markdown")

                        # Mermaid diagram
                        if data.get("mermaid_diagram"):
                            st.subheader("📊 Architecture Diagram")
                            st.code(data["mermaid_diagram"], language="mermaid")
                    else:
                        st.error(data.get("error", "Generation failed."))
                else:
                    error_detail = response.json().get("detail", response.text)
                    st.error(f"API Error ({response.status_code}): {error_detail}")

            except requests.ConnectionError:
                st.error(
                    "Could not connect to the backend. "
                    "Make sure the FastAPI server is running on http://localhost:8000"
                )
            except requests.Timeout:
                st.error("Request timed out. The project may be too large.")
            except Exception as exc:
                st.error(f"Unexpected error: {exc}")

st.divider()
st.caption("Built with FastAPI, Google Gemini, and Streamlit")
