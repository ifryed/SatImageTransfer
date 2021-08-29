import shutil
import sys

from matplotlib import pyplot as plt
import os

from src import LIT
from src.LIT import KBYTE
from src.SIClib import classifyImg, starFinder
import utils
import numpy as np

out_fld = '../output'


def main():
    gray = False
    cvt = lambda x: x[:, :, [2, 1, 0]]
    img = None
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        print('Running Demo')
        import cv2
        np.random.seed()
        img_path = '../data/classes/stars/'
        # img_path += np.random.choice(os.listdir(img_path), 1)[0] + '/'
        img_path += np.random.choice(os.listdir(img_path), 1)[0]
        # img_path = '../data/sat_village.png'
        img = cv2.imread(img_path)

    # Create dirs
    os.makedirs(out_fld + '/meta', exist_ok=True)

    save_paths, img = LIT.CompressImage(img, out_fld, max_size=16 * KBYTE, comp_gray=gray)
    res_lap_load = LIT.LoadImage('../output')
    plt.imshow(res_lap_load)

    img_class, img_class_ser = classifyImg(img)

    utils.save_meta(img_class_ser, img, len(save_paths), out_fld, h_copy=True)
    utils.read_meta('{}/meta/metafile.bin'.format(out_fld), verbos=True)

    total_size = sum([os.path.getsize(os.path.join(out_fld, x)) for x in os.listdir(out_fld) if x.startswith('lap')])
    print("Tot Size:", total_size)
    print(save_paths)
    print("Class: {}".format(img_class))

    if img_class == 'stars':
        stars_xy = starFinder(img, disp=True)
        np.save('{}/meta/stars.npy'.format(out_fld), stars_xy.astype(np.uint16))
        print("Stars size:", os.path.getsize('{}/meta/stars.npy'.format(out_fld)))
        print()
    else:
        plt.imshow(cvt(img))
        plt.title(img_class)
        plt.show()


if __name__ == '__main__':
    shutil.rmtree(out_fld, ignore_errors=True)
    main()
