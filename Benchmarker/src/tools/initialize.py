import time,sys,os

from tool import get_command_output,BITCRACK_DIR,BITCRACK_EXE_DIR

if __name__ == '__main__':
    print("Starting initialization ...")
    time.sleep(10)
    q = get_command_output("nvidia-smi --query-gpu=compute_cap --format=csv | tail -n +2 | sort | uniq",[])
    print("Found compute capabity list : "+str(q))
    sys.stdout.flush()

    l = ""
    s = ""

    for item in q:
        cc = item.replace(".","")

        if os.path.exists(BITCRACK_EXE_DIR+"/bin"+cc):
            print("Already compiled for CC : "+cc)
            s+=cc+" "
            continue

        print("Compiling for CC : "+cc)
        sys.stdout.flush()
        os.system("(cd "+BITCRACK_DIR+" && make BUILD_CUDA=1 COMPUTE_CAP="+cc+")")
        if os.path.exists(BITCRACK_DIR+"/bin"):
            os.system("mv "+BITCRACK_DIR+"/bin "+BITCRACK_EXE_DIR+"/bin"+cc)
            l+=cc+" "
        else:
            print("Failed to compile for CC : "+cc)
        sys.stdout.flush()

        print("Initialization done for following compute capability : "+l+((" , skipped for "+s+" (target directory already exist)") if s != "" else ""))
        print("Open a shell and use benchmark.py script to do the benchmarking")
    while True:
        time.sleep(10)
        sys.stdout.flush()

