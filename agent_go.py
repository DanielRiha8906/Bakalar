import os
from dotenv import load_dotenv
from tools import *
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.agents import initialize_agent, AgentType
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.memory import ConversationBufferMemory


load_dotenv()
role_loader = TextLoader("docs/agent_role.txt")
role_documents = role_loader.load()

text_splitter = CharacterTextSplitter(chunk_size=600, chunk_overlap=50)
role_chunks = text_splitter.split_documents(role_documents)

embeddings = OpenAIEmbeddings()
role_vectorstore = FAISS.from_documents(role_chunks, embeddings)

role_retriever = role_vectorstore.as_retriever()

retrieved_role_docs = role_retriever.invoke("What is the agent's role?")
role_prompt_text = "\n".join([doc.page_content for doc in retrieved_role_docs])

history = ConversationBufferMemory(memory_key="chat_history", return_messages=True)


prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(role_prompt_text),
    HumanMessagePromptTemplate.from_template("{input}"),
])

toolset = return_all_implemented_tools()
llm = ChatOpenAI(model="gpt-4o", temperature=0)

agent = initialize_agent(
    tools=toolset,
    llm=llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    agent_kwargs={"input_variables": ["input", "chat_history"]},
    verbose=True,
    memory=history,
    handle_parsing_errors=True
)



while True:
    print('\n-----------------------USER INPUT -----------------------')
    user_input = input("\nYou: ")
    if user_input.lower() in ("exit", "quit"):
        break

    result = agent.invoke({"input": user_input})
    print("\n-----------------------AGENT RESPONSE -----------------------")
    print(result)

print(history.buffer)
