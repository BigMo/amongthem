from os import close
import sys


def main(argv):
    namespath = argv[0] if len(argv) > 0 else '.\\namedump.txt'
    dumppath = argv[1] if len(
        argv) > 1 else 'C:\\Users\\morit\\Downloads\\among\\2020.10.22\\v1\\dump_Full.cs'
    outpath = argv[2] if len(argv) > 2 else 'dump_renamed.cs'

    print("Opening renames-file...")
    with open(namespath, 'r') as file:
        renames = [l.strip().split('/') for l in file.readlines()]
    renames = list(filter(lambda r: len(r) > 1 and type(r) == list, renames))
    print(f' > Imported {len(renames)} renames!')

    print("Opening output-file...")
    fout = open(outpath, 'w', encoding='utf-8')
    print("Opening dump-file...")
    with open(dumppath, 'r', encoding='utf-8') as fdump:
        for line in fdump.readlines():
            for ren in renames:
                line = line.replace(ren[0], ren[1])
            fout.write(line)
            #print('.', end='')
    fout.close()
    print("Done!")


if __name__ == '__main__':
    main(sys.argv[1:])
