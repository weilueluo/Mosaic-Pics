# :white_square_button:Mosaic-Pics
[中文](https://github.com/Redcxx/Mosaic-Pics/blob/master/README.cn.md)
-  [Sample Image Source](https://twitter.com/sukemyon_443/status/1030028596339822594)
-  Dimension: 4650 x 8280
-  Database: 33k+
-  Used: 6k+
- If you do not have images, I can build it for you, make a issue!


![sample image](https://github.com/Redcxx/Mosaic-Pics/blob/master/picture_outputs/euclidean/picture_0.7.jpg)
# Usage
```
> main.py

arguments:
  -src --source         the image to stimulate
  -s --size             the size of each pieces
  -d --dest             the images output folder
  -f --folder           the folder containing images used to stimulate the source

optional arguments:
  -m --method          the method used to compute difference of two colors,
                         default use euclidean (can be change in settings.py)
  -r --repeat           allow build with repeating images
  -fa --factor          result size compared to original size

  ---
  method currently supported
  ---
  euclidean              classic euclidean distance between colors
  weighted euclidean     euclidean but RGB fit to human perception: 0.3R, 0.59G, 0.11B
  weighted euclidean+    closer approx than weighted euclidean: 2R, 4G, 3B
  weighted euclidean++   closer approx than weighted euclidean, details see source
  all                    run all methods

  method source: https://en.wikipedia.org/wiki/Color_difference
  ps: use " to surround multiple words input

  ---
  relative speed (my machine)
  ---
  euclidean:             k
  weighted euclidean:    k+-(~5%)
  weighted euclidean+:   k+-(~5%)
  weighted euclidean++:  k+(~20%)

```
# Note
- On first run it will create a database in source folder, subsequent run with same database will be much faster, see [settings.py](https://github.com/Redcxx/Mosaic-Pics/blob/master/settings.py) for more details
- You should config [settings.py](https://github.com/Redcxx/Mosaic-Pics/blob/master/settings.py) before the first run on new database folder
