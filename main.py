import argparse
import functools
import math
import os
from multiprocessing.dummy import Pool

from PIL import Image

import settings
import utilities
from database import ImageDatabase


def resize_to_factor(source, factor):
    width, height = source.size
    return source.resize((int(width * factor), int(height * factor)))


def make_diff_blended_images(background, foreground):
    # make 1/10 to 9/10 blended
    for blend_ratio in range(1, 10):
        blend_ratio = blend_ratio / 10
        blended_images = Image.blend(foreground, background, blend_ratio)
        yield blended_images, blend_ratio


def save_images(source, background, folder, input_file):
    print('Blending & saving images ... ', end='')

    if not os.path.isdir(folder):
        os.mkdir(folder)

    input_file_name, _ = os.path.splitext(input_file)

    source_file = os.path.join(folder, input_file_name + '_0.0_source.jpg')
    source.save(source_file)

    background_file = os.path.join(folder, input_file_name + '_1.0_background.jpg')
    background.save(background_file)

    output_file = os.path.join(folder, input_file_name + '_{}.jpg')
    for image, blend_percent in make_diff_blended_images(background, source):
        image.save(output_file.format(blend_percent))

    print('[ done ]')


def generate_matcher(folder, size):
    database = ImageDatabase(folder, width=size, height=size)
    database.load_database()

    return database.generate_matcher()


def _match_one(chunk_index, source, background, matcher, use_repeat, method):
    chunk = source.crop(chunk_index)
    best_match = matcher.find_closest(chunk, method=method)
    if not use_repeat:
        matcher.remove(best_match)
    background.paste(best_match.image, (chunk_index[0], chunk_index[1]))


def _build_without_repeat(source, background, matcher, chunk_indexes, method):
    _build_ = functools.partial(_match_one, background=background, source=source, matcher=matcher, use_repeat=False,
                                method=method)
    total = len(chunk_indexes)
    for index, chunk_index in enumerate(chunk_indexes):
        _build_(chunk_index)
        utilities.print_progress(index + 1, total)
    utilities.print_done()
    return background


def _build_with_repeat(source, background, matcher, chunk_indexes, method):
    _build_ = functools.partial(_match_one, background=background, source=source, matcher=matcher, use_repeat=True,
                                method=method)
    # This is actually slower
    # pool = Pool()
    # total = len(chunk_indexes)
    # for index, _ in enumerate(pool.imap_unordered(_build_, chunk_indexes, chunksize=1)):
    #     utilities.print_progress(index + 1, total)
    # utilities.print_done()
    # return background

    total = len(chunk_indexes)
    for index, chunk_index in enumerate(chunk_indexes):
        _build_(chunk_index)
        utilities.print_progress(index + 1, total)
    utilities.print_done()
    return background


def _build(source, matcher, step, use_repeat, method):
    source_width, source_height = source.size

    total_chunks = math.ceil(source_width / step) * math.ceil(source_height / step)

    if matcher.size < total_chunks and not use_repeat:
        raise ValueError('Database does not have enough images: {} < {}'.format(matcher.size, total_chunks))

    print('')  # new line
    print('Gathering chunks | {}'.format(total_chunks))

    curr_chunk_num = 0
    chunk_indexes = []
    for upper in range(0, source_height, step):
        for left in range(0, source_width, step):
            right = left + step
            lower = upper + step
            if right > source_width:
                right = source_width
            if lower > source_height:
                lower = source_height
            chunk_indexes.append((left, upper, right, lower))
            # curr_chunk = source.crop((left, upper, right, lower))
            # chunks.append(curr_chunk)
            # best_match = matcher.find_closest(curr_chunk, method=method)
            # if not use_repeat:
            #     matcher.remove(best_match)
            # background.paste(best_match.image, (left, upper))
            curr_chunk_num += 1
            utilities.print_progress(curr_chunk_num, total_chunks)
    utilities.print_done()

    background = Image.new(source.mode, source.size, 'black')

    print(
        'building image | {} | {} x {} | [{}] -> {} '.format(method, background.width, background.height, matcher.size,
                                                             total_chunks))
    if use_repeat:
        return _build_with_repeat(source, background, matcher, chunk_indexes, method)
    else:
        return _build_without_repeat(source, background, matcher, chunk_indexes, method)


def build(source_file, dest_folder, database_folder, size, factor, use_repeat,
          method=settings.DEFAULT_COLOR_DIFF_METHOD):
    matcher = generate_matcher(database_folder, size)
    resized_source = resize_to_factor(Image.open(source_file).convert('RGB'), factor)

    if not os.path.isdir(dest_folder):
        os.mkdir(dest_folder)

    if method == 'all':
        total = len(settings.ALLOWED_METHODS)
        for index, method in enumerate(settings.ALLOWED_METHODS):
            result_image = _build(resized_source, matcher, size, use_repeat=use_repeat, method=method)
            result_folder = os.path.join(dest_folder, settings.ALLOWED_METHODS_SIGNATURE[method])

            if not os.path.isdir(result_folder):
                os.mkdir(result_folder)

            save_images(resized_source, result_image, result_folder, source_file)
            matcher.restore()
            print(' >>> {} / {} | {} [ done ] => {}'.format(index + 1, total, method, result_folder))

    else:
        result_image = _build(resized_source, matcher, size, use_repeat=use_repeat, method=method)
        save_images(resized_source, result_image, dest_folder, source_file)

    print('')  # new line
    print('[= done =] => {}'.format(dest_folder))


def main():
    parser = argparse.ArgumentParser(description='build image from images')

    # required
    parser.add_argument('-src', '--source', help='the image to stimulate', required=True)
    parser.add_argument('-s', '--size', type=int, help='the size of each pieces', required=True)
    parser.add_argument('-d', '--dest', help='the images output folder', required=True)
    parser.add_argument('-f', '--folder', help='the folder containing images used to stimulate the source',
                        required=True)

    # optional
    parser.add_argument('-m', '--method',
                        help='the method used to compute difference of two images, default use '
                             'settings.DEFAULT_COLOR_DIFF_METHOD', default=settings.DEFAULT_COLOR_DIFF_METHOD,
                        choices=settings.ALLOWED_INPUT_METHODS)
    parser.add_argument('-r', '--repeat', action='store_true', help='allow build with repeating images')
    parser.add_argument('-fa', '--factor', type=float, help='result size compared to original size', default=1)

    args = parser.parse_args()

    w, h = Image.open(args.source).size
    total_pieces = math.ceil((w * args.factor) / args.size) * math.ceil((h * args.factor) / args.size)
    print('=' * 50)
    print('src folder:', args.folder)
    print('dest folder:', args.dest)
    print('factor:', args.factor)
    print('size:', args.size)
    print('total:', total_pieces)
    print('repeat:', args.repeat)
    print('method:', args.method)
    print('=' * 50)
    print('')  # new line

    # main process
    build(source_file=args.source, dest_folder=args.dest, database_folder=args.folder, size=args.size,
          factor=args.factor, use_repeat=args.repeat, method=args.method)


if __name__ == '__main__':
    main()
