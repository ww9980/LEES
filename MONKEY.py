from tkinter import *
 
from MONK import *
from tkinter.messagebox import *
from tkinter import messagebox
import warnings
import pylab
import numpy

###########################
#   The material dictionary
#   The key is the function name in MONK.pylab
#   The value is in format of 'A, B, C'
#      where A is the name of the material same as the function
#            B is the wavelength in format of min-max um.
#                 note must not add space
#                 must use um as unit
#            C is a general remark/ the long name of the material
###########################


# MOconst is the dictionary for wavelength-independent materials
MOconst = {Air: 'Air, wavelength-independent', BCB: 'BCB, cyclotone'}

# MOw is the dictionary for n only result, 1 input (wavelength) only
MOw = {Si:'Si, 0.400-1.200 um', AlAs: 'AlAs, 0.56-2.2 um', GaAs: 'GaAs, 1.4-11 um',\
GaAs_mIR: 'GaAs_mIR, 0.97-17 um', InAs_fIR: 'InAs_fIR, 3.7-31.3 um', InAs: 'InAs, 0.5299-1.907 um',\
InP:'InP, 0.950-10 um', GaP:'GaP, 0.800-10 um', JAW_ThermalSiO2:'JAW_ThermalSiO2, 0.3-2 um, J.A. Woolam thermal oxide model', \
FusedSiO2:'FusedSiO2, 0.3-2 um, Fused silica', IBD_Ta2O5_DJ2007: 'IBD_Ta2O5_DJ2007, 0.3-2 um, Ion-Beam Sputtered Ta2O5',\
IBD_SiO2_DJ2011:'IBD_SiO2_DJ2011, 0.3-2 um, Ion-Beam Sputtered oxide', IBD_SiN_DJ2010:'IBD_SiN_DJ2010, 0.3-2 um, Ion-Beam Sputtered nitride', \
PECVD_SiN:'PECVD_SiN, 0.3-2 um, PECVD nitride', PECVD_SiO:'PECVD_SiO, 0.3-2 um, PECVD oxide',NbO:'NbO, 0.295-2.5 um', a_Si:'a_Si, 2.254-4.959 um, amorphous silicon'}

# MOw is the dictionary for n+k result, 1 input (wavelength) only
MOwk = {AlAs_interp: 'AlAs_interp, 0.206-2.480 um', GaAs_interp: 'GaAs_interp, 0.206-2.066 um', GaSb_interp: 'GaSb_interp, 0.2066-0.8266 um'}

# MOcomplex is the dictionary for n only result, 2 inputs (component ratio, wavelength) 
MOcomplex = {AlGaAs:'AlGaAs, 0.970-2.2 um, complex material', InGaAs: 'InGaAs, 0.970-1.907 um, complex material', InGaP:'InGaP, 0.950-1.907 um, complex material',\
GaAsP: 'GaAsP, 0.970-2.2 um, complex material', AlInGaAs: 'AlInGaAs, 0.900-2.100 um,  x: 0.3-1.0, complex material'}

# MOcomplexk is the dictionary for n+k result, 2 inputs (component ratio, wavelength) 
MOcomplexk = {AlGaAs_interp: 'AlGaAs_interp, 0.206-2.066 um, complex material'}


class MOGUI(Frame):
 
    
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.parent = master
        self.parent.resizable(width=False, height=False)
        self.pack()
        self.create_widgets()
     
    # Create main GUI window
    def create_widgets(self):
        self.search_var = StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.update_list())
        self.entry = Entry(self, textvariable=self.search_var, width=20)
        self.lbox = Listbox(self, width=45, height=15)
         
        self.entry.grid(row=0, column=0, padx=10, pady=3,columnspan=2)
        self.lbox.grid(row=1, column=0, padx=10, pady=3,columnspan=2)
        
        
        self.WLE = Entry(self)
        self.WLE.grid(row=2, column=0)
        self.WLE.insert(0,'0.670')
        self.WLEunit = Label(self, text = 'μm')
        self.WLEunit.grid(row=2, column=1)
        self.XPE = Entry(self)
        self.XPE.grid(row=3, column=0)
        self.XPE.insert(0,'0.3')
        self.XPEunit = Label(self, text = 'x')
        self.XPEunit.grid(row=3, column=1)
        self.ShowBtn = Button(self, text='   Show   ', command=self.ShowNK)
        self.ShowBtn.grid(row=4, column=0, padx=10, pady=3)
        self.PlotBtn = Button(self, text='   Plot   ', command=self.PlotNK)
        self.PlotBtn.grid(row=4, column=1, padx=10, pady=3)
        # Function for updating the list/doing the search.
        # It needs to be called here to populate the listbox.
        self.MatDetail = Label(self, text = '')
        self.MatDetail.grid(row=5, column=0, columnspan=2)
        self.MatNK = Label(self, text = '')
        self.MatNK.grid(row=6, column=0, columnspan=2)
        self.update_list()
     
    def update_list(self):
        search_term = self.search_var.get()
     
        lbox_list = ['Si', 'Air', 
        'AlAs', 'AlAs_interp', 'GaAs', 'GaAs_interp', 'GaSb_interp', 'InP',\
        'GaP', 'AlGaAs', 'AlGaAs_interp', 'InGaAs', 'InGaP', 'GaAsP', 'AlInGaAs', \
        'JAW_ThermalSiO2', 'FusedSiO2', \
        'IBD_Ta2O5_DJ2007', 'IBD_SiO2_DJ2011', 'IBD_SiN_DJ2010', 'PECVD_SiN', 'PECVD_SiO',\
        'NbO', 'a_Si', 'PR']
         
        self.lbox.delete(0, END)
     
        for item in lbox_list:
            if search_term.lower() in item.lower():
                self.lbox.insert(END, item)
    
    def ShowNK(self):
        sel = self.lbox.curselection()
        if len(sel) != 1:
            return
        idx = int(sel[0])
        text=self.lbox.get(idx)
        for key, val in MOconst.items():
            Mat = val.split(',')
            if text == Mat[0]:
                self.MatDetail.configure(text=val)
                self.MatNK.configure(text=key)
        
        for key, val in MOw.items():
            Mat = val.split(',')
            if text == Mat[0]:
                self.MatDetail.configure(text=val)
                try:
                    self.MatNK.configure(text=key(float(self.WLE.get().strip())))
                except:
                    messagebox.showerror('Error', 'The specified wavelength is out of the available data range. The result might be invalid. , ', detail='', type=OK)
        for key, val in MOwk.items():
            Mat = val.split(',')
            if text == Mat[0]:
                self.MatDetail.configure(text=val)
                try:
                    self.MatNK.configure(text=key(float(self.WLE.get().strip()), True))
                except:
                    messagebox.showerror('Error', 'The specified wavelength is out of the available data range. The result might be invalid. , ', detail='', type=OK)
        for key, val in MOcomplex.items():
            Mat = val.split(',')
            if text == Mat[0]:
                self.MatDetail.configure(text=val)
                with warnings.catch_warnings(record=True) as w:
                    warnings.simplefilter("always")
                    self.MatNK.configure(text=key(float(self.XPE.get().strip()),float(self.WLE.get().strip())))
                    w = filter(lambda i: issubclass(i.category, UserWarning), w)
                    if len(list(w)):
                        messagebox.showerror('Error', 'The specified wavelength or component ratio is out of the available data range. The result might be invalid. , ', detail='', type=OK)
        for key, val in MOcomplexk.items():
            Mat = val.split(',')
            if text == Mat[0]:
                self.MatDetail.configure(text=val)
                try:
                    self.MatNK.configure(text=key(float(self.XPE.get().strip()),float(self.WLE.get().strip()), True))
                except:
                    messagebox.showerror('Error', 'The specified wavelength or component ratio is out of the available data range. The result might be invalid. , ', detail='', type=OK)

    def PlotNK(self):
        sel = self.lbox.curselection()
        if len(sel) != 1:
            return
        idx = int(sel[0])
        text=self.lbox.get(idx)
        for key, val in MOconst.items():
            Mat = val.split(',')
            if text == Mat[0]:
                self.MatDetail.configure(text=val)
                self.MatNK.configure(text=key)
                fig1, ax1 = pylab.subplots(nrows=1, ncols=1, sharex=True)
                ax1.set_title(r'%s' % (Mat[0]))
                ax1.plot(range(20), [key for i in range(20)], '-g')
                ax1.set_xlabel('wavelength (um)')
                ax1.set_ylabel('n value')
                ax1.grid(True)
                fig1.show()
                pylab.show()
                
        for key, val in MOw.items():
            Mat = val.split(',')
            if text == Mat[0]:
                self.MatDetail.configure(text=val)
                self.MatNK.configure(text=key(float(self.WLE.get().strip())))
                minmax = Mat[1].split(' ')[1]
                min = float(minmax.split('-')[0].strip())
                max = float(minmax.split('-')[1].strip())
                fig1, ax1 = pylab.subplots(nrows=1, ncols=1, sharex=True)
                ax1.set_title(r'%s' % (Mat[0]))
                xr = numpy.linspace(min,max,50)
                yr = [key(i).real for i in xr]
                #yi = [key(i).imag for i in xr]
                ax1.plot(xr, yr, '-g', label='n value')
                #ax1.plot(xr, yi, '-', label='i value')
                ax1.set_xlabel('wavelength (um)')
                ax1.set_ylabel('n & k value')
                ax1.legend(loc='upper right')
                ax1.grid(True)
                fig1.show()
                pylab.show()
        for key, val in MOwk.items():
            Mat = val.split(',')
            if text == Mat[0]:
                self.MatDetail.configure(text=val)
                self.MatNK.configure(text=key(float(self.WLE.get().strip()),True))
                minmax = Mat[1].split(' ')[1]
                min = float(minmax.split('-')[0].strip())
                max = float(minmax.split('-')[1].strip())
                fig1, ax1 = pylab.subplots(nrows=1, ncols=1, sharex=True)
                ax1.set_title(r'%s' % (Mat[0]))
                xr = numpy.linspace(min,max,50)
                yr = [key(i, True).real for i in xr]
                yi = [key(i, True).imag for i in xr]
                ax1.plot(xr, yr, '-g', label='n value')
                ax1.plot(xr, yi, '-', label='i value')
                ax1.set_xlabel('wavelength (um)')
                ax1.set_ylabel('n & k value')
                ax1.legend(loc='upper right')
                ax1.grid(True)
                fig1.show()
                pylab.show()
        for key, val in MOcomplex.items():
            Mat = val.split(',')
            if text == Mat[0]:
                self.MatDetail.configure(text=val)
                self.MatNK.configure(text=key(float(self.XPE.get().strip()),float(self.WLE.get().strip())))
                minmax = Mat[1].split(' ')[1]
                min = float(minmax.split('-')[0].strip())
                max = float(minmax.split('-')[1].strip())
                fig1, ax1 = pylab.subplots(nrows=1, ncols=1, sharex=True)
                ax1.set_title(r'%s' % (Mat[0]))
                xr = numpy.linspace(min,max,50)
                yr = [key(float(self.XPE.get().strip()),i).real for i in xr]
                yi = [key(float(self.XPE.get().strip()),i).imag for i in xr]
                ax1.plot(xr, yr, '-g', label='n value')
                ax1.plot(xr, yi, '-', label='i value')
                ax1.set_xlabel('wavelength (um)')
                ax1.set_ylabel('n & k value')
                ax1.legend(loc='upper right')
                ax1.grid(True)
                fig1.show()
                pylab.show()
        for key, val in MOcomplexk.items():
            Mat = val.split(',')
            if text == Mat[0]:
                self.MatDetail.configure(text=val)
                self.MatNK.configure(text=key(float(self.XPE.get().strip()),float(self.WLE.get().strip()), True))
                minmax = Mat[1].split(' ')[1]
                min = float(minmax.split('-')[0].strip())
                max = float(minmax.split('-')[1].strip())
                fig1, ax1 = pylab.subplots(nrows=1, ncols=1, sharex=True)
                ax1.set_title(r'%s' % (Mat[0]))
                xr = numpy.linspace(min,max,50)
                yr = [key(float(self.XPE.get().strip()),i,True).real for i in xr]
                yi = [key(float(self.XPE.get().strip()),i,True).imag for i in xr]
                ax1.plot(xr, yr, '-g', label='n value')
                ax1.plot(xr, yi, '-', label='i value')
                ax1.set_xlabel('wavelength (um)')
                ax1.set_ylabel('n & k value')
                ax1.legend(loc='upper right')
                ax1.grid(True)
                fig1.show()
                pylab.show()





root = Tk()
root.title('MONKEY (Material Optical N & K EnquirY)')
app = MOGUI(master=root)
app.mainloop()
