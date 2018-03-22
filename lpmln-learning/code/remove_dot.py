import os
import sys

ipt = open(sys.argv[1], 'r')
buffer = []
for line in ipt:
	line = line.strip().replace('\n', '').replace('\r', '')
	if line != '.':
		buffer.append(line)

os.remove(sys.argv[1])
out = open(sys.argv[1], 'w')
for line in buffer:
	out.write(line + '\n')