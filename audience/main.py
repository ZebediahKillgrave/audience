from sys import argv

def main():
    if len(argv) != 2:
        print ("Usage : audience [link]\n"
               "Example : audience https://twitter.com/SDEntrepreneurs/status/431412241150529536")
        return

    print "Ca compute lol"

if __name__ == "__main__":
    main()
