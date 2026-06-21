import streamlit as st
import chromadb
import pandas as pd
import os

# Configure the page
st.set_page_config(page_title="Local ChromaDB Viewer", layout="wide")
st.title("🗂️ Local ChromaDB Viewer")
st.markdown("View and explore local vector databases used in the Modular RAG system.")

# Connection Settings
st.sidebar.header("Connection Settings")
connection_type = st.sidebar.radio("Connect via", ["Local Directory", "HTTP Server"])

client = None

if connection_type == "Local Directory":
    default_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "chroma_db"))
    db_path = st.sidebar.text_input("Persistent Directory Path:", default_path)
    
    if st.sidebar.button("Connect"):
        if not os.path.exists(db_path):
            st.sidebar.error(f"Directory not found: `{db_path}`")
        else:
            try:
                client = chromadb.PersistentClient(path=db_path)
                st.sidebar.success("Connected successfully!")
            except Exception as e:
                st.sidebar.error(f"Failed to connect: {e}")
                
    # Auto-connect if it exists and they haven't manually clicked connect yet
    if 'client' not in st.session_state and os.path.exists(db_path):
        try:
            client = chromadb.PersistentClient(path=db_path)
        except:
            pass
            
else:
    host = st.sidebar.text_input("Host:", "localhost")
    port = st.sidebar.text_input("Port:", "8000")
    
    if st.sidebar.button("Connect"):
        try:
            client = chromadb.HttpClient(host=host, port=port)
            st.sidebar.success("Connected successfully!")
        except Exception as e:
            st.sidebar.error(f"Failed to connect: {e}")

# Store client in session state
if client is not None:
    st.session_state['client'] = client

# Main logic
if 'client' in st.session_state and st.session_state['client'] is not None:
    client = st.session_state['client']
    
    try:
        collections = client.list_collections()
        collection_names = [c.name for c in collections]
        
        if not collection_names:
            st.info("No collections found in this database.")
        else:
            st.sidebar.header("Explore Database")
            selected_collection = st.sidebar.selectbox("Collections", collection_names)
            
            if selected_collection:
                collection = client.get_collection(selected_collection)
                count = collection.count()
                st.subheader(f"Collection: `{selected_collection}`")
                st.write(f"**Total Documents:** {count}")
                
                if count > 0:
                    fetch_limit = min(5000, count) # Safety limit
                    results = collection.get(
                        limit=fetch_limit,
                        include=['documents', 'metadatas']
                    )
                    
                    if results and results.get("ids"):
                        df_data = []
                        for i in range(len(results["ids"])):
                            row = {
                                "ID": results["ids"][i],
                                "Document": results["documents"][i],
                            }
                            if results["metadatas"] and results["metadatas"][i]:
                                for k, v in results["metadatas"][i].items():
                                    row[f"Meta: {k}"] = v
                            df_data.append(row)
                            
                        df = pd.DataFrame(df_data)
                        
                        search_term = st.text_input("Search documents (local filtering):", "")
                        if search_term:
                            df = df[df['Document'].str.contains(search_term, case=False, na=False)]
                            st.write(f"Found {len(df)} matching documents.")
                        
                        limit = st.slider("Number of documents to display", min_value=1, max_value=max(10, len(df)), value=min(10, len(df)))
                        st.dataframe(df.head(limit), use_container_width=True)
                    else:
                        st.warning("No documents could be fetched.")
    except Exception as e:
        st.error(f"Error reading collections: {e}")
else:
    st.info("Please connect to a ChromaDB instance using the sidebar.")
