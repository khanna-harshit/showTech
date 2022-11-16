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




![alt text](https://github.com/khanna-harshit/ShowTech/blob/main/assets/main.png)

This is the first screen that the user see (MyLayout is the name used in project.py and project.kv file) 

![alt tag](https://github.com/khanna-harshit/ShowTech/blob/main/assets/upload_file.png)

This is the second screen that the user see (MyPopup is the name used in project.py and project.kv file). This screen will be seen when the user wants to upload a file for the analysis purpose by clicking on the upload file button. 

![alt tag](https://github.com/khanna-harshit/ShowTech/blob/main/assets/analyze.png)

This is the third screen that the user see (Analyse is the name used in project.py and project.kv file)  

![alt tag](https://github.com/khanna-harshit/ShowTech/blob/main/assets/Results.png)
This is the fourth screen that the user see (Results is the name used in project.py and project.kv file)  



