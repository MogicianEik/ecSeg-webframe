import pexpect
from pexpect import popen_spawn
# add process here

child = pexpect.spawn("python3 ecSeg.py -i {}".format('images'))
index = child.expect(['Successfully',pexpect.EOF],timeout=None)

if index == 0:
    print("success")
else:
    print("failed")
