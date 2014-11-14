from geopy.distance import distance, great_circle
import multiprocessing
import json
import itertools
import math
import sys
import ctypes
#import timeit
import time

cldist = ctypes.CDLL("./cldist.dll")


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
    self.origin_dist = None #great_circle(ocords, (self.lat, self.lng)).meters
  def __iter__(self):
    return iter((self.lat, self.lng))
  
  def __str__(self):
    s = "(lat,lng): (%s, %s)\n id: %s pid: %s" % (str(self.lat), str(self.lng), self.id, self.place_id)
    return s
    
def build_geodata(json):
  geodatas = []
  for j in json:
    g = Geodata(j["geometry"]["location"]["lat"], j["geometry"]["location"]["lng"], j["id"], j["place_id"])
    geodatas.append(g)
  #geodatas.sort(key=lambda x: x.origin_dist)
  return geodatas

def bmin(json):
  geodatas = []
  for j in json:
    g = (j["geometry"]["location"]["lat"], j["geometry"]["location"]["lng"])
    geodatas.append(g)
  #geodatas.sort(key=lambda x: x.origin_dist)
  return geodatas

def compute_displacement(list):
  list.append(list[0])
  return great_circle(*list).meters

def main():
  
  f1 = open("haircut.json")
  f2 = open("grocery.json")  
  f3 = open("car_wash.json")
  delt = lambda x: print("Delta:", time.time() - x)
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
  
  tlist = [haircut_geodata, grocery_geodata, gamestop_geodata]
  tmp = time.time()
  product = list(itertools.product(*tlist))
  
  magic = lambda x: itertools.chain.from_iterable(x)
  print("delta:", time.time() - tmp)
  hjson = gsjson = gamestopjson = None
  coords = []
  total_size = len(product)
  tuple_size = len(product[0])
  print("tuple_size: ", tuple_size)
  dtmp = time.time()
  mini = []
  limit = len(product)
  stress_test = True

  for g in product:
    for x in g:
      coords.append(x.lat)
      coords.append(x.lng)
  print("time taken to go from megalist to x,ys...:", time.time() - dtmp)
 
  if stress_test:
    geoareas = []
    stress = time.time()
    for g in product:
      geoareas.append(Geoarea(list(g), compute_displacement(list(g))))
    old_delta = time.time() - stress
    geoareas.sort(key=lambda x: x.delta)
    with open("output.txt", "w") as out:
      t5 = geoareas[:5]
      for g in t5:
        print(g, file=out)
  
  coords_size = (len(coords))
  
  print("len coords:", coords_size, "total size: ", total_size)
  
  arg1 = (ctypes.c_float * coords_size)()
  arg1[:] = coords
  outarg = (ctypes.c_float * (total_size))()
  magictime = time.time()
  result = cldist.compute_distance(arg1, coords_size, tuple_size, total_size, ctypes.byref(outarg))
  new_delta = time.time() - magictime
  
  with open("benchmark.txt", "a") as myf:
    if stress_test:
      print("old method took: ", old_delta, "seconds!", file=myf)
    print("OPENCL NEW BLACK MAGIC TOOK: ", new_delta, "SECONDS!", file=myf)
  tmp = time.time()
  floatlist = [outarg[i] for i in range(total_size)]
  delt(tmp)
  
  print("flist len:", len(floatlist))
  
  t = time.time()
  sorted_by_dist = sorted(zip(product, floatlist), key=lambda x: x[1])
  delt(t)
  
  top5 = sorted_by_dist[:5]
  #print(top5)
  with open("output_cl.txt", "w") as of:
    for g, d in top5:
      ga = Geoarea(g, d)
      print(ga, file=of)
  
  
  
  
  exit()
  origin_coords = Geodata(42.730678, -73.686662)
  
  
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
    indstart = chunksize * i
    indend = chunksize * (i + 1)
    t = gThread(c, i, mpq, indstart, indend)
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
  #start_time = time.time()
  main()
  #print("process took a total of %s time!" % (str(time.time() - start_time)))