

from PIL import Image

import utilities


class DatabaseItem(object):
    def __init__(self, filename, width, height):
        self.image = Image.open(filename).resize((width, height)).convert(mode='RGB')
        self.r, self.g, self.b = utilities.get_avg_rgb(self.image)


class ImageItem(object):
    def __init__(self, item, width, height):

        if isinstance(item, DatabaseItem):
            self.image = item.image.resize((width, height))
        elif isinstance(item, Image.Image):
            self.image = item.resize((width, height)).convert(mode='RGB')
        elif isinstance(item, str):
            self.image = Image.open(item).resize((width, height)).convert(mode='RGB')
        else:
            raise ValueError('item must be either str | DatabaseItem | PIL.Image.Image')

        self.r, self.g, self.b = utilities.get_avg_rgb(self.image)

    # def convert_to_lab(self):
    #     self.l, self.a, self.b = utilities.rgb_to_lab(self.r, self.g, self.b)
    #     del self.r
    #     del self.g
    #     # self.b has been overwritten

# class ColorSpaceDatabase(object):
#     class ColorSpaceFragment(object):
#         def __init__(self, locations, r, g, b):
#             self.locations = locations
#             self.center_r = r
#             self.center_g = g
#             self.center_b = b
#
#     def __init__(self, images):
#         self.color_space_size = settings.MAX_RGB_VALUE
#         self.fragment_size = settings.COLOR_SPACE_FRAGMENT_SIZE
#         self.color_space = self.make_color_space(images)
#
#     def make_color_space(self, images):
#         print('Generating color space | size {}'.format(settings.COLOR_SPACE_FRAGMENT_SIZE))
#         start_time = time.time()
#         # 256 x 256 x 256 list
#         color_space = np.empty((256, 256, 256, 0)).tolist()
#         # color_space = [[[[] for _ in range(256)] for _ in range(256)] for _ in range(256)]
#         print(time.time() - start_time)
#         total = len(images)
#
#         for index, image in enumerate(images):
#             color_space[int(image.r + 0.5)][int(image.g + 0.5)][int(image.b + 0.5)].append(image.image)
#             utilities.print_progress(index + 1, total)
#
#         utilities.print_done(time.time() - start_time)
#         images = None  # save space, no longer used
#         return utilities.remove_empty(color_space)
#
#     def find_by_color_space(self, other, use_repeat):
#         r, g, b = other.r, other.g, other.b
#
#         r = int(r / self.color_space_size * (len(self.color_space) - 1) + 0.5)
#         g = int(g / self.color_space_size * (len(self.color_space[r]) - 1) + 0.5)
#         b = int(b / self.color_space_size * (len(self.color_space[r][g]) - 1) + 0.5)
#
#         item = self.color_space[r][g][b][0]
#         if not use_repeat:
#             self.remove_from_color_space(r, g, b, item)
#
#         return item
#
#     def remove_from_color_space(self, r, g, b, item):
#         self.color_space[r][g][b].remove(item)
#         if not self.color_space[r][g][b]:
#             self.color_space[r][g].remove(self.color_space[r][g][b])
#             if not self.color_space[r][g]:
#                 self.color_space[r].remove(self.color_space[r][g])
#                 if not self.color_space[r]:
#                     self.color_space.remove(self.color_space[r])



    # def find_by_color_space(self, other, use_repeat):
    #     if not self.color_space_database:
    #         self.color_space_database = ColorSpaceDatabase(self.loaded_image_items)
    #         self.loaded_image_items = None
    #
    #     return self.color_space_database.find_by_color_space(other, use_repeat)
