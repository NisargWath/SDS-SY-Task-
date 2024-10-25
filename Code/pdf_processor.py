import google.generativeai as genai
import os
import urllib
import warnings
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import ChatGoogleGenerativeAI

warnings.filterwarnings("ignore")

google_api_key = "AIzaSyCpDjrKq5lkm3LaW_U3N53IvNbHc4h5cnA"
genai.configure(api_key=google_api_key)
model = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=google_api_key)


def get_pdf_answer(pdf_file, question, num_pages=30):
    """
    Process the PDF file, extract context, and get the answer to the question.
    
    Args:
        pdf_file (str): Path to the PDF file.
        question (str): Question to ask about the PDF content.
        num_pages (int): Number of pages to consider for context (default is 30).
    
    Returns:
        str: Answer to the question based on the PDF context.
    """
    pdf_loader = PyPDFLoader(pdf_file)
    pages = pdf_loader.load_and_split()

    context = "\n".join(str(p.page_content) for p in pages[:num_pages])

    prompt_template = """Answer the question as precise as possible using the provided context. If the answer is
                        not contained in the context, say "try to Generate relateable answer" \n\n
                        Context: \n {context}?\n
                        Question: \n {question} \n
                        Answer:
                      """

    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

    stuff_chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    stuff_answer = stuff_chain({"input_documents": pages[:num_pages], "question": question}, return_only_outputs=True)

    return stuff_answer


if __name__ == "__main__":
    pdf_file = "/Users/appleApple/Desktop/MindStaq/try/m/llama2.pdf"
    question = "What is Reinforcement Learning with Human Feedback (RLHF)"
    result = get_pdf_answer(pdf_file, question)
    print(result)
