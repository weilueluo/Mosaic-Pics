import pickle
import re
import time

import numpy as np
from math import *


def clean_filename_for_windows(filename):
    return re.sub(r'[<>:"/\\|?*]', '', str(filename))


def save(item, path):
    with open(path, 'wb') as file:
        pickle.dump(item, file, protocol=pickle.HIGHEST_PROTOCOL)


def load(path):
    with open(path, 'rb') as file:
        return pickle.load(file)


def get_chunksize(files_count):
    max_divider = 100  # 100%
    files_per_divider = 0
    while files_per_divider < 1 and max_divider >= 1:
        files_per_divider = files_count // max_divider
        max_divider -= 1
    if files_per_divider < 1:
        files_per_divider = 1

    return files_per_divider


def get_avg_rgb(im):
    return np.array(im).mean(axis=(0, 1)).tolist()


#
# conversions
#

# not use
def rgb_to_lch(r, g, b):
    x, y, z = rgb_to_xyz(r, g, b)
    l, a, b = xyz_to_lab(x, y, z)
    return lab_to_lch(l, a, b)


def rgb_to_lab(r, g, b):
    x, y, z = rgb_to_xyz(r, g, b)
    return xyz_to_lab(x, y, z)


def forward_trans_func(value):
    delta = 216 / 24389.0
    k = 24389 / 27.0

    if value > delta:
        value = pow(value, 0.333333333333333)
    else:
        value = (k * value + 16) / 116.0

    return value


def xyz_to_lab(x, y, z):
    # Illuminant D65
    x /= 95.0489
    y /= 100.0
    z /= 108.8840

    forwarded_trans_y = forward_trans_func(y)
    l = 116 * forwarded_trans_y - 16
    a = 500 * (forward_trans_func(x) - forwarded_trans_y)
    b = 200 * (forwarded_trans_y - forward_trans_func(z))

    l = round(l, 4)
    a = round(a, 4)
    b = round(b, 4)

    return l, a, b


def rgb_to_xyz(r, g, b):
    rgb = [r, g, b]  # for looping
    # reverse gamma correction
    for i in range(3):
        rgb[i] = rgb[i] / 255.0
        if rgb[i] <= 0.04045:
            rgb[i] = rgb[i] / 12.92
        else:
            rgb[i] = pow(((rgb[i] + 0.055) / 1.055), 2.4)

    # linear transformation to xyz
    x = rgb[0] * 0.4124 + rgb[1] * 0.3576 + rgb[2] * 0.1805
    y = rgb[0] * 0.2126 + rgb[1] * 0.7152 + rgb[2] * 0.0722
    z = rgb[0] * 0.0193 + rgb[1] * 0.1192 + rgb[2] * 0.9504

    return x, y, z


# not use
def lab_to_lch(l, a, b):
    # http://www.brucelindbloom.com/index.html?Eqn_Lab_to_LCH.html
    l = l
    c = sqrt(pow(a, 2) + pow(b, 2))
    if b == 0 and a == 0:
        h = 0
    else:
        h = degrees(atan2(b, a))
        h = h if h >= 0 else h + 360

    return l, c, h


####
# EVERY COLOR DIFF ALGORITHMS IMPLEMENTED BELOW MISSING A SQRT FOR THE END RESULT
# BECAUSE WHEN FINDING MIN IMAGE COLOR DIFFERENCE I DO NOT CARE ABOUT THE ACTUAL DISTANCE
####








def delta_e_94(l1, a1, b1, l2, a2, b2):
    a1b1_dist = sqrt(pow(a1, 2) + pow(b1, 2))
    a2b2_dist = sqrt(pow(a2, 2) + pow(b2, 2))
    ab_dist_diff = a1b1_dist - a2b2_dist
    hue_diff = sqrt(pow((a1 - a2), 2) + pow((b1 - b2), 2) - pow(ab_dist_diff, 2))

    # using graphic art weighting
    sc = 1 + (0.045 * a1b1_dist)
    sh = 1 + (0.015 * a2b2_dist)

    return pow((l1 - l2), 2) + pow((ab_dist_diff / sc), 2) + (hue_diff / sh)


def delta_e_00(l1, a1, b1, l2, a2, b2):
    # Assuming Kc and Kh are 1
    # Using graphic arts for kL, k1 and k2

    a1b1_dist = sqrt(pow(a1, 2) + pow(b1, 2))
    a2b2_dist = sqrt(pow(a2, 2) + pow(b2, 2))

    c_mean = (a1b1_dist + a2b2_dist) / 2.0
    c_mean_pow7 = pow(c_mean, 7)

    c_mean_25_pow7 = c_mean_pow7 + 6103515625  # 25 ** 7
    rev_c_mean_dist = 1 - sqrt(c_mean_pow7 / c_mean_25_pow7)
    a_1 = a1 + (a1 / 2.0) * rev_c_mean_dist
    a_2 = a2 + (a2 / 2.0) * rev_c_mean_dist
    c_diff = a2b2_dist - a1b1_dist

    h1 = degrees(atan2(b1, a_1)) % 360
    h2 = degrees(atan2(b2, a_2)) % 360

    h_diff_abs = fabs(h1 - h2)

    h_sum = h1 + h2
    if a1b1_dist == 0 or a2b2_dist == 0:
        h_diff = 0
        h = h_sum
    elif h_diff_abs <= 180:
        h_diff = h2 - h1
        h = h_sum / 2.0
    else:  # h_diff_abs > 180
        if h2 <= h1:
            h_diff = h2 - h1 + 360
        else:
            h_diff = h2 - h1 - 360
        if h_sum < 360:
            h = (h_sum + 360) / 2.0
        else:
            h = (h_sum - 360) / 2.0

    delta_h = 2 * sqrt(a2b2_dist * a1b1_dist) * degrees(sin(radians(h_diff / 2.0)))

    t = 1 - (0.17 * cos(h - 30)) + (0.24 * cos(radians(2 * h))) + (
            0.32 * cos(radians((3 * h) + 6))) - (0.2 * cos(radians((4 * h) - 63)))

    l_mean = (l1 + l2) / 2.0
    sl = 1 + (0.015 * (l_mean - 50) ** 2) / sqrt(20 + pow((l_mean - 50), 2))
    sc = 1 + (0.045 * c_mean)
    sh = 1 + 0.015 * c_mean * t

    rt = -2 * sqrt(c_mean_pow7 / c_mean_25_pow7) * sin(radians(60 * exp(-pow(((h - 275) / 25), 2))))

    c_diff_div_sc = c_diff / sc
    delta_h_div_sh = delta_h / sh

    return pow(((l2 - l1) / sl), 2) + pow(c_diff_div_sc, 2) + pow(delta_h_div_sh, 2) + (
            rt * c_diff_div_sc * delta_h_div_sh)


# This Algorithm violate symmetry, that is, cmc_diff(c1,c2) != cmc_diff(c2,c1)
def cmc_diff(l1, a1, b1, l2, a2, b2, l, c):
    l = float(l)
    c = float(c)

    c1 = sqrt(pow(a1, 2) + pow(b1, 2))
    c2 = sqrt(pow(a2, 2) + pow(b2, 2))
    c_diff = c1 - c2
    l_diff = l1 - l2
    a_diff = a1 - a2
    b_diff = b1 - b2
    delta_h = sqrt((pow(a_diff, 2)) + pow(b_diff, 2) - pow(c_diff, 2))

    if l1 < 16:
        sl = 0.511
    else:
        sl = (0.040975 * l1) / (1 + (0.01765 * l1))

    sc = ((0.0638 * c1) / (1 + 0.0131 * c1)) + 0.638

    h = degrees(atan2(b1, a1))

    h1 = h if h >= 0 else h + 360

    if 164 <= h1 <= 345:
        t = 0.56 + fabs(0.2 * cos(radians(h1 + 168)))
    else:
        t = 0.36 + fabs(0.4 * cos(radians(h1 + 35)))

    c_pow4 = pow(c1, 4)
    f = sqrt(c_pow4 / (c_pow4 + 1900))

    sh = sc * (f * t + 1 - f)

    return (l_diff / pow((l * sl), 2)) + (c_diff / pow((c * sc), 2)) + pow(delta_h / sh, 2)


def cmc_21_diff(l1, a1, b1, l2, a2, b2):
    return cmc_diff(l1, a1, b1, l2, a2, b2, 2, 1)


def cmc_11_diff(l1, a1, b1, l2, a2, b2):
    return cmc_diff(l1, a1, b1, l2, a2, b2, 1, 1)


def remove_empty(a_list):
    if not isinstance(a_list, list):
        return a_list
    a_list[:] = [remove_empty(item) for item in a_list if item]
    return a_list


#
# below is for printing progress bars
#
class Printer(object):

    def __init__(self):
        self.is_first_print = True
        self.last_percent = None
        self.last_percent_time_left = None
        self.last_percent_print_time = None
        self.est_time_lefts = [0, 0, 0]
        self.start_time = None

    def print_progress(self, curr, total):
        curr_percent = floor(curr / total * 100)
        curr_time = time.time()
        if self.is_first_print:
            est_time_left = float("inf")
            self.is_first_print = False
            self.last_percent_time_left = est_time_left
            self.last_percent_print_time = curr_time
            self.start_time = time.time()
        elif self.last_percent == curr_percent:
            est_time_left = self.last_percent_time_left
        else:
            bad_est_time_left = (curr_time - self.last_percent_print_time) / (curr_percent - self.last_percent) * (
                    100 - curr_percent)
            self.est_time_lefts.append(bad_est_time_left)
            self.est_time_lefts = self.est_time_lefts[1:]
            percent_left = 100 - curr_percent
            percent_diff = curr_percent - self.last_percent
            chunk_left = round(percent_left / percent_diff)
            if chunk_left < len(self.est_time_lefts):
                est_time_left = sum(self.est_time_lefts[-chunk_left:]) / chunk_left if chunk_left != 0 else 0.00
            else:
                est_time_left = sum(self.est_time_lefts) / len(self.est_time_lefts)
            self.last_percent_time_left = est_time_left
            self.last_percent_print_time = curr_time

        self.last_percent = curr_percent

        if est_time_left != 0.0:
            print('\r >>> {0} / {1} => {2}% | Time Left est. {3:.2f}s'.format(curr, total, curr_percent, est_time_left),
                  end='')
        else:
            print('\r >>> {0} / {1} => {2}% '.format(curr, total, curr_percent), end='')

    def print_done(self, msg=None):
        if isinstance(msg, str):
            print(' [ done ] => {msg}s'.format(msg=msg))
        else:  # a float, time taken
            if not self.is_first_print:
                print(' [ done ] => {0:.2f}s'.format(time.time() - self.start_time))
        self.is_first_print = True
        self.start_time = None
        self.last_percent = None
        self.last_percent_print_time = None
        self.last_percent_time_left = None
        self.est_time_lefts = [0, 0, 0]


printer = Printer()


def print_progress(curr, total):
    global printer
    printer.print_progress(curr, total)


def print_done(msg=None):
    global printer
    printer.print_done(msg)
