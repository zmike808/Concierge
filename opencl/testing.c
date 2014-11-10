#include <projcl.h>

int main() {
  printf("started!\n");
  cl_int error = CL_SUCCESS;
  printf("started!\n");

  PLContext *ctx = pl_context_init(CL_DEVICE_TYPE_GPU, &error);
  printf("started!\n");
  PLCode *code = pl_compile_code(ctx, "C:/Concierge/opencl/kernel", 
          PL_MODULE_DATUM | PL_MODULE_GEODESIC | PL_MODULE_PROJECTION, &error);
  printf("started!\n");
  error = pl_load_code(ctx, code);
  printf("started!\n");
  int count1 = 1;
  float *xy1_in = malloc(2 * count1 * sizeof(float));
  xy1_in[0] = 42.714326;
  xy1_in[1] = -73.812327;

  int count2 = 1;
  float *xy2_in = malloc(2 * count2 * sizeof(float));
  xy2_in[0] = 42.730678;
  xy2_in[1] = -73.686662;

  float *dist_out = malloc(count1 * count2 * sizeof(float));
  int num_dists = sizeof(dist_out) / sizeof(float);
  
  PLInverseGeodesicBuffer *buf = pl_load_inverse_geodesic_data(ctx, 
          xy1_in, count1, 1, xy2_in, count2, &error);

  error = pl_inverse_geodesic(ctx, buf, dist_out, PL_SPHEROID_SPHERE, 
          1.0 /* scale */);
  printf("len of dist_out = %d & dist_out[0] = %f\n", num_dists, dist_out[0]);
  pl_unload_inverse_geodesic_data(buf);
}