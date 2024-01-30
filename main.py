import requests
import openai

# Set up OpenAI API
openai.api_key = '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'

# Predefined SPARQL queries
sparql_queries = [
    "SELECT ?country WHERE {?country a dbo:Country .} LIMIT 5",
    "SELECT ?person WHERE {?person a dbo:Person .} LIMIT 5",
    # Add more queries as needed
]

# Function to execute SPARQL queries and retrieve answers
def execute_sparql_query(query):
    # DBPEDIA SPARQL endpoint
    endpoint = "http://dbpedia.org/sparql"
    # Set up the query parameters
    params = {
        "format": "json",
        "query": query
    }
    # Execute the query
    response = requests.get(endpoint, params=params)
    # Extract the answer from the response
    data = response.json()
    if "results" in data and "bindings" in data["results"]:
        bindings = data["results"]["bindings"]
        if bindings:
            return bindings[0].get(list(bindings[0].keys())[0], {}).get("value", "No answer")
    return "No answer"

# Function to generate plain English expressions using ChatGPT
# Function to generate plain English expressions using ChatGPT
def generate_plain_english(query, answer):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Query: {query}\nAnswer: {answer}\nTranslate the question and answer into plain English."},
        ],
        max_tokens=150
    )
    return response['choices'][0]['message']['content']




# Main function
def main():
    query_answers = {}
    english_expressions = {}

    # Execute queries and retrieve answers
    for query in sparql_queries:
        answer = execute_sparql_query(query)
        query_answers[query] = answer

    # Generate plain English expressions using ChatGPT
    for query, answer in query_answers.items():
        english_expressions[query] = generate_plain_english(query, answer)

    # Present results in a table format
    print("-----------------------------------------------------------------------------")
    print("| Query                                              | Answer                |")
    print("-----------------------------------------------------------------------------")
    for query, answer in query_answers.items():
        print(f"| {query:<50} | {answer:<20} |")
    print("-----------------------------------------------------------------------------")
    print("\nPlain English Expressions:")
    for query, expression in english_expressions.items():
        print(f"Query: {query}\nPlain English: {expression}\n")

if __name__ == "__main__":
    main()
