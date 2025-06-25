import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA

load_dotenv()


loader = TextLoader("docs/example.txt")
documents = loader.load()

text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = text_splitter.split_documents(documents)


embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(docs, embeddings)


retriever = vectorstore.as_retriever()
llm = ChatOpenAI(model_name="gpt-4o", temperature=0)


qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)


query = "Respond to me as an expert in software development, are there any discrepencies, is there anything that is missing? Provide examples."
response = qa_chain.invoke(query)

print(response)
t