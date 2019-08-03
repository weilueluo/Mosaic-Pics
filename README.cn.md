# :white_square_button:Mosaic-Pics
-  [图片来源](https://twitter.com/sukemyon_443/status/1030028596339822594)
-  尺寸: 4650 x 8280
-  图片数据库数量: 3.3w
-  使用的图片数量: 0.6w
-  如果你想我帮你做，写一个issue就行辣


![例图](https://github.com/Redcxx/Mosaic-Pics/blob/master/picture_outputs/euclidean/picture_0.7.jpg)
# 用法
```
> main.py

参数:
  -src --source         要模拟的图片
  -s --size             每张小图的大小
  -d --dest             输出文件夹
  -f --folder           用于模拟图片的图片文件夹

可选参数:
  -m --method           用于计算色差的算法
                        默认欧几里德，可在settings.py中修改
  -r --repeat           允许重复，默认不允许
  -fa --factor          输出图片为输入图片的多少倍，支持浮点数

  ---
  当前支持的算法
  ---
  euclidean              经典的欧几里德算法
  weighted euclidean     更接近人类感知的欧几里德算法： 0.3红, 0.59绿, 0.11蓝
  weighted euclidean+    更更接近人类感知的欧几里德算法: 2红, 4绿, 3蓝
  weighted euclidean++   更更接近人类感知的欧几里德算法, 详情参考来源
  all                    每个算法都用

  来源: https://en.wikipedia.org/wiki/Color_difference
  ps：用 " 包裹多个字的算法

  ---
  相对速度 （在我的电脑上）
  ---
  euclidean:             k
  weighted euclidean:    k+-(~5%)
  weighted euclidean+:   k+-(~5%)
  weighted euclidean++:  k+(~20%)

```
# 注意
- 用新图片文件运行时，程序会在文件夹建立一个数据库，加快接下来的运行，详情参考[settings.py](https://github.com/Redcxx/Mosaic-Pics/blob/master/settings.py)
- 用新文件夹之前，最好改一下[settings.py](https://github.com/Redcxx/Mosaic-Pics/blob/master/settings.py)里的数据库参数
- 程序只会用jpg和png文件，并且不会深入文件夹中的文件夹搜寻图片
