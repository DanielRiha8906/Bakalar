import os
from dotenv import load_dotenv
from mcp_tools import  call_mcp, get_file, write_file
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.agents import initialize_agent, AgentType
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.tools import tool
from langchain.memory import ConversationBufferMemory


load_dotenv()
role_loader = TextLoader("docs/agent_role.txt")
role_documents = role_loader.load()

text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
role_chunks = text_splitter.split_documents(role_documents)

embeddings = OpenAIEmbeddings()
role_vectorstore = FAISS.from_documents(role_chunks, embeddings)

role_retriever = role_vectorstore.as_retriever()

retrieved_role_docs = role_retriever.get_relevant_documents("What is the agent's role?")
role_prompt_text = "\n".join([doc.page_content for doc in retrieved_role_docs])


code_loader = TextLoader("docs/code_context.txt")
code_documents = code_loader.load()
code_chunks = text_splitter.split_documents(code_documents)
code_vectorstore = FAISS.from_documents(code_chunks, embeddings)
code_retriever = code_vectorstore.as_retriever()

history = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

tools = [get_file, write_file]
prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(role_prompt_text),
    HumanMessagePromptTemplate.from_template("{input}")
])

llm = ChatOpenAI(model="gpt-4o", temperature=0)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    agent_kwargs={"prompt": prompt},
    verbose=True,
    handle_parsing_errors=True,
    memory=history
)



while True:
    print('\n-----------------------USER INPUT -----------------------')
    user_input = input("\nYou: ")
    if user_input.lower() in ("exit", "quit"):
        break
    result = agent.invoke({"input": user_input})

print(history.buffer)
