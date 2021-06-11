import os

import numpy as np


def save_meta(img_class, img, img_num, out_path, h_copy=False):
    if h_copy:
        with open('{}/meta/metafile.txt'.format(out_path), 'w') as f:
            f.write(str(img_class) + ',')
            f.write(','.join([str(x) for x in img.shape]))
            if len(img.shape) < 3:
                f.write(',1')
            f.write(',{}'.format(img_num))

    with open('{}/meta/metafile.bin'.format(out_path), 'wb') as fbin:
        fbin.write(img_class.astype(np.uint8).tobytes())
        for x in img.shape[:2]:
            fbin.write(np.array(x).astype(np.uint16).tobytes())
        c = 1 if len(img.shape) < 3 else img.shape[-1]
        fbin.write(np.array(c).astype(np.uint8).tobytes())

        fbin.write(np.array(img_num).astype(np.uint8).tobytes())


def read_meta(path, verbos=False):
    with open(path, 'rb') as f:
        class_num = int.from_bytes(f.read(1), 'little')
        h = int.from_bytes(f.read(2), 'little')
        w = int.from_bytes(f.read(2), 'little')
        c = int.from_bytes(f.read(1), 'little')
        img_num = int.from_bytes(f.read(1), 'little')

    if verbos:
        print("Class: {}".format(class_num))
        print("Lap depth: {}".format(img_num))
        print("Size: {},{},{}".format(h, w, c))
        print("File Size:", os.path.getsize(path))
        print()
