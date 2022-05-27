#这个加密算法的特点在于 
#1)采用生命游戏的机制生成密码表，并用16进制储存 
#2)奇数行和偶数行分别生成密码表，而对特殊字符的标识则需要两个key的共同参与(否则目前看起来会报错)
#3)利用所谓“移位”思想，从而使密码表的一一对应性看起来不是很明显 
#4)在“移位”算法中，保证不影响逆向解密的前提下，显著提高了随机性
#目前可以处理英文、中文和大多数符号，仅限于类似于.txt类型的文件，.doc和.jpg之类的另说
#别问我为什么没有做得更好，bobo快猝死了...
#顺便吐槽一下文件的编码这块，真TM烦人，学了茫茫久才知道大概该怎么处理，不过现在还是没办法处理所有类型的文件
#20190304凌晨又是一个通宵，成功的把UI界面做出来了，本来还想再帅一点，但没料到UI和源程序的接口这么难弄，累死了
#20190304晚上到20190305凌晨把程序做了几十倍的加速，大幅修改了编码机制，但是还是只能处理文本文件
#20220527 translate some words into English, and uploaded to github
import random,numpy,numba,os,chardet,time,sys,ctypes
import tkinter as tk
from tkinter import filedialog,messagebox

maxlen=95#根据unicode码算了好久orz

whnd = ctypes.windll.kernel32.GetConsoleWindow()#这几段话是从网上直接下载下来的
if whnd != 0:    #这几段话是从网上直接下载下来的
 ctypes.windll.user32.ShowWindow(whnd, 0)    #这几段话是从网上直接下载下来的
 ctypes.windll.kernel32.CloseHandle(whnd)#这几段话是从网上直接下载下来的


def createmat(lifespan,encryptornot,name,typ,keymap):#生命游戏，最终达到有限的给定的随机产生的寿命，结束演化

 @numba.jit(nopython=True)#用numba模块进行运算加速(把脚本转化成机器码)，但是语法上就很头大
 def nstep(aa):           #所以这里就在想我干嘛想不开要用python，明明pascal快上几百倍(numba没开，开了也还差几倍)
  d=numpy.zeros((maxlen+2,maxlen+2),dtype=numpy.int32)
  for i in range(1,maxlen+1):
   for j in range(1,maxlen+1):
    s=0
    for k in range(8): s+=aa[i+ks[k][0]][j+ks[k][1]]#生命游戏规则
    if s==3: d[i][j]=1
    elif s==2: d[i][j]=aa[i][j]
    else: d[i][j]=0
  return d
 
 def iniencrypt(aa):   #根据我内定的密度density来随机生成初始状态
  for i in range(1,maxlen+1):
   for j in range(1,maxlen+1):
    t=random.randint(1,100)
    if t<density: aa[i][j]=1
    else: aa[i][j]=0 
  createkey(aa,lifespan,name)
  return aa
 
 density=65
 ks=numpy.array([[-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]])
 a=numpy.zeros((maxlen+2,maxlen+2),dtype=numpy.int32) 
 if encryptornot: a=iniencrypt(a)
 else:   #如果是为了解密的话就得读入存了的初始状态(写成这样是可以看起来短一点)
  for i in range(1,maxlen+1):
   for j in range(1,maxlen+1):
    a[i][j]=keymap[i][j]
 life=0
 while 1:#not(finish(2) or finish(3)):
  a=nstep(a)
  if life%10==0:
   canvas.itemconfig(ringo[typ],extent=int(71*life/lifespan))#UI环形进度条
   canvas.itemconfig(ringi[typ],extent=int(71*life/lifespan))
   root.update()
  life+=1
  sum=0
  for i in range(maxlen+2):
   for j in range(maxlen+2):
    sum+=a[i][j]
  #print('life=',life,'  density=%0.4f'%(sum/65536)) #这个是用来评估够不够用来做密码表的
  if life==lifespan:
   canvas.itemconfig(ringo[typ],extent=71)#把它尽可能补满
   canvas.itemconfig(ringi[typ],extent=71)
   root.update()
   break;
 return a

 
 
def createkey(mat,lifespan,name):
 st=[]
 for i in range(1,maxlen+1):
  st.append(' ')
  for j in range(maxlen//4):
   s=0
   for k in range(1,5):
    s+=mat[i][j*4+k]*(2**(4-k))#把初始细胞状态转化为16进制储存(不是整行转化，而是4个4个来(这其实跟整行是相等的)，最后3个单独弄)
   st[i-1]+=hex(s).replace('0x','')#虽然python没有数值上限，但是还是怕占了太多内存
  s=0
  for j in range((maxlen//4)*4+1,maxlen+1):
   s+=mat[i][j]*(2**(maxlen-j))
  st[i-1]+=hex(s).replace('0x','')
 
 st.append(' ')
 st[maxlen]+=hex(lifespan).replace('0x','')#跑多久也同样16进制化储存 
 os.mkdir('v3data\\'+name) 
 f=open('v3data\\'+name+'\\A'+name+'.dat','w')#将奇数行和偶数行分别储存在A和B里面
 for i in range(maxlen):
  if i%2==0:
   f.write(st[i][1:len(st[i])]+'\n');
 f.write(st[maxlen][1:])#关于中文的特殊字段标识，16进制化储存
 f.close()
 f=open('v3data\\'+name+'\\B'+name+'.dat','w')#将奇数行和偶数行分别储存在A和B里面
 for i in range(maxlen):
  if i%2==1:
   f.write(st[i][1:len(st[i])]+'\n');
 #f.write(hex(cjkkey['B']).replace('0x',''))#关于中文的特殊字段标识，16进制化储存
 f.close() 

 
 
def standardize(mat,typ,click):#将杂乱的细胞生存情况转化为1对1的矩阵形式，贪心算法，效率还可以，大概只有10%不到的需要最后再补上
 choice=[[False for i in range(maxlen+1)] for j in range(maxlen+1)] 
 for i in range(1,maxlen+1):
  s=0
  for j in range(1,maxlen+1):s+=mat[j][i]#统计各纵列上有多少活着的细胞，便于贪心
  mat[0][i]=s
 for i in range(1,maxlen+1):             #我贪心算法用的不是很好，所以这里就不具体解释了
  chosen=200
  chosenid=0
  for j in range(1,maxlen+1):
   if (mat[i][j]>0) and (chosen>mat[0][j]) and (not choice[0][j]):#之所以用贪心是因为所有映射交叉点都能活着不太可能
    chosen=mat[0][j]
    chosenid=j
  if chosenid>0:
   choice[0][chosenid]=True
   choice[i][chosenid]=True
   choice[i][0]=True
 for i in range(1,maxlen+1):
  if not choice[i][0]:
   for j in range(1,maxlen+1):
    if not choice[0][j]:
     choice[i][j]=True
     choice[0][j]=True
     choice[i][0]=True
     break
 canvas.itemconfig(ringo[typ],extent=72)#UI环形进度条
 canvas.itemconfig(ringi[typ],extent=72) 
 root.update()
 return choice

 
 
def encrypt(ori,cho,typ):
 
 chonumpy=numpy.zeros((maxlen+1,maxlen+1),dtype=numpy.int32)
 for i in range(maxlen+1):
  for j in range(maxlen+1):
   if cho[i][j]:  chonumpy[i][j]=1
   
 def numberwork(ori):  #处理编码和标识问题
  #print(type(ori))
  fin=['' for i in range(len(ori))]
  clip=[[]for i in range(len(ori))]
  intold=0
  
  @numba.jit(nopython=True) #又TM不得不加速了
  def speedup2(st):
   clipar=numpy.array([0 for i in range(len(st))],dtype=numpy.int32)
   ii=1
   while len(st)>=1: #input+32，input范围控制到1位数或2两位数,0在最左侧单独拿出,output控制在32-126
     #print('lenst=',len(st),'  st[0]=',st[0])
     if st[0]==0:   #将fin[each]这个string按上述规律分割编码，不得不说这是被unicode的汉字编码逼的
      clipar[ii]=32  #但是用这种方法的确可以起到一定的混淆作用，还可以在下面添加随机
      st=st[1:]
     elif len(st)==1:
      clipar[ii]=st[0]+32
      st=st[1:]
     else:
        if st[0]*10+st[1]>94:
         clipar[ii]=st[0]+32
         st=st[1:]
        else:	
         t=random.randint(1,1000)
         if t<=248:   #这里添加随机以后，相同的明文可以有不同的密文，但反向不影响
          clipar[ii]=st[0]+32
          st=st[1:]
         else:
          clipar[ii]=10*st[0]+st[1]+32
          st=st[2:]
     ii+=1
   clipar[0]=ii
   return clipar
  
  
  for each in range(len(ori)):
   #if each%2==typ:
    c=random.randint(100,999)  #在整个数串左端增加三位随机数字，实现移位
    fin[each]+=str(c)
    ordrecord=False
	
    for i in range(len(ori[each])):
     fin[each]+=str(len(str(ord(ori[each][i]))))
     fin[each]+=str(ord(ori[each][i]))
    clipt=numpy.array([0 for i in range(len(fin[each]))],dtype=numpy.int32)
    for i in range(len(fin[each])): clipt[i]=int(fin[each][i])
    cliptt=speedup2(clipt)
    clip[each]=cliptt.tolist()[1:cliptt.tolist()[0]]
	
    if int(50*each/len(ori))>intold:
     intold+=1
     canvas.itemconfig(ringo[typ],extent=72+144*count+int(intold*71/50))#UI环形进度条
     canvas.itemconfig(ringi[typ],extent=72+144*count+int(intold*71/50))
     root.update()
    #print(each)#
  return clip
 
 
 @numba.jit(nopython=True) #又TM不得不加速了 
 def changecode(st): #生命游戏密码表的映射
  stt=numpy.array([0 for i in range(len(st))],dtype=numpy.int32)
  for j in range(len(st)):
   for i in range(1,maxlen+1):
    if chonumpy[st[j]-31][i]==1:
     achange=i+31
     break
   stt[j]=achange
  return stt
 
 fin=ori[:]
 for count in range(2):   #重复1次，以实现更好的打乱效果，但重复过多会导致密文过长
  clip=numberwork(fin)
  #print(clip[0])
  intold=0
  for each in range(len(ori)):
    fin[each]=''
    finint=changecode(clip[each])
    for eachord in finint:
     fin[each]+=chr(eachord)
    if int(50*each/len(ori))>intold:
     intold+=1
     canvas.itemconfig(ringo[typ],extent=144+144*count+int(intold*71/50))#UI环形进度条
     canvas.itemconfig(ringi[typ],extent=144+144*count+int(intold*71/50))
     root.update()
 return fin
 
 
 
def inidecrypt(keyA,keyB): #这个主要是从读取到的字符串列表中提取出细胞初始状态、生长时间、汉字等的特殊标识，写的很乱
 keyAmap=numpy.zeros((2+(maxlen//2),maxlen+2),dtype=numpy.int32)
 keyBmap=numpy.zeros((1+(maxlen//2),maxlen+2),dtype=numpy.int32)
 keymaplist=[[]]
 keyAmapline,keyBmapline=['' for i in range((maxlen//2)+1)],['' for i in range(maxlen//2)]
 #print(keyA[maxlen])
 for i in range(maxlen//2):   #下面主要是把16进制转化回2进制，再还原地图信息(注意：95不是4的倍数，所以存在0b***的数，专门处理)
  for j in range(maxlen//4):
   keyAmapline[i]+='%04d'%int(bin(int('0x'+keyA[i][j],16)).replace('0b',''))
   keyBmapline[i]+='%04d'%int(bin(int('0x'+keyB[i][j],16)).replace('0b',''))
  j=maxlen//4
  keyAmapline[i]+='%03d'%int(bin(int('0x'+keyA[i][j],16)).replace('0b','')) #这里就是处理0b***
  keyBmapline[i]+='%03d'%int(bin(int('0x'+keyB[i][j],16)).replace('0b',''))
  #print(i)
  for j in range(maxlen):
   keyAmap[i+1][j+1]=int(keyAmapline[i][j:j+1])
   keyBmap[i+1][j+1]=int(keyBmapline[i][j:j+1])
 i=maxlen//2
 for j in range(maxlen//4): keyAmapline[i]+='%04d'%int(bin(int('0x'+keyA[i][j],16)).replace('0b',''))
 j=maxlen//4
 keyAmapline[i]+='%03d'%int(bin(int('0x'+keyA[i][j],16)).replace('0b',''))
 for j in range(maxlen):keyAmap[i+1][j+1]=int(keyAmapline[i][j:j+1])
 keylife=int('0x'+keyA[(maxlen//2)+1][:3],16)
 for i in range(1,maxlen+1):
  if i%2==1:
   keymaplist.append(keyAmap[(i//2)+1].tolist())
  else:
   keymaplist.append(keyBmap[i//2].tolist())
 return [keymaplist,keylife]
 
 
 
def decrypt(cht,cho):#转化完密钥文件后用密码表来解密
 clip=[[]for i in range(len(cht))]
 fin=cht[:]
 global flagg
 flagg=True
 chonumpy=numpy.zeros((maxlen+1,maxlen+1),dtype=numpy.int32)
 for i in range(maxlen+1):
  for j in range(maxlen+1):
   if cho[i][j]:  chonumpy[i][j]=1
 
 try:
    
  @numba.jit(nopython=True) #又TM不得不加速了 
  def changecode_(st): #生命游戏密码表的映射
   stt=numpy.array([0 for i in range(len(st))],dtype=numpy.int32)
   for j in range(len(st)):
    if st[j]-31>maxlen: raise IndexError('not correctly encrypted')
    for i in range(1,maxlen+1):
     if chonumpy[i][st[j]-31]==1:
      achange=i+31
      break
    stt[j]=achange
   return stt
  
  intold=0
  for each in range(len(cht)):
   #if each%2==typ:
    fin[each]=''
    #print(each)
    chtlist=('orz_woTMfole2333'.join(cht[each])).split('orz_woTMfole2333')
    for i in range(len(chtlist)): chtlist[i]=ord(chtlist[i])
    finint=changecode_(chtlist)
    for eachord in finint:
     fin[each]+=str(eachord-32)#还原第二次密码表映射
	
    clip[each]=[]
    fin[each]=fin[each][3:]  #还原第二次移位完成
    #print('test1')
    while len(fin[each])>=1:
     length=int(fin[each][0])
     clip[each].append(int(fin[each][1:1+length]))
     fin[each]=fin[each][1+length:]
    #print(clip[each])             #到这里fin已经被还原，unicode码被分割开，因为第一次移位后就保证不会有汉字出现，所以这里还比较简单
    
    fin[each]=''
    finint=changecode_(clip[each])
    for eachord in finint:
     fin[each]+=str(eachord-32)#还原第一次密码表映射

    clip[each]=[]
    fin[each]=fin[each][3:]    #还原第一次移位完成
    
    #这时候fin已经是将明文的unicode码连在一起的数串了，下面就是把它还原分割
    while len(fin[each])>=1:
     length=int(fin[each][0])
     clip[each].append(int(fin[each][1:1+length]))
     fin[each]=fin[each][1+length:]
    
    fin[each]=''
    for any in clip[each]:    #还原分割完毕，利用unicode码还原明文
     fin[each]+=chr(any)
	 
    if int(100*each/len(cht))>intold:
     intold+=1
     canvas.itemconfig(ringo[1],extent=72+int(intold*287/100))#UI环形进度条
     canvas.itemconfig(ringi[1],extent=72+int(intold*287/100))
     root.update()
 except (OSError,IndexError,TypeError) as reason:
  print(reason)
  tk.messagebox.showerror('ERROR','possible reasons:\n1.the source file is not *.txt\n2.the file and the key do not match\n3.fatal error about the key\n4.uncorrected encrypted')
  flagg=False
 #print(flagg)
 return fin
 

 
 
 

def ui2encrypt(y,click): #从UI到加密算法
 try: 
  global name
  #print(y)
  f=open(y,'rb')
  balabala=[]
  p=''
  
  while 1:
   tt=f.readline()
   #print(type(tt),' ',tt)
   if len(tt)>0:
    if len(p)==0:
     p=chardet.detect(tt)['encoding']            #这个最后解密回去的时候格式是需要记录在密文里面的，不过我懒得给格式再加一次密了
     tt=tt.decode(chardet.detect(tt)['encoding'])#按照文件的编码方式进行解码
    else:
     tt=tt.decode(p)
   else:
    tt=''  #防止报错
   #print(type(tt),' ',tt)
   if not tt:break
   balabala.append(tt)
  for each in range(len(balabala)):
   if balabala[each][len(balabala[each])-2:len(balabala[each])]=='\r\n':  #解决换行符和回车符的问题，因为有转码所以会有'\r'
    balabala[each]=balabala[each][:len(balabala[each])-2]
    #print('test')
  f.close() 

  ori=[]
  lifespan=random.randint(-50,50)+500 
  end1=createmat(lifespan,True,varkeyname.get(),0,0) #运行生命游戏，生成若干代后的矩阵
  cho1=standardize(end1,0,click)#将矩阵变化为纵轴和横轴坐标一一对应
  fin1=encrypt(balabala,cho1,0)#加密 

  canvas.itemconfig(ringo[0],extent=0)#UI环形进度条
  canvas.itemconfig(ringi[0],extent=0)
  click.widget['state']='normal' 
  finishedtext.set('Encryption Finished')
  root.update()
  time.sleep(1)
  outputy=filedialog.asksaveasfilename(defaultextension='.txt',filetype=[('TXT','txt')])
  if outputy>'':
   f=open(outputy,'w') #这里反正只有32-126的字符，所以直接存就完事儿了
   for i in range(len(fin1)):
    f.write(fin1[i]+'\n')
   f.write(varkeyname.get()+'\n')
   f.write(p+'\n')
   f.close()
   c='v3data\\'+varkeyname.get()
   #print(c)
   os.startfile(c)
   finishedtext.set('')
  else:
   c='v3data\\'+varkeyname.get()
   os.remove('v3data\\'+name+'\\A'+name+'.dat')
   os.remove('v3data\\'+name+'\\B'+name+'.dat')
   os.rmdir(c)
   finishedtext.set('')
   tk.messagebox.showwarning('WARNING','you did not save the encrypted file')
  #print('E:\\机械王加密解密v3data\\'+varkeyname.get())
  
  name=str(random.randint(10000000,99999999))
  varkeyname.set(name)
 except OSError as reason:
  tk.messagebox.showerror('ERROR','no file selected or the file already exists')
  click.widget['state']='normal'
  root.update()

  
def ui2decrypt(y,click,keyApath,keyBpath):  #从UI到解密算法
 try: 
  f=open(y,'rb') 
  keyA=['' for i in range(maxlen+1)]
  keyB=['' for i in range(maxlen+1)]
  balabala=[]
  p=''
  
  while 1:
   tt=f.readline()
   #print(type(tt),' ',tt)
   if len(tt)>0:
    if len(p)==0:
     p=chardet.detect(tt)['encoding']            #这个最后解密回去的时候格式是需要记录在密文里面的，不过我懒得给格式再加一次密了
     tt=tt.decode(chardet.detect(tt)['encoding'])#按照文件的编码方式进行解码
    else:
     tt=tt.decode(p)
   else:
    tt=''  #防止报错
   #print(type(tt),' ',tt)
   if not tt:break
   balabala.append(tt)

  for each in range(len(balabala)):
   if balabala[each][len(balabala[each])-2:len(balabala[each])]=='\r\n':  #解决换行符和回车符的问题，因为有转码所以会有'\r'
    balabala[each]=balabala[each][:len(balabala[each])-2]
   #print('test')
  f.close() 
  
  name=balabala[len(balabala)-2]
  p=balabala[len(balabala)-1]
  del balabala[len(balabala)-1]
  del balabala[len(balabala)-1]#记得把key的序号和文件初始格式读取了
  try:#尝试打开keyA
   f=open(keyApath,'r')
   for i in range(maxlen+1):
    keyA[i]=f.readline()
   f.close()
   try:#尝试打开keyB
    f=open(keyBpath,'r')
    for i in range(maxlen+1):
     keyB[i]=f.readline()
    f.close()
    t=inidecrypt(keyA,keyB)
    keymap=numpy.array(t[0])
    keylife=t[1]

    end2=createmat(keylife,False,name,1,keymap)
    cho2=standardize(end2,1,click)
    fin2=decrypt(balabala,cho2) #解密 
    canvas.itemconfig(ringo[1],extent=0)#UI环形进度条
    canvas.itemconfig(ringi[1],extent=0)
    click.widget['state']='normal' 
    if flagg:
     finishedtext.set('Decryption Finished')
     root.update()
     time.sleep(1)
     outputy=filedialog.asksaveasfilename(filetype=[('TXT','txt')])
     if outputy>'':
      f=open(outputy,'wb') #这里反正只有32-126的字符，所以直接存就完事儿了
      for i in range(len(fin2)):
       f.write(fin2[i].encode(p)+b'\r\n')
       #print(fin2[i])
      f.close()
     else:
      tk.messagebox.showwarning('WARNING','you did not save decrypted file')
     finishedtext.set('') 
   except OSError as reason:
    tk.messagebox.showerror('ERROR','lacking key B')    #给一些人性化的提示
    click.widget['state']='normal'
  except OSError as reason:
   tk.messagebox.showerror('ERROR','lacking key A')    #给一些人性化的提示
   click.widget['state']='normal'
 except OSError as reason:
  tk.messagebox.showerror('ERROR','no file selected')
  click.widget['state']='normal'
 root.update()
 
 
 
 
 
 
if not os.path.exists('v3data'):
 os.mkdir('v3data') 
#这下面就是UI界面的实现过程了，使用了一个叫tkinter的模块#

root=tk.Tk()
top=tk.Toplevel(root)
top.overrideredirect(True)
root.configure(background='black')
root.title('Lord-of-Machine Encryption v3.3')
root.geometry('400x480+200+100')
root.wm_attributes('-topmost', True)
root.overrideredirect(True)
top.geometry('400x480+200+100')
canvas=tk.Canvas(root,width=420,height=500,bg='black',bd=0)
canvas.place(x=-10,y=0)  
selectedbt1,selectedbt2,keyAbind,keyBbind,flagg=False,False,False,False,False
filename0,keyAname0,keyBname0='','',''#初始化，设定了窗口文件和canvas，还有一些global变量

def ed(): #退出程序
 sys.exit()

def filedia(open_event):#用来获得目标文件地址
 global filename0
 filename=filedialog.askopenfilename()
 filename0=filename
 #print(filename)
 filenamebyte=str(filename.encode('utf-8'))
 lenf=len(filename)+filenamebyte.count('\\')//3
 if lenf>40:
  #print(filename.rfind('/'))
  filenamer=filename[filename.rfind('/'):]
  filenamerbyte=str(filenamer.encode('utf-8'))
  lenr=len(filenamer)+filenamerbyte.count('\\')//3
  #print(filenamer)
  #print(filenamerbyte)
  filenamel=filename[:40-lenr]
  #print(40-lenr)
  if lenr>40:
   filename=filenamer
  else:
   filename=filenamel+'...'+filenamer  
 if filename>'':
  pathtext.set(filename)
 else:
  pathtext.set('-----Click to Select Source File-----')

def filekeyB(linshi):  #用来获得keyB的地址
 global keyBname0
 if keyBbind:
  filekeyBname=filedialog.askopenfilename()
  keyBname0=filekeyBname
  filekeyBname=filekeyBname[filekeyBname.rfind('/')+1:]
  if filekeyBname>'':
   keyBtext.set(filekeyBname)
  else:
   keyBtext.set('-----Address of Key B-----')

def filekeyA(linshi):  #用来获得keyA的地址
 global keyAname0
 if keyAbind:
  filekeyAname=filedialog.askopenfilename()
  keyAname0=filekeyAname
  filekeyAname=filekeyAname[filekeyAname.rfind('/')+1:]
  if filekeyAname>'':
   keyAtext.set(filekeyAname)
  else:
   keyAtext.set('-----Address of Key A-----')
 
def progressring1(bt1_click):#处理加密解密选择问题，还有环形进度条的
 global selectedbt1,selectedbt2,keyAbind,keyBbind
 if selectedbt1:
  if bt1_click.widget['state'] in ['active','normal']:
   selectedbt1=False
   bt1.config(fg='gray')
   checkdefault.config(fg='#3c3c3c',state='disabled')
   zidingyilabel.config(fg='#3c3c3c')
   keyname.config(fg='#3c3c3c',disabledforeground='#3c3c3c',state='disabled')
   warnkeynamelabel.config(fg='#3c3c3c')
   canvas.itemconfig(linekeyname,fill='#3c3c3c')
   bt1_click.widget['state']='disabled'
   #print(name)
   t=ui2encrypt(filename0,bt1_click)
 else:
  selectedbt1=True
  bt1.config(fg='white')
  bt2.config(fg='gray')
  checkdefault.config(fg='white',state='normal')
  keyname.config(fg='white',disabledforeground='gray')
  warnkeynamelabel.config(fg='yellow')
  if vardefault.get()==0:
   zidingyilabel.config(fg='white')
   canvas.itemconfig(linekeyname,fill='white')
   keyname.config(state='normal')
  else:
   zidingyilabel.config(fg='gray')
   canvas.itemconfig(linekeyname,fill='gray')
  selectedbt2=False
  keyAlabel.config(fg='#3c3c3c')
  keyBlabel.config(fg='#3c3c3c')
  keyAbind,keyBbind=False,False
  canvas.itemconfig(keyAline,fill='#3c3c3c')
  canvas.itemconfig(keyBline,fill='#3c3c3c')

def progressring2(bt2_click):#处理加密解密选择问题，还有环形进度条的
 global selectedbt1,selectedbt2,keyAbind,keyBbind
 if selectedbt2:
  if bt2_click.widget['state'] in ['active','normal']:
   selectedbt2=False
   bt2.config(fg='gray')
   keyAlabel.config(fg='#3c3c3c')
   keyBlabel.config(fg='#3c3c3c')
   keyAbind,keyBbind=False,False
   canvas.itemconfig(keyAline,fill='#3c3c3c')
   canvas.itemconfig(keyBline,fill='#3c3c3c')
   bt2_click.widget['state']='disabled'
   t=ui2decrypt(filename0,bt2_click,keyAname0,keyBname0) 
 else:
  selectedbt1=False
  bt2.config(fg='white')
  bt1.config(fg='gray')
  checkdefault.config(fg='#3c3c3c',state='disabled')
  zidingyilabel.config(fg='#3c3c3c')
  keyname.config(fg='#3c3c3c',disabledforeground='#3c3c3c',state='disabled')
  warnkeynamelabel.config(fg='#3c3c3c')
  canvas.itemconfig(linekeyname,fill='#3c3c3c')
  selectedbt2=True
  keyAlabel.config(fg='white')
  keyBlabel.config(fg='white')
  keyAbind,keyBbind=True,True
  canvas.itemconfig(keyAline,fill='white')
  canvas.itemconfig(keyBline,fill='white')

def checkon():#checkdefault的一个函数
 global name
 checkedornot=vardefault.get()
 if checkedornot==1:
  name=str(random.randint(10000000,99999999))
  varkeyname.set(name)
  canvas.itemconfig(linekeyname,fill='gray')
  zidingyilabel.config(fg='gray')
  keyname.config(state='disabled')
  warnkeynamelabel.place(x=950,y=293)
 else:
  varkeyname.set('')
  keyname.config(state='normal')
  zidingyilabel.config(fg='white')
  canvas.itemconfig(linekeyname,fill='white')
  
def restrictlen(key_input):#限制自定义密钥名的长度，防止显示不过来
 if len(varkeyname.get())>=11:
  warnkeynamelabel.place(x=273,y=293)
 if len(varkeyname.get())>11:
  varkeyname.set(varkeyname.get()[:11])
  root.update()
 if len(varkeyname.get())<=10:
  warnkeynamelabel.place(x=950,y=293)
  
def bthelp():  #华丽丽的帮助文档
 helptop=tk.Toplevel(root)
 helptop.wm_attributes('-topmost',True)
 helptop.overrideredirect(True)
 helptop.geometry('400x500+200+100')
 helptop.configure(bg='black')
 helpdoc=("""
                                   -简介-
      本程序采用独特的生命游戏和移位算法，对
  文本文件进行加密。其中密钥被分为AB两个部
  分，缺一不可，一定程度上加强了安全性。本
  程序由波波工作室独立开发，是机械网加密解
  密系列的最新版，部分开源，请联系作者微信
  或QQ获得，版本号为3.3。
  本程序仅供学习和研究使用，禁用于商业用途
	      波  写于  2019.03.04凌晨
  ————————————————————
                                   -操作-
  点击1次“加密”或“解密”按钮，将选中该功能
  再次点击将执行对应功能  
  加密 1.点击中央文本栏，选择待加密的文本文
              件的路径
           2.确认后点击“加密”按钮，待进度条满后
              会提示“加密完成”
           3.加密完成后请选择密文的存储路径，随
              后将自动打开密钥文件夹
           4.如勾选了“默认”栏，密钥名字随机生成
           5.自定义密钥名长度上限为11个字符
           6.请保存好您的密钥，因为密钥无法还原
  解密 1.选择待解密的文本文件的路径
           2.选择密钥A和密钥B后，点击“解密”
           3.完成解密后选择明文的存储路径，随后
              自动打开明文文件夹
 """)
 helptext=tk.Text(helptop,bg='black',fg='white',font=('等线',12),width=400,height=410,bd=0)
 helptext.insert(tk.INSERT,helpdoc)
 helptext.place(x=30,y=0)
 
 def back():
  helptop.destroy()
 
 btback=tk.Button(helptop,bg='black',bd=0,font=('等线',12),activebackground='black',activeforeground='red',fg='white',text='返 回',command=back)
 btback.place(x=175,y=470)

bt1=tk.Button(root,bg='black',bd=0,font=('等线',16),activebackground='black',activeforeground='red',fg='gray',text='加密')#下面是几个按钮
bt1.bind('<ButtonRelease-1>',progressring1)
bt1.place(x=95,y=145)
bt2=tk.Button(root,bg='black',bd=0,font=('等线',16),activebackground='black',activeforeground='red',fg='gray',text='解密')
bt2.bind('<ButtonRelease-1>',progressring2)
bt2.place(x=245,y=145)
bted=tk.Button(root,bg='black',bd=0,font=('等线',12),activebackground='black',activeforeground='red',fg='white',text='退 出',command=ed)
bted.place(x=175,y=440)
btabhelp=tk.Button(root,bg='black',bd=0,font=('等线',12),activebackground='black',activeforeground='red',fg='white',text='帮 助',command=bthelp)
btabhelp.place(x=175,y=415)
pic2=tk.PhotoImage(file='ui\\wing.png')#下面是logo部分
pic2label=tk.Label(root,image=pic2,bd=0) 
pic2label.place(x=0,y=0)
pic1=tk.PhotoImage(file='ui\\logo3.png')
pic1label=tk.Label(root,image=pic1,bd=0) 
pic1label.place(x=140,y=0)
versionlabel=tk.Label(root,bd=0,text="3.3",font=('Small Fonts',7),fg='white',bg='black')
versionlabel.place(x=191,y=64.5)
pathtext=tk.StringVar()#下面是文件选择框部分
pathtext.set('-----Click to Select Source File-----')
path=tk.Label(root,bg='black',fg='#cbe4ea',width=40,bd=0,font=('等线',10),textvariable=pathtext)
path.place(x=58,y=210)
path.bind('<Button-1>',filedia)
canvas.create_line(62,230,356,230,fill='#cbe4ea') 
finishedtext=tk.StringVar()#下面是加密/解密完成后的提示字符
finishedtext.set('')
finishedlabel=tk.Label(root,bd=0,textvariable=finishedtext,bg='black',fg='yellow',font=('等线',10),width=20)
finishedlabel.place(x=126,y=240)
vardefault=tk.IntVar()#下面是默认设置选项
vardefault.set(0)
checkdefault=tk.Checkbutton(root,bg='black',state='disabled',bd=0,selectcolor='black',fg='#3c3c3c',font=('等线',10),command=checkon,activebackground='black',activeforeground='white',variable=vardefault,text='Default name and address')
checkdefault.place(x=120,y=260)
varkeyname=tk.StringVar()#下面是自定义密钥名称
name=str(random.randint(10000000,99999999))
varkeyname.set(name)
keyname=tk.Entry(root,bg='black',fg='#3c3c3c',bd=0,disabledbackground='black',textvariable=varkeyname,font=('等线',10),insertbackground='white',insertwidth=1,selectbackground='darkgray',width=21)
keyname.bind('<KeyRelease>',restrictlen)
keyname.place(x=128,y=290)
zidingyilabel=tk.Label(root,bd=0,text='Key Name',font=('等线',10),bg='black',fg='#3c3c3c')
zidingyilabel.place(x=42,y=293) 
warnkeynametext=tk.StringVar()
warnkeynametext.set('max length')
warnkeynamelabel=tk.Label(root,bd=0,textvariable=warnkeynametext,bg='black',fg='yellow',font=('等线',10),width=14)
warnkeynamelabel.place(x=950,y=293)
linekeyname=canvas.create_line(134,310,290,310,fill='#3c3c3c')
keyAtext=tk.StringVar()#下面是密钥A地址部分
keyAtext.set('-----Address of Key A-----')
keyAlabel=tk.Label(root,bg='black',fg='#3c3c3c',bd=0,font=('等线',10),textvariable=keyAtext,width=21)
keyAlabel.place(x=128,y=340)
keyAlabel.bind('<Button-1>',filekeyA)
keyAline=canvas.create_line(134,360,290,360,fill='#3c3c3c') 
keyBtext=tk.StringVar()#下面是密钥B地址部分
keyBtext.set('-----Address of Key B-----')
keyBlabel=tk.Label(root,bg='black',fg='#3c3c3c',bd=0,font=('等线',10),textvariable=keyBtext,width=21)
keyBlabel.place(x=128,y=370)
keyBlabel.bind('<Button-1>',filekeyB)
keyBline=canvas.create_line(134,390,290,390,fill='#3c3c3c') 
ringo,ringi=[],[]#下面准备环形进度条
ringo.append(canvas.create_arc(96,124,170,198,start=90,extent=0,fill="#fffed1"))
ringi.append(canvas.create_arc(100,128,166,194,start=90,extent=0,fill="black"))
ringo.append(canvas.create_arc(246,124,320,198,start=90,extent=0,fill="#fffed1"))
ringi.append(canvas.create_arc(250,128,316,194,start=90,extent=0,fill="black"))


root.mainloop()

