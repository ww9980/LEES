# -*- coding: utf-8 -*-

from tkinter import *
from tkinter import filedialog
from tkinter import messagebox

from copy import copy, deepcopy
import os
import sys

import pylab
import numpy
import EMpy

import nk

passing_n = None
passing_k = None
EditMode = -1

class MainGUI:
    def __init__(self, master):
        self.parent = master
        self.parent.title("Fan's Laser Endpoint Etch Simulator")
        self.frame = Frame(self.parent)
        self.frame.pack(fill=BOTH, expand=1)
        self.parent.resizable(width=False, height=False)

        # Initialize class variables
        # LayerStack
        self.LayerStack = []
        #self.wavelength = 0
        
        
        
        # Common Materials
        n_air = 1.0
        mat_air = EMpy.materials.IsotropicMaterial('air', EMpy.materials.RefractiveIndex(n0_const=n_air))
        Layer = EMpy.utils.Layer
        self.air = Layer(mat_air, numpy.inf)
        n_PR = 1.57   # Resist
        mat_PR = EMpy.materials.IsotropicMaterial('PR', EMpy.materials.RefractiveIndex(n0_const=n_PR))
        self.PR = Layer(mat_PR, numpy.inf)
        n_SiC = 2.6255   # SiC
        mat_SiC = EMpy.materials.IsotropicMaterial('SiC', EMpy.materials.RefractiveIndex(n0_const=n_SiC))
        self.SiC = Layer(mat_SiC, numpy.inf)
        n_Si = 3.8224 - 1j * 0.014554   # Si
        mat_Si = EMpy.materials.IsotropicMaterial('Si', EMpy.materials.RefractiveIndex(n0_const=n_Si))
        self.Si = Layer(mat_Si, numpy.inf)
        n_Sapphire = 1.7644   # sapphire
        mat_Sapphire = EMpy.materials.IsotropicMaterial('Sapphire', EMpy.materials.RefractiveIndex(n0_const=n_Sapphire))
        self.Sapphire = Layer(mat_Sapphire, numpy.inf)
        n_quartz = 1.456   # fused quartz
        mat_quartz = EMpy.materials.IsotropicMaterial('Quartz', EMpy.materials.RefractiveIndex(n0_const=n_quartz))
        self.Quartz = Layer(mat_quartz, numpy.inf)

        # ------------------ GUI ---------------------

        # Layer structure
        self.LayerStructure = Frame(self.frame)
        self.LayerStructure.grid(row=0, column=0, sticky=W + N)
        self.Layersl = Label(self.LayerStructure, text="Layer structure").pack(fill=X, side=TOP)
        self.LayerBox = Listbox(self.LayerStructure, width=80, height=24)
        self.LayerBox.pack(fill=Y, side=LEFT)
        self.scrollbar = Scrollbar(self.LayerStructure, orient="vertical")
        self.scrollbar.config(command=self.LayerBox.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.LayerBox.config(yscrollcommand=self.scrollbar.set)
        
        # Layer Edit Buttons
        self.LayerEdit = Frame(self.frame)
        self.LayerEdit.grid(row=0, column=1, sticky=W + N)
        self.helpBtn = Button(self.LayerEdit, text='?', command=self.helpct)
        self.helpBtn.pack(fill=X, side=TOP)
        # self.InsertBtn = Button(self.LayerEdit, text='+', command=self.insertLayer)
        # self.InsertBtn.pack(fill=X, side=TOP)
        self.DelBtn = Button(self.LayerEdit, text='-', command=self.DelLayer)
        self.DelBtn.pack(fill=X, side=TOP)
        self.EditBtn = Button(self.LayerEdit, text='E', command=self.EditLayer)
        self.EditBtn.pack(fill=X, side=TOP)
        self.dupBtn = Button(self.LayerEdit, text='x2', command=self.DuplicateLayer)
        self.dupBtn.pack(fill=X, side=TOP)
        self.MoveUpBtn = Button(self.LayerEdit, text='↑', command=self.MoveUpLayer)
        self.MoveUpBtn.pack(fill=X, side=TOP)
        self.MoveDownBtn = Button(self.LayerEdit, text='↓', command=self.MoveDownLayer)
        self.MoveDownBtn.pack(fill=X, side=TOP)
        
        # Layer properties
        self.LayerProp = LabelFrame(self.frame, text='Layer edit')
        self.LayerProp.grid(row=0, column=2, sticky=W + N)
        self.ltl = Label(self.LayerProp, text='Layer thickness:')
        self.ltl.grid(row=0, column=0)
        self.ltE = Entry(self.LayerProp, text="")
        self.ltE.grid(row=0, column=1)
        self.ltu = Label(self.LayerProp, text='nm')
        self.ltu.grid(row=0, column=2)
        self.lnl = Label(self.LayerProp, text='Material name:')
        self.lnl.grid(row=1, column=0)
        self.lnE = Entry(self.LayerProp, text="")
        self.lnE.grid(row=1, column=1)
        self.ImpMatBtn = Button(self.LayerProp, text='+', command=self.ImpMat)
        self.ImpMatBtn.grid(row=1, column=2)
        self.ipl = Label(self.LayerProp, text='n value:')
        self.ipl.grid(row=2, column=0)
        self.ipE = Entry(self.LayerProp, text="")
        self.ipE.grid(row=2, column=1)
        self.kpl = Label(self.LayerProp, text='k value:')
        self.kpl.grid(row=3, column=0)
        self.kpE = Entry(self.LayerProp, text="")
        self.kpE.grid(row=3, column=1)
        self.AddBtn = Button(self.LayerProp, text='   Add   ', command=self.AddLayer)
        self.AddBtn.grid(row=4, column=1)
        
        # Save and Run button
        self.SimRun = Frame(self.frame)
        self.SimRun.grid(row=1, column=2, sticky=W + N)
        self.Wavelengthl = Label(self.SimRun, text='Wavelength:')
        self.Wavelengthl.grid(row=0, column=0)
        self.WavelengthE = Entry(self.SimRun, text="")
        self.WavelengthE.grid(row=0, column=1)
        self.WavelengthE.insert(0,'670')
        self.WavelengthU = Label(self.SimRun, text='nm')
        self.WavelengthU.grid(row=0, column=2)
        self.TimeStepl = Label(self.SimRun, text='Time step:')
        self.TimeStepl.grid(row=1, column=0)
        self.TimeStepE = Entry(self.SimRun, text="")
        self.TimeStepE.grid(row=1, column=1)
        self.TimeStepE.insert(0,'1')
        self.TimeStepU = Label(self.SimRun, text='ns')
        self.TimeStepU.grid(row=1, column=2)
        self.Substratel = Label(self.SimRun, text='Substrate/stop:')
        self.Substratel.grid(row=2, column=0)
        OPTIONS = [
            "Silicon","Sapphire","SiC","Quartz","Nitride","GaAs","Metal"]
        self.variable = StringVar(self.SimRun)
        self.variable.set(OPTIONS[0])
        self.SubstrateMenu = OptionMenu(*(self.SimRun, self.variable) + tuple(OPTIONS))
        self.SubstrateMenu.grid(row=2, column=1)
        self.RunBtn = Button(self.SimRun, text='         Run >>      ', command=self.Run)
        self.RunBtn.grid(row=3, column=0)
        
    def find_nearest(self, a, a0):
        '''Return element in ndArray `a` that has value closest to the
        scalar value `a0`.'''
        idx = numpy.abs(a - a0).argmin()
        return a.flat[idx]


    def arg_find_nearest(self, a, a0):
        '''Return index to element in ndArray `a` that has value closest
        to the scalar value `a0`.'''
        idx = numpy.abs(a - a0).argmin()
        return idx


    def count_noninf(self, multilayer):
        '''Return number of non-infinite layers in an EMpy Multilayer
        object.'''
        out = 0
        for x in multilayer:
            #print(x)
            out = out + 0 if numpy.isinf(x.thickness) else out + 1
        return out


    def arg_inf(self, multilayer):
        '''Return index to layers with infinite-thickness in an EMpy Multilayer object.'''
        out = []
        for ix, x in enumerate(multilayer):
            if numpy.isinf(x.thickness):
                out.append(ix)
        return out
        
        
    def insertLayer(self):
            print('Function disabled')
            
    def DelLayer(self):
        sel = self.LayerBox.curselection()
        if len(sel) != 1:
            return
        idx = int(sel[0])
        #self.LayerStack.pop(idx)
        self.LayerBox.delete(idx)
        self.LayerBox.select_set(idx-1)
            
    def EditLayer(self):
        global EditMode
        sel = self.LayerBox.curselection()
        if len(sel) != 1:
            return
        idx = int(sel[0])
        text=self.LayerBox.get(idx)
        seltext = text.split(',')
        ln = seltext[0].strip()
        self.lnE.insert(0,ln)
        lt = float(seltext[1].split(' ')[1].strip())
        self.ltE.insert(0,lt)
        li = float(seltext[2].strip())
        self.ipE.insert(0,li)
        lk = float(seltext[3].strip())
        self.kpE.insert(0,lk)
        self.AddBtn.configure(text="   Edit   ")
        EditMode = idx
    
    def ImpMat(self):
        print('!')
    
    def helpct(self):
            messagebox.showinfo("Help", \
            "Please DO NOT include the substrate/stop layer in the layer structure. \
            \n\n Only isotropic materials are supported. \
            \n \n x2 - Duplicate the selection. \
            \n \n E - Edit the selected layer. ")
            
    def DuplicateLayer(self):
        sel = self.LayerBox.curselection()
        if len(sel) != 1:
            return
        idx = int(sel[0])
        if idx==0:
            return
        text=self.LayerBox.get(idx)
        self.LayerBox.insert(idx+1, text)
        self.LayerBox.select_set(idx)
        
    def MoveUpLayer(self):
        sel = self.LayerBox.curselection()
        if len(sel) != 1:
            return
        idx = int(sel[0])
        if idx==0:
            return
        text=self.LayerBox.get(idx)
        self.LayerBox.delete(idx)
        self.LayerBox.insert(idx-1, text)
        self.LayerBox.select_set(idx-1)
            
    def MoveDownLayer(self):
        sel = self.LayerBox.curselection()
        if len(sel) != 1:
            return
        idx = int(sel[0])
        if idx==self.LayerBox.size()-1:
            return
        text=self.LayerBox.get(idx)
        self.LayerBox.delete(idx)
        self.LayerBox.insert(idx+1, text)
        self.LayerBox.select_set(idx+1)
            
    def AddLayer(self):
        global EditMode
        if self.checkValues() is not True:
            return
        if EditMode != -1:
            self.LayerBox.delete(EditMode)
            self.LayerBox.insert(EditMode, '%s, %.2f nm , %.2f, %.2f' % (self.lnE.get().strip(), float(self.ltE.get().strip()), float(self.ipE.get().strip()), float(self.kpE.get().strip())))
            self.AddBtn.configure(text="   Add   ")
        else:
            self.LayerBox.insert(END, '%s, %.2f nm , %.2f, %.2f' % (self.lnE.get().strip(), float(self.ltE.get().strip()), float(self.ipE.get().strip()), float(self.kpE.get().strip())))
        self.ltE.delete(0, END)
        self.lnE.delete(0, END)
        self.ipE.delete(0, END)
        self.kpE.delete(0, END)
        EditMode = -1
            
    def Run(self):
        # setup the initial environment
        wl_lasermon = int(self.WavelengthE.get().strip()) * 1e-9
        EtchStep = float(self.TimeStepE.get().strip()) * 1e-9
        wls = numpy.array([wl_lasermon - 1e-9, wl_lasermon, wl_lasermon + 1e-9])
        theta_inc = EMpy.utils.deg2rad(0)  # incidence angle
        
        # setup the layers
        layers = [self.air]
        for i, listbox_entry in enumerate(self.LayerBox.get(0, END)):
            seltext = listbox_entry.split(',')
            ln = seltext[0].strip()
            lt = float(seltext[1].split(' ')[1].strip())
            li = float(seltext[2].strip())
            lk = float(seltext[3].strip())
            nn = li - 1j * lk
            matl = EMpy.materials.IsotropicMaterial(ln, EMpy.materials.RefractiveIndex(nn))
            ly = EMpy.utils.Layer(matl, lt * 1e-9)
            layers.append(ly)
        if self.variable.get() == 'Silicon':
            sub = self.Si
        layers.append(sub)
        layers = EMpy.utils.Multilayer([copy(l) for l in layers])
        
        # setup etching loop
        EtchStep_current = EtchStep  # how much left to etch in current loop iteration
        go = True                    # while loop switch
        i = -1                       # while loop counter
        etchedlayers = []            # save stacks of etched layers
        solutions = []               # IsotropicTransferMatrix object storing R/T solutions
        EtchSteps = []               # x-axis data
        Rlaser = []                  # y-axis data - reflectivity
        RefrIdx = []                 # y-axis data - refractive index
        wlidx = self.arg_find_nearest(wls, wl_lasermon) # get index to laser-monitor wavelength in `wls` array
        idxtemp = 0 # 0 if etching away from first layer in list, -1 if etching from last
        print("Etching...")
        while go is True:
            i = i + 1
            sys.stdout.write('.')
            sys.stdout.flush()
            if self.count_noninf(layers) > 0:
                if i <= 0:
                    EtchStep_current = 0.0
                    indexno = idxtemp
                else:
                    while numpy.isinf(layers[idxtemp].thickness):
                        idxtemp = idxtemp + 1  
                    indexno = idxtemp
                if layers[indexno].thickness <= EtchStep_current:
                    EtchStep_current = EtchStep_current - layers[indexno].thickness
                    layers.pop(indexno)
                elif layers[indexno].thickness > EtchStep_current:
                    layers[indexno].thickness = (layers[indexno].thickness - EtchStep_current)
                    etchedlayers.append(deepcopy(layers))
                    RefrIdx.append(etchedlayers[-1][idxtemp].mat.n(wl_lasermon).real)
                    if i <= 0:
                        EtchSteps.append(0.0)
                    else:
                        EtchSteps.append(EtchSteps[-1] + EtchStep)  # Add x-axis point
                        EtchStep_current = EtchStep     # reset EtchStep_current
                    # solve for reflectivity at laser monitor wavelength
                    
                    solutions.append(
                        EMpy.transfer_matrix.IsotropicTransferMatrix(
                            etchedlayers[-1], theta_inc).solve(wls))
                    Rlaser.append(solutions[-1].Rs[wlidx])
            else:
                go = False
        print('\n Simulation completed.\n')
        fig1, [ax1, ax2] = pylab.subplots(nrows=2, ncols=1, sharex=True)
        ax1.set_title(r'Reflectivity at $\lambda = %0.1fnm$' % (wls[wlidx] * 1e9))
        ax1.plot(numpy.array(EtchSteps) * 1e9, RefrIdx, '-g')
        ax1.set_ylabel('Refractive Index')
        ax1.grid(True)
        ax2.plot(numpy.array(EtchSteps) * 1e9, numpy.array(Rlaser) * 100, '-')
        ax2.set_ylabel('Laser Reflectivity (%)')
        ax2.set_xlabel('Etch Depth (nm)')
        ax2.grid(True)
        fig1.show()
        pylab.show()
        
        
        
    
    def checkValues(self):
        if self.ltE.get().strip() is not "" and self.kpE.get().strip() is not "" and self.lnE.get().strip() is not "" and self.ipE.get().strip() is not "":
            return True
        else:
            messagebox.showerror("Error", "Input error. Check the inputs. ")
            
class MatLibGUI:
    pass




if __name__ == '__main__':
    root = Tk()
    imgicon = PhotoImage(file='icon2.gif')
    root.tk.call('wm', 'iconphoto', root._w, imgicon)
    tool = MainGUI(root)
    root.mainloop()
