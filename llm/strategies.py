from typing import List
from concurrent.futures import ThreadPoolExecutor
from llm.llm import LLM

def simple(context: str, query: str, llm: LLM):
    simple_prompt = """"
    With the supplied context, answer the query from the user, using just the context supplied.
    Be very specfic in your answer.

    Context: {}
    Query: {}

    Use only the information in the context to answer the query.

    If there is no information that answer the query, return "I don't know".
    Using internal information is not allowed. You must not use any information that is not in the context.
    It is not allowed to use common sense or internal knowledge to answer the query.
    Only use the information in the context to answer the query.
    Use the context to give the most specific information possible.
    """.format(context, query)

    return llm.generate_text(simple_prompt, max_length=300)


def swarm(context:List[str], query:str, llm:LLM):

    """"
    Method used to refine the context and answer the query using the refined context.
    The context is split into 4 smaller chunks and processed in parallel.
    The main idea here is to use more context without compromising the speed of the response.
    While the simple method uses only the context to answer the query, the swarm method uses a multiple refined context.
    """

    def refine_context(context:str, query:str):
        return """
        You are supplied with the following context:
        {}

        The user has asked the following query:
        {}

        Based on that select from above only the information that is relevant to the query.
        And return it exactly as it is. 
        Without any additional information. 
        Without any additional context. 
        Without any additional explanation.
        If there is no information that answer the query, return an empty string ("").
        """.format(context, query)

    def refiner_helper(context:str, query:str):
        return llm.generate_text(refine_context(context=context, query=query))

    # Split the context into 4 smaller chunks to be processed in parallel
    ctx_length = len(context)
    chunk_size = ctx_length // 4
    contents = [
        context[i:i + chunk_size]
        for i in range(0, ctx_length, chunk_size)
    ]

    # Process the chunks in parallel
    unified_ctxs = [
        "\n".join(chunk)
        for chunk in contents
    ]

    with ThreadPoolExecutor(max_workers=4) as executor:
        refined_contexts = list(executor.map(refiner_helper, unified_ctxs, [query]*4))

    unified_refined_ctx = "\n".join(refined_contexts)

    return llm.generate_text(simple(refine_context=unified_refined_ctx,query=query, max_length=300))