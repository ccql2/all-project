#!/usr/bin/env python
# coding: utf-8


import torch
import torch.nn as nn
import torch.utils.data as Data
import matplotlib.pyplot as plt
import numpy as np
import PIL.Image
import os





def loadData():#加载数据的方法
    xData = list()#存图片数据
    yData = list()#存标签，12类，所以是0-11
    labelNameDict = dict()
    dataPath = "./GarbageClassification/"#数据路径
    listdir  = os.listdir(dataPath)#遍历文件夹下所有子文件夹
    for label,labelName in enumerate(listdir):
        labelNameDict[label] = labelName
        for filename in os.listdir(dataPath + labelName):#索引和名称进行对应
           if not filename.endswith('.jpg'):#判断图片格式
               continue
           imageSize = (32,32)#尺寸的缩放
           x = PIL.Image.open(dataPath + labelName + '/' +filename).resize(imageSize)
           x = torch.FloatTensor(np.array(x))/255#归一化
           #[32,32,3]->[3,32,32]#32是像素比，3是通道数，需要转化为通道在前面
           x = x.permute(2,0,1)#这相当于就是索引
           xData.append(x)
           yData.append(label)#类别对应的序号0到11
    return xData, yData, labelNameDict


class Dataset(Data.Dataset):
    def __init__(self):
        pass
    def __len__(self):
        return len(xData)
    def __getitem__(self, i):
        return xData[i], yData[i]




class Model(nn.Module):#下面是做卷积
    def __init__(self):
        super().__init__()
        self.cnn1 = nn.Conv2d(in_channels=3,#输入三个通道
                              out_channels=16,#输入就是十六个通道
                              kernel_size=5,#卷积核大小
                              stride=2,#步长2
                              padding=0)#填充设为0
        self.cnn2 = nn.Conv2d(in_channels=16,
                              out_channels=32,
                              kernel_size=3,
                              stride=1,
                              padding=1)
        self.cnn3 = nn.Conv2d(in_channels=32,
                              out_channels=128,
                              kernel_size=7,
                              stride=1,
                              padding=0)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)#池化层，我们做的是最大池化
        self.relu = nn.ReLU()
        self.fc = nn.Linear(in_features=128, out_features=12)#线性层，因为我们的结果需要线性分类，out是12因为我们有12个类别的图像分类
    def forward(self, x):
        # [8 3 32 32] -> [8 16 14 14] #这是经历第一次卷积后
        x = self.cnn1(x)
        x = self.relu(x)
        # [8 16 14 14] -> [8 32 14 14]
        x = self.cnn2(x)
        x = self.relu(x)
        # [8 32 14 14] -> [8 32 7 7]
        x = self.pool(x)
        # [8 32 7 7] -> [8 128 1 1]
        x = self.cnn3(x)
        x = self.relu(x)
        # [8 128 1 1] -> [8 128]
        x = x.flatten(start_dim=1)
        return self.fc(x)






def train():
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)#Adam是优化器的一种
    loss_fun = nn.CrossEntropyLoss()#交叉熵损失函数
    model.train()
    for epoch in range(3):   #先跑5轮试一下
        for step, (x, y) in enumerate(loader):
            out = model(x.to(device))
            loss = loss_fun(out.to("cpu"), y)
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
            if step % 200 == 0:#每跑200批次算一次准确率
                acc = (out.to("cpu").argmax(dim=1) == y).sum().item() / len(y)
                print(f"epoch：{epoch}轮，序号：{step:<5}，损失：{loss.item():<20}，准确率：{acc}")

    torch.save(model, "./垃圾分类.model")#保存一下模型





@torch.no_grad()
def test():
    model = torch.load("./垃圾分类.model").to("cpu")
    model.eval()
    correct = 0
    total = 0
    for i in range(100):
        x, y = next(iter(loader))
        out = model(x).argmax(dim=1)
        correct += (out == y).sum().item()
        total += len(y)
    print("准确率：" + str(correct / total))



#####################################################################



device = torch.device("cuda:0"if torch.cuda.is_available()else "cpu")





xData, yData, labelNameDict = loadData()


len(xData),len(yData),xData[0].shape,yData[0]





dataset = Dataset()


loader = Data.DataLoader(dataset=dataset,
                         batch_size=8,
                         shuffle=True,
                         drop_last=True)





x, y = next(iter(loader))


len(loader), x.shape, y



model = Model().to(device)

train()#训练一下试一下



test()



x, y = next(iter(loader))
model = torch.load("./垃圾分类.model").to("cpu")
out = model(x).argmax(dim=1)
x.shape


plt.rcParams['font.sans-serif'] = ['SimHei']
titles = [f"预测{labelNameDict[pre]}，真实：{labelNameDict[label]}" for pre, label in zip(out.tolist(), y.tolist())]
image = [img for img in x.permute(0, 2, 3, 1).numpy()]
plt.figure(figsize=(50, 50))
for i in range(8):
    plt.subplot(2, 4, i + 1)
    plt.imshow(image[i])
    plt.title(titles[i])
    plt.xticks([]),plt.yticks([])
    plt.savefig('./savefig_{}_example.png'.format(i+1))

plt.show




