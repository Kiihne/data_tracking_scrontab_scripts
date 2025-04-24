#!/usr/bin/env python
# coding: utf-8

# In[1]:


# import  epmt query 
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
# In[2]:


#We gather initial estimates and get a list of IDs for the specific date
today_date = datetime.datetime.today()
start_date = today_date + datetime.timedelta(days =off_set_days)   #day that ends the week
older_date = start_date + datetime.timedelta(days =-1) 
date = (start_date.strftime("%m")+'-'+start_date.strftime("%d")+'-'+start_date.strftime("%y")) #date in an easy to read format
#use orm and trigger_post_process=False to get data quickly
older_orm = eq.get_jobs(after=older_date, fmt = 'orm',trigger_post_process=False)
start_orm = eq.get_jobs(after=start_date, fmt = 'orm',trigger_post_process=False)
job_num = older_orm.count() - start_orm.count()    #clip off the jobs that happened between current time and the end of the week being reported on
all_jobs=eq.get_jobs(limit =int(job_num), offset = start_orm.count(), fmt='orm',trigger_post_process=False)

#formal names are those that appear on plots and in file name
formal_names = ['esm4.2','esm4.5', 'SPEAR','am4', 'cm4', 'om4','om5']
#names are what the category appears under in jobs[tags][exp_name]
names = ['ESM4p2','ESM4p5', 'SPEAR','AM4','CM4','OM4','OM5']
for name_number in range(len(names)):
    #check to see if day is already recorded. if it is, exit code
    #this allows code to be run much more frequently, without redoing days, which helps whith timing out issues
    recent_job = eq.get_jobs(limit = 1, after = off_set_days, fmt = 'orm')[0]

    recent_job_date = recent_job.created_at
    current_date = str(recent_job_date.strftime("%m")+'-'+recent_job_date.strftime("%d")+'-'+recent_job_date.strftime("%y"))
    filename = formal_names[name_number]+'_history_'+'DO_NOT_DELETE.pkl'
    # Read dictionary pkl file
    with open(filename, 'rb') as fp:
        metrics_history = pickle.load(fp)
    if current_date in metrics_history['date']:
        sys.exit(['date already recorded for universal names'])

    print(names[name_number])
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
        if (names[name_number] in exp_name) or (names[name_number].lower() in exp_name.lower()):
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
            esm4p2_jobs = eq.get_jobs(jobs = ESM_exp_jobids, fmt = 'dict', trigger_post_process=False)
            for job in esm4p2_jobs:
                breakage = False
                for metric in metrics_list:
                    if job.get(metric) == None:
                        job = eq.get_jobs(jobs = job['jobid'], fmt = 'dict', trigger_post_process=True)[0]\
                        
                        
                    #if metric sstill does not exist, skip this job instance
                    if job.get(metric) == None:
                        breakage = True
                        continue
                    metrics_dict[metric].append(job[metric])
                
                if breakage == False:
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
        filename = formal_names[name_number]+'_history_'+'DO_NOT_DELETE.pkl'
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




