# ShowTechAnalyzer

Show Tech Analyzer is a tool which is used to analyze/debug various commands used in the configuration of routers and switchs in networking. This tool is used for SONiC commands. It highlights errors, warnings etc., of these various commands which are mentioned below. This tool uses the python kivy module for making its GUI. Commands analyzed are:

1. show platform summary
2. show syslog
3. show syslog 1
4. show version
5. show ip neighbour
6. show arp (Linux)
7. show reboot cause
8. show interface status
9. show broadcom knet link
10. show broadcom ps
11. show bridge vlan
12. show vlan summary
13. show vlan (Linux)
14. show docker stats (without Linux)
15. show docker ps
16. show frr interfaces
17. show top
18. show lldp control
19. show bgp summary
20. show mirror summary
21. show port summary
22. show ip route
23. show ip neighbour
24. show bridge fdb
25. show ip interface

# prerequisite 

Before running this tool you need MongoDB to be pre installed in your system.

# How the tool works

1. First you need to select show tech tar file 
2. Then just click the "Analyze" button 
3. After few seconds you will see the analyzed results.

# Technologies used

1. Kivy
2. Python
3. Datetime
4. MongoDB

# Demo

## 1. This is the first page that the user see

![alt text](https://github.com/khanna-harshit/ShowTech/blob/main/assets/main.png)


## 2. From here you need to select the show tech file which you want to analyze

![alt tag](https://github.com/khanna-harshit/ShowTech/blob/main/assets/upload_file.png)


## 3. This page will shown for few seconds 

![alt tag](https://github.com/khanna-harshit/ShowTech/blob/main/assets/analyze.png)


## 4. Here you will see your analyzed results

![alt tag](https://github.com/khanna-harshit/ShowTech/blob/main/assets/Results.png)


