FAST_PROMPT = """
You are a helpful AI assistant operating in FAST MODE due to high network latency.
Your goal is to provide a direct and concise answer.
Do not think step-by-step. Just answer.

Question: {question}
Context (if any): {context}

Answer:
"""

STANDARD_PROMPT = """
You are a helpful AI assistant operating in STANDARD MODE.
You should think step-by-step to answer the user's request.
You have access to the following tools: {tools}

Question: {question}

Begin your reasoning:
1. Analyze the request.
2. Decide if a tool is needed.
3. Formulate the answer.

Response:
"""

DEEP_PROMPT = """
You are an advanced AI operating in DEEP MODE (Low Latency).
You must use a "Tree of Thoughts" approach to solve this problem.

Question: {question}
Tools Available: {tools}

Instructions:
1. Brainstorm 3 distinct approaches to solve this problem.
2. Critique each approach for completeness and accuracy.
3. Select the best approach.
4. Execute the best approach using available tools if necessary.
5. Provide a comprehensive final answer.

Output your internal monologue and then the final answer.
"""
