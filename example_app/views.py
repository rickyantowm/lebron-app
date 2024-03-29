from django.shortcuts import render, redirect
from SPARQLWrapper import SPARQLWrapper, JSON
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

namespace = "kb"
sparql = SPARQLWrapper("http://35.230.101.94:8889/bigdata/namespace/"+ namespace + "/sparql")
sparql.setReturnFormat(JSON)

def index(request):
    return render(request, 'index.html')


def search_result(request):
  response = {}
  search = request.POST['search']
  search = search.lower()
  sparql.setQuery("""prefix :      <http://127.0.0.1:8000/rdf-data/> 
  prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
  prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> 

  SELECT DISTINCT ?entity_uri ?player_name ?country_name ?player_wiki_uri (group_concat(distinct ?team_name;separator=", ") as ?teams)
  WHERE{
      ?entity_uri rdfs:label ?player_name .
      ?entity_uri rdf:type :BasketballPlayer .
      FILTER contains(LCASE(?player_name),"%s")
      ?entity_uri :season ?seasons .
    ?seasons :hasTeam ?team .
      ?team rdfs:label ?team_name .
    ?entity_uri :country ?country .
      ?country rdfs:label ?country_name .
      ?entity_uri :player_iri ?player_wiki_uri
      
      FILTER(strlen(?team_name) > 3)
  }GROUP BY ?entity_uri ?player_name ?country_name ?player_wiki_uri""" % search)

  sparql.setReturnFormat(JSON)
  results = sparql.query().convert()
  response['data'] = results["results"]["bindings"]
  if response['data'] == []:
    sparql.setQuery("""prefix :      <http://127.0.0.1:8000/rdf-data/> 
    prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#>  
    prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 

    SELECT DISTINCT ?player_name 
    WHERE{
        ?player rdf:type :BasketballPlayer .
        ?player rdfs:label ?player_name .
    }
    """)
    results2 = sparql.query().convert()
    dat = results2["results"]["bindings"]
    aa = {}
    for i in range(len(dat)):
      ratio = fuzz.ratio(search, dat[i]["player_name"]["value"].lower())
      if ratio >= 50:
        aa[dat[i]["player_name"]["value"]] = ratio

    sorted_aa = sorted(aa.items(), key=lambda x:x[1], reverse=True)
    if len(sorted_aa) > 5:
      sorted_aa = sorted_aa[0:5]

    for i in range(0, len(sorted_aa)):
      for j in sorted_aa[i]:
        if (type(j) == str):
          sorted_aa[i] = j

    response['similar'] = sorted_aa
  
  response['search'] = request.POST['search']
  return render(request, 'search_result.html', response)

def get_player_detail(request, wiki_uri, entity_uri):
  response = {}
  player = entity_uri.split("+")
  search = ""
  for i in player:
    search += i + " "
  search = search[0:len(search)]
  wiki_uri = "<http://www.wikidata.org/entity/" + wiki_uri + ">"
  entity_uri = "<http://127.0.0.1:8000/rdf-data/" + entity_uri + ">"

  sparql.setQuery("""prefix :      <http://127.0.0.1:8000/rdf-data/> 
  prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#>  

  SELECT DISTINCT ?season_name ?age ?team_name ?team_iri ?gp ?height ?weight ?net_rating ?ts_pct ?usg_pct ?dreb_pct ?oreb_pct ?reb ?ast_pct ?ast ?pts
  WHERE{
      %s :season ?seasons .
      ?seasons :hasSeason ?season_name .
      ?seasons :hasAge ?age .
      ?seasons :hasAst ?ast .
      ?seasons :hasAst_pct ?ast_pct .
      ?seasons :hasDreb_pct ?dreb_pct .
      ?seasons :hasGp ?gp .         
      ?seasons :hasHeight ?height .
      ?seasons :hasNet_rating ?net_rating .
      ?seasons :hasOreb_pct ?oreb_pct .
      ?seasons :hasPts ?pts .
      ?seasons :hasReb ?reb .
      ?seasons :hasTeam ?team .
      ?team :teamIri ?team_iri .
      ?team rdfs:label ?team_name .
      ?seasons :hasTs_pct ?ts_pct .
      ?seasons :hasUsg_pct ?usg_pct .
      ?seasons :hasWeight ?weight .
      FILTER(strlen(?team_name) > 3)
  }
  order by ?season_name""" % entity_uri)

  sparql.setReturnFormat(JSON)
  results = sparql.query().convert()
  #data = TABEL YG points assist rebound
  response['data'] = results["results"]["bindings"]

  sparql.setQuery("""prefix :      <http://127.0.0.1:8000/rdf-data/> 
  prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> 
  PREFIX wdt: <http://www.wikidata.org/prop/direct/>

  SELECT ?positions ?image ?nickname ?jersey_number 
  WHERE {
    SERVICE <https://query.wikidata.org/sparql> {
      {
  select ?image (group_concat(distinct ?label_pos;separator=", ") as ?positions) ?nickname (group_concat(distinct ?jersey;separator=", ") as ?jersey_number)
  where {
    OPTIONAL{%s wdt:P413 ?pos .
    ?pos rdfs:label ?label_pos .}
    OPTIONAL{%s wdt:P18 ?image .}
    OPTIONAL{%s wdt:P1449 ?nickname .}
    OPTIONAL{%s wdt:P1618 ?jersey}
    FILTER (lang(?label_pos) = 'en')

  }GROUP BY ?image ?nickname
  ORDER BY DESC(?year)                                                              
      }
    }
  }""" % (wiki_uri, wiki_uri, wiki_uri, wiki_uri))

  results = sparql.query().convert()
  response['data2'] = results["results"]["bindings"]

  sparql.setQuery("""prefix :      <http://127.0.0.1:8000/rdf-data/> 
  prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> 
  PREFIX p: <http://www.wikidata.org/prop/>
  PREFIX ps: <http://www.wikidata.org/prop/statement/>
  PREFIX pq: <http://www.wikidata.org/prop/qualifier/>

  SELECT ?award_name (group_concat(distinct ?year;separator=", ") as ?years) WHERE {
    SERVICE <https://query.wikidata.org/sparql> {
      {
  select ?award_name ?year
  where {
    OPTIONAL{%s p:P166 ?statement .
          ?statement ps:P166 ?award .
          ?statement pq:P585 ?time .
          ?award rdfs:label ?award_name .
          BIND (year(?time) AS ?year)}
    FILTER (lang(?award_name) = 'en')
  }
  ORDER BY ASC(?year)                                                              
      }
    }
  }GROUP BY ?award_name ?count""" % (wiki_uri))

  results = sparql.query().convert()
  response['data3'] = results["results"]["bindings"]

  sparql.setQuery("""prefix : <http://127.0.0.1:8000/rdf-data/> 
  prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#>  

  SELECT DISTINCT ?player_name ?college_name ?college_iri ?draft_number ?draft_round ?draft_year
  WHERE{
      %s rdfs:label ?player_name ;
        :draft_number ?draft_number;
        :draft_round ?draft_round ;
        :draft_year ?draft_year .
      OPTIONAL{%s :college ?college .
      ?college rdfs:label ?college_name .
      ?college :college_iri ?college_iri .}
  }
  LIMIT 1""" % (entity_uri, entity_uri))

  results = sparql.query().convert()
  response['data4'] = results["results"]["bindings"]
  response['search'] = search
  return render(request, 'player_detail.html', response)

def get_detail_college(request, college_uri):
  response = {}
  wiki_uri = "<http://www.wikidata.org/entity/" + college_uri + ">"

  sparql.setQuery("""prefix :      <http://127.0.0.1:8000/rdf-data/> 
  prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> 
  PREFIX wdt: <http://www.wikidata.org/prop/direct/>

  SELECT ?label_univ ?univ_logo ?address ?student_count ?postal_code ?official_web
  WHERE {
    SERVICE <https://query.wikidata.org/sparql> {
      {
  select ?label_univ ?univ_logo ?address ?postal_code ?official_web ?student_count
  where {
    OPTIONAL {%s rdfs:label ?label_univ}
    OPTIONAL{%s wdt:P154 ?univ_logo }
    OPTIONAL{%s wdt:P6375 ?address }
    OPTIONAL{%s wdt:P1618 ?postal_code }
    OPTIONAL{%s wdt:P856 ?official_web }
    OPTIONAL{%s wdt:P2196 ?student_count }
    FILTER (lang(?label_univ) = 'en')

  }                                                            
      }
    }
  }""" % (wiki_uri, wiki_uri, wiki_uri, wiki_uri, wiki_uri, wiki_uri))

  sparql.setReturnFormat(JSON)
  results = sparql.query().convert()
  #data = Tabel College
  response['data'] = results["results"]["bindings"]
  response['search'] = response['data'][0]['label_univ']['value']

  return render(request,"college_detail.html", response)

def get_detail_team(request, team_uri):
  response = {}
  wiki_uri = "<http://www.wikidata.org/entity/" + team_uri + ">"

  sparql.setQuery("""prefix :      <http://127.0.0.1:8000/rdf-data/> 
  prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> 
  PREFIX wdt: <http://www.wikidata.org/prop/direct/>

  SELECT ?label_team ?team_logo ?label_country ?label_head_coach ?label_home_venue
  WHERE {
    SERVICE <https://query.wikidata.org/sparql> {
      {
  select ?label_team ?team_logo ?label_country ?label_head_coach ?label_home_venue
  where {
    OPTIONAL {%s rdfs:label ?label_team}
    OPTIONAL{%s wdt:P154 ?team_logo}
    OPTIONAL{%s wdt:P17 ?country .
    ?country rdfs:label ?label_country . }
    OPTIONAL{%s wdt:P286 ?head_coach .
    ?head_coach rdfs:label ?label_head_coach . }
    OPTIONAL{%s wdt:P115 ?home_venue .
    ?home_venue rdfs:label ?label_home_venue .}
    FILTER (lang(?label_team) = 'en')
    FILTER (lang(?label_country) = 'en')
    FILTER (lang(?label_head_coach) = 'en')
    FILTER (lang(?label_home_venue) = 'en')

  }                                                            
      }
    }
  }""" % (wiki_uri, wiki_uri, wiki_uri, wiki_uri, wiki_uri))

  sparql.setReturnFormat(JSON)
  results = sparql.query().convert()
  #data = Tabel College
  response['data'] = results["results"]["bindings"]
  response['search'] = response['data'][0]['label_team']['value']

  return render(request, "team_detail.html", response)