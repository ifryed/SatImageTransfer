import os
import sys
import LIT

import matplotlib.pyplot as plt


def main(fld_path):
    if not os.path.isdir(fld_path):
        print("{} is not a directory".format(fld_path))
        exit()

    img = LIT.LoadImage(fld_path)

    plt.imshow(img)
    plt.show()


if __name__ == '__main__':
    main(sys.argv[1])
