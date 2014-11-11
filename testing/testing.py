from geopy.distance import distance, great_circle
import multiprocessing
import json
import itertools
import math
import time
import sys
import gc
 
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
    #self.clat = self.lat * (math.pi * 6378137 / 180)
    #self.clng = self.lng * (math.pi * 6378137 / 180)
    self.id = id
    self.place_id = pid
    self.origin_dist = great_circle(ocords, (self.lat, self.lng)).meters
  
  def __iter__(self):
    return iter((self.lat, self.lng))
  
  def __str__(self):
    s = "%s\n%s\norigin_dist:\n%s\nid: %s pid: %s" % (str(self.lat), str(self.lng), self.origin_dist, self.id, self.place_id)
    return s
    
def build_geodata(json):
  geodatas = []
  for j in json:
    g = Geodata(j["geometry"]["location"]["lat"], j["geometry"]["location"]["lng"], j["id"], j["place_id"])
    geodatas.append(g)
  geodatas.sort(key=lambda x: x.origin_dist)
  return geodatas

def compute_displacement(list):
  list.append(list[0])
  return great_circle(*list).meters

def main(start_time):
  #gc.set_debug(gc.DEBUG_UNCOLLECTABLE)
  #gc.set_debug(gc.DEBUG_STATS)
  f1 = open("haircut.json")
  f2 = open("grocery.json")  
  f3 = open("car_wash.json")
      
  hjson = (json.load(f1))["results"]
  gsjson = (json.load(f2))["results"]
  gamestopjson = (json.load(f3))["results"]
  f1.close()
  f2.close()
  f3.close()
  f1 = f2 = f3 = None

  haircut_geodata = build_geodata(hjson)
  grocery_geodata = build_geodata(gsjson)
  gamestop_geodata = build_geodata(gamestopjson)
  hjson = gsjson = gamestopjson = None

  origin_coords = Geodata(42.730678, -73.686662)
  
  tlist = [haircut_geodata, grocery_geodata, gamestop_geodata]#haircut_geodata + grocery_geodata + gamestop_geodata
  product = list(itertools.product(*tlist))
  haircut_geodata = grocery_geodata = gamestop_geodata = tlist = None
  #print("time before forceing gc collection: ", str(time.time() - start_time))
  gc.collect()
  #print("time after force gc", str(time.time() - start_time))
  
  geoareas = []
  threads = [] 

  mpq = multiprocessing.Queue()

  if(len(sys.argv) == 2):
    nprocs = int(sys.argv[1])
  else:
    nprocs = 10

  chunksize = int(math.ceil(len(product) / float(nprocs)))

  for i in range(nprocs):#for i in range(chunks):
    c = product[chunksize * i:chunksize * (i + 1)]
    t = gThread(c, i, mpq)
    t.start()
    threads.append(t)
  
  product = None
  #print("time before forceing gc collection: ", str(time.time() - start_time))
  gc.collect()
  #print("time after force gc", str(time.time() - start_time))

  for i in range(nprocs):
    geoareas.extend(mpq.get())
  
  for t in threads:
    t.join()
  
  mpq = threads = None 
  #print("time before forceing gc collection: ", str(time.time() - start_time))
  gc.collect()
  #print("time after force gc", str(time.time() - start_time))
  
  print("PRE-SORT TIME DELTA:", str(time.time() - start_time))
  geoareas.sort(key=lambda x: x.delta)
  print("POST-SORT TIME DELTA:", str(time.time() - start_time))
  
  output = open("output.txt",'w')

  for x in range(5):
    print(geoareas[x], file=output)
  
  output.close()
  output = None

if __name__ == '__main__':
  start_time = time.time()
  main(start_time)
  print("process took a total of %s time!" % (str(time.time() - start_time)))