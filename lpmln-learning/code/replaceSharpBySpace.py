import sys

ipt = open(sys.argv[1], 'r')
buffer = []
for line in ipt:
	buffer.append(line.replace('^', ' '))
ipt.close()
opt = open(sys.argv[1], 'w')
for line in buffer:
	opt.write(line)
opt.close()