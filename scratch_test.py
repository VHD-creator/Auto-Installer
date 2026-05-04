import subprocess
import time

with open("test.bat", "w") as f:
    f.write("@echo off\necho Hello World\nping 127.0.0.1 -n 3 > nul\n")

print("Starting...")
subprocess.run('start /wait "" "test.bat"', shell=True)
print("Done!")
