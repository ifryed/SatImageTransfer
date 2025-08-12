import os
from joblib import dump, load
import cv2
import numpy as np

import matplotlib.pyplot as plt

def setSize(new_size):
    global im_size,rand_points
    im_size = tuple((np.ones((2, 1),dtype=int) * new_size).flatten())
    rand_points = getRandomPoints(im_size[0])


def randomDiff(img, im_size, rand_points):
    img = cv2.resize(img, im_size).astype(int)

    ret_vec = np.zeros(len(rand_points))
    for i in range(len(rand_points)):
        x1, y1 = rand_points[i][0]
        x2, y2 = rand_points[i][1]
        ret_vec[i] = img[y1, x1] - img[y2, x2]

    return ret_vec


def getRandomPoints(n=32, seed=42):
    if seed:
        np.random.seed(seed)
    ret_points = []
    for _ in range(n):
        p1 = np.random.randint(0, im_size[0]), np.random.randint(0, im_size[1])
        p2 = np.random.randint(0, im_size[0]), np.random.randint(0, im_size[1])

        ret_points.append((p1, p2))
    return ret_points


def extractFeat(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    gray = hsv[:, :, 2]
    feat = np.array([1])

    hist_hsv, bins = np.histogram(hsv[:, :, 0].ravel(), 90, [0, 180])
    hist_hsv = hist_hsv / hist_hsv.sum()
    feat = np.concatenate([feat, hist_hsv])

    hist_hsv, bins = np.histogram(gray.ravel(), 100, [0, 256])
    hist_hsv = hist_hsv / hist_hsv.sum()
    feat = np.concatenate([feat, hist_hsv])

    channels = list()
    channels.append(('r-hsv', hsv[:, :, 0]))
    channels.append(('r-gray', gray))
    ix = cv2.Sobel(gray.astype(np.float32), -1, 1, 0, ksize=3)
    iy = cv2.Sobel(gray.astype(np.float32), -1, 0, 1, ksize=3)
    grad = np.arctan2(iy, ix)
    mag = np.hypot(iy, ix)
    channels.append(('r-sobelX', ix))
    channels.append(('r-sobelY', iy))
    channels.append(('r-mag', mag))
    channels.append(('r-mag', grad + np.pi))

    for idx, (n, c) in enumerate(channels):
        # rand_points = getRandomPoints(seed=idx)
        rs = randomDiff(c, im_size, rand_points)
        feat = np.concatenate([feat, rs])

        hist, bins = np.histogram(c.ravel(), 6, )
        hist = hist / hist.sum()
        feat = np.concatenate([feat, hist])

    return feat


def classifyImg(img, model_path=None):
    if model_path is None:
        model_path = [x for x in os.listdir() if x.endswith('rfm')][-1]
    model = load(model_path)

    feat = extractFeat(img)

    pred = model.predict([feat])
    return pred[0], np.where(model.classes_ == pred[0])[0][0]


def nms(img, min_dist, max_peaks=10):
    img = img / img.max()
    pts = np.where(img > 0.25)
    pts_v = img[pts[0], pts[1]]
    pts = np.vstack([pts[0], pts[1], pts_v]).T

    pts = pts[(-pts[:, 2]).argsort()]
    ret_pts = []

    while len(pts):
        if len(ret_pts) == max_peaks:
            break

        y, x, v = pts[0, :]
        ret_pts.append([y, x])

        dists = np.square(pts[:, :2] - np.array([y, x])).sum(axis=1) < np.square(min_dist)
        idx_to_delete = np.where(dists)
        pts = np.delete(pts, idx_to_delete, axis=0)

    return np.array(ret_pts, dtype=np.uint16)


def starFinder(img, star_num=20, disp=False):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    min_dist = np.hypot(h, w) * 0.03
    pts = nms(gray, min_dist, max_peaks=star_num)

    if disp:
        can = np.zeros_like(gray)
        can[pts[:, 0], pts[:, 1]] = 1
        plt.subplot(1, 2, 1)
        plt.imshow(img[:, :, [2, 1, 0]])
        ax = plt.gca()
        for p in pts:
            # circle = plt.Circle((p[1], p[0]), min_dist, color='r', fill=False)
            # ax.add_artist(circle)
            circle = plt.Circle((p[1], p[0]), 5, color='r', fill=False)
            ax.add_artist(circle)
            plt.text(p[1] + 1, p[0] + 2, "x:{}\ny:{}".format(*p), color='y', fontsize=10)

        plt.subplot(1, 2, 2)
        plt.imshow(can, cmap='jet')
        for p in pts:
            plt.text(p[1] + 1, p[0] + 2, "x:{}\ny:{}".format(*p), color='y', fontsize=10)
        plt.show()

    return pts


setSize(32)