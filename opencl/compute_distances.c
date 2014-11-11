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
    //printf("2\n");      

    ciErrNum = clGetPlatformIDs (0, NULL, &num_platforms);
    //printf("2\n");     
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


float* compute_distances(float* latlng1, int len1, float* latlng2, int len2) {
  cl_int error = CL_SUCCESS;
  
  cl_platform_id npid = NULL;
  cl_int ciErrNum = oclGetPlatformID (&npid);
  
  cl_device_id device_id;
  cl_uint numdevices = 0;

  PLContext *ctx = pl_context_init(npid, CL_DEVICE_TYPE_GPU, &error);
  

  PLCode *code = pl_compile_code(ctx, "./kernel", PL_MODULE_GEODESIC, &error);
  
  error = pl_load_code(ctx, code);

  float *dist_out = malloc(len1 * len2 * sizeof(float));
  PLInverseGeodesicBuffer *buf = pl_load_inverse_geodesic_data(ctx, 
          latlng1, len1, 1, latlng2, len2, &error);
          
  error = pl_inverse_geodesic(ctx, buf, dist_out, PL_SPHEROID_WGS_84, 1.0);
  pl_unload_inverse_geodesic_data(buf);
  return dist_out;
}