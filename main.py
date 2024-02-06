import requests
import openai
from prettytable import PrettyTable
import time

# Set up OpenAI API
openai.api_key = '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'

# Because of the requests per min (RPM): Limit 3 per request we are forced to use 3 per every Request.
# Predefined SPARQL queries
sparql_queries = [
     "SELECT ?country WHERE {?country a dbo:Country .} LIMIT 5",
     "SELECT ?person WHERE {?person a dbo:Person .} LIMIT 5",
     "SELECT DISTINCT ?lat ?lng where{ <http://dbpedia.org/resource/Bristol> <http://www.w3.org/2003/01/geo/wgs84_pos#lat> ?lat; <http://www.w3.org/2003/01/geo/wgs84_pos#long> ?lng.}",

    #"PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX foaf: <http://xmlns.com/foaf/0.1/> SELECT ?person ?name WHERE { ?person rdf:type foaf:Person . ?person foaf:name ?name . } LIMIT 5",
    # "PREFIX owl: <http://www.w3.org/2002/07/owl#> PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-Schema#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX foaf: <http://xmlns.com/foaf/0.1/> PREFIX dc: <http://purl.org/dc/elements/1.1/> PREFIX : <http;//dbpedia.org/resource/> PREFIX dbpedia2: <http://dbpedia.org/property/> Prefix dbpedia: <http://dbpedia.org/> PREFIX skos: <http://www.w3.org/2004/02/skos/core#> SELECT * where { ?city foaf:homepage ?homepage . ?country rdf:type <http://dbpedia.org/ontology/Country> . ?country <http://dbpedia.org/ontology/capital> ?city . } LIMIT 5",
    #"PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#> PREFIX foaf:<http://xmlns.com/foaf/0.1/> SELECT DISTINCT ?title ?page ?lat ?long where {?link rdfs:label ?title; foaf:isPrimaryTopicOf ?page; geo:lat ?lat; geo:long ?long . FILTER (regex(?title, 'West Sussex', 'i')) } LIMIT 2",

    # "SELECT ?property ?hasValue ?isValueOf where { { <http://dbpedia.org/resource/%C3%88ve_Curie> ?property ?hasValue }   UNION   { ?isValueOf ?property <http://dbpedia.org/resource/%C3%88ve_Curie> } } LIMIT 3",
    # "PREFIX owl: <http://www.w3.org/2002/07/owl#> PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX foaf: <http://xmlns.com/foaf/0.1/> PREFIX dc: <http://purl.org/dc/elements/1.1/> PREFIX : <http://dbpedia.org/resource/> PREFIX dbpedia2: <http://dbpedia.org/property/> PREFIX dbpedia: <http://dbpedia.org/> PREFIX skos: <http://www.w3.org/2004/02/skos/core#> SELECT ?state ?population where {   ?state rdf:type <http://dbpedia.org/class/yago/State108168978>.   ?state dbpedia2:populationEstimate ?population   FILTER(xsd:Integer(?population) > '10000000'^^xsd:Integer).    OPTIONAL { ?state dbpedia2:yearEnd ?yearEnd }   FILTER (!bound(?yearEnd))  }",
    # "SELECT  ?relation ?relationLabel ?object ?objectLabel where { <http://dbpedia.org/resource/Eyes_Wide_Shut> ?relation ?object.?relation <http://www.w3.org/2000/01/rdf-schema#label> ?relationLabel . ?object <http://www.w3.org/2000/01/rdf-schema#label> ?objectLabel . FILTER (langMatches(lang(?relationLabel), 'EN')) . FILTER (langMatches(lang(?objectLabel), 'EN')) . } LIMIT 2",

    # "SELECT DISTINCT count( ?person ) where {   ?person  skos:broader ?f . }",
    # "select distinct ?Concept where {[] a ?Concept} LIMIT 10",
   #  "PREFIX owl: <http://www.w3.org/2002/07/owl#> PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX foaf: <http://xmlns.com/foaf/0.1/> PREFIX dc: <http://purl.org/dc/elements/1.1/> PREFIX : <http://dbpedia.org/resource/> PREFIX dbpedia2: <http://dbpedia.org/property/> PREFIX dbpedia: <http://dbpedia.org/> PREFIX skos: <http://www.w3.org/2004/02/skos/core#> SELECT * from <http://dbpedia3.8> where {   :United_Reformed_Churches_in_North_America ?p ?o. } Limit 2",

    # "PREFIX owl: <http://www.w3.org/2002/07/owl#> PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX foaf: <http://xmlns.com/foaf/0.1/> PREFIX dc: <http://purl.org/dc/elements/1.1/> PREFIX : <http://dbpedia.org/resource/> PREFIX dbpedia2: <http://dbpedia.org/property/> PREFIX dbpedia: <http://dbpedia.org/> PREFIX skos: <http://www.w3.org/2004/02/skos/core#> PREFIX dbowl: <http://dbpedia.org/ontology/> PREFIX dc2: <http://purl.org/dc/terms/> PREFIX cat: <http://dbpedia.org/resource/Category:>  SELECT ?person where {     ?person a foaf:Person .    ?person dc2:subject cat:American_film_actors .    }  limit 4",
    # "select distinct ?city where  { [] <http://dbpedia.org/ontology/city> ?city } LIMIT 5 OFFSET 500",
    #"SELECT ?film WHERE { ?film rdf:type dbo:Film . } LIMIT 5",
    #"SELECT ?book WHERE { ?book rdf:type dbo:Book . } LIMIT 5",
    #"SELECT ?actor WHERE { ?actor rdf:type dbo:Actor . } LIMIT 5",
    #"SELECT ?director WHERE { ?director rdf:type dbo:Director . } LIMIT 5",
    #"SELECT ?album WHERE { ?album rdf:type dbo:Album . } LIMIT 5",
    #"SELECT ?song WHERE { ?song rdf:type dbo:Song . } LIMIT 5",
    #"SELECT ?painting WHERE { ?painting rdf:type dbo:Painting . } LIMIT 5",
    #"SELECT ?sculpture WHERE { ?sculpture rdf:type dbo:Sculpture . } LIMIT 5",
    #"SELECT ?author WHERE { ?author rdf:type dbo:Author . } LIMIT 5",
    #"SELECT ?architect WHERE { ?architect rdf:type dbo:Architect . } LIMIT 5",
    #"SELECT ?athlete WHERE { ?athlete rdf:type dbo:Athlete . } LIMIT 5",
    #"SELECT ?city WHERE { ?city rdf:type dbo:City . } LIMIT 5",
    #"SELECT ?river WHERE { ?river rdf:type dbo:River . } LIMIT 5",
    #"SELECT ?animal WHERE { ?animal rdf:type dbo:Animal . } LIMIT 5",
    #"SELECT ?plant WHERE { ?plant rdf:type dbo:Plant . } LIMIT 5",
    #"SELECT ?organization WHERE { ?organization rdf:type dbo:Organization . } LIMIT 5",
    #"SELECT ?company WHERE { ?company rdf:type dbo:Company . } LIMIT 5",
    #"SELECT ?university WHERE { ?university rdf:type dbo:University . } LIMIT 5",
    #"SELECT ?language WHERE { ?language rdf:type dbo:Language . } LIMIT 5",
    #"SELECT ?scientist WHERE { ?scientist rdf:type dbo:Scientist . } LIMIT 5",
    #"SELECT ?planet WHERE { ?planet rdf:type dbo:Planet . } LIMIT 5",
    #"SELECT ?asteroid WHERE { ?asteroid rdf:type dbo:Asteroid . } LIMIT 5",
    #"SELECT ?constellation WHERE { ?constellation rdf:type dbo:Constellation . } LIMIT 5",
    #"SELECT ?galaxy WHERE { ?galaxy rdf:type dbo:Galaxy . } LIMIT 5",
    #"SELECT ?comet WHERE { ?comet rdf:type dbo:Comet . } LIMIT 5",
    #"SELECT ?volcano WHERE { ?volcano rdf:type dbo:Volcano . } LIMIT 5",
    #"SELECT ?ocean WHERE { ?ocean rdf:type dbo:Ocean . } LIMIT 5",
    #"SELECT ?mountain WHERE { ?mountain rdf:type dbo:Mountain . } LIMIT 5",
    #"SELECT ?mineral WHERE { ?mineral rdf:type dbo:Mineral . } LIMIT 5",
    #"SELECT ?fossil WHERE { ?fossil rdf:type dbo:Fossil . } LIMIT 5",
    #"SELECT ?artifact WHERE { ?artifact rdf:type dbo:Artifact . } LIMIT 5",
    #"SELECT ?ruin WHERE { ?ruin rdf:type dbo:Ruin . } LIMIT 5",
    #"SELECT ?island WHERE { ?island rdf:type dbo:Island . } LIMIT 5",
    #"SELECT ?castle WHERE { ?castle rdf:type dbo:Castle . } LIMIT 5",
    #"SELECT ?cave WHERE { ?cave rdf:type dbo:Cave . } LIMIT 5",
    #"SELECT ?legend WHERE { ?legend rdf:type dbo:Legend . } LIMIT 5",
    #"SELECT ?myth WHERE { ?myth rdf:type dbo:Myth . } LIMIT 5",
    #"SELECT ?folklore WHERE { ?folklore rdf:type dbo:Folklore . } LIMIT 5",
    #"SELECT ?tradition WHERE { ?tradition rdf:type dbo:Tradition . } LIMIT 5",
    #"SELECT ?ritual WHERE { ?ritual rdf:type dbo:Ritual . } LIMIT 5"

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
            result = []
            for binding in bindings:
                for elem in range(len(binding.keys())):
                    result.append(binding.get(list(bindings[0].keys())[elem], {}).get("value", "No answer"))
            return result
            # return bindings[0].get(list(bindings[0].keys())[0], {}).get("value", "No answer")
    return "No answer"

# Function to generate plain English expressions using ChatGPT


def generate_plain_english(query, answers):
    final_answer = ""
    for answer in answers:
        final_answer += answer + ","

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Query: {query}\nAnswer: {final_answer}\nTranslate the question and answer into plain English. Make complete question and answer. The question/answer should not be splited in many rows. When mentioning the classifier remove the dbo from the word. The prefix is good. Mention the number it should give as an example in the question if no filter is atributed. Get creative with the guestion and answer"},
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
    print(query_answers)

    # Generate plain English expressions using ChatGPT
    for query, answers in query_answers.items():
        english_expressions[query] = generate_plain_english(query, answers)

    # Present results in a table format
    table = PrettyTable(["Nr", "Query", "Question", "Answer"])
    table.max_width["Nr"] = 5
    table.max_width["Query"] = 20
    table.max_width["Question"] = 20
    table.max_width["Answer"] = 20
    i = 1
    for query, expression in english_expressions.items():
        phrase = expression.split("\n", 2)
        table.add_row([i, query, phrase[0], phrase[2]], divider=True)
        i = i + 1
    print(table)


if __name__ == "__main__":
    main()