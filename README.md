# IdeaForge AI — Streamlit MVP

A simple public-facing prototype for turning natural-language software ideas into Python starter projects.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy

1. Create a GitHub repository and upload `app.py`, `requirements.txt`, and this README.
2. In Streamlit Community Cloud, select the repository and `app.py`.
3. Deploy. No API key is needed for the offline starter mode.
4. For AI generation, turn on Gemini AI in the sidebar and enter your own Gemini API key. API availability and usage limits depend on your Google account.

## Important limitations

- Offline mode generates a generic starter template, not bespoke AI-written code.
- Gemini mode requests custom code and project plans; review all generated code before running it.
- The Python practice section is display-only; no untrusted code is executed on the server.
- A production multi-user platform needs authentication, persistent project storage, usage quotas, abuse protection, and isolated code execution infrastructure.
- Generated code is not guaranteed to be correct or secure.
