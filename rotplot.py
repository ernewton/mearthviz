# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 09:48:21 2016

@author: enewton
"""

import os
import types
import pickle
import matplotlib.pylab as plt
import matplotlib as mpl
import numpy as np
from astropy.time import Time
from zachopy import oned as zponed
import math
import seaborn as sns

import mearth_lc as melc

pgf_with_pdflatex = {
    "pgf.texsystem": "pdflatex",
    "pgf.preamble": [
         r"\usepackage[utf8x]{inputenc}",
         r"\usepackage[T1]{fontenc}",
         r"\usepackage{mathpazo}",
         r"\usepackage{tgpagella}",
         ],
    "font.family": 'texgyrepagella',
}
mpl.rcParams.update(pgf_with_pdflatex)
mpl.rc('xtick', labelsize=16)
mpl.rc('ytick', labelsize=16)
mpl.rc('axes', labelsize=16)

from matplotlib.backends.backend_pgf import FigureCanvasPgf
mpl.backend_bases.register_backend('pdf', FigureCanvasPgf)

def short_period(lc, xlim=None, days=False, save=False):

  lc.hjd_off = 0.
  try:
    print xlim-1
  except:
    xlim = [lc.hjd[0], lc.hjd[-1]]      

  if days:
    cc = 1.
    xlab = 'Time (days)'
  else:
    cc = 24
    xlab=  'Time (hours)'
  
  fig = plt.figure(figsize=(6,4.5))
  ax = fig.add_subplot(111)

  time = lc.phase_fold(binned=True) # reference to time
  yy = lc.flux_reduce(binned=True)
  yy = np.power(10, -1*yy/2.5)-1

  plt.scatter(time*lc.period*cc, yy, color='#004080', s=40, alpha=0.5)
  plt.scatter((time+1)*lc.period*cc, yy, color='gray', s=40, alpha=0.2)
  plt.scatter((time-1)*lc.period*cc, yy, color='gray', s=40, alpha=0.2)
  tmp = np.abs(yy) < (5*np.nanstd(np.abs(yy)))
  lim = 5*np.nanstd(np.abs(yy[tmp]))
  print (5*np.nanstd(np.abs(yy))), lim
  plt.ylim(-lim, lim)
  plt.xlim(-1*lc.period*0.4*cc, (lc.period)*1.4*cc)     
  ax.set_ylabel('Rel. brightness (mag)', fontsize=18)
  ax.set_xlabel(xlab, fontsize=18)
  
  y = [0.05, 0.04, 0.03, 0.02, 0.01, 0.0, -0.01, -0.02, -0.03, -0.04, -0.05]
  ylab = ['5%', '4%', '3%', '2%', '1%', 'Normal', '-1%', '-2%', '-3%', '-4%', '-5%']
  plt.yticks(y, ylab)
  plt.tight_layout()
  if save:
    plt.savefig('short_phased.jpg')

  
def long_period(lc, xlim=None, alpha=0.4, binwidth=None, binned=False, save=False):
  
  color = '#004080'
  if binwidth:
      color = '#b2df8a'
  lc.hjd_off = 0.

  fig = plt.figure(figsize=(12,5))
  ax = fig.add_subplot(111)

  colors = sns.color_palette()

  if binned:
    xx = Time(lc.hjd_bin+2400000.5,format='jd')
    xxx= lc.hjd_bin
    yy = lc.flux_reduce(binned=True)
  else:
    xx = Time(lc.hjd+2400000.5,format='jd')
    xxx= lc.hjd
    yy = lc.flux_reduce()
  yy = np.power(10, -1*yy/2.5)-1
  ax.plot_date(xx.plot_date,yy, zorder=2,
               markeredgecolor='none', color=color, alpha=alpha)

  if binwidth is not None:
    xa, y, error = zponed.binto(x=xxx[np.isfinite(yy)], y=yy[np.isfinite(yy)], 
                                         sem=True, binwidth=binwidth)
    x = Time(xa+2400000.5, format='jd')
    gd, = np.where(error < 3*np.nanstd(error))
    print "std of error", np.nanstd(error)
    plt.errorbar(x[gd].plot_date, y[gd], error[gd], zorder=3, 
                 elinewidth=3, capthick=3, capsize=3, linewidth=0, color='#1f78b4')
                 
  y = [0.05, 0.04, 0.03, 0.02, 0.01, 0.0, -0.01, -0.02, -0.03, -0.04, -0.05]
  ylab = ['5%', '4%', '3%', '2%', '1%', 'Normal', '-1%', '-2%', '-3%', '-4%', '-5%']
  plt.yticks(y, ylab)
  
  tmp = np.abs(yy) < (5*np.nanstd(np.abs(yy)))
  lim = 5*np.nanstd(np.abs(yy[tmp]))
  plt.ylim(-lim, lim)
  plt.gcf().autofmt_xdate()
  
  ax.set_ylabel('Relative brightness (%)', size=16, labelpad=10)
  ax.set_xlabel('Date', size=16)
  
  plt.tight_layout()
  if save:
    plt.savefig('long_stretch.jpg')


def check_best():
  star('00445930-1516166', load=True, south=True, tel=11,
       model=True, alpha=0.2, binned=True, binwidth=2)

  star('14294291-6240465', load=True, south=True,
       model=True, alpha=0.2, binned=True, binwidth=2)

  star('10145184-4709244', load=False, south=True,
       model=True, alpha=0.2, binned=True, binwidth=2)
       
  
def star(lspm, load=True, tel=None, south=False, model=False, 
         alpha=0.4, plotlong=None, binwidth=None, binned=False):
  
  if type(lspm) == types.InstanceType:
      lc = lspm
  else:  
      # southern stars have a different naming convention
      if south:
        prefix = "2massj"
        suffix = "daily"
        ls = lspm
      else:
        prefix = "lspm"
        suffix = "lc"
        ls = str(int(lspm))
      if tel:
        suffix = "tel"+str(int(tel))+'_'+suffix
        pickfile = "data/"+prefix+ls+"_"+str(int(tel))
        plotfile = "plots/"+prefix+ls+"_"+str(int(tel))+'.jpg'
      else:
        pickfile = "data/"+prefix+ls
        plotfile = "plots/"+prefix+ls+'.jpg'


      # load the data from pickle?
      if load:
        lc = pickle.load( open(pickfile+".pkl", "rb") )
      # else must read it in!
      else:
        f = "data/"+prefix+ls+"_"+suffix+".fits"
        print f
        lc = melc.LightCurve(f, id=lspm, south=south, date_lim=False)
        buf = lc.prep_period()
        fit = melc.fit_period(buf, pmax=200)
        lc.update_model(fit)
        pickle.dump( lc, open(pickfile+".pkl", "wb" ) )
        
        f = open(pickfile+".dat","wb")
        for x, y, yerr in zip(lc.hjd, lc.flux_reduce(), lc.eflux):
          f.write('{0} {1} {2}\n'.format(x,y,yerr))

  plt.close()
  plt.close()

  if (lc.period > 10) or plotlong==True:
    long_period(lc, alpha=alpha, binwidth=binwidth, binned=binned)
    if model:
        colors = sns.color_palette()
        step = (lc.period/50)
        axrange = np.arange(lc.hjd[0],lc.hjd[-1], step)
        xx = Time(axrange+2400000.5,format='jd')
        y = lc.amp*np.sin(2*math.pi*(axrange)/lc.period + lc.phase)
        plt.plot(xx.plot_date,y,c=colors[1], zorder=2)
  else:
    short_period(lc)

  plt.tight_layout()
  plt.savefig(plotfile)
  
  print "Period is: ", lc.period, "days"
  print "   ... or  ", lc.period*24, "hours"

def add_model(lspm, south=False):
  # southern stars have a different naming convention
  if south:
    prefix = "2massj"
    suffix = "daily"
    ls = lspm
  else:
    prefix = "lspm"
    suffix = "lc"
    ls = str(int(lspm))
  
  colors = sns.color_palette()
  lc = pickle.load( open("data/"+prefix+ls+".pkl", "rb") )
  step = (lc.period /50)
  axrange = np.arange(lc.time[0],lc.time[-1], step)+2400000.5
  xx = Time(axrange,format='jd')
  y = lc.amp*np.sin(2*math.pi*(axrange)/lc.period + lc.phase)
  plt.plot_date(axrange,y, linestyle='-', fmt='.', c=colors[1], zorder=2)

plt.close()