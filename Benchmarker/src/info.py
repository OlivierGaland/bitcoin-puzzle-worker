#!/usr/bin/python3
import argparse,os,sys
from tools.tool import get_command_output


if __name__ == '__main__':

    #sys.argv = ["main", "-i", "0"]             # test only

    parser = argparse.ArgumentParser(description='Show GPU info and clock/power tuning capabilities')
    parser.add_argument('-i','--gpu_id', help='GPU id to target', required=False)
    parser.parse_args()
    args = vars(parser.parse_args())

    gid = args['gpu_id']

    print('')
    if gid is None:
        print("GPU detected on this system :")
        q = get_command_output("nvidia-smi --query-gpu=name,compute_cap,persistence_mode,power.limit,clocks.mem --format=csv",[])
        for i in range(len(q)):
            print(((str(i-1)+": ") if i !=0 else "id : ")+q[i])
        print('')
        print("To display gpu capabilities : ./info -i <id>")
    else:
        print("GPU tuning capabilities on device id : "+str(gid))
        q = get_command_output("nvidia-smi -q -d SUPPORTED_CLOCKS | grep Memory | sed s'/.*: //'",[])
        print("Memory clock : "+str(q))
        q = get_command_output("nvidia-smi -q -d POWER | grep 'Power Limit' | head -5 | tail -2 | sed s'/.*: //'",[])
        print("Power limit : from "+str(q[0])+" to "+str(q[1]))
        print('')
        print("To enable persistency mode : nvidia-smi -i "+str(gid)+" -pm 1 (persistency keep driver in video card memory so save time initializing)")
        print("To change memory clock : nvidia-smi -i "+str(gid)+" -lmc 5001  (where 5001 is one lmc picked in the above list)")
        print("To change power limit : nvidia-smi -i "+str(gid)+" -pl 100  (where 100 is one power limit matching above boundaries)")
        print('')
        print("If docker is hosted on windows machine run those commands in a powershell terminal (Win+X), note persistency mode is not available on Windows")
    print('')


