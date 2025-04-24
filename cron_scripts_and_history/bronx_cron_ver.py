#!/usr/bin/env python
# coding: utf-8

# # bronx testing
# In order to track bronx progress over time, we will setup methods to collect data day by day, and then produce time dependent plots to show progress
# 
# Recorded data will be average per job format, with error. Sort by date.

# In[2]:


# import  epmt query

print('running bronx script')
import epmt_query as eq
# import matplot for better plotting functions
import sys

import numpy as np
import datetime
import time
# import pandas. optional but helpful 'display.max_columns' arg shows all DataFrame columns when printing
import pandas as pd
import pickle   #to load in metrics history
pd.set_option('display.max_columns', None)

off_set_days = -3
# In[17]:
#check to see if day is already recorded. if it is, exit code
#this allows code to be run much more frequently, without redoing days, which helps whith timing out issues
recent_job = eq.get_jobs(limit = 1, after = off_set_days, fmt = 'orm')[0]

recent_job_date = recent_job.created_at
current_date = str(recent_job_date.strftime("%m")+'-'+recent_job_date.strftime("%d")+'-'+recent_job_date.strftime("%y"))
filename = 'bronx_history_DO_NOT_DELETE.pkl'
# Read dictionary pkl file
with open(filename, 'rb') as fp:
    metrics_history = pickle.load(fp)
if current_date in metrics_history['date']:
    sys.exit(['date already recorded'])

#We gather initial estimates and get a list of IDs for the specific date
today_date = datetime.datetime.today()
start_date = today_date + datetime.timedelta(days =off_set_days)   #offset to allow for job completion
older_date = start_date + datetime.timedelta(days =-1) 
date = (start_date.strftime("%m")+'-'+start_date.strftime("%d")+'-'+start_date.strftime("%y")) #date in an easy to read format
#use orm and trigger_post_process=False to get data quickly
older_orm = eq.get_jobs(after=older_date, fmt = 'orm',trigger_post_process=False)
start_orm = eq.get_jobs(after=start_date, fmt = 'orm',trigger_post_process=False)
job_num = older_orm.count() - start_orm.count()    #clip off the jobs that happened between current time and the end of the week being reported on
all_jobs=eq.get_jobs(limit =int(job_num), offset = start_orm.count(), fmt='orm',trigger_post_process=False)
#sort data by esm4.2 tag inexp_fre_mod
bronx_jobids=[]
bronx_exp_names=[]
total_jobs=all_jobs.count()
job_num=0

#check to see if day is already recorded. if it is, exit code
#this allows code to be run much more frequently, without redoing days, which helps whith timing out issues
recent_job = eq.get_jobs(limit = 1, after = off_set_days, fmt = 'orm')[0]

recent_job_date = recent_job.created_at
current_date = str(recent_job_date.strftime("%m")+'-'+recent_job_date.strftime("%d")+'-'+recent_job_date.strftime("%y"))
filename = 'bronx_history_'+'DO_NOT_DELETE.pkl'
# Read dictionary pkl file
with open(filename, 'rb') as fp:
    metrics_history = pickle.load(fp)
if current_date in metrics_history['date']:
    sys.exit(['date already recorded for bronx'])

for job in all_jobs:
    job_num=job_num+1
    exp_fre_mod=job.tags.get('exp_fre_mod')
    if exp_fre_mod is None:
        continue
    if ('bronx' in exp_fre_mod) or ('bronx' in exp_fre_mod.lower()):
        bronx_jobids.append(job.jobid)
        if exp_fre_mod in bronx_exp_names:
            continue
        else:
            bronx_exp_names.append(exp_fre_mod)

if len(bronx_jobids) < 10:
    sys.exit('insuficient data')
    
else:


    # In[18]:


    #get jobs in dict format, if there is more than 10
    if len(bronx_jobids) >= 10:
        #setup dictionaries
        metrics_list = {'rssmax','write_bytes','duration','cpu_time','read_bytes', 'num_procs', 'time_waiting'}
        metrics_dict = {}
        for metric in metrics_list:
            metrics_dict[metric] = []
        metrics_dict['flux'] = []
        bronx_jobs = eq.get_jobs(jobs = bronx_jobids, fmt = 'dict', trigger_post_process=False)
        for job in bronx_jobs:
            breakage = False
            for metric in metrics_list:
                if job.get(metric) == None:
                    job = eq.get_jobs(jobs = job['jobid'], fmt = 'dict', trigger_post_process=True)[0]
                    
                if job.get(metric) == None:
                    breakage = True
                    continue
                metrics_dict[metric].append(job[metric])
            if breakage == False:
                metrics_dict['flux'].append((job['read_bytes']+job['write_bytes'])/job['cpu_time'])


    # # record keeping
    # We transform data into averages and append that dictionary onto a file that can be called even once the DB is erased.

    # In[19]:


    #process data by getting average, and add errors
    for metric in list(metrics_dict.keys()):
        metrics_dict[metric+'_error'] = np.std(metrics_dict[metric])/(len(metrics_dict[metric]))**.5
        metrics_dict[metric] = sum(metrics_dict[metric])/len(metrics_dict[metric])
    metrics_dict['date'] = date
    metrics_dict['num_jobs'] = len(bronx_jobids)


    # In[20]:


    #record metrics based on date (to avoid repitition)
    filename = 'bronx_history_'+'DO_NOT_DELETE.pkl'
    # Read dictionary pkl file
    with open(filename, 'rb') as fp:
        metrics_history = pickle.load(fp)
    #record new dates
    if date not in metrics_history['date']:
        for key in list(metrics_history.keys()):
            metrics_history[key].append(metrics_dict[key])
    else:
        print('bronx data already recorded for this date')
    # save dictionary to bronx_history_DO_NOT_DELETE.pkl file
    with open(filename, 'wb') as fp:
        pickle.dump(metrics_history, fp)
        print('dictionary saved successfully to file')







    # In[ ]:




