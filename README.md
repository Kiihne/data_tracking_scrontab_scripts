# scrontab_scripts

## Description
This project was designed around gathering long term data that cannot fit in the EPMT Data Base, via scripts automated with scrontab. each time scrontab runs, several scripts pull every job for a given date, 7 days ealier than the current date. These scripts break jobs into multiple, and sometimes overlapping categories, and record # of jobs, average rssmax, duration, read_bytes, write_bytes, cpu_time, time_waiting, num_procs, flux ((read +write bytes)/cpu_time) and their error for that date. Currently, we are tracking esm4.2,esm4.5, SPEAR,am4, cm4, canopy, bronx, and a number of power users. Jupyter notebook copies of the .py script exist for ease of understanding and experimentation. Several other notebooks handle ways of viewing this data.

# Scron command
This is the command currently in scrontab:
```
#SCRON --time=00:59:00
#SCRON --job-name=daily_metric_scraper
#SCRON --output=kiihne_scron_output/log.%j
0 * * * * /home/Avery.Kiihne/cron_run.sh
```
The cron_run.sh file contains the commands:
```
cd /home/Avery.Kiihne/epmt_analysis_notebooks/scrontab_scripts/cron_scripts_and_history
module load epmt/4.9.2
epmt python bronx_cron_ver.py
epmt python canopy_cron_ver.py
epmt python universal_name_cron.py
epmt python ../individual_user_tracking/universal_user_tracking.py

echo "python script run"
```
## Usage
### view_history_plots.ipynb
This jupyter notebook creates the plots for esm4.2,esm4.5, SPEAR,am4, cm4, canopy, and bronx. Only change chosen_name = '$chosen name$' in the 2nd cell, then run all other cells.
### history_maker.ipynb
creates or resets files in which history for a category is recorded.
### cron_scripts_and_history
where history files and scripts for scron are stored.

## Roadmap
Data is being gathered for future, long sighted projects. We hope to leverage ML approaches to this data in the future.

## Authors and acknowledgment
By Avery Kiihne, for EPMT at GFDL
