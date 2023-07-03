from flask import Flask, render_template, request
import os
import getpass
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.prompts import PromptTemplate, FewShotPromptTemplate
from langchain.chains import LLMChain, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.llms import OpenAI

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    loader = CSVLoader(file_path='data.csv')
    raw_documents = loader.load()

    embeddings = OpenAIEmbeddings()
    retriever = Chroma.from_documents(raw_documents, embeddings)

    prefix = """
    you are acting as a recommendation system for me. you have to recommend me an exact number of  
    companies from Industry that user specify in the query, from the db. if the company is
    not in the list then search for other industries in the db which are similar to the input industry name.
    For example:
    user: Give me four AR/VR companies name
    AI: Apple, Microsoft, Google, Meta
    
    In this example, the industry name is AR/VR but that industry is not listed in the db so the AI
    will suggest companies that are in the Technology industry as AR/VR is a sub-industry of Technology.
    Similarly, if the user asks for HRMR Industry and HRMR is not in the list then the AI should suggest the 
    companies which are related to that industry like as HRMR is a sub-industry of Technology and corporate.
    separate the companies' names with a comma (,) give me only the company name without any explanation and stay idle.
    """

    suffix = """
    user: {query}
    AI: """

    examples = [
        {"user": "Give me four AR/VR companies name", "bot": "Apple, Microsoft, Google, Meta"},
        {"user": "Give me two HRMR companies name", "bot": "Apple, IBM"}
    ]

    example_template = """
    user: {query}
    bot: {answer}
    """

    example_prompt = PromptTemplate(input_variables=["query", "answer"], template=example_template)

    few_shot = FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
        prefix=prefix,
        suffix=suffix,
        input_variables=["query"],
        example_separator="\n"
    )

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    qa = ConversationalRetrievalChain.from_llm(
        OpenAI(temperature=0.1),
        condense_question_prompt=few_shot,
        retriever=retriever.as_retriever(),
        memory=memory
    )

    no_of_recc = request.form['recommendations']
    ind_type = request.form['industry']
    query = f"{no_of_recc} companies in {ind_type}"
    result = qa({"question": query})

    return render_template('result.html', result=result["answer"])

if __name__ == '__main__':
    os.environ['OPENAI_API_KEY'] = getpass.getpass('OpenAI_API_Key:')
    app.run()
