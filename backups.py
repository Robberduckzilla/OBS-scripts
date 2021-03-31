import datetime
import os
import shutil
import time

delay_in_minutes = 0.1
source = "C:/Users/isabelle/appdata/roaming/obs-studio/"
dest =  "C:/Users/isabelle/Creative Cloud Files/Initiative Design/Client Work/02_Bristol Adventurers Guild/projects/01 Twitch Charity Stream/obs-backups/"

print(f'Backing up OBS stuff every {delay_in_minutes} minutes.')
i=0

while(True):
    timestamp = datetime.datetime.now().strftime(r'%Y-%m-%d_%H-%M')
    src_files = os.listdir(source)
    directory = dest + timestamp + "/"
    os.makedirs(os.path.dirname(directory), exist_ok=True)

    for file_name in src_files:
        full_file_name = os.path.join(source, file_name)
        if os.path.isfile(full_file_name):
            shutil.copytree(full_file_name, directory + file_name) 
    i+=1
    print(f'Backups so far: {i}')
    
    time.sleep(60 * delay_in_minutes)
