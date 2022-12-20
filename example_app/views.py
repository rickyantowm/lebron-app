from django.shortcuts import render
from SPARQLWrapper import SPARQLWrapper, JSON

def index(request):
    return render(request, 'index.html')


def search_result(request):
    response = {}
    search = request.POST['search']
    namespace = "kb"
    sparql = SPARQLWrapper("http://localhost:9999/blazegraph/namespace/"+ namespace + "/sparql")

    sparql.setQuery("""prefix :      <http://127.0.0.1:8000/rdf-data/> 
prefix owl:   <http://www.w3.org/2002/07/owl#> 
prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> 
prefix team:  <http://www.example.org/data/team#> 
prefix v:     <http://www.example.org/vocab#> 
prefix vcard: <http://www.w3.org/2006/vcard/ns#>
prefix xsd:   <http://www.w3.org/2001/XMLSchema#> 
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wds: <http://www.wikidata.org/entity/statement/>
PREFIX wdv: <http://www.wikidata.org/value/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX ps: <http://www.wikidata.org/prop/statement/>
PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
PREFIX bd: <http://www.bigdata.com/rdf#>


SELECT DISTINCT ?player_name ?country_name ?positions ?image WHERE {
  SERVICE <https://query.wikidata.org/sparql> {
    {
select DISTINCT ?player_name ?country_name ?player_iri ?image (group_concat(distinct ?label_pos;separator=", ") as ?positions) ?followers
where {
  ?player_iri wdt:P413 ?pos .
  ?pos rdfs:label ?label_pos .
  OPTIONAL{?player_iri wdt:P18 ?image .}
  OPTIONAL{?player_iri wdt:P8687 ?followers .}
  FILTER (lang(?label_pos) = 'en')
}GROUP BY ?player_name ?country_name ?player_iri ?image ?followers
    }
  }
{SELECT DISTINCT ?player_name ?country_name ?player_iri
WHERE {
  ?root rdfs:label ?player_name .
  ?root :country ?country .
  ?country rdfs:label ?country_name .
  ?root :player_iri ?player_iri
  FILTER contains(LCASE(?player_name), "%s")
}}
}ORDER BY DESC (xsd:integer(?followers))""" % search)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    response['data'] = results["results"]["bindings"]
    response['search'] = search

    print(search)
    print(response['data'])
    print(results)


    return render(request, 'search_result.html', response)



# response['data'] = [{ 'player_name' : { 'value': "Keren"},
#       "country_name": {"value": "Keren"},
#       "positions": {"value": "Keren"},
#       "image": { "value": "https://media.discordapp.net/attachments/876950446479126529/1054665731763077170/075474300_1599984513-LA_Lakers_Vs_Houston_Rockets_01-removebg-preview.png?width=303&height=30"}}
#     ]