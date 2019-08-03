import functools
import glob
import os
import shutil
from multiprocessing.dummy import Pool

import settings
import utilities
from items import DatabaseItem, ImageItem
from matcher import Matcher


class ImageDatabase(object):

    def __init__(self, folder, width, height):
        self.folder = str(folder)
        self.width = width
        self.height = height
        self.files = glob.glob(self.folder + os.path.sep + '*[jpg|png]')
        self.database_path = self.folder + os.path.sep + utilities.clean_filename_for_windows(settings.DATABASE_NAME)
        self.database_meta_file = self.database_path + os.path.sep + settings.DATABASE_META_FILE + settings.DATABASE_FILE_TYPE
        self.image_path_template = self.database_path + os.path.sep + '{index}' + settings.DATABASE_FILE_TYPE
        self.save_image_count = 0
        self.loaded_image_items = None
        self.color_space = None
        self.color_space_database = None

    def get_save_image_path(self):
        self.save_image_count += 1
        return self.image_path_template.format(index=self.save_image_count)

    def update_existing_database(self):
        print('Updating existing database')
        meta_dict = utilities.load(self.database_meta_file)

        files_to_add = [file for file in self.files if file not in meta_dict['files']]
        total_files = len(files_to_add)
        if total_files == 0:
            print('There is no new images found ... [ done ]')
            return
        database_width = meta_dict['image width']
        database_height = meta_dict['image height']
        max_chunk_size = meta_dict['chunk size']
        chunk_count = meta_dict['chunk count']
        file_type = meta_dict['file type']
        database_path = meta_dict['database path']
        cache_images = []
        num_of_cache_images = 0
        data_paths = []

        for index, file in enumerate(files_to_add):
            cache_images.append(DatabaseItem(file, database_width, database_height))
            num_of_cache_images += 1
            if num_of_cache_images >= max_chunk_size:
                chunk_count += 1
                data_path = database_path + os.path.sep + chunk_count + file_type
                utilities.save(cache_images, data_path)
                data_paths.append(data_path)
                cache_images = []
                num_of_cache_images = 0
            utilities.print_progress(index + 1, total_files)
        utilities.print_done()

        # save remaining cached images
        if cache_images:  # if not empty
            chunk_count += 1
            data_path = database_path + os.path.sep + chunk_count + file_type
            utilities.save(cache_images, data_path)
            data_paths.append(data_path)

        meta_dict['number of files'] += len(files_to_add)
        meta_dict['files'] += files_to_add
        meta_dict['paths'] += data_paths
        meta_dict['chunk count'] += chunk_count

        utilities.save(meta_dict, meta_dict['meta file path'])

    def create_database(self):

        print('Creating database | {} | '.format(self.database_path), end='')

        # remove existing database if any
        if os.path.isdir(self.database_path):
            shutil.rmtree(self.database_path)

        os.mkdir(self.database_path)

        pool = Pool()
        file_size = len(self.files)
        database_item_generator = functools.partial(DatabaseItem, width=settings.DATABASE_IMAGE_WIDTH,
                                                    height=settings.DATABASE_IMAGE_HEIGHT)
        print('total {} '.format(file_size))

        data_paths = []
        cache_images = []
        cache_images_size = 0

        print(' >>> waiting for arrival of chunks ...', end='')

        for index, items in enumerate(pool.imap_unordered(database_item_generator, self.files)):
            cache_images.append(items)  # database item
            cache_images_size += 1

            if (cache_images_size >= settings.DATABASE_CHUNK_SIZE) or index + 1 == file_size:
                data_path = self.get_save_image_path()
                data_paths.append(data_path)
                utilities.save(cache_images, data_path)
                cache_images = []
                cache_images_size = 0

            utilities.print_progress(index + 1, file_size)

        database_meta = {
            'number of files': file_size,
            'chunk size': settings.DATABASE_CHUNK_SIZE,
            'files': self.files,
            'paths': data_paths,
            'image width': settings.DATABASE_IMAGE_WIDTH,
            'image height': settings.DATABASE_IMAGE_HEIGHT,
            'chunk count': self.save_image_count,
            'file type': settings.DATABASE_FILE_TYPE,
            'database path': self.database_path,
            'meta file path': self.database_meta_file
        }

        # save meta
        utilities.save(database_meta, self.database_meta_file)

        utilities.print_done()

    def create_and_load_database(self):
        self.create_database()
        self.check_and_load_database()

    def check_and_load_database(self):

        # do some checking first
        if not os.path.isdir(self.database_path):
            raise ValueError('Database does not exists')

        if not os.path.isfile(self.database_meta_file):
            raise ValueError('Corrupted database: missing meta file')

        meta_dict = utilities.load(self.database_meta_file)
        database_chunk_size = meta_dict['chunk size']
        if database_chunk_size != settings.DATABASE_CHUNK_SIZE:
            raise ValueError('Existing database has different chunk size signature | database {} | program {}'.format(
                database_chunk_size, settings.DATABASE_CHUNK_SIZE))

        if settings.DATABASE_IMAGE_WIDTH != meta_dict['image width']:
            raise ValueError('Existing database has different image width signature | database {} | program {}'.format(
                settings.DATABASE_IMAGE_WIDTH, meta_dict['image width']))

        if settings.DATABASE_IMAGE_HEIGHT != meta_dict['image height']:
            raise ValueError('Existing database has different image height signature | database {} | program {}'.format(
                settings.DATABASE_IMAGE_HEIGHT, meta_dict['image height']))

        # now process the database
        num_of_database_images = meta_dict['number of files']
        num_of_files_found = len(self.files)

        if num_of_database_images != num_of_files_found:

            if num_of_database_images == 0:
                self.create_and_load_database()
                return

            while True:
                print('Files found: {} | Database size: {}'.format(num_of_files_found, num_of_database_images))
                print('[1] use existing database')
                print('[2] create new database')
                print('[3] update existing database')
                res = input('Please enter a number:')
                if res == '1':
                    break
                elif res == '2':
                    self.create_and_load_database()
                    return
                elif res == '3':
                    self.update_existing_database()
                    meta_dict = utilities.load(self.database_meta_file)  # update for below use
                    break
                print('Please provide your answer as \'y\' or \'n\'')

        images_list_paths = meta_dict['paths']
        images_list_size = len(images_list_paths)

        print('Loading database | {} | chunks {} | size per chunk {}'.format(self.database_path,
                                                                             images_list_size,
                                                                             meta_dict['chunk size']))

        self.loaded_image_items = []

        for index, images_path in enumerate(images_list_paths):
            try:
                database_items = utilities.load(images_path)
            except AttributeError as e:
                raise ValueError(
                    'Database Object has different signature, did you change your code structure? | {}'.format(e))
            self.loaded_image_items += [ImageItem(item, self.width, self.height) for item in
                                        database_items]
            utilities.print_progress(index + 1, images_list_size)
        utilities.print_done()

    def load_database(self):
        if not os.path.isdir(self.database_path):
            self.create_database()

        try:
            self.check_and_load_database()
            return
        except ValueError as e:
            print(e)

        while True:
            res = input('check and load database failed, destroy and create new? [y/n]:')
            if res == 'y':
                self.create_and_load_database()
                return
            elif res == 'n':
                print('No database is loaded, exiting ...')
                exit(-1)
            print('Please provide your answer as \'y\' or \'n\'')

    def generate_matcher(self):
        if not self.loaded_image_items:
            raise ValueError('Please load images first')

        matcher = Matcher(self.loaded_image_items, self.width, self.height)
        del self.loaded_image_items
        return matcher
