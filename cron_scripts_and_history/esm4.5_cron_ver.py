#!/usr/bin/env python
# coding: utf-8

# In[1]:


# import  epmt query 
print('importing epmt_query')
import epmt_query as eq
# import matplot for better plotting functions
import sys

import numpy as np
import datetime
import time
# import pandas. optional but helpful 'display.max_columns' arg shows all DataFrame columns when printing
print('importing pandas')
import pandas as pd
import pickle   #to load in metrics history
pd.set_option('display.max_columns', None)


# In[2]:


#We gather initial estimates and get a list of IDs for the specific date
today_date = datetime.datetime.today()
start_date = today_date + datetime.timedelta(days =-7)   #day that ends the week
older_date = start_date + datetime.timedelta(days =-1) 
date = (start_date.strftime("%m")+'-'+start_date.strftime("%d")+'-'+start_date.strftime("%y")) #date in an easy to read format
#use orm and trigger_post_process=False to get data quickly
older_orm = eq.get_jobs(after=older_date, fmt = 'orm',trigger_post_process=False)
start_orm = eq.get_jobs(after=start_date, fmt = 'orm',trigger_post_process=False)
job_num = older_orm.count() - start_orm.count()    #clip off the jobs that happened between current time and the end of the week being reported on
all_jobs=eq.get_jobs(limit =int(job_num), offset = start_orm.count(), fmt='orm',trigger_post_process=False)
#sort data by esm4.2 tag in exp_name
ESM_exp_jobids=[]
ESM_exp_names=[]
total_jobs=all_jobs.count()
job_num=0
for job in all_jobs:
    job_num=job_num+1
    exp_name=job.tags.get('exp_name')
    if exp_name is None:
        continue
    if ('ESM4p5' in exp_name) or ('esm4p5' in exp_name.lower()):
        ESM_exp_jobids.append(job.jobid)
        if exp_name in ESM_exp_names:
            continue
        else:
            ESM_exp_names.append(exp_name)    
            
if len(ESM_exp_jobids) < 10:
    print('insuficient data')
else:

    # In[3]:


    #get jobs in dict format, if there is more than 10
    if len(ESM_exp_jobids) >= 10:
        #setup dictionaries
        metrics_list = {'rssmax','write_bytes','duration','cpu_time','read_bytes', 'num_procs', 'time_waiting'}
        metrics_dict = {}
        for metric in metrics_list:
            metrics_dict[metric] = []
        metrics_dict['flux'] = []
        esm4p5_jobs = eq.get_jobs(jobs = ESM_exp_jobids, fmt = 'dict', trigger_post_process=False)
        for job in esm4p5_jobs:
            if job.get('rssmax') == None:
                job = eq.get_jobs(jobs = job['jobid'], fmt = 'dict')[0]

            for metric in metrics_list:
                metrics_dict[metric].append(job[metric])
            metrics_dict['flux'].append((job['read_bytes']+job['write_bytes'])/job['cpu_time'])


    # In[ ]:


    #process data by getting average, and add errors
    for metric in list(metrics_dict.keys()):
        metrics_dict[metric+'_error'] = np.std(metrics_dict[metric])/(len(metrics_dict[metric]))**.5
        metrics_dict[metric] = sum(metrics_dict[metric])/len(metrics_dict[metric])
    metrics_dict['date'] = date
    metrics_dict['num_jobs'] = len(ESM_exp_jobids)


    # In[ ]:


    #record metrics based on date (to avoid repitition)
    filename = 'esm4.5_history_'+'DO_NOT_DELETE.pkl'
    # Read dictionary pkl file
    with open(filename, 'rb') as fp:
        metrics_history = pickle.load(fp)
    #record new dates
    if date not in metrics_history['date']:
        for key in list(metrics_history.keys()):
            metrics_history[key].append(metrics_dict[key])
    # save dictionary to weekly_metric_storage_DO_NOT_DELETE.pkl file
    with open(filename, 'wb') as fp:
        pickle.dump(metrics_history, fp)
        print('dictionary saved successfully to file')


    # In[ ]:




