#!/usr/local/bin/python2.7
# encoding: utf-8
##############################################################################
# Author: Liam Deacon                                                        #
#                                                                            #
# Contact: liam.deacon@diamond.ac.uk                                         #
#                                                                            #
# Copyright: Copyright (C) 2013-2015 Liam Deacon                             #
#                                                                            #
# License: MIT License                                                       #
#                                                                            #
# Permission is hereby granted, free of charge, to any person obtaining a    #
# copy of this software and associated documentation files (the "Software"), #
# to deal in the Software without restriction, including without limitation  #
# the rights to use, copy, modify, merge, publish, distribute, sublicense,   #
# and/or sell copies of the Software, and to permit persons to whom the      #
# Software is furnished to do so, subject to the following conditions:       #
#                                                                            #
# The above copyright notice and this permission notice shall be included in #
# all copies or substantial portions of the Software.                        #
#                                                                            #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR #
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,   #
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL    #
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER #
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING    #
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER        #
# DEALINGS IN THE SOFTWARE.                                                  #
#                                                                            #
##############################################################################
from math import sqrt
"""
rfactor.py - calculate RFactor for a set of LEED IV curves

"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division, with_statement

import iv

import sys
import os

CNORM = 2./3.  # normalisation factor for rb

def r1(expt_data, theory_data):
    n_eng = len(theory_data[0])
    
    theory_intensities = theory_data[1]
    expt_intensities = expt_data[1]
    
    theory_sum = sum(theory_intensities)
    expt_sum = sum(expt_intensities)
    
    norm_te = theory_sum / expt_sum
    norm_theory_sum = theory_sum / n_eng
    
    rfac_sum = theory_sum - expt_data*norm_te
    norm_sum = theory_data[1] - norm_theory_sum
    
    return rfac_sum/norm_sum

def r2(expt_data, theory_data):
    '''
    Calculates R2-factor.
    
    \f$ R_2 = \sqrt{ S(I_t - norm_te*I_e)^2 / {S * I_t^2} } \f$
    
    \f$ norm_te = \sqrt( S|It|^2 / S|Ie|^2) \f$
    
    .. note: Normalisation is changed with respect to common use. 
    Instead of \f$ S {(I_t)}^2 \f$ it is now \f$ S {(I_t - <I_t>)}^2 \f$, 
    where \f$ <I_t> = \frac{(S I_t)}{dE} \f$ .
    
    \param[in] eng pointer to list of energy values.
    \param[in] e_int pointer to list of experimental intensity values.
    \param[in] t_int pointer to list of theoretical intensity values.
    
    .. warning: expt_data and theory_data should be 2-dimensional and
    the same length.
    
    Returns R2-factor if successful.
    '''
    n_eng = len(theory_data[0])
    
    theory_intensities = theory_data[1]
    expt_intensities = expt_data[1]
    
    theory_sum = sum(theory_intensities)
    expt_sum = sum(expt_intensities)
    
    theory_avg = theory_sum / n_eng
    
    norm_te = sqrt(theory_sum / expt_sum)
    norm_theory_sum = theory_sum / n_eng
    
    # compute R-factor (rfac_sum) and normalisation factor (norm_sum)
    rfac_sum = sum(pow(theory_intensities[i] - 
                       (expt_intensities[i] * norm_te), 2) 
                   for i in range(n_eng))
    
    norm_sum = sum(pow(theory_intensities[i] - theory_avg, 2) 
                   for i in range(2))
    
    return sqrt(rfac_sum/norm_sum)

def rb(expt_data, theory_data):
    n_eng = len(theory_data[0])
    
    theory_intensities = theory_data[1]
    expt_intensities = expt_data[1]
    
    rfac_sum = sum(imap(lambda x, y: x*y, 
                        expt_intensities, theory_intensities))
    
    expt_sq_sum = sum(x*x for x in expt_intensities)
    theory_sq_sum = sum(x*x for x in theory_intensities)
    
    rfac_sum /= sqrt(theory_sq_sum * expt_sq_sum)
    
    return (1. - rfac_sum) / (1. - CNORM)

def rp(expt_data, theory_data, vi=4.):
    '''
    Computes Pendry's R-factor:
  
    \f$ R_p = S(Y_e - Y_t)^2 / S(Y_e^2 + Y_t^2) \f$
 
    \param[in] eng pointer to list of energies.
    \param[in] e_int pointer to list of experimental intensities.
    \param[in] t_int pointer to list of theoretical intensities.

    \param vi Imaginary part of the optical potential.
    
    return Rp if successful. 
    '''
    n_eng = len(theory_data[0])
    
    theory_intensities = theory_data[1]
    expt_intensities = expt_data[1]
    
    energies = expt_data[0]
    
    # compute integrals
    expt_y_sum = 0.
    theory_y_sum = 0.
    rfac_sum = 0.
    for i in range(1, n_eng):
        e_step = energies[i] - energies[i-1]
        
        # theoretical Y function
        L = (theory_intensities[i] - 
             theory_intensities[i-1]) / (e_step * 0.5 * 
                        theory_intensities[i] + theory_intensities[i-1])
             
        Y_theory = L / (1. + (L*L*vi*vi))
        theory_y_sum += Y_theory*Y_theory*e_step
        
        # experimental Y function
        L = (expt_intensities[i] - 
             expt_intensities[i-1]) / (e_step * 0.5 * 
                        expt_intensities[i] + expt_intensities[i-1])
             
        Y_expt = L / (1. + (L*L*vi*vi))
        expt_y_sum += Y_expt*Y_expt*e_step
        
        # compute R-factor sum
        rfac_sum +=  pow(Y_theory - Y_expt, 2)*e_step
    
    # divide rfac_sum by the normalisation factor and return result
    return rfac_sum / (expt_y_sum + theory_y_sum) 

RFACTORS = {"r1": r1, 
            "r2": r2, 
            "rb": rb, 
            "rp": rp}

class RFactor(object):
    ''' 
    Class for calculating the R-Factor for a set of IV curves or 
    multiple groups of curves (e.g. for handling multiple angles of 
    incidence)
    '''
    def __init__(self, iv_groups=[], **kwargs):
        self.iv_groups = iv_groups
        self.__dict__.update(kwargs)
    
    @staticmethod
    def calculate_r1(iv_group):
        try:
            for iv_pair in [iv_pair for iv_pair in iv_group if iv_pair.used]:
                pass
        except:
            raise
    
    @property
    def iv_groups(self):
        return self._iv_groups
    
    @iv_groups.setter
    def iv_groups(self, iv_groups):
        self._iv_groups = [group for group in iv_groups 
                           if isinstance(group, iv.IVCurveGroup)]
    
    def rfactor(self, type=None, iv_groups=[]):
        '''
        Returns the R-Factor given by `type` and for the IV groups 
        given by `iv_groups`.
        '''
        if iv_groups == []:
            iv_groups = self._iv_groups
            
        # filter groups by 
        for i in iv_groups:
            pass
            
        return sum(RFACTOR(group) for group in iv_groups)/len(iv_groups) 
    
    def rr(self, iv_groups=[]):
        return 1.
    
    def total_energy_shift(self, iv_groups=[]):
        return 0.
    
    def total_energy_range(self, iv_groups=[]):
        return 0.
    
    def theory_to_experiment_integration_ratio(self, iv_groups=[]):
        return 1.
    
