from django.shortcuts import render
from SPARQLWrapper import SPARQLWrapper, JSON

namespace = "kb"
sparql = SPARQLWrapper("http://localhost:9999/blazegraph/namespace/"+ namespace + "/sparql")

def index(request):
    return render(request, 'index.html')


def search_result(request):
    response = {}
    search = request.POST['search']
    sparql.setQuery("""prefix :      <http://127.0.0.1:8000/rdf-data/> 
prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> 

SELECT DISTINCT ?root ?player_name ?country_name ?player_iri (group_concat(distinct ?team_name;separator=", ") as ?teams)
WHERE{
    ?root rdfs:label ?player_name .
    FILTER contains(LCASE(?player_name),"%s")
    ?root :season ?seasons .
	?seasons :hasTeam ?team .
    ?team rdfs:label ?team_name .
 	?root :country ?country .
    ?country rdfs:label ?country_name .
  	?root :player_iri ?player_iri
  	
    FILTER(strlen(?team_name) > 3)
}GROUP BY ?root ?player_name ?country_name ?player_iri""" % search)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    response['data'] = results["results"]["bindings"]
    return render(request, 'search_result.html', response)

def get_player_detail(request):
  print(request)
  data = dict(request.POST)
  print(data)

  return render(request, 'search_result.html', {})