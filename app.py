import streamlit as st
import os
from groq import Groq

st.set_page_config(page_title="CodeRx", page_icon="💊", layout="wide")

# --- GROQ CLIENT ---
@st.cache_resource
def get_groq_client():
    api_key = None
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        st.error("GROQ_API_KEY not found. Please add it to Streamlit Secrets.")
        st.stop()
    return Groq(api_key=api_key)

client = get_groq_client()

# --- BILLING PROMPT ---
billing_prompt = """You are an expert medical coder. Analyze the following SOAP note and suggest the most likely billing codes.

Output ONLY a markdown table with three columns:
| Code Type | Code | Justification |
|---|---|---|
| ICD-10 | [code] | [Why this code?] |
| CPT | [code] | [Why this code?] |

If you are unsure, provide your best guess based on standard US billing guidelines. Do not output anything else."""

# --- UI LAYOUT ---
st.title("💊 CodeRx")
st.write("Convert clinical SOAP notes into accurate ICD-10 and CPT billing codes instantly.")

# Create two columns
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Paste SOAP Note")
    
    # File uploader for .txt files
    uploaded_file = st.file_uploader("Or upload a .txt file", type=["txt"])
    
    # Default text to display in the box
    default_text = ""
    
    # If the user uploaded a file, read it
    if uploaded_file is not None:
        default_text = uploaded_file.read().decode("utf-8")
    
    # The text area will show the uploaded text, or let the user type/paste
    soap_input = st.text_area(
        "Doctor's note:", 
        value=default_text,
        height=400, 
        placeholder="SUBJECTIVE:\nPatient reports 3 days of fever...\n\nOBJECTIVE:\nTemp 101F...\n\nASSESSMENT:\nViral URI...\n\nPLAN:\nRest, fluids, Paracetamol..."
    )
    
    generate_btn = st.button("⚡ Generate Billing Codes", use_container_width=True)

with col2:
    st.subheader("2. Suggested Billing Codes")
    
    if generate_btn:
        if not soap_input.strip():
            st.warning("Please paste a SOAP note first.")
        else:
            with st.spinner("Analyzing note and generating codes..."):
                try:
                    response = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[
                            {"role": "system", "content": billing_prompt},
                            {"role": "user", "content": f"Here is the SOAP note:\n\n{soap_input}"}
                        ],
                        temperature=0.1
                    )
                    codes = response.choices[0].message.content
                    st.success("Codes generated successfully!")
                    st.markdown(codes)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
    else:
        st.info("Billing codes will appear here once you paste a note and click Generate.")

# Footer
st.divider()
st.caption("CodeRx · For demonstration purposes only. Always verify billing codes with a certified medical coder.")
