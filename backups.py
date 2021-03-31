import datetime
import os
import shutil
from shutil import ignore_patterns
import time

delay_in_minutes = 30
source = 'C:/Users/isabelle/appdata/roaming/obs-studio/basic/'
dest =  'C:/Users/isabelle/Creative Cloud Files/Initiative Design/Client Work/02_Bristol Adventurers Guild/projects/01 Twitch Charity Stream/obs-backups/'

print(f'Backing up OBS stuff every {delay_in_minutes} minutes.')

i=0

while(True):
    timestamp = datetime.datetime.now().strftime(r'%Y-%m-%d_%H-%M')
    directory = dest + timestamp + '/'
    shutil.copytree(source, directory, ignore=ignore_patterns('*LOCK','*.pyc')) 
    
    i+=1
    print(f'Backups so far: {i}')
    time.sleep(60 * delay_in_minutes)

#👍
#¯\_(ツ)_/¯
