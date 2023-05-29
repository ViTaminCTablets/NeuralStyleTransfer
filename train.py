# 这段代码属于数据预处理模块，它定义了从原始图像文件创建训练集的过程。在这里，它将指定目录下的所有图像文件转换为指定大小并保存到HDF5文件中，以便后续的训练程序能够快速读取和加载。
import argparse
import os
import sys
import random
from PIL import Image
import numpy as np
import torch
import glob
from torch.optim import Adam, LBFGS
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.utils import save_image
from models import TransformerNet, VGG16, VGG19
from utils import *


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parser for Fast-Neural-Style")
    parser.add_argument("--dataset_path", type=str, required=True, help="path to training dataset")
    parser.add_argument("--style_image", type=str, default="style-images/mosaic.jpg", help="path to style image")
    parser.add_argument("--epochs", type=int, default=1, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=4, help="Batch size for training")
    parser.add_argument("--image_size", type=int, default=256, help="Size of training images")
    parser.add_argument("--style_size", type=int, help="Size of style image")
    parser.add_argument("--lambda_content", type=float, default=1e5, help="Weight for content loss")
    parser.add_argument("--lambda_style", type=float, default=1e10, help="Weight for style loss")
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate")
    parser.add_argument("--checkpoint_model", type=str, help="Optional path to checkpoint model")
    parser.add_argument("--checkpoint_interval", type=int, default=2000, help="Batches between saving model")
    parser.add_argument("--sample_interval", type=int, default=1000, help="Batches between saving image samples")
    args = parser.parse_args()
    style_name = args.style_image.split("/")[-1].split(".")[0]
    os.makedirs(f"images/outputs/{style_name}-training", exist_ok=True)
    os.makedirs(f"checkpoints", exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 创建dataloader
    train_dataset = datasets.ImageFolder(args.dataset_path, train_transform(args.image_size))
    dataloader = DataLoader(train_dataset, batch_size=args.batch_size)

    # 模型定义（生成器和特征提取器） 即风格迁移网络和VGG网络
    transformer = TransformerNet().to(device)
    #vgg=vgg19.VGG19(weights='imagenet',include_top=False)
    #vgg = VGG19(requires_grad=False).to(device)
    vgg = VGG16(requires_grad=False).to(device)


    # Load checkpoint model if specified
    if args.checkpoint_model:
        transformer.load_state_dict(torch.load(args.checkpoint_model))

    # 指定优化器和损失
    #optimizer = LBFGS(transformer.parameters(), lr=args.lr)
    optimizer = Adam(transformer.parameters(), args.lr)
    # MSELoss函数计算两幅图像的均方误差，用于计算内容损失和风格损失
    l2_loss = torch.nn.MSELoss().to(device)

    # Load style image
    style = style_transform(args.style_size)(Image.open(args.style_image))
    style = style.repeat(args.batch_size, 1, 1, 1).to(device)

    # 提取风格特征
    features_style = vgg(style)
    gram_style = [gram_matrix(y) for y in features_style]

    # Sample 8 images for visual evaluation of the model
    image_samples = []
    png_files = glob.glob(f"{args.dataset_path}/*.png")
    if png_files:
        for path in random.sample(png_files, min(8, len(png_files))):
            img = Image.open(path)
            img_tensor = train_transform(args.image_size)(img)
            image_samples += [img_tensor]
    image_samples = torch.stack(image_samples)

    def save_sample(batches_done):
        """ Evaluates the model and saves image samples """
        transformer.eval()
        if len(image_samples) > 0:
            with torch.no_grad():
                output = transformer(image_samples.to(device))
            image_grid = denormalize(torch.cat((image_samples.cpu(), output.cpu()), 2))
            save_image(image_grid, f"images/outputs/{style_name}-training/{batches_done}.jpg", nrow=4)
        transformer.train()

    # def closure():
    #     optimizer.zero_grad()
    
    #     images_original = next(iter(dataloader))[0].to(device)
    #     images_transformed = transformer(images_original)

    #     # Extract features
    #     features_original = vgg(images_original)
    #     features_transformed = vgg(images_transformed)

    #     # Compute content loss as MSE between features
    #     content_loss = args.lambda_content * l2_loss(features_transformed.relu2_2, features_original.relu2_2)

    #     # Compute style loss as MSE between gram matrices
    #     style_loss = 0
    #     for ft_y, gm_s in zip(features_transformed, gram_style):
    #         gm_y = gram_matrix(ft_y)
    #         style_loss += l2_loss(gm_y, gm_s[: images_original.size(0), :, :])
    #     style_loss *= args.lambda_style

    #     total_loss = content_loss + style_loss
    #     total_loss.backward()

    #     return total_loss

    for epoch in range(args.epochs):
        epoch_metrics = {"content": [], "style": [], "total": []}
        for batch_i, (images, _) in enumerate(dataloader):
            optimizer.zero_grad()
            

            images_original = images.to(device)
            images_transformed = transformer(images_original)

            # Extract features
            features_original = vgg(images_original)
            features_transformed = vgg(images_transformed)


            # Compute content loss as MSE between features
            content_loss = args.lambda_content * l2_loss(features_transformed.relu2_2, features_original.relu2_2)

            # Compute style loss as MSE between gram matrices
            style_loss = 0
            for ft_y, gm_s in zip(features_transformed, gram_style):
                gm_y = gram_matrix(ft_y)
                style_loss += l2_loss(gm_y, gm_s[: images.size(0), :, :])
            style_loss *= args.lambda_style

            total_loss = content_loss + style_loss
            total_loss.backward()

            optimizer.step()
            #optimizer.step(closure)
            epoch_metrics["content"] += [content_loss.item()]
            epoch_metrics["style"] += [style_loss.item()]
            epoch_metrics["total"] += [total_loss.item()]

            sys.stdout.write(
                "\r[Epoch %d/%d] [Batch %d/%d] [Content: %.2f (%.2f) Style: %.2f (%.2f) Total: %.2f (%.2f)]"
                % (
                    epoch + 1,
                    args.epochs,
                    batch_i,
                    len(train_dataset),
                    content_loss.item(),
                    np.mean(epoch_metrics["content"]),
                    style_loss.item(),
                    np.mean(epoch_metrics["style"]),
                    total_loss.item(),
                    np.mean(epoch_metrics["total"]),
                )
            )

            batches_done = epoch * len(dataloader) + batch_i + 1
            if batches_done % args.sample_interval == 0:
                save_sample(batches_done)

            if args.checkpoint_interval > 0 and batches_done % args.checkpoint_interval == 0:
                style_name = os.path.basename(args.style_image).split(".")[0]

                torch.save(transformer.state_dict(), f"checkpoints/{style_name}_{batches_done}.pth")