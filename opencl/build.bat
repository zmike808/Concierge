gcc -g -L./ -I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v6.5\include" -I./include -lOpenCL64 -lProjCL ./testing.c -w -o testing.exe