
def simple(context: str, query: str):
    return """"
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
    """.format(context, query)