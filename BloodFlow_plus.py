import tkinter as Tk
import matplotlib
import numpy as np
from tkinter import filedialog
import cv2
from skimage import filters,img_as_ubyte,io
from skimage.transform import radon
from skimage import external
from skimage.color import rgb2gray
from numpy import pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
from matplotlib.figure import Figure
matplotlib.use('TkAgg')

# validate input of the Tk.Entry is float type
def test(inp):
        b = '1234567890.'
        count = 0
        for i in range(len(inp)):
            if inp[i]=='.':
                count+=1
        for i in range(len(inp)):
           if bool(inp[i] in b[:]) and count <= 1:
                   return True
        else:
                print("Please input a number")
                return False
#End tkinter window
def _quit():
        root.quit()
        root.destroy()
def select():
    global gray, canvas, frm2, select_count,f1, a1, a2, f2, path, image_sobel
    path = filedialog.askopenfilename()
    if len(path) > 0 and select_count==0:
        gray = external.tifffile.imread(path)
        if len(gray.shape)>= 4:
            gray = rgb2gray(gray)
        else:
            gray = gray 
        image_blur = filters.gaussian(gray,0.2)
        if len(gray.shape) == 3:
                image_sobel = []
                for i in range(image_blur.shape[0]):
                        image_sobel.append(filters.sobel_h(image_blur[i]))
                        sobelshow = image_sobel[0]
                        image_blurshow = image_blur[0]
        elif len(gray.shape) == 2:
                image_sobel = filters.sobel_h(image_blur)
                sobelshow = image_sobel
                image_blurshow = image_blur
        img = img_as_ubyte(sobelshow)
        grayshow = image_blurshow

        
        f1 = Figure(dpi=100)
        a1 = f1.add_subplot(121)
        a1.imshow(grayshow,cmap='gray')
        a1.set_title('Original gray image')
        
        a2 = f1.add_subplot(122)
        a2.set_title('Sobel tranform')
        a2.imshow(img,cmap='gray')
        
#show images on the tkinter window
        frm2 = Tk.Frame(root)
        frm2.grid(row=0)
        canvas =FigureCanvasTkAgg(f1, master=frm2)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=Tk.BOTH)
        toolbar =NavigationToolbar2Tk(canvas, frm2)
        toolbar.update()
        canvas._tkcanvas.pack(fill=Tk.BOTH)
        select_count+=1
        return gray
    elif len(path) > 0 and select_count > 0:
        frm2.destroy()
        gray = io.imread(path,as_gray = False)
        if len(gray.shape)>= 4:
            gray = rgb2gray(gray)
        else:
            gray = gray
        image_blur = filters.gaussian(gray,0.2)
        
        
        if len(gray.shape) == 3:
                image_sobel = []
                for i in range(image_blur.shape[0]):
                        image_sobel.append(filters.sobel_h(image_blur[i]))
                        sobelshow = image_sobel[0]
                        image_blurshow = image_blur[0]

        elif len(gray.shape) == 2:
                image_sobel = filters.sobel_h(image_blur)
                sobelshow = image_sobel
                image_blurshow = image_blur
        img = img_as_ubyte(sobelshow)
        grayshow = image_blurshow
        
        f1 = Figure(dpi=100)
        a1 = f1.add_subplot(121)
        
        a1.imshow(grayshow,cmap='gray')
        a1.set_title('Original gray image')
        a2 = f1.add_subplot(122)
        a2.imshow(img,cmap='gray')
        a2.set_title('Sobel tranform')
        
#show images on the tkinter window
        frm2 = Tk.Frame(root)
        frm2.grid(row=0)
        canvas =FigureCanvasTkAgg(f1, master=frm2)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=Tk.BOTH)
        toolbar =NavigationToolbar2Tk(canvas, frm2)
        toolbar.update()
        canvas._tkcanvas.pack(fill=Tk.BOTH)
        select_count+=1
        return gray

def findangle(image, precision):
    firsttheta = 0
    lasttheta = 180
    stepangle = (lasttheta - firsttheta)/25

    while stepangle*20 >= precision:
        theta = np.linspace(firsttheta, lasttheta, 25, endpoint=False)
        sinogram = radon(image, theta=theta, circle=True)
        diff = np.std(sinogram,axis=0)
        Mx=max(diff)
        diff=diff.tolist()
        num=diff.index(Mx)+1
        global angle
        angle = float(firsttheta) + (num*stepangle-stepangle/2)
        firsttheta =angle-2*stepangle
        lasttheta =angle+2*stepangle
        stepangle = (lasttheta-firsttheta)/25

def bloodflow (image,precision,readstep):
        global count, value, stepL
        if len(gray.shape) == 2:  
            img = img_as_ubyte(image_sobel)
            readlength = img.shape[0]
            readstart = 0
            readstop = readstep
            count = 0
            value = []
            stepL = []
            while (readstop <= readlength):
                imageread = img[readstart:readstop,:]
                findangle(imageread,precision)
                value.append(angle)
                stepL.append((count+1)*readstep)
                readstart= int(readstop)
                readstop = int(readstart)+readstep
                count+=1
        elif len(gray.shape) == 3:
                count = 0
                value = []
                stepL = []
                for i in range(gray.shape[0]):
                        img = img_as_ubyte(image_sobel[i])
                        readlength = img.shape[0]
                        readstart = 0
                        readstop = readstep
                        while (readstop <= readlength):
                                imageread = img[readstart:readstop,:]
                                findangle(imageread,precision)
                                value.append(angle)
                                stepL.append((count+1)*readstep)
                                readstart= int(readstop)
                                readstop = int(readstart)+readstep
                                count+=1

     
def measure():
    bloodflow(gray, float(Entry_precsision.get()), int(Entry_stepsize.get()))
    global speedlist, Timesteplist
    value_radians = np.asarray(value)/180.0*pi
	
    #calculate the tan(value_radians)
    tanA = np.tan(value_radians)
    # get x, y scale
    xscale = float(Entry_xscale.get())
    yscale = float(Entry_yscale.get())
    # calculate flow speed
    flow_speed =tanA*xscale/yscale
    flowmean = np.mean(flow_speed, axis=0)
    flowsd = np.std(flow_speed, axis=0)
    flowi=0
    while (flowi < len(flow_speed)):
            if flowi!= len(flow_speed)-1 and (flow_speed[flowi]> flowmean+2*flowsd or flow_speed[flowi]< flowmean-2*flowsd):
                    flow_speed[flowi]=(flow_speed[flowi-1]+flow_speed[flowi+1])/2
            elif flowi==len(flow_speed)-1 and (flow_speed[flowi]> flowmean+2*flowsd or flow_speed[flowi]< flowmean-2*flowsd):
                        flow_speed[flowi]=flow_speed[flowi-1]
            flowi+=1
            
    speedlist = flow_speed.tolist()
    Timestep = np.asarray(stepL)/yscale
    Timesteplist = Timestep.tolist()
    
    f2 = Figure(dpi = 100)
    a3 = f2.add_subplot(111)
    a3.plot(Timesteplist,speedlist, marker = 'o',markerfacecolor = 'white')
    a3.set_xlabel('Time (ms)')
    a3.set_ylabel('Blood flow (mm/s)')
    a3.set_title('Blood flow')
    frm4 = Tk.Frame(root)
    frm4.grid(row=0,column = 1)
    canvas =FigureCanvasTkAgg(f2, master=frm4)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=Tk.BOTH)
    toolbar =NavigationToolbar2Tk(canvas, frm4)
    toolbar.update()
    canvas._tkcanvas.pack(fill=Tk.BOTH)
    return Timesteplist,speedlist
def save_data(): 
		result = np.append(Timesteplist, speedlist, axis = 0)
		result = result.reshape((2,len(speedlist))).transpose().astype(str)
	
		file_ = path.split('/')[-1]
		
		f=filedialog.asksaveasfile(mode = "w",initialdir = path.split(file_)[0],initialfile =file_.split('.')[-2], defaultextension=".cvs", filetypes=( ('CSV file', '.CSV'),('text files', '.txt'),('excel file', '.xls')))
		
		f.write("speed(mm/s) time(ms)" + "\n")
		for line in result:
			separator = ' '
			f.writelines(separator.join(line) + "\n")
		f.close()	
root =Tk.Tk()
root.title("Blood flow measure (line scanning)")

global gray, canvas, frm2, select_count, f1
select_count=0

frm1 = Tk.Frame(root)
button =Tk.Button(frm1, text='Quit', padx="10", command=_quit)
button.pack(side=Tk.RIGHT)
btn1 = Tk.Button(frm1, text="Select an image", command = select)
btn1.pack(side=Tk.LEFT)
btn3 = Tk.Button(frm1, text="Save data", command = save_data)
btn3.pack(side=Tk.RIGHT, expand="no", pady="10")
btn2 = Tk.Button(frm1, text="Measure", command = measure)
btn2.pack(side=Tk.RIGHT, expand="no", padx="10", pady="10")
frm1.grid(row=2)
frm3 = Tk.Frame(root)
v1= Tk.DoubleVar()
v1.set('0.1')
v2= Tk.DoubleVar()
v2.set('50')
v3= Tk.DoubleVar()
v3.set('1.0')
v4= Tk.DoubleVar()
v4.set('1.0')
inptest = root.register(test) #register validate function
L1 = Tk.Label(frm3, text = 'Angle precsision:').grid(row=0)
Entry_precsision = Tk.Entry(frm3,width = 6, textvariable = v1, validate = 'focusout', validatecommand = (inptest, '%P'))
Entry_precsision.grid(row=0, column = 1)
L2 = Tk.Label(frm3, text = 'Step size (pixels):').grid(row=0,column = 2)
Entry_stepsize = Tk.Entry(frm3,width = 6,textvariable = v2, validate = 'focusout', validatecommand = (inptest, '%P'))
Entry_stepsize.grid(row=0, column = 3)
L3 = Tk.Label(frm3, text = 'μm/pixel:').grid(row=0,column = 4)
Entry_xscale = Tk.Entry(frm3,width = 6,textvariable = v3, validate = 'focusout', validatecommand = (inptest, '%P'))
Entry_xscale.grid(row=0, column = 5)
L4 = Tk.Label(frm3, text = 'ms/pixel:').grid(row=0,column = 6)
Entry_yscale = Tk.Entry(frm3,width = 6,textvariable = v4, validate = 'focusout', validatecommand = (inptest, '%P'))
Entry_yscale.grid(row=0, column = 7,pady="10")
frm3.grid(row=1)
Tk.mainloop()
