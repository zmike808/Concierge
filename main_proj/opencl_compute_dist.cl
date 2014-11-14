__kernel void compute_distance(__global float2 *c, __global float *output, unsigned int tuple_size, unsigned int total_size) 
{
  // total_size = # of tuples (which have a size of tuple_size)
  int g = get_global_id(0);
      
    int i = tuple_size * g; // index of tuple of lat,lng values

    float dist = 0.0;
    int j = 0;
    // out of bounds check, not too sure when this would happen but better safe then fucked in the ass?
    // also not sure if this is the proper 
    for (j = 0; j < tuple_size; ++j) {
      int ind = i+j;
      float lat1 = radians(c[ind].x);
      float lng1 = radians(c[ind].y);
      float lat2, lng2;
      // to replace having to append c[i] to end to complete the cycle saves transfering over an extra float every tuple
      if(ind+1 == tuple_size) {      
        lat2 = radians(c[i].x);
        lng2 = radians(c[i].y);
      }
      else {
        lat2 = radians(c[ind+1].x);
        lng2 = radians(c[ind+1].y);
      }

      float cos_lat1 = 0.0;
      float sin_lat1 = sincos(lat1, &cos_lat1);
      
      float cos_lat2 = 0.0;
      float sin_lat2 = sincos(lat2, &cos_lat2);
    
      float delta_lng = lng2 - lng1;
      float cos_delta_lng;
      float sin_delta_lng = sincos(delta_lng, &cos_delta_lng);
    
      dist += 6372795.0 * (atan2(
        sqrt(
        ((cos_lat2 * sin_delta_lng) * (cos_lat2 * sin_delta_lng)) +
        ((cos_lat1 * sin_lat2 - sin_lat1 * cos_lat2 * cos_delta_lng) * (cos_lat1 * sin_lat2 - sin_lat1 * cos_lat2 * cos_delta_lng)) 
        ),
       (sin_lat1 * sin_lat2) + (cos_lat1 * cos_lat2 * cos_delta_lng)
       ));
    }
    output[g] = dist;
}