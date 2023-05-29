from torchvision import transforms
import torch
import numpy as np
import av

# 这段代码是工具函数模块，包含了一些常用的图像处理函数和计算函数。它提供了以下功能：

# extract_frames：从视频文件中提取帧。

# gram_matrix：计算给定特征图的 Gram 矩阵，用于计算风格损失。

# train_transform：训练时用于对输入图像进行预处理的变换，包括 resize、random crop、ToTensor 和 Normalize 等操作。

# style_transform：用于对样式图像进行预处理的变换，包括 resize、ToTensor、Lambda 和 Normalize 等操作。

# denormalize：使用平均值和标准差对图像张量进行反归一化。

# deprocess：反归一化和缩放图像张量，以便将其保存为图像文件。

# 因此，这个模块主要涵盖了图像处理和特征计算方面的功能。

# Mean and standard deviation used for pre-trained PyTorch models
mean = [0.485, 0.456, 0.406]
std = [0.229, 0.224, 0.225]

def train_transform(image_size):
    """ 对训练集图像进行transforms """
    transform = transforms.Compose(
        [
            transforms.Resize(int(image_size * 1.15)),
            transforms.RandomCrop(image_size),
            transforms.ToTensor(),
            transforms.Normalize(mean, std),
        ]
    )
    return transform

def extract_frames(video_path):
    """ 从视频文件中提取帧 """
    frames = []
    video = av.open(video_path)
    for frame in video.decode(0):
        yield frame.to_image()


def gram_matrix(y):
    """ Returns the gram matrix of y (used to compute style loss) """
    (b, c, h, w) = y.size()
    features = y.view(b, c, w * h)
    features_t = features.transpose(1, 2)
    gram = features.bmm(features_t) / (c * h * w)
    return gram



def style_transform(image_size=None):
    """ Transforms for style image """
    resize = [transforms.Resize(image_size)] if image_size else []
    transform = transforms.Compose(resize + [transforms.ToTensor(), transforms.Lambda(lambda x: x.expand(3, -1, -1)), transforms.Normalize(mean, std)])
    return transform


def denormalize(tensors):
    """ Denormalizes image tensors using mean and std """
    for c in range(3):
        tensors[:, c].mul_(std[c]).add_(mean[c])
    return tensors


def deprocess(image_tensor):
    """ Denormalizes and rescales image tensor """
    image_tensor = denormalize(image_tensor)[0]
    image_tensor *= 255
    image_np = torch.clamp(image_tensor, 0, 255).cpu().numpy().astype(np.uint8)
    image_np = image_np.transpose(1, 2, 0)
    return image_np
