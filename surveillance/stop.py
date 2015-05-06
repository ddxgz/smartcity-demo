import subprocess

pidfile = open('./pids', 'r')
for pid in pidfile:
    pid = pid.strip()
    child = subprocess.Popen(['kill', int(pid)])
