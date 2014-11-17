import json
import itertools
import ctypes
from urllib.request import urlopen
import time
import datetime
from geopy.geocoders import GoogleV3
LOG_DIR = "./logs"
type_list = ['accounting', 'airport', 'amusement_park', 'aquarium', 'art_gallery', 'atm', 'bakery', 'bank', 'bar', 'beauty_salon', 'bicycle_store', 'book_store', 'bowling_alley', 'bus_station', 'cafe', 'campground', 'car_dealer', 'car_rental', 'car_repair', 'car_wash', 'casino', 'cemetery', 'church', 'city_hall', 'clothing_store', 'convenience_store', 'courthouse', 'dentist', 'department_store', 'doctor', 'electrician', 'electronics_store', 'embassy', 'establishment', 'finance', 'fire_station', 'florist', 'food', 'funeral_home', 'furniture_store', 'gas_station', 'general_contractor', 'grocery_or_supermarket', 'gym', 'hair_care', 'hardware_store', 'health', 'hindu_temple', 'home_goods_store', 'hospital', 'insurance_agency', 'jewelry_store', 'laundry', 'lawyer', 'library', 'liquor_store', 'local_government_office', 'locksmith', 'lodging', 'meal_delivery', 'meal_takeaway', 'mosque', 'movie_rental', 'movie_theater', 'moving_company', 'museum', 'night_club', 'painter', 'park', 'parking', 'pet_store', 'pharmacy', 'physiotherapist', 'place_of_worship', 'plumber', 'police', 'post_office', 'real_estate_agency', 'restaurant', 'roofing_contractor', 'rv_park', 'school', 'shoe_store', 'shopping_mall', 'spa', 'stadium', 'storage', 'store', 'subway_station', 'synagogue', 'taxi_stand', 'train_station', 'travel_agency', 'university', 'veterinary_care', 'zoo']

AUTH_KEY = "AIzaSyACatSX6QVEyeo-HKMlP9lreIgJDHRoDRs"
tstamp = lambda x: "[%s] " % (str(datetime.datetime.fromtimestamp(x).strftime('%m-%d-%Y_%H:%M:%S')))
fstamp = lambda x: "[%s]" % (str(datetime.datetime.fromtimestamp(x).strftime('%m-%d-%Y_%H-%M-%S')))
DEFAULT_PLACE_RATING = 3.0

cldist = ctypes.CDLL("cldist.dll")

class JSONEncoder(json.JSONEncoder):
  def default(self, o):
    return o.__dict__

class Place:
  def __init__(self, placeid, authkey):
    self.raw_data = self.req_place_details(placeid, authkey)
    for key, val in self.raw_data.items():
      setattr(self, key, val)
    self.compute_rating()
  
  def compute_rating(self):
    if "ratings" in self.raw_data:
      self.rating = float(self.raw_data['ratings'])
    elif "reviews" in self.raw_data:
      rating_count = 0
      rating = 0.0
      for review in self.raw_data['reviews']:
        if "rating" in review:
          rating = rating + float(review['rating'])
          rating_count = rating_count + 1
      self.rating = float(rating) / float(rating_count)
    else:
      self.rating = DEFAULT_PLACE_RATING

  def req_place_details(self, placeid, authkey):
    url = "https://maps.googleapis.com/maps/api/place/details/json?placeid=%s&key=%s" % (placeid, authkey)
    resp = urlopen(url)
    resp_json = resp.readall().decode('utf-8')
    jsondata = json.loads(resp_json)
    if jsondata['status'] == "OK":
      return jsondata['result']
  
  def __str__(self):
    s = tstamp(time.time()) + "%s = %s\n" % ("internal_rating", str(self.rating))
    printlist = ["name", "rating", "reviews", "types", "formatted_address"]
    for key in printlist:
      if key in self.raw_data:
        s = s + tstamp(time.time()) + "%s = %s\n" % (str(key), str(getattr(self, key)))
    return s

class Coordinates:
  def __init__(self, lat, lng):
    self.lat = lat
    self.lng = lng
  def __str__(self):
    s = "%s,%s" % (str(self.lat), str(self.lng))
    return s

class Geoarea:
  def __init__(self, geodatas, delta):
    self.geodatas = geodatas
    self.delta = delta
    self.places = self.get_places()
    self.total_rating = self.compute_total_rating()
  
  def get_places(self):
    places = []
    for g in self.geodatas:
      p = Place(g.place_id, AUTH_KEY)
      places.append(p)
    return places
  
  def compute_total_rating(self):
    total_rating = 0.0
    for place in self.places:
      total_rating = total_rating + place.rating
    return ((total_rating) / (len(self.places)))
  
  def __str__(self):
    s = tstamp(time.time()) + "Total displacement without origin: %s\n" % (str(self.delta))
    s = s + "Overall GeoArea Rating: %s\n" % (str(self.total_rating))
    for p in self.places:
      s = s + str(p) + "\n"
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

def get_top_n(product, n=0):
  crds = []
  total_size = len(product)
  tuple_size = len(product[0])
  print("tuple_size: ", tuple_size)
  stress_test = False
  dtmp = time.time()
  for g in product:
    for x in g:
      crds.append(x.lat)
      crds.append(x.lng)
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
  
  crds_size = (len(crds))
  
  print("len crds:", crds_size, "total size: ", total_size)
  
  arg1 = (ctypes.c_float * crds_size)()
  arg1[:] = crds
  outarg = (ctypes.c_float * (total_size))()
  magictime = time.time()
  result = cldist.compute_distance(arg1, crds_size, tuple_size, total_size, ctypes.byref(outarg))
  new_delta = time.time() - magictime
  if stress_test:
    with open("benchmark.txt", "a") as myf:
      print("old method took: ", old_delta, "seconds!", file=myf)
      print("OPENCL NEW BLACK MAGIC TOOK: ", new_delta, "SECONDS!", file=myf)
  
  floatlist = [outarg[i] for i in range(total_size)]
  
  print("flist len:", len(floatlist))
  tstart = time.time()
  sorted_by_dist = sorted(zip(product, floatlist), key=lambda x: x[1])
  delta = time.time() - tstart
  print("time taken sorting ziplist: %s seconds!" % (str(delta)))

  if n == 0:
    return sorted_by_dist
  else:
    return sorted_by_dist[:n]
  

def load_jsons(filepaths):
  tlist = []
  for filepath in filepaths:
    f = open(filepath)
    j = (json.load(f))["results"]
    tlist.append(build_geodata(j))
    f.close()
  print("len of tlist:", len(tlist))
  clen = len(filepaths)
  #print(len(tlists))
  t = time.time()
  product = list(itertools.combinations(tlist, clen))
  print("time taken to generate product:", time.time() - t)
  print("len of product:", len(product))
  return product
  
def radar_request(argdict):
  url = "https://maps.googleapis.com/maps/api/place/radarsearch/json?"
  for key, val in argdict.items():
    if len(val) > 0:
      url = url + '%s=%s&' % (str(key), str(val))
      if "+" in val:
        url = url + '%s="%s"&' % (str(key), str(val))
      else:
        url = url + '%s=%s&' % (str(key), str(val))
    else:
      url = url + "%s&" % (str(key))
  # Send the GET request to the Place details service (using url from above)
  url = url[:-1]
  response = urlopen(url)

  # Get the response and use the JSON library to decode the JSON
  json_raw = response.readall().decode('utf-8')
  json_data = json.loads(json_raw)
  if json_data['status'] == 'OK' and 'results' in json_data:
    return json_data['results']
  else:
    raise

def build_base_dict(authkey, coords, r):
  return dict(key=authkey, location=str(coords), radius=str(r))

def main_procedure(origin_address, query_list, radius):
  geolocator = GoogleV3(AUTH_KEY)
  location = geolocator.geocode(origin_address)
  print(location)
  origin_coords = Coordinates(location.latitude, location.longitude)
  
  radar_reqs = []
  base_dict = build_base_dict(AUTH_KEY, origin_coords, radius)

  for query in query_list:
    qtype = query.replace(" ", "_")
    qkey = query.replace(" ", "+")
    qdict = dict(base_dict)
    if qtype in type_list:
      qdict["types"] = qtype
    else:
      qdict["keyword"] = qkey
    print(qdict)
    try:
      req = radar_request(qdict)
    except:
      if "keyword" in qdict:
        tmp = qdict["keyword"]
        qdict["keyword"] = tmp.replace("_", "+")
        req = radar_request(qdict)
    fname = LOG_DIR + "/" + qtype + ".json"
    with open(fname, "w") as cached:
      cached.write(json.dumps(req, indent=2))
    geod = build_geodata(req)
    radar_reqs.append(geod)
  
  print(len(radar_reqs))
  #fp1 = ["haircut.json", "grocery.json", "car_wash.json"]
  tstart = time.time()
  product = list(itertools.product(*radar_reqs))
  print("producing took: %s seconds!" % (str(time.time() - tstart)))
  print("len product:", len(product))
  top5 = get_top_n(product, 5)
  geoareas = []
  for g, d in top5:
    geoareas.append(Geoarea(g,d))
  
  geoareas.sort(key=lambda x: x.delta)
  fname = LOG_DIR + "/" + fstamp(time.time()) + "_OUTPUT.TXT"
  
  with open(fname, "a+") as of:
    print(tstamp(time.time()), "--BEGIN--", file=of)
    count = 1
    for ga in geoareas:
      print(tstamp(time.time()), "%s OF %s" % (str(count), str(len(top5))), file=of)
      print(tstamp(time.time()), str(ga), file=of)
      count = count + 1
    print(tstamp(time.time()), "--END--", file=of)
  return json.dumps(geoareas, cls=JSONEncoder, sort_keys=True, indent=2)

def main():
  radius = 15000
  origin = "5 clubway mount kisco ny"
  example_query = ["car wash", "haircut", "grocery_shopping", "mail_package"]
  json_resp = main_procedure(origin, example_query, radius)
  with open(LOG_DIR + "/jsonresp.json", "w") as jsonresp:
    print(json_resp, file=jsonresp)

if __name__ == '__main__':
  start_time = time.time()
  main()
  print("process took a total of %s time!" % (str(time.time() - start_time)))