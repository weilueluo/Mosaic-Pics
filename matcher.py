import settings
import utilities
from items import ImageItem


class Matcher(object):
    def __init__(self, images, width, height):
        self.images = images
        self.width = width
        self.height = height
        self.removed_images = []
        self.converted_to_lab = False

    def find_closest(self, other, method=settings.DEFAULT_COLOR_DIFF_METHOD):
        if not self.images:
            raise ValueError('Please load database first')
        other = ImageItem(other, self.width, self.height)
        return self._find_by_rgb_method(other, getattr(Matcher, settings.ALLOWED_METHODS_SIGNATURE[method]))

    def _find_by_rgb_method(self, other, method):

        if self.converted_to_lab:
            raise ValueError('Conversion from LAB to RGB is not supported')

        min_item = min(self.images,
                       key=lambda image: method(image.r, image.g, image.b, other.r, other.g, other.b))

        return min_item

    @staticmethod
    def euclidean(r1, g1, b1, r2, g2, b2):
        # https://en.wikipedia.org/wiki/Color_difference
        return sqrt(pow((r1 - r2), 2) + pow((g1 - g2), 2) + pow((b1 - b2), 2))

    @staticmethod
    def weighted_euclidean(r1, g1, b1, r2, g2, b2):
        # https://en.wikipedia.org/wiki/Color_difference
        return sqrt(0.3 * pow((r1 - r2), 2) + 0.59 * pow((g1 - g2), 2) + 0.11 * pow((b1 - b2), 2))

    @staticmethod
    def weighted_euclidean_plus(r1, g1, b1, r2, g2, b2):
        # https://en.wikipedia.org/wiki/Color_difference
        return sqrt(2 * pow((r1 - r2), 2) + 4 * pow((g1 - g2), 2) + 3 * pow((b1 - b2), 2))

    @staticmethod
    def weighted_euclidean_plus_plus(r1, g1, b1, r2, g2, b2):
        # https://en.wikipedia.org/wiki/Color_difference
        r_mean = (r1 + r2) / 2.0
        return sqrt((2 + (r_mean / 256.0)) * pow((r1 - r2), 2) + 4 * pow((g1 - g2), 2) + ((2 + (255 - r_mean) / 256.0) * pow(
            (b1 - b2), 2)))

    def remove(self, image):
        self.images.remove(image)
        self.removed_images.append(image)

    def restore(self):
        self.images += self.removed_images
        self.removed_images = []

    @property
    def size(self):
        return len(self.images)
    # def convert_to_lab(self):
    #
    #     for image in self.images:
    #         image.convert_to_lab()
    #     self.converted_to_lab = True
    #
    # def _find_by_lab_method(self, other, method):
    #     if not self.converted_to_lab:
    #         self.convert_to_lab()
    #
    #     other.convert_to_lab()
    #
    #     min_item = min(self.images, key=lambda image: method(image.l, image.a, image.b, other.l, other.a, other.b))
    #
    #     return min_item
    #
    # def find_by_cie76(self, other):
    #     return self._find_by_lab_method(other, utilities.euclidean_diff)
    #
    # def find_by_cie94(self, other):
    #     return self._find_by_lab_method(other, utilities.delta_e_94)
    #
    # def find_by_ciede2000(self, other):
    #     return self._find_by_lab_method(other, utilities.delta_e_00)
    #
    # def find_by_cmc_21(self, other):
    #     return self._find_by_lab_method(other, utilities.cmc_21_diff)
    #
    # def find_by_cmc_11(self, other):
    #     return self._find_by_lab_method(other, utilities.cmc_11_diff)
