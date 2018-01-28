# xmr-stak-monitor

A simple monitor to check whatever xmr-stak is working or has hanged.

I run xmr-stak as a daemon in Windows using nssm but some times ramdomly xmr-stak stops responding and stops mining. This program will check if the http page of the miner is working, and if its not working, it will restart the daemon.

