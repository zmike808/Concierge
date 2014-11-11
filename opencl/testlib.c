int main() {
  //int count1 = 1;
  //float *xy1_in = malloc(2 * count1 * sizeof(float));
  /* origin:
    42.730678
   -73.686662

  
  xy1_in[0] = 42.730678;
  xy1_in[1] = -73.686662;
  */
  
  int count2 = 3;
  float xy2_in[count2*2]; //= malloc(2 * count2 * sizeof(float));// = malloc(2 * count2 * sizeof(float));
  //10428.188651860528
  xy2_in[0] = 42.714326;
  xy2_in[1] = -73.812327;
  //10409.108520068827
  xy2_in[2] = 42.714306;
  xy2_in[3] = -73.812085;
  //10319.612561553628
  xy2_in[4] = 42.715151;
  xy2_in[5] = -73.811174;
  int count1 = count2 - 1;
  float xy1_in[count1*2]; //= malloc(2 * count1 * sizeof(float));
  xy1_in[0] = 42.714326;
  xy1_in[1] = -73.812327;
  //10409.108520068827
  xy1_in[2] = 42.714306;
  xy1_in[3] = -73.812085;
  int lenxy  = count2 * 2;
  int counter = 0;
  //printf("len of xy2_in = %d\n", lenxy);
/*
  for(;counter<lenxy;++counter) {
   printf("xy1[%d] = %f\n", counter, xy1_in[counter]);
   printf("xy2[%d] = %f\n", counter, xy2_in[counter]);
  }
   */
   int num_dists = count1 * count2;
   printf("len of dist_out = %d\n", num_dists);
  counter = 0;
  float* dist_out = compute_distances(xy1_in, count1, xy2_in, count2);
  for(;counter<num_dists;++counter) {   
    printf("dist_out[%d] = %f\n", counter, dist_out[counter]);
  }
  int i,j;
  for(i=0;i<count1;i++) {
    for(j=0;j<count2;j++) {
       int doind = i*count2+j;
       printf("i = %d\nj = %d\ndist_out[%d] = %f\n\n", i, j, doind, dist_out[doind]);
    }
  }

  return 0;
}