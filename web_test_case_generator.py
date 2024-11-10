from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import WebBaseLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
import streamlit as st

class WebTestCaseGenerator:
    def __init__(self, api_key=None, model_name="gpt-4o-mini", temperature=0.5):
        self.api_key = api_key or st.session_state.get("api_key")
        if not self.api_key:
            st.error("API key is required for generating responses.")
            return
        self.model = ChatOpenAI(api_key=self.api_key, model_name=model_name, temperature=temperature)
        self.prompt = self.create_prompt()

    def create_prompt(self):
        template = (
            "You are an expert website analyst. {question}. Review the provided website content {context} and answer the user's question directly. Provide clear and relevant information as requested."
        )
        return PromptTemplate(template=template, input_variables=["question", "context"])

    def load_web_documents(self, url):
        try:
            loader = WebBaseLoader(url)
            documents = loader.load()
            if not documents:
                st.error("No documents found from the URL. Please try a different URL.")
            else:
                for doc in documents:
                    doc.page_content = ' '.join(doc.page_content.split())
            return documents
        except Exception as e:
            st.error(f"Failed to load documents from URL: {e}")
            return None

    def create_vector_store(self, documents):
        if not documents:
            return None
        embeddings = OpenAIEmbeddings(api_key=self.api_key)
        return FAISS.from_documents(documents, embeddings)

    def prepare_web_data(self, url):
        documents = self.load_web_documents(url)
        if documents:
            st.session_state.vector_store = self.create_vector_store(documents)
            if st.session_state.vector_store:
                st.session_state.web_data_loaded = True
                return "Web data loaded and processed successfully!"
            else:
                return "Error: Failed to create vector store from web data."
        else:
            return "Error: Failed to load documents from the specified URL."

    def generate_response(self, query):
        if "vector_store" not in st.session_state or st.session_state.vector_store is None:
            return "Error: Vector store is not initialized. Please load web data first."

        chain_type_kwargs = {"prompt": self.prompt}
        chain = RetrievalQA.from_chain_type(
            llm=self.model,
            chain_type="stuff",
            retriever=st.session_state.vector_store.as_retriever(search_kwargs={"k": 1}),
            chain_type_kwargs=chain_type_kwargs
        )
        response = chain.run(query)
        return response
