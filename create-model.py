import numpy as np
import matplotlib.pyplot as plt
from IPython.core.debugger import set_trace

import torch
import torch.nn as nn
import torch.nn.functional as F  
import torch.optim as optim
import torchvision
from torchvision import transforms

import glob
import os
from skimage.io import imread
from dataloader import DataLoader
from Unet import Unet
from torch.utils import data
from torch.utils.data import random_split

batch=16

dataset = DataLoader(split="trenink")
trainset, valset, test= random_split(dataset, [530,70,70])
#print(len(trainset))

trainloader = torch.utils.data.DataLoader(
    trainset, batch_size=1, num_workers=8, shuffle=True, drop_last=True)
testloader = torch.utils.data.DataLoader(
    valset, batch_size=1, num_workers=8, shuffle=True, drop_last=True)
finaltestloader = torch.utils.data.DataLoader(
    test, batch_size=1, num_workers=8, shuffle=True, drop_last=True)
#print(len(finaltestloader))    

net=Unet().cuda()
net.requires_grad=True

optimizer = torch.optim.Adam(net.parameters(), lr=0.001)
device="cuda" if torch.cuda.is_available() else "cpu"
net=net.to(device)

train_loss=[]
test_loss=[]
position=[]
train_loss_tmp=[]
test_loss_tmp=[]
#train_acc=[]
#test_acc=[]
#train_acc_tmp=[]
#test_acc_tmp=[]

it=-1
for epoch in range(1):
  for k,(data,lbl) in enumerate(trainloader):
    it+=1
    print(it)
    
    data=data.cuda()
    lbl=lbl.cuda()
    
    data.requires_grad=True
    lbl.requires_grad=True
    
    optimizer.zero_grad()   # zero the gradient buffers
    net.train()
    output=net(data)
    #output=F.sigmoid(output)
    
    loss=torch.mean((lbl-output)**2)
    loss.backward()  ## claculate gradients
    optimizer.step() ## update parametrs
    
    #lbl_num=np.argmax(lbl.detach().cpu().numpy(),axis=1)
    #clas=np.argmax(output.detach().cpu().numpy(),axis=1)
    #acc=np.mean((clas==lbl_num))
    
    
    #train_acc_tmp.append(acc)
    train_loss_tmp.append(loss.detach().cpu().numpy())
    
    if it%50==0:
                  
      fig = plt.figure()
      fig.add_subplot(1, 3, 1)
      plt.imshow(data[0, 0, :, :].detach().cpu().numpy(), cmap="gray")
      fig.add_subplot(1, 3, 2)
      plt.imshow(output[0, 0, :, :].detach().cpu().numpy(), cmap="gray")
      fig.add_subplot(1, 3, 3)
      plt.imshow(lbl[0, 0, :, :].detach().cpu().numpy(), cmap="gray")

      for kk,(data,lbl) in enumerate(testloader):
          
          data=data.cuda()
          lbl=lbl.cuda()
          
          #data.requires_grad=True
          #lbl.requires_grad=True
          #optimizer.zero_grad()   # zero the gradient buffers

          net.eval()
          output=net(data)
          #output=F.sigmoid(output)

          loss=torch.mean((lbl-output)**2)

          #lbl_num=np.argmax(lbl.detach().cpu().numpy(),axis=1)
          #clas=np.argmax(output.detach().cpu().numpy(),axis=1)
          #acc=np.mean((clas==lbl_num))
        
        
          #train_acc_tmp.append(acc)
          test_loss_tmp.append(loss.detach().cpu().numpy())
        
          fig = plt.figure()
          fig.add_subplot(1, 3, 1)
          plt.imshow(data[0, 0, :, :].detach().cpu().numpy(), cmap="gray")
          fig.add_subplot(1, 3, 2)
          plt.imshow(output[0, 0, :, :].detach().cpu().numpy(), cmap="gray")
          fig.add_subplot(1, 3, 3)
          plt.imshow(lbl[0, 0, :, :].detach().cpu().numpy(), cmap="gray")
                
      
      train_loss.append(np.mean(train_loss_tmp))
      test_loss.append(np.mean(test_loss_tmp))
      #train_acc.append(np.mean(train_acc_tmp))
      #test_acc.append(np.mean(test_acc_tmp))
      position.append(it)
      
      train_loss_tmp=[]
      test_loss_tmp=[]
      #train_acc_tmp=[]
      #test_acc_tmp=[]
      
      fig = plt.figure()
      plt.plot(position,train_loss, label="training loss")      #oznaceni legendy
      plt.plot(position,test_loss,label="validation loss")
      plt.legend()
      plt.ylabel('Chybová funkce')                                           #označení os
      plt.xlabel('Počet snímků')
      plt.show()
      
      #plt.plot(position,train_acc)
      #plt.plot(position,test_acc)
      #plt.show()
      
      plt.savefig('images/training_loss.png')
      #plt.close("all")

torch.save(net.state_dict(), '/home/ubmi/Documents/data_vse/model2.pt')

print('Training finished!!!')

################################################################# testováí
device = torch.device("cuda")
net = Unet()                                                               #instancování třídy vytvořené v modelu
net.load_state_dict(torch.load('/home/ubmi/Documents/data_vse/model.pt'))  #volání natrénovaného modelu
net=net.to(device)

it=-1
for jj,(data,lbl) in enumerate(finaltestloader):
    it+=1
    print(it)
          
    data=data.cuda()
    lbl=lbl.cuda()

    net.eval()
    output=net(data)     
    
    fig = plt.figure()
    fig.add_subplot(1, 3, 1)
    plt.imshow(data[0, 0, :, :].detach().cpu().numpy(), cmap="gray")
    fig.add_subplot(1, 3, 2)
    plt.imshow(output[0, 0, :, :].detach().cpu().numpy(), cmap="gray")
    fig.add_subplot(1, 3, 3)
    plt.imshow(lbl[0, 0, :, :].detach().cpu().numpy(), cmap="gray")

      
    #prevest na np array,ulozit
    data = data.data.cpu().numpy()
    np.save('images/final/data/data'+ str(it), data)
    output = output.data.cpu().numpy()
    np.save('images/final/output/output' + str(it), output)
    lbl = lbl.data.cpu().numpy()
    np.save('images/final/lbl/lbl'+ str(it), lbl)
    

    #output = output.clip(0, 255)
    #output = output.astype(np.uint8)
    #io.imsave('images/final/img1.png', output)
    
