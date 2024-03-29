import subprocess

BITCRACK_DIR = '/app/BitCrack'
BITCRACK_EXE_DIR = '/app/exe'

def get_command_output(cmd,discard_lines = [0]):
    ret = list()
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=True,
                            universal_newlines=True)

    std_out, std_err = proc.communicate()
    i = 0
    if proc.returncode == 0:
        for line in std_out.splitlines():
            if i not in discard_lines:
                ret.append(line)
            i+=1
    else:
        raise Exception(std_err) 
    return ret
