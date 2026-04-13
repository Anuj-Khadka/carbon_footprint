import sys

N = 100  # changes per file

def setup():
    # fill data structures
    pass

def algorithm():
    # run algorithm
    # return checksum
    pass

def main():
    setup()
    
    sys.stdout.write("ready\n")
    sys.stdout.flush()
    
    for line in sys.stdin:
        sys.stdout.write(str(algorithm()) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()