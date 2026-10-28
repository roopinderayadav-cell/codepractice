import io
import json
import os
import re
import zipfile
import requests
import streamlit as st

st.set_page_config(page_title='IdeaForge AI', page_icon='💡', layout='wide')
st.title('💡 IdeaForge AI')
st.caption('Turn an idea into a Python project plan, starter code, and downloadable ZIP.')

LIBRARIES = {
    'dashboard': ['streamlit', 'pandas', 'plotly'],
    'chatbot': ['streamlit', 'requests'],
    'automation': ['pandas', 'openpyxl'],
    'website': ['fastapi', 'uvicorn', 'jinja2'],
    'data': ['pandas', 'numpy', 'plotly'],
}

def recommend(idea):
    t = idea.lower()
    matches = [k for k in LIBRARIES if k in t]
    if not matches:
        matches = ['dashboard']
    libs = list(dict.fromkeys(x for k in matches for x in LIBRARIES[k]))
    return libs

def starter_code(idea):
    return '''import streamlit as st\n\nst.set_page_config(page_title="My Prototype")\nst.title("My Prototype")\nst.write("Idea: " + ''' + repr(idea) + ''')\nuser_input = st.text_input("Enter a value")\nif st.button("Submit"):\n    st.success(f"Received: {user_input}")\n'''

def generate_ai(idea, api_key, model):
    prompt = ('You are a Python product architect. Return ONLY valid JSON with keys: '
              'summary (string), features (array of strings), libraries (array of strings), '
              'steps (array of strings), files (object mapping safe relative filenames to full text content). '
              'Build a small functional Streamlit MVP, include requirements.txt and README.md. '
              'No secrets, no shell execution, no external paid services required. User idea: ' + idea)
    response = requests.post(
        f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
        headers={'x-goog-api-key': api_key, 'Content-Type': 'application/json'},
        json={'contents': [{'parts': [{'text': prompt}]}], 'generationConfig': {'responseMimeType': 'application/json'}},
        timeout=90,
    )
    response.raise_for_status()
    raw = response.json()['candidates'][0]['content']['parts'][0]['text']
    return json.loads(raw)

def safe_files(files):
    clean = {}
    for name, content in files.items():
        name = name.replace('\\', '/')
        parts = name.split('/')
        if (not name or name.startswith('/') or '..' in parts or
            not all(re.fullmatch(r'[A-Za-z0-9_.-]+', p) for p in parts) or
            not isinstance(content, str) or len(content) > 200_000):
            continue
        clean[name] = content
    return clean

def make_zip(files):
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, content in files.items():
            z.writestr('ideaforge-project/' + name, content)
    return output.getvalue()

with st.sidebar:
    st.header('Generation settings')
    use_ai = st.toggle('Use Gemini AI', value=False)
    api_key = st.text_input('Gemini API key (optional)', type='password') if use_ai else ''
    model = st.text_input('Gemini model ID', value='gemini-2.5-flash') if use_ai else ''
    st.info('Your key is used for this session only. Do not put API keys in generated code.')

idea = st.text_area('Describe your application idea', placeholder='I want to build a KPI tracking dashboard for my team...', height=140)
if st.button('✨ Create prototype', type='primary'):
    if not idea.strip():
        st.warning('Please enter an idea first.')
    elif len(idea) > 5000:
        st.warning('Please limit your idea to 5,000 characters.')
    else:
        try:
            if use_ai:
                if not api_key:
                    st.error('Enter a Gemini API key or turn off Gemini AI.')
                    st.stop()
                result = generate_ai(idea, api_key, model)
                files = safe_files(result.get('files', {}))
            else:
                libs = recommend(idea)
                files = {
                    'app.py': starter_code(idea),
                    'requirements.txt': 'streamlit>=1.36\n',
                    'README.md': '# My Prototype\n\nRun with `streamlit run app.py`.\n',
                }
                result = {
                    'summary': 'Starter Streamlit application for: ' + idea,
                    'features': ['Idea summary', 'Text input', 'Submit action'],
                    'libraries': libs,
                    'steps': ['Download the ZIP', 'Extract it', 'Install requirements', 'Run streamlit run app.py'],
                }
            st.session_state['result'] = result
            st.session_state['files'] = files
        except (requests.RequestException, ValueError, KeyError) as exc:
            st.error('Generation failed. Check your model ID, API key, or connectivity. Details: ' + str(exc)[:300])

if 'result' in st.session_state:
    r = st.session_state['result']
    files = st.session_state['files']
    st.subheader('Solution blueprint')
    st.write(r.get('summary', ''))
    a, b = st.columns(2)
    with a:
        st.markdown('**Features**')
        for x in r.get('features', []): st.write('•', x)
        st.markdown('**Libraries**')
        st.write(', '.join(r.get('libraries', [])))
    with b:
        st.markdown('**Build steps**')
        for i, x in enumerate(r.get('steps', []), 1): st.write(f'{i}. {x}')
    st.subheader('Generated project files')
    if files:
        selected = st.selectbox('Choose a file', list(files))
        st.code(files[selected], language='python' if selected.endswith('.py') else 'text')
        st.download_button('⬇️ Download complete project ZIP', make_zip(files), 'ideaforge-project.zip', 'application/zip')
    else:
        st.warning('No usable files returned. Try again.')

st.divider()
st.subheader('🐍 Python practice')
st.write('Edit this sample and copy it into your own local Python environment. For safety, arbitrary code is not executed on this shared server.')
st.code('name = "World"\nprint(f"Hello, {name}!")', language='python')
st.caption('This first version offers code viewing and export, not a live execution sandbox.')
