import json
import itertools
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
  return geodatas

def get_top_n(product, n):
  coords = []
  total_size = len(product)
  tuple_size = len(product[0])
  print("tuple_size: ", tuple_size)
  stress_test = False
  dtmp = time.time()
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
  if stress_test:
    with open("benchmark.txt", "a") as myf:
      print("old method took: ", old_delta, "seconds!", file=myf)
      print("OPENCL NEW BLACK MAGIC TOOK: ", new_delta, "SECONDS!", file=myf)
  tmp = time.time()
  floatlist = [outarg[i] for i in range(total_size)]
  delt(tmp)
  
  print("flist len:", len(floatlist))
  
  t = time.time()
  sorted_by_dist = sorted(zip(product, floatlist), key=lambda x: x[1])
  delt(t)
  
  return sorted_by_dist[:n]
  

def load_jsons(filepaths):
  tlist = []
  for filepath in filepaths:
    f = open(filepath)
    j = (json.load(f))["results"]
    tlist.append(build_geodata(j))
    f.close()
  print("len of tlist:", len(tlist))
  t = time.time()
  product = list(itertools.product(*tlist))
  print("time taken to generate product:", time.time() - t)
  print("len of product:", len(product))
  return product

def main():
  delt = lambda x: print("Delta:", time.time() - x)

  filepaths = ["haircut.json", "grocery.json", "car_wash.json", "gamestop.json"]
  product = load_jsons(filepaths)

  top5 = get_top_n(product, 5)
  with open("output_cl.txt", "w") as of:
    for g, d in top5:
      ga = Geoarea(g, d)
      print(ga, file=of)

if __name__ == '__main__':
  start_time = time.time()
  main()
  print("process took a total of %s time!" % (str(time.time() - start_time)))