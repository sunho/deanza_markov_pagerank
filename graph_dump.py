from collections import deque
from bs4 import BeautifulSoup
import requests
import json
 
WIKI_URL = 'https://en.wikipedia.org/wiki/{}'
STARTER = "San_Jose,_California"
MAX_DEPTH = 2
banned = ['ISBN_(identifier)', "Georgia_Institute_of_Technology", "History_of_Lorentz_transformations"]
def get_links_from_one_page(body: str):
  doc = BeautifulSoup(body)
  # get main content
  content = doc.find_all("div", {"id": "mw-content-text"})[0].find_all('p')
  out = set()
  def process_one(one):
    # filter and preprocess the stuffs
    links = map(lambda x: x.get('href'), one.find_all("a"))
    def filter_non_wiki(x):
      if x is None:
        return False
      return x.startswith('/wiki')
    links = filter(filter_non_wiki, links)
    def filter_special(x):
      specials = ['Category', 'File', 'Portal', 'Help', 'Wikipedia', 'Special']
      for s in specials:
        if x.startswith('/wiki/{}:'.format(s)):
          return False
      return True
    links = filter(filter_special, links)
    links = map(lambda x: x[len('/wiki/'):], links)
    def filter_ban(x):
      return x not in banned
    links = filter(filter_ban, links)
    for l in links:
      out.add(l)
  for c in content:
    process_one(c)
  # remove duplicates
  return [*out]

def get_links_from_doc(doc: str):
  url = WIKI_URL.format(doc)
  r = requests.get(url)
  return get_links_from_one_page(r.text)

visited = set()

q = deque()
q.append((STARTER, 0))

graph = {}

# BFS
while q:
  doc, depth = q.popleft()
  print("processing: " + doc)
  if depth >= MAX_DEPTH:
    continue
  links = get_links_from_doc(doc)
  graph[doc] = links
  for u in links:
    if u in visited:
      continue
    q.append((u, depth+1))
    visited.add(u)

json_str = json.dumps(graph, indent=4)

with open("graph.json", "w") as outfile:
  outfile.write(json_str)