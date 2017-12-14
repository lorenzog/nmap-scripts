# nmap-scripts

Script to query a NMAP XML output and sort the result *by port*.

## Quickstart:

	python nmap-by-port.py nmap-top1k.xml

Will show:

	80/tcp ['192.168.1.1', '192.168.1.2']
	443/tcp ['192.168.1.1, '192.168.1.3']

Custom queries e.g. by service name:

	python nmap-by-port.py nmap-top100.xml -f '*[@name="https"]'

Will show:

	443/tcp ['192.168.1.1', '192.168.1.3']

For help use:

	python nmap-by-port.py -h
