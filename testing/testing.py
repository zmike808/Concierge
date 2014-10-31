from geopy.distance import distance
import json
origin_coords = (42.730678, -73.686662)
search_radius = 17000.0
class Geodata:
  def __init__(self, json):
    #print(json)
    self.coords = (json["geometry"]["location"]["lat"], json["geometry"]["location"]["lng"])
    self.id = json["id"]
    self.place_id = json["place_id"]
    self.origin_dist = distance(origin_coords, self.coords).meters

def build_geodata(json):
  geodatas = []
  for j in json:
    g = Geodata(j)
    geodatas.append(g)
  return sorted(geodatas, key=lambda x: x.origin_dist)

def top5_closest(first, second):
  closest_dist = -1.0
  closest = []
  old_origin_dist = ()
  modifier = 5.0
  
  for x in first:
    for y in second:
      dist = distance(x.coords, y.coords).meters
      #if  x.origin_dist > search_radius/2 or y.origin_dist > search_radius/2:
      #continue
      if closest_dist == -1.0 or dist < closest_dist:
        closest.append((x, y, dist))
        closest_dist = dist
        old_origin_dist = (x.origin_dist, y.origin_dist)
  
  sortedlist = sorted(closest, key=lambda x: x[2])
  return sortedlist#return (closest_dist, closest[0], closest[1])
      
def main():
  f1 = open("haircut.json")
  f2 = open("grocery.json")  
  output = open("output.txt",'w')
  hjson = (json.load(f1))["results"]
  gsjson = (json.load(f2))["results"]
  #print(hjson, file=output)
  haircut_geodata = build_geodata(hjson)
  grocery_geodata = build_geodata(gsjson)
  top5 = top5_closest(haircut_geodata, grocery_geodata)

  for closest in top5:
    x = closest[0]
    y = closest[1]
    print("between x and y in meters: ", closest[2], file=output)
    print("dist from origin for x:", x.origin_dist, file=output)
    print("dist from origin for y:", y.origin_dist, file=output)
    print("Closest haircut place_id: ", x.place_id, file=output)
    print("Closest grocery shopping id: ", y.place_id, file=output)
    print("",file=output)
  f1.close()
  f2.close()
  output.close()
main()