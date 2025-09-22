import asyncio
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

async def main() -> None:
    # Set up LLM and embeddings
    llm = ChatOllama(model="llama3")
    embeddings = OllamaEmbeddings(model="all-minilm")

    # Populate vector store
    texts = [
        "Sally's savings from 2023 are $50,000",
        "Jack's savings from 2020 are $100,000",
        "My savings from 2023 are $70,000"
    ]
    vectorstore = FAISS.from_texts(texts, embedding=embeddings)
    retriever = vectorstore.as_retriever()
    
    # Prompt template
    prompt_template_str = """
    {input}
    Generate a response beased on the user input above.
    This is the background information for you. You can use or not use it.
    {document}
    You can say "I don't know" if you do not have an answer.
    """
    prompt = ChatPromptTemplate.from_template(prompt_template_str)
    
    # RAG chain
    chain = (
        {"document": retriever, "input": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    # Invoke chain
    user_input = "Do you know Sally's savings from 2023?"
    response = await chain.ainvoke(user_input)
    
    print(f"User: {user_input}")
    print(f"LLM says: {response}")

if __name__ == "__main__":
  asyncio.run(main())
