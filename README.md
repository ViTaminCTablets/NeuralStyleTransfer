**程序运行环境配置安装指南** 

1.安装使用PyCharm Community Edition 2022.3.3 

2.安装Python 

3.安装Anaconda 

4.安装PyTorch,opencv,numpy,av,torchvision,ffmpeg,skvideo,pillow,os,tqdm,numpy

5.启动项目 

打开cmd，找到对应的项目目录，在anaconda运行python app.py ,后访问 [http://127.0.0.1:5000](http://127.0.0.1:5000/) 可打开网页。 

6.训练模型

运行python train.py  --dataset_path data/coco/images/ --style_image images/styles/adriaen-van-ostade_landscape.jpg --epochs 1 --batch_size 4 --image_size 256

data/coco/images/替换为自己的数据集地址；

images/styles/adriaen-van-ostade_landscape.jpg 替换为要训练的风格图片地址；



**程序操作指南** 

1.图片风格迁移功能 

打开浏览器，输入[http://127.0.0.1:5000](http://127.0.0.1:5000/)，进入系统首页，在图片风格迁移板块，点击“选择文件”，从本地选择图片上传，后原本为“未选择任何文件”的区域，会显示上传图片的名称和格式。接着在选择风格模型的下拉框里，选择你想要进行风格迁移的风格，点击“apply style”，等待一段时间后，页面会刷新，生成的图片会刷新在新的页面上。 

 

2. 视频风格迁移功能 

打开浏览器，输入[http://127.0.0.1:5000](http://127.0.0.1:5000/)，进入系统首页，在视频风格迁移板块，点击“选择文件”，从本地选择视频上传，后原本为“未选择任何文件”的区域，会显示上传视频的名称和格式。接着在选择风格模型的下拉框里，选择你想要进行风格迁移的风格，点击“apply style”，等待一段时间后，页面会刷新，生成的视频会刷新在新的页面上。 

 

# NeuralStyleTransfer
