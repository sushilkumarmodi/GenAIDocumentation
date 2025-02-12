from langchain_groq import ChatGroq

llm = ChatGroq(
    temperature=0,
    groq_api_key='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',
    model_name="llama-3.3-70b-versatile"
)


def LLM_Call(input):
    response = llm.invoke(f"Functional code document of:\n{input}")
    return response.content
