import streamlit as st
import sys
import os

# Add tools directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

from ollama_client import OllamaClient
from generator_logic import SYSTEM_PROMPT, validate_test_cases

# Page Configuration
st.set_page_config(
    page_title="B.L.A.S.T. Test Generator",
    page_icon="🚀",
    layout="wide"
)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    model_name = st.text_input("Ollama Model", value="llama3.2:3b")
    st.info("Ensure Ollama is running (`ollama serve`).")
    
    st.markdown("---")
    st.markdown("**B.L.A.S.T. Protocol**")
    st.markdown("Blueprint • Link • Architect • Stylize • Trigger")

# Main Interface
st.title("🚀 Local LLM Test Case Generator")
st.markdown("Generate deterministic, structured test cases using your local **Ollama** instance.")

# Input
user_input = st.text_area("Requirement / User Story / Code Snippet:", height=200, placeholder="e.g., A login screen that locks the user out after 3 failed attempts...")

if st.button("Generate Test Cases", type="primary"):
    if not user_input.strip():
        st.warning("Please enter a requirement first.")
    else:
        with st.spinner("🤖 Orchestrating agents... (Connecting to local brain)"):
            try:
                # 1. Initialize Client
                client = OllamaClient(model_name=model_name)
                
                # 2. Check Logic (Validation handled in step 4)
                
                # 3. Call LLM
                raw_response = client.generate_response(SYSTEM_PROMPT, user_input)
                
                # 4. Validate & Parse
                test_cases = validate_test_cases(raw_response)
                
                # 5. Display Results
                st.success(f"Generated {len(test_cases)} Test Cases!")
                
                # Render as Cards
                for tc in test_cases:
                    with st.expander(f"📌 {tc['id']}: {tc['title']} ({tc['priority']})", expanded=True):
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.markdown(f"**Description:** {tc['description']}")
                            st.markdown("**Expected Result:**")
                            st.info(tc['expected_result'])
                        with col2:
                            st.markdown("**Steps:**")
                            for idx, step in enumerate(tc['steps'], 1):
                                st.text(f"{idx}. {step}")
                            
                            st.markdown("**Preconditions:**")
                            if tc['preconditions']:
                                for pre in tc['preconditions']:
                                    st.caption(f"• {pre}")
                            else:
                                st.caption("None")
                                
                            st.markdown(f"**Type:** `{tc['type']}`")
                
                # JSON Export
                st.download_button(
                    label="Download JSON",
                    data=raw_response,
                    file_name="test_cases_blast.json",
                    mime="application/json"
                )
                
            except ConnectionError as ce:
                st.error(f"🔌 Link Failure: {str(ce)}")
            except ValueError as ve:
                st.error(f"🧠 Parsing Error: {str(ve)}")
                with st.expander("Debug Raw Output"):
                    st.code(raw_response if 'raw_response' in locals() else "No response")
            except Exception as e:
                st.error(f"💥 System Error: {str(e)}")
