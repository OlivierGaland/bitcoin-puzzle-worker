#!/usr/bin/env python3
import argparse,os,sys
from tools.tool import BITCRACK_EXE_DIR,get_command_output


if __name__ == '__main__':

    #sys.argv = ["main", "-i", "0"]             # test only
    #sys.argv = ["main", "-h"]                  # test only

    parser = argparse.ArgumentParser(description='Run a benchmark on a given GPU id')
    parser.add_argument('-i','--gpu_id', help='GPU id to target', required=True)
    parser.add_argument('-b','--blocks', help='CUDA blocks', required=False)
    parser.add_argument('-t','--threads', help='CUDA threads', required=False)
    parser.add_argument('-p','--points', help='CUDA points', required=False)
    parser.parse_args()
    args = vars(parser.parse_args())

    gid = args['gpu_id']
    b = args['blocks']
    t = args['threads']
    p = args['points']
    mem, pl, cc = get_command_output("nvidia-smi -i "+str(gid)+" --query-gpu=clocks.mem,power.limit,compute_cap --format=csv")[0].split(", ")
    cc = cc.replace(".","")

    params = " -d "+str(gid)
    params += (" -b "+str(b)) if b is not None else ""
    params += (" -t "+str(t)) if t is not None else ""
    params += (" -p "+str(p)) if p is not None else ""

    q = get_command_output("nvidia-smi -i "+str(gid)+" --query-gpu=utilization.gpu  --format=csv | sed 's/ %//'")
    if len(q) == 1 and int(q[0]) < 5:
        pass
    else:
        print("Cannot launch benchmark on device id : "+str(gid)+", it seems the GPU is not idle, stop any process/container currently using this gpu")
        exit(-1)

    os.system(BITCRACK_EXE_DIR+"/bin"+cc+"/cuBitCrack -c"+params+" --keyspace 1000000000:1fffffffff 14iXhn8bGajVWegZHJ18vJLHhntcpL4dex")  
    print("Run done on device id          :  "+str(gid))  
    print("CUDA blocks , threads , points :  "+(str(b) if b is not None else "default")+" , "+(str(t) if t is not None else "default")+" , "+(str(p) if p is not None else "default"))
    q = get_command_output("nvidia-smi -i "+str(gid)+" --query-gpu=clocks.mem,power.limit --format=csv")   
    print("Memory clock , Power limit     :  "+mem+" , "+pl)

