from geopy.distance import distance
import multiprocessing
import json
import itertools
import math
import time
import sys
search_radius = 17000.0
 
class gThread(multiprocessing.Process):
  def __init__(self, list, tid, queue):
    multiprocessing.Process.__init__(self)
    self.tid = tid
    self.list = list
    self.queue = queue
  def run(self):
    tmp = []
    for x in self.list:
      geodatas = list(x)
      delta = compute_displacement(geodatas)
      ga = Geoarea(geodatas, delta)
      tmp.append(ga)
    self.queue.put(tmp)

ocords = (42.730678, -73.686662)
class Geoarea:
  def __init__(self, geodatas, delta):
    self.geodatas = geodatas
    self.delta = delta
    
  def __str__(self):
    s = "Total displacement without origin: %s\n" % (str(self.delta))
    for g in self.geodatas:
      s = s + str(g) + "\n"
    return s

class Geodata:
  def __init__(self, lat, lng, id=-1, pid=-1):
    self.lat = lat
    self.lng = lng
    self.clat = self.lat * (math.pi * 6378137 / 180)
    self.clng = self.lng * (math.pi * 6378137 / 180)
    self.id = id
    self.place_id = pid
    self.origin_dist = distance(ocords, (self.lat, self.lng)).meters
  
  def __str__(self):
    s = "(lat,lng): (%s, %s)\norigin_dist: %s id: %s pid: %s" % (str(self.lat), str(self.lng), self.origin_dist, self.id, self.place_id)
    return s
    
def build_geodata(json):
  geodatas = []
  for j in json:
    g = Geodata(j["geometry"]["location"]["lat"], j["geometry"]["location"]["lng"], j["id"], j["place_id"])
    geodatas.append(g)
  return sorted(geodatas, key=lambda x: x.origin_dist)

def compute_displacement(list):
  d = 0.0
  points = list
  points.append(points[0])
  plen = len(points) - 1
  for x in range(plen):
    p2 = (points[x + 1].lat, points[x+1].lng)
    p1 = (points[x].lat, points[x].lng)
    dtmp = distance(p1, p2).meters
    d = d + dtmp
  return d

def main():
  f1 = open("haircut.json")
  f2 = open("grocery.json")  
  f3 = open("car_wash.json")
  
  start_time = time.time()
  
  output = open("output.txt",'w')
  
  hjson = (json.load(f1))["results"]
  gsjson = (json.load(f2))["results"]
  gamestopjson = (json.load(f3))["results"]

  haircut_geodata = build_geodata(hjson)
  grocery_geodata = build_geodata(gsjson)
  gamestop_geodata = build_geodata(gamestopjson)

  origin_coords = Geodata(42.730678, -73.686662)
  tlist = [haircut_geodata, grocery_geodata, gamestop_geodata]#haircut_geodata + grocery_geodata + gamestop_geodata
  product = list(itertools.product(*tlist))
  
  geoareas = []
  mpq = multiprocessing.Queue()

  if(len(sys.argv) == 2):
    nprocs = int(sys.argv[1])
  else:
    nprocs = 10

  chunksize = int(math.ceil(len(product) / float(nprocs)))
  threads = []
  
  for i in range(nprocs):#for i in range(chunks):
    c = product[chunksize * i:chunksize * (i + 1)]
    t = gThread(c, i, mpq)
    t.start()
    threads.append(t)
  
  for i in range(nprocs):
    geoareas.extend(mpq.get())
  
  for t in threads:
    t.join()
  
  print("PRE-SORT TIME DELTA:", str(time.time() - start_time))
  sortedareas = sorted(geoareas, key=lambda x: x.delta)
  print("POST-SORT TIME DELTA:", str(time.time() - start_time))

  for x in range(5):
    print(sortedareas[x], file=output)
  
  output.close()
  
  end_time = time.time()
  delta = end_time - start_time
  print("process took a total of %s time!" % (str(delta)))
  f1.close()
  f2.close()
  f3.close()

if __name__ == '__main__':
  main()