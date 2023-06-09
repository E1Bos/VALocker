import subprocess

try:
    subprocess.check_call(["pip", "install", "-r", "requirements.txt"])
    print("Requirements installed successfully.")
except subprocess.CalledProcessError as e:
    print("Failed to install requirements:", str(e))
