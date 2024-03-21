import requests
import openai
from openai.error import RateLimitError
from prettytable import PrettyTable
import pandas as pd
import time

# Set up OpenAI API
openai.api_key = ''

# Predefined SPARQL queries
sparql_queries = [
    "SELECT ?country WHERE {?country a dbo:Country .} LIMIT 5",
    "SELECT ?person WHERE {?person a dbo:Person .} LIMIT 5",
    "SELECT DISTINCT ?lat ?lng where{ <http://dbpedia.org/resource/Bristol> <http://www.w3.org/2003/01/geo/wgs84_pos#lat> ?lat; <http://www.w3.org/2003/01/geo/wgs84_pos#long> ?lng.}",
    "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX foaf: <http://xmlns.com/foaf/0.1/> SELECT ?person ?name WHERE { ?person rdf:type foaf:Person . ?person foaf:name ?name . } LIMIT 5",
    "PREFIX owl: <http://www.w3.org/2002/07/owl#> PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-Schema#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX foaf: <http://xmlns.com/foaf/0.1/> PREFIX dc: <http://purl.org/dc/elements/1.1/> PREFIX : <http;//dbpedia.org/resource/> PREFIX dbpedia2: <http://dbpedia.org/property/> Prefix dbpedia: <http://dbpedia.org/> PREFIX skos: <http://www.w3.org/2004/02/skos/core#> SELECT * where { ?city foaf:homepage ?homepage . ?country rdf:type <http://dbpedia.org/ontology/Country> . ?country <http://dbpedia.org/ontology/capital> ?city . } LIMIT 5",
    "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#> PREFIX foaf:<http://xmlns.com/foaf/0.1/> SELECT DISTINCT ?title ?page ?lat ?long where {?link rdfs:label ?title; foaf:isPrimaryTopicOf ?page; geo:lat ?lat; geo:long ?long . FILTER (regex(?title, 'West Sussex', 'i')) } LIMIT 2",
    "SELECT ?property ?hasValue ?isValueOf where { { <http://dbpedia.org/resource/%C3%88ve_Curie> ?property ?hasValue }   UNION   { ?isValueOf ?property <http://dbpedia.org/resource/%C3%88ve_Curie> } } LIMIT 3",
    "PREFIX owl: <http://www.w3.org/2002/07/owl#> PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX foaf: <http://xmlns.com/foaf/0.1/> PREFIX dc: <http://purl.org/dc/elements/1.1/> PREFIX : <http://dbpedia.org/resource/> PREFIX dbpedia2: <http://dbpedia.org/property/> PREFIX dbpedia: <http://dbpedia.org/> PREFIX skos: <http://www.w3.org/2004/02/skos/core#> SELECT ?state ?population where {   ?state rdf:type <http://dbpedia.org/class/yago/State108168978>.   ?state dbpedia2:populationEstimate ?population   FILTER(xsd:Integer(?population) > '10000000'^^xsd:Integer).    OPTIONAL { ?state dbpedia2:yearEnd ?yearEnd }   FILTER (!bound(?yearEnd))  }",
    "SELECT  ?relation ?relationLabel ?object ?objectLabel where { <http://dbpedia.org/resource/Eyes_Wide_Shut> ?relation ?object.?relation <http://www.w3.org/2000/01/rdf-schema#label> ?relationLabel . ?object <http://www.w3.org/2000/01/rdf-schema#label> ?objectLabel . FILTER (langMatches(lang(?relationLabel), 'EN')) . FILTER (langMatches(lang(?objectLabel), 'EN')) . } LIMIT 2",
    "SELECT DISTINCT count( ?person ) where {   ?person  skos:broader ?f . }",
    "select distinct ?Concept where {[] a ?Concept} LIMIT 10",
    "PREFIX owl: <http://www.w3.org/2002/07/owl#> PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX foaf: <http://xmlns.com/foaf/0.1/> PREFIX dc: <http://purl.org/dc/elements/1.1/> PREFIX : <http://dbpedia.org/resource/> PREFIX dbpedia2: <http://dbpedia.org/property/> PREFIX dbpedia: <http://dbpedia.org/> PREFIX skos: <http://www.w3.org/2004/02/skos/core#> SELECT * where {   :United_Reformed_Churches_in_North_America ?p ?o. } Limit 2",
    "PREFIX owl: <http://www.w3.org/2002/07/owl#>  PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>  PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>  PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>  PREFIX foaf: <http://xmlns.com/foaf/0.1/>  PREFIX dc: <http://purl.org/dc/elements/1.1/>  PREFIX : <http://dbpedia.org/resource/>  PREFIX dbpedia2: <http://dbpedia.org/property/>  PREFIX dbpedia: <http://dbpedia.org/>  PREFIX skos: <http://www.w3.org/2004/02/skos/core#>  SELECT *  where { ?subject <http://purl.org/dc/terms/subject> <http://dbpedia.org/resource/Category:Car_manufacturers>. } LIMIT 7",
    "PREFIX owl: <http://www.w3.org/2002/07/owl#> PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX foaf: <http://xmlns.com/foaf/0.1/> PREFIX dc: <http://purl.org/dc/elements/1.1/> PREFIX : <http://dbpedia.org/resource/> PREFIX dbpedia2: <http://dbpedia.org/property/> PREFIX dbpedia: <http://dbpedia.org/> PREFIX skos: <http://www.w3.org/2004/02/skos/core#> PREFIX dbowl: <http://dbpedia.org/ontology/> PREFIX dc2: <http://purl.org/dc/terms/> PREFIX cat: <http://dbpedia.org/resource/Category:>  SELECT ?person where {     ?person a foaf:Person .    ?person dc2:subject cat:American_film_actors .    }  limit 4",
    "SELECT distinct ?city where  { [] <http://dbpedia.org/ontology/city> ?city } LIMIT 5 OFFSET 500",
    "PREFIX owl: <http://www.w3.org/2002/07/owl#> PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX foaf: <http://xmlns.com/foaf/0.1/> PREFIX dc: <http://purl.org/dc/elements/1.1/> PREFIX : <http://dbpedia.org/resource/> PREFIX dbpedia2: <http://dbpedia.org/property/> PREFIX dbpedia: <http://dbpedia.org/> PREFIX skos: <http://www.w3.org/2004/02/skos/core#> SELECT * where { ?subject <http://purl.org/dc/terms/subject> <http://dbpedia.org/resource/Category:National_Basketball_Association_teams>. } Limit 10",
    "PREFIX owl: <http://www.w3.org/2002/07/owl#> PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX foaf: <http://xmlns.com/foaf/0.1/> PREFIX dc: <http://purl.org/dc/elements/1.1/> PREFIX : <http://dbpedia.org/resource/> PREFIX dbpedia2: <http://dbpedia.org/property/> PREFIX dbpedia: <http://dbpedia.org/> PREFIX skos: <http://www.w3.org/2004/02/skos/core#> SELECT ?subject ?population  where { ?subject rdf:type <http://dbpedia.org/ontology/City>. ?subject <http://dbpedia.org/ontology/populationUrban> ?population. FILTER (xsd:integer(?population) > 2000000) } ORDER BY DESC(xsd:integer(?population)) LIMIT 5",
    "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>   SELECT Count(distinct ?film_title) where { ?film_title rdf:type <http://dbpedia.org/ontology/Film> . ?film_title rdfs:comment ?film_abstract  }",
    "select distinct ?property ?label where { [] a <http://dbpedia.org/ontology/Mountain>; ?property [].OPTIONAL{ ?property rdfs:label ?label. } FILTER (langMatches(lang(?label),'en'))}  limit 10",
    "SELECT DISTINCT ?s ?label where {?s rdfs:label ?label . FILTER (lang(?label) = 'en'). ?label bif:contains 'Obama' . ?s dcterms:subject ?sub  } LIMIT 5",
    "SELECT DISTINCT ?resource ?label where {?resource rdfs:label ?label . FILTER (lang(?label) = 'en'). ?label bif:contains 'Ferrar' . ?resource dcterms:subject ?sub  } LIMIT 4",
    "PREFIX owl: <http://www.w3.org/2002/07/owl#> PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX foaf: <http://xmlns.com/foaf/0.1/> PREFIX dc: <http://purl.org/dc/elements/1.1/> PREFIX : <http://dbpedia.org/resource/> PREFIX dbpedia2: <http://dbpedia.org/property/> PREFIX dbpedia: <http://dbpedia.org/> PREFIX skos: <http://www.w3.org/2004/02/skos/core#> SELECT DISTINCT ?subject ?employees ?homepage where { ?subject  rdf:type <http://dbpedia.org/class/yago/Company108058098>  .       ?subject  dbpedia2:numEmployees  ?employees         FILTER  ( xsd:integer(?employees) >= 50000 )                                     . ?subject  foaf:homepage ?homepage . }    ORDER BY  DESC(xsd:integer(?employees))   LIMIT  4",
    "PREFIX owl: <http://www.w3.org/2002/07/owl#> PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX foaf: <http://xmlns.com/foaf/0.1/> PREFIX dc: <http://purl.org/dc/elements/1.1/> PREFIX : <http://dbpedia.org/resource/> PREFIX dbpedia2: <http://dbpedia.org/property/> PREFIX dbpedia: <http://dbpedia.org/> PREFIX skos: <http://www.w3.org/2004/02/skos/core#> PREFIX dbo: <http://dbpedia.org/ontology/>  SELECT ?name ?birth ?death ?person where {?person dbo:birthPlace :Berlin . ?person dbo:birthDate ?birth . ?person foaf:name ?name . ?person dbo:deathDate ?death .FILTER (?birth < '1900-01-01'^^xsd:date) . } ORDER BY ?name LIMIT 5",
    "PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>PREFIX p: <http://dbpedia.org/property/>PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>SELECT * where {<http://dbpedia.org/resource/Arsenal_F.C.> p:name ?player.?player dbpedia-owl:birthPlace ?city;  dbpedia-owl:birthDate ?dob.} LIMIT 7",
    "PREFIX owl: <http://www.w3.org/2002/07/owl#> PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX foaf: <http://xmlns.com/foaf/0.1/> PREFIX dc: <http://purl.org/dc/elements/1.1/> PREFIX : <http://dbpedia.org/resource/> PREFIX dbpedia2: <http://dbpedia.org/property/> PREFIX dbpedia: <http://dbpedia.org/> PREFIX skos: <http://www.w3.org/2004/02/skos/core#> PREFIX dbo: <http://dbpedia.org/ontology/>  SELECT ?name ?birth ?death ?person  where {      ?person dbpedia2:birthPlace <http://dbpedia.org/resource/Seoul> .      ?person dbo:birthDate ?birth .      ?person foaf:name ?name .      ?person dbo:deathDate ?death . } LIMIT 3",
    "PREFIX owl: <http://www.w3.org/2002/07/owl#> PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX foaf: <http://xmlns.com/foaf/0.1/> PREFIX dc: <http://purl.org/dc/elements/1.1/> PREFIX : <http://dbpedia.org/resource/> PREFIX dbpedia2: <http://dbpedia.org/property/> PREFIX dbpedia: <http://dbpedia.org/> PREFIX skos: <http://www.w3.org/2004/02/skos/core#> PREFIX onto: <http://dbpedia.org/ontology/> SELECT (str(?name) as ?result) ?page where {      ?band rdf:type <http://dbpedia.org/ontology/Band> .      ?band onto:genre :Indie_rock .      ?band rdfs:label ?name .      FILTER (LANG(?name) = 'en') .      ?band foaf:isPrimaryTopicOf ?page       } ORDER BY ?name LIMIT 4",
    "select (MIN(?l3) as ?l3)  (MIN(?l2) as ?l2)  ?c where {?c rdfs:label 'Paris'@en. ?c rdfs:label ?l3. ?c rdf:type ?t. ?t rdfs:label ?l2. } group by ?c  order by ?l3",
    "select ?actor where { <http://dbpedia.org/resource/The_Butcher_Boy_(1917_film)> <http://dbpedia.org/ontology/starring> ?actor. }",
    "select ?director where { <http://dbpedia.org/resource/The_Moon_Is_Blue> <http://dbpedia.org/ontology/director> ?director. }",
    "select ?lan where { <http://dbpedia.org/resource/The_Way_of_the_Gun> <http://dbpedia.org/property/language> ?lan. }",
    "select ?date where { <http://dbpedia.org/resource/Lone_Wolf_McQuade> <http://dbpedia.org/ontology/releaseDate> ?date. }",
    "select ?date where { <http://dbpedia.org/resource/Festival_in_Cannes> <http://dbpedia.org/ontology/releaseDate> ?date. }",
    "select ?con from <http://dbpedia3.8> where { <http://dbpedia.org/resource/Sonnenallee> <http://dbpedia.org/property/country> ?con. }",
    "SELECT DISTINCT * where {<http://dbpedia.org/resource/Category:Biology> ?property ?object.FILTER ((( isIRI(?object) && ?property != <http://xmlns.com/foaf/0.1/depiction> )|| ?property = <http://www.w3.org/2000/01/rdf-schema#label>  || ?property = <http://www.georss.org/georss/point> || ?property = <http://xmlns.com/foaf/0.1/surname> || ?property = <http://xmlns.com/foaf/0.1/name> || ?property = <http://purl.org/dc/elements/1.1/title>))}  ORDER BY ?property",
    "PREFIX owl: <http://www.w3.org/2002/07/owl#> PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX foaf: <http://xmlns.com/foaf/0.1/> PREFIX dc: <http://purl.org/dc/elements/1.1/> PREFIX : <http://dbpedia.org/resource/> PREFIX dbpedia2: <http://dbpedia.org/property/> PREFIX dbpedia: <http://dbpedia.org/> PREFIX skos: <http://www.w3.org/2004/02/skos/core#> PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>         SELECT * where {         ?s a dbo:Place  .         ?s geo:lat ?lat .         ?s geo:long ?long .   FILTER (?lat > 15  && ?lat < 20) .      FILTER (?long > 15 && ?long < 20) .  }",
    "SELECT ?property ?hasValue ?isValueOf where {   { <http://dbpedia.org/resource/Real_Madrid_C.F.> ?property ?hasValue }   UNION   { ?isValueOf ?property <http://dbpedia.org/resource/Real_Madrid_C.F.> } } LIMIT 3",
    "PREFIX owl: <http://www.w3.org/2002/07/owl#> PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX foaf: <http://xmlns.com/foaf/0.1/> PREFIX dc: <http://purl.org/dc/elements/1.1/> PREFIX : <http://dbpedia.org/resource/> PREFIX dbpedia2: <http://dbpedia.org/property/> PREFIX dbpedia: <http://dbpedia.org/> PREFIX skos: <http://www.w3.org/2004/02/skos/core#> PREFIX dbpedia-owl: <http://dbpedia.org/ontology/> PREFIX dct: <http://purl.org/dc/terms/>  SELECT *  where{     { ?team a dbpedia-owl:SportsTeam }    }  Limit 3",
    "PREFIX owl: <http://www.w3.org/2002/07/owl#> PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX foaf: <http://xmlns.com/foaf/0.1/> PREFIX dc: <http://purl.org/dc/elements/1.1/> PREFIX : <http://dbpedia.org/resource/> PREFIX dbpedia2: <http://dbpedia.org/property/> PREFIX dbpedia: <http://dbpedia.org/> PREFIX skos: <http://www.w3.org/2004/02/skos/core#> PREFIX dbo: <http://dbpedia.org/ontology/>  SELECT ?manufacturer ?name ?car where {     ?car <http://purl.org/dc/terms/subject> <http://dbpedia.org/resource/Category:Luxury_vehicles> .     ?car foaf:name ?name .     ?car dbo:manufacturer ?man .     ?man foaf:name ?manufacturer } ORDER by ?manufacturer ?name LIMIT 5",
    "SELECT ?film WHERE { ?film rdf:type dbo:Film . } LIMIT 5",
    "SELECT ?book WHERE { ?book rdf:type dbo:Book . } LIMIT 5",
    "SELECT ?actor WHERE { ?actor rdf:type dbo:Actor . } LIMIT 5",
    "SELECT ?director WHERE { ?director rdf:type dbo:Director . } LIMIT 5",
    "SELECT ?album WHERE { ?album rdf:type dbo:Album . } LIMIT 5",
    "SELECT ?song WHERE { ?song rdf:type dbo:Song . } LIMIT 5",
    "SELECT ?painting WHERE { ?painting rdf:type dbo:Painting . } LIMIT 5",
    "SELECT ?sculpture WHERE { ?sculpture rdf:type dbo:Sculpture . } LIMIT 5",
    "SELECT ?author WHERE { ?author rdf:type dbo:Author . } LIMIT 5",
    "SELECT ?architect WHERE { ?architect rdf:type dbo:Architect . } LIMIT 5",
    "SELECT ?athlete WHERE { ?athlete rdf:type dbo:Athlete . } LIMIT 5",
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
    return "No answer"

# Function to generate plain English expressions using ChatGPT
def generate_plain_english(query, answers):
    final_answer = []
    if answers != "No answer":
        final_answer = ", ".join(answers)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Query: {query}\nAnswer: {final_answer}\nTranslate the question and answer into plain English. Make complete question and answer. The question/answer should not be splited in many rows. When mentioning the classifier remove the dbo from the word. The prefix is good. Mention the number it should give as an example in the question if no filter is atributed. Get creative with the guestion and answer. Avoid using separated lines and present them more like a phrase. If no answer is available say that you don't know."},
            ],
            max_tokens=1500
        )
        return response['choices'][0]['message']['content']
    except RateLimitError as e:
        print(f"Rate limit reached. Waiting for 20 seconds before retrying.")
        time.sleep(20)  # Wait for 20 seconds before retrying
        return generate_plain_english(query, answers)  # Retry the request

# Main function
def main():
    # Present results in a table format
    table = PrettyTable(["Nr", "Query", "Question", "Answer"])
    table.max_width["Nr"] = 5
    table.max_width["Query"] = 20
    table.max_width["Question"] = 20
    table.max_width["Answer"] = 20

    saved_queries = pd.DataFrame()
    filtered_sparql_queries = []
    try:
        saved_queries = pd.read_csv("output.csv", header=0);
        filtered_sparql_queries = [i for i in sparql_queries if i not in list(saved_queries["Query"])]

    except pd.errors.EmptyDataError:
        saved_queries = pd.DataFrame();
        filtered_sparql_queries = [];
    i = 1
    for query in filtered_sparql_queries:
        answer = execute_sparql_query(query)
        english_expression = generate_plain_english(query, answer)

        # Add results to PrettyTable
        phrase = english_expression.split("\n", 2)
        saved_queries.loc[len(saved_queries)] = [len(saved_queries) + 1, query, phrase[0], phrase[2]]
        table.add_row([i, query, phrase[0], phrase[2]], divider = True)
        i = i + 1
    print(table)

    saved_queries.to_csv("output.csv", index=False)

if __name__ == "__main__":
    main()
