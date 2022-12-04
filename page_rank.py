import json
import numpy as np
from numpy.linalg import matrix_power
from numpy import linalg as LA

with open("graph.json", "r") as f:
  graph = json.loads(f.read())

n = len(graph)

# doc to doc id
next_id = 0
doc_to_id = {}
doc_names = []
for key, _ in graph.items():
  doc_to_id[key] = next_id
  doc_names.append(key)
  next_id+=1

A = np.zeros(shape=(n,n))
# construct markov matrix
for doc, neighbor in graph.items():
  m = 0
  for u in neighbor:
    if u not in doc_to_id:
      continue
    m += 1
  for u in neighbor:
    if u not in doc_to_id:
      continue
    A[doc_to_id[doc]][doc_to_id[u]] = 1.0/m
# A = 0.95 * A + np.ones(shape=(n,n)) * 0.05 * (1.0/(n*n))


# res = np.matmul(matrix_power(A, 1000),np.ones(shape=(n, )) * (1.0/n))
w,v = LA.eig(A)
ranks = np.argsort(np.real(v[-1]))
for r in ranks:
  print(doc_names[r])

from pyvis.network import Network

net = Network()
ranks = ranks[:13]
added = set()
ii = 0
for r in ranks:
  net.add_node(r, label=doc_names[r], value=n-ii)
  added.add(r)
  ii+=1

for r in ranks:
  neighbor = graph[doc_names[r]]
  for u in neighbor:
    if u not in doc_to_id:
      continue
    if doc_to_id[u] not in added:
      continue
    net.add_edge(r, doc_to_id[u])

net.show("viz.html")