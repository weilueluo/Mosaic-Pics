DEFAULT_COLOR_DIFF_METHOD = 'euclidean'
ALLOWED_METHODS = ['euclidean', 'weighted euclidean', 'weighted euclidean+', 'weighted euclidean++']
# for checking input
ALLOWED_INPUT_METHODS = ['euclidean', 'weighted euclidean', 'weighted euclidean+', 'weighted euclidean++', 'all']
# for saving to different folder if 'all' method is passed in and for method reference
ALLOWED_METHODS_SIGNATURE = {
            'euclidean': 'euclidean',
            'weighted euclidean': 'weighted_euclidean',
            'weighted euclidean+': 'weighted_euclidean_plus',
            'weighted euclidean++': 'weighted_euclidean_plus_plus'
        }
"""
https://en.wikipedia.org/wiki/Color_difference

# using rgb color space
'euclidean'  # euclidean algorithm
'euclidean+'  # said to be slightly better than euclidean, speed: euclidean +(~5%)
'weighted euclidean'  # weighted approach, said to be better than euclidean+, speed: euclidean +(~5%)
'euclidean++'  # said to be much better than euclidean, speed: euclidean +(~20%)

# XXX These METHODS BELOW ARE BUGGY
# using CIE LAB Illuminant D65 color space, converted from rgb
'cie76'  # euclidean algorithm for LAB, speed: euclidean (~0%)
'cie94'  #  cie94 algorithm, speed: euclidean +(~100%)
'ciede2000'  # ciede2000 algorithm, speed, euclidean +(~500%)  
'cmc21'
'cmc11'
"""

# do not change below after database is created
# should be config before first run
DATABASE_NAME = '.image_database'
DATABASE_FILE_TYPE = '.data'
DATABASE_META_FILE = 'meta'

# reduce below if first run countered memory error

# size of cache chunk before saving to local, must be >= 1
# setting a low chunk size will result in subsequent run
# set this amount as high as possible for highest performance
DATABASE_CHUNK_SIZE = 2000
# the size of each image in database
# input size should not be less than value below
DATABASE_IMAGE_HEIGHT = 120
DATABASE_IMAGE_WIDTH = 120

# constants, never change
MAX_RGB_VALUE = 256
