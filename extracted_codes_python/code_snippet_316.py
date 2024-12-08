#! /vols/cms/tr1123/condor_tools/env/bin/python
import sys
import os
import htcondor
import argparse
import subprocess
import getpass
import datetime
from typing import DefaultDict
from collections import defaultdict
from termcolor import colored
from prettytable import PrettyTable

# Initialize the Collector and Schedd
collector = htcondor.Collector()
schedd = htcondor.Schedd()

def get_real_name(username: str) -> str:
    """ Uses the 'pinky' command to get the real name of a user from their username """
    try:
        # Parse output of 'pinky' to extract the real name
        result = subprocess.run(['pinky', '-l', username], stdout=subprocess.PIPE, text=True)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'In real life:' in line:
                    return line.split('In real life:')[1].strip()
    except Exception:
        pass
    return ""

def fetch_jobs() -> DefaultDict:
    """ Fetch and print job details from HTCondor schedd, grouped and ranked by user based on job count """
    status_dict = {1: 'Idle', 2: 'Running', 3: 'Removed', 4: 'Completed', 5: 'Held', 6: 'Transferring Output', 7: 'Suspended'}
    
    # Query for jobs
    jobs = schedd.query(
        projection=["ClusterId", "ProcId", "Owner", "JobStatus", "RemoteHost", "RequestGPUs"]
    )

    # Group jobs by owner and count statuses, differentiated by machine type
    user_jobs = defaultdict(list)
    user_stats = defaultdict(lambda: {'CPU': defaultdict(int), 'GPU': defaultdict(int), 'Total': defaultdict(int)})
    for job in jobs:
        job_info = {
            "Job ID": f"{job['ClusterId']}.{job['ProcId']}",
            "Status": status_dict.get(job.get("JobStatus"), "Unknown"),
            "Machine": job.get("RemoteHost", "N/A")
        }
        owner = job["Owner"]
        if 'gpu' in job_info["Machine"].lower():
            machine_type = 'GPU'
        elif job_info["Machine"] == "N/A":
            gpus = job.get('RequestGPUs', 0)
            if gpus != 0:
                machine_type = 'GPU'
            else:
                machine_type = 'CPU'
        else:
            machine_type = 'CPU'
        user_jobs[owner].append(job_info)
        user_stats[owner][machine_type][job_info["Status"]] += 1
        user_stats[owner]['Total'][job_info["Status"]] += 1

    return user_stats

def format_table(user_stats: DefaultDict, current_user: str=None) -> PrettyTable:
    # Setup table
    if priority:
        headers = ['User', 'Name', 'Priority', 'CPU', 'GPU', 'Total']
    else:
        headers = ['User', 'Name', 'CPU', 'GPU', 'Total']
    tab = PrettyTable(headers, align='l', hrules=1)
    status_for_print = ['Running', 'Idle', 'Held']
    machine_stats = defaultdict(lambda: dict(zip(status_for_print, [0]*len(status_for_print))))
    
    # Get stats by user, per machine type
    for user, jobs in user_stats.items():
        row = [user]
        row.append(get_real_name(user))
        if priority:
            row.append(user_priorities.get(user, -1))
        for machine_type, stats in jobs.items():
            s = ''
            total = 0
            for status in status_for_print:
                val = stats[status]
                s += f"{status}: {val}\n"
                total += val
                machine_stats[machine_type][status] += val
            s += f"Total: {total}"
            row.append(s)
        if user == current_user:
            c_row = []
            for entry in row:
                # Apply color to the text content only, not the dividers
                colored_lines = [colored(line, 'green') for line in str(entry).split('\n')]
                colored_entry = '\n'.join(colored_lines)
                c_row.append(colored_entry)
            tab.add_row(c_row)
        else:
            tab.add_row(row)
    
    # Get totals by machine type
    totals = []
    for stats in machine_stats.values():
        s = ''
        for status in status_for_print:
            s += colored(f"{status}: {stats[status]}", 'red') + '\n'
        s += colored(f"Total: {sum(stats.values())}", 'red')
        totals.append(s)
    try:
        if priority:
            tab.add_row([colored('Total', 'red'), '', ''] + totals)
        else:
            tab.add_row([colored('Total', 'red'), ''] + totals)
    except ValueError:
        print("No jobs found in current schedd.")
        sys.exit(1)

    return tab

def log():
    """ Logs the usage of the script """
    # Get the current user's username
    username = getpass.getuser()
    real_name = get_real_name(username)
    
    # Get the current timestamp
    timestamp = datetime.datetime.now().isoformat()
    
    # Log to file
    script_dir = os.path.dirname(os.path.realpath(__file__))
    log_file_path = os.path.join(script_dir, "usage_log.txt")
    with open(log_file_path, "a+") as log_file:
        # Write the timestamp, username, and real name to the log file
        log_file.write(f"{timestamp}, {username}, {real_name}\n")
        
if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Display HTCondor job stats.')
    parser.add_argument('--priority', action='store_true', help='Display user priorities.')
    args = parser.parse_args()
    priority = args.priority

    # Print intro message with current date and time
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    intro_message = f"HTCondor Job Stats @ {current_datetime}"
    print(intro_message)
    
    # Get the user who ran the script
    username = getpass.getuser()
    
    if priority:
        # Get user priorities from condor_userprio --allusers
        # because the AdTypes.Negotiator leaves out some users
        user_priorities = defaultdict(float)
        result = subprocess.run(['condor_userprio', '-allusers', '-priority'], stdout=subprocess.PIPE)
        lines = result.stdout.decode('utf-8').split('\n')[4:-3] # Cursed
        for line in lines:
            parts = line.split()
            if len(parts) >= 3:
                user_priorities[parts[0].split('@')[0]] = float(parts[1])  # Use the second column as the priority
    
    log()
    user_stats = fetch_jobs()
    table = format_table(user_stats, current_user=username)
    print(table)
