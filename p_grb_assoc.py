#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  4 10:34:09 2021

@author: Damien Turpin : damien.turpin@cea.fr

function that gives the chance probability of having a positive spatial and 
temporal match between a GRB and a ZTF transient candidate
Inputs:
    error radius of the GRB localization region in degree: error_radius
    size of the searching time window in year: size_time_window
    GRB detection rate for a given satellite in events/year : R_GRB
Outputs:
    Serendipituous probabilities for a GRB/ZTF candidate association
"""

from math import pi, sqrt
from scipy.stats import poisson
from scipy import special
from scipy.optimize import minimize



def p_ser_grb(error_radius,size_time_window, r_grb):

    # omega = 2*pi*(1-cos(radians(error_radius))) # solid angle in steradians
    grb_loc_area = pi*(error_radius)**2 # in square degrees
    allsky_area = 4*pi*(180/pi)**2 # in square degrees
    ztf_coverage_rate = 3750 # sky coverage rate of ZTF in square degrees per hour
    limit_survey_time = 4 #duration (in hour) during which ZTF will cover individual parts of the sky in a night
    
    # short and long GRB detection rate
    r_sgrb = r_grb/3
    r_lgrb = r_grb-r_sgrb
    
    # Poisson probability of detecting a GRB during a searching time window
    
    p_grb_detect_ser = 1-poisson.cdf(1,r_grb*size_time_window)
    p_lgrb_detect_ser = 1-poisson.cdf(1,r_lgrb*size_time_window)
    p_sgrb_detect_ser = 1-poisson.cdf(1,r_sgrb*size_time_window)
    
    # we limit the fraction of the sky ZTF is able to cover to 4 hours of continuous survey
    # we consider that every day (during several days only) ZTF will cover the same part of
    # the sky with individual shots (so no revisit) during 4 hours
        
    if size_time_window*365.25*24 <= limit_survey_time:
        ztf_sky_frac_area = (ztf_coverage_rate*size_time_window*365.25*24)
    else:
        ztf_sky_frac_area = ztf_coverage_rate*limit_survey_time
    
    # probability of finding a GRB within the region area paved by ZTF during a given amount of time
    p_grb_in_ztf_survey = (ztf_sky_frac_area/allsky_area) * p_grb_detect_ser
    p_lgrb_in_ztf_survey = (ztf_sky_frac_area/allsky_area) * p_lgrb_detect_ser
    p_sgrb_in_ztf_survey = (ztf_sky_frac_area/allsky_area) * p_sgrb_detect_ser
    
    # probability of finding a ZTF transient candidate inside the GRB error box 
    # knowing the GRB is in the region area paved by ZTF during a given amount of time

    p_ser_grb = p_grb_in_ztf_survey*(grb_loc_area/ztf_sky_frac_area)
    
    p_ser_lgrb = p_lgrb_in_ztf_survey*(grb_loc_area/ztf_sky_frac_area)
    
    p_ser_sgrb = p_sgrb_in_ztf_survey*(grb_loc_area/ztf_sky_frac_area)
    
    p_sers = [p_ser_grb, p_ser_lgrb, p_ser_sgrb]
    
    return p_sers

def sig_est(prob):
    fun = lambda x: abs(prob-special.erf(x/sqrt(2)))
    res = minimize(fun, [0] , method='Nelder-Mead')
    
    return res.x