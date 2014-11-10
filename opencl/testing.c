#include <projcl/projcl.h>
#include <stdio.h>
#include <CL/opencl.h>
#include <CL/cl.h>

cl_int oclGetPlatformID(cl_platform_id* clSelectedPlatformID);

cl_int oclGetPlatformID(cl_platform_id* clSelectedPlatformID)
{
    char chBuffer[1024];
    cl_uint num_platforms; 
    cl_platform_id* clPlatformIDs;
    cl_int ciErrNum;
    *clSelectedPlatformID = NULL;

    // Get OpenCL platform count
    printf("2\n");      

    ciErrNum = clGetPlatformIDs (0, NULL, &num_platforms);
    printf("2\n");     
    if (ciErrNum != CL_SUCCESS)
    {
        //printf(" Error %i in clGetPlatformIDs Call !!!\n\n", ciErrNum);
        return -1000;
    }
    else 
    {
        if(num_platforms == 0)
        {
            //printf("No OpenCL platform found!\n\n");
            return -2000;
        }
        else 
        {
            // if there's a platform or more, make space for ID's
            if ((clPlatformIDs = (cl_platform_id*)malloc(num_platforms * sizeof(cl_platform_id))) == NULL)
            {
                //printf("Failed to allocate memory for cl_platform ID's!\n\n");
                return -3000;
            }

            // get platform info for each platform and trap the NVIDIA platform if found
            ciErrNum = clGetPlatformIDs (num_platforms, clPlatformIDs, NULL);
            cl_uint i = 0;
            for(; i < num_platforms; ++i)
            {
                ciErrNum = clGetPlatformInfo (clPlatformIDs[i], CL_PLATFORM_NAME, 1024, &chBuffer, NULL);
                if(ciErrNum == CL_SUCCESS)
                {
                    if(strstr(chBuffer, "NVIDIA") != NULL)
                    {
                        *clSelectedPlatformID = clPlatformIDs[i];
                        break;
                    }
                }
            }

            // default to zeroeth platform if NVIDIA not found
            if(*clSelectedPlatformID == NULL)
            {
                printf("WARNING: NVIDIA OpenCL platform not found - defaulting to first platform!\n\n");
                *clSelectedPlatformID = clPlatformIDs[0];
            }

            free(clPlatformIDs);
        }
    }

    return CL_SUCCESS;
}


int main() {
  cl_int error = CL_SUCCESS;
  
  cl_platform_id npid = NULL;
  printf("1\n");      
  cl_int ciErrNum = oclGetPlatformID (&npid);

  printf("got npid\n");
  
  cl_device_id device_id;
  cl_uint numdevices = 0;
  //printf("PRE ID: %d NUM DEVS: %d\n", device_id, numdevices);

  //error = clGetDeviceIDs(npid, CL_DEVICE_TYPE_GPU, 1, &device_id, &numdevices);
  //printf("ID: %d NUM DEVS: %d\n", device_id, numdevices);

  PLContext *ctx = pl_context_init(npid, CL_DEVICE_TYPE_GPU, &error);
  if(error != CL_SUCCESS) {
    printf("wtf?\n");
    }
  printf("ctx success\n");
  cl_int error1 = CL_SUCCESS;

  PLCode *code = pl_compile_code(ctx, "C:/Concierge/opencl/kernel", 
            PL_MODULE_GEODESIC, &error1);
  if(error1 != CL_SUCCESS) {
    printf("wtf1.1?\n");
    }
    cl_int error7 = CL_SUCCESS;
  error7 = pl_load_code(ctx, code);
  
  if(error7 != CL_SUCCESS) {
    printf("wtf1.2?\n");
    }
    
  int count1 = 1;
  float *xy1_in = malloc(2 * count1 * sizeof(float));
  xy1_in[0] = 42.714326;
  xy1_in[1] = -73.812327;

  int count2 = 1;
  float *xy2_in = malloc(2 * count2 * sizeof(float));// = malloc(2 * count2 * sizeof(float));
  xy2_in[0] = 42.730678;
  xy2_in[1] = -73.686662;
  int lenxy  = sizeof(xy2_in) / sizeof(float);
  int counter = 0;
  for(;counter<lenxy;++counter) {
   printf("xy1[%d] = %f\n", counter, xy1_in[counter]);
   printf("xy2[%d] = %f\n", counter, xy2_in[counter]);
   }
  float *dist_out = malloc(count1 * count2 * sizeof(float));
  int num_dists = sizeof(dist_out) / sizeof(float);
  cl_int error2 = CL_SUCCESS;
  PLInverseGeodesicBuffer *buf = pl_load_inverse_geodesic_data(ctx, 
          xy1_in, count1, 1, xy2_in, count2, &error2);
          
if(error2 != CL_SUCCESS) {
    printf("wtf2?\n");
    }
    
    cl_int error3 = CL_SUCCESS;
  error3 = pl_inverse_geodesic(ctx, buf, dist_out, PL_SPHEROID_WGS_84, 
          1.0);
          
  if(error3 != CL_SUCCESS) {
    printf("wtf3?\n");
    }
    
  printf("len of dist_out = %d\n", num_dists);
  counter = 0;
  for(;counter<num_dists;++counter) {
   //printf("xy1[%d] = %f\n", counter, xy1_in[counter]);
   //printf("xy2[%d] = %f\n", counter, xy2_in[counter]);
   
   printf("dist_out[%d] = %f\n", counter, dist_out[counter]);
   }
  pl_unload_inverse_geodesic_data(buf);
  return 0;
}