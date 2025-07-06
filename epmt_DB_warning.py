# This script is designed to notice if the EPMT Data Base is not processing files, and send out a warning or critical email if no procs files found
print('importing epmt_query')
import epmt_query as eq
# import matplot for better plotting functions
import numpy as np
# import pandas. optional but helpful 'display.max_columns' arg shows all DataFrame columns when printing
print('importing pandas')
import os
import pandas
import datetime
import time
import pickle   #to load in metrics history
import smtplib as smtplib
print('imported smtplib succesfully')

status = 'no status'
procs_count = 0
for hour in range(1,25):
    if procs_count == 0:   #this allows the code to not keep making queries if their are already procs detected
        limiter = eq.get_jobs(limit = 10, after=-1*(hour)/24, before =-1*(hour-1)/24, fmt = 'dict')
        for job in limiter:
            procs_count += int(job['num_procs'])

        if hour == 13:
            status = 'warning'
        if hour == 24:
            status = 'critical'

    else:
        continue
#create function to send email with input text

def send_email(subject,body, send_to): #takes the subject line of the email, and the boday of text
    # SMTP server configuration
    import smtplib as smtplib
    smtp_host = 'relay2'  # Replace with your SMTP relay host
    smtp_port = 25        # Replace with SMTP port that I will figure out later

    # Email sender and receiver
    sender_email = 'Avery.Kiihne@noaa.gov'  # Replace with your sender email address
    receiver_email = send_to  # Replace with recipient email address

    # Construct the email headers and body manually
    email_message = f"From: {sender_email}\nTo: {receiver_email}\nSubject: {subject}\n\n{body}"


    try:
        # Connect to the SMTP server
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            # Send the email
            server.sendmail(sender_email, receiver_email, email_message)
            print(f'Email sent successfully to {receiver_email}')

    except Exception as e:
        print(f'Error: {e}')

#set list of recipients
recipients = ['Avery.Kiihne@noaa.gov','chandin.wilson@noaa.gov','chris.blanton@noaa.gov','ian.laflotte@noaa.gov']


if status == 'warning':
    #make warning email
    subject = 'Warning: DB at risk'
    body = 'script epmt_DB_warning.py has detected abnormally low levels of procs files in the last 12 hours'
    for send_to in recipients:
        send_email(subject,body,send_to)
    #make warning email

if status == 'critical':
    #make critical status email
    subject = 'Critcal Warning: DB down'
    body = 'script epmt_DB_warning.py has detected no procs files in the last 24 hours. The EPMT DataBase is most likely down. This email will send again in 24 hours if still down.'
    for send_to in recipients:
        send_email(subject,body,send_to)#for testing
#send_email('test subject','test body')
