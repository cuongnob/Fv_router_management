#Open SSHv2 connection to devices
import paramiko
import re
import sys
import time
import os

def find_hostname(config):
#Find hostname in configuration file
    line = config.split("hostname ")[1]
    hostname = line.split("\n",1)[0]
    hostname = hostname[:-1]
    return hostname

def host_is_up(ipv4):
#Check ping to host, if host is up response will be 0
    response = os.system("ping -c 3 " + ipv4)
    return response == 0

def check_ipv4_validity(ip_address):
    a = ip_address.split(".")
    return (len(a)==4) and (1 <= int(a[0]) <= 255) and (0 <= int(a[1]) <= 255) and (0 <= int(a[2]) <= 255) and (0 <= int(a[3]) <= 255)

def excute_command(ip,username,password,cmd_file):
    #Change exception message
    try:
        #Logging into device (applied for SSH to Cisco Router
        print "------------------------------------------------------------------------------"
        print "Started logging into device %s" % ip
        session = paramiko.SSHClient()

        session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
        session.connect(ip, username = username, password = password, timeout = 5)
        
        connection = session.invoke_shell()
        
        #Entering global config mode
        connection.send("\n")
        connection.send("enable\n")
        time.sleep(1)
        
        #Setting terminal length for entire output - no pagination
        connection.send("terminal length 0\n")
        time.sleep(1)
        
        #Open user selected file for reading
        selected_cmd_file = open(cmd_file, 'r')
            
        #Starting from the beginning of the file
        selected_cmd_file.seek(0)
        
        #Writing each line in the file to the device
        for each_line in selected_cmd_file.readlines():
            connection.send(each_line + '\n')
            time.sleep(3)
              
        #Closing the command file
        selected_cmd_file.close()
        
        #Checking command output for IOS syntax errors
        output = connection.recv(65535)
        
        if re.search(r"% Invalid input detected at", output):
            print "* There was at least one IOS syntax error on device %s" % ip
        else:    
            #Find hostname in config file and write to file with same name
            hostname = find_hostname(output)
            newfile = open(hostname,"w")
            newfile.write(output)
            newfile.close
            print "Saved configuration file of device %s" % hostname
            print "------------------------------------------------------------------------------"
            
        #Closing the connection
        session.close()
     
    except paramiko.AuthenticationException:
        print "* Invalid username or password. \n* Please check the username/password file or the device configuration!"
        print "* Closing program...\n"
    except paramiko.SSHException:
        print "* The device is not available"
        
#Define the input file, inlcuding ip, username and password file
input_file = sys.argv[1]
cmd_file = sys.argv[2]
        
#Open the input file
selected_input_file = open(input_file, 'r')
selected_input_file.seek(0)

#Getting each line in the input file to process
for each_line in selected_input_file.readlines():
    temp = each_line.split(" ")
    ipv4 = temp[0]
    username = temp[1]
    password = temp[2].rstrip("\n")
    
    #print 'IP is', ipv4
    #print 'Username is', username
    #print 'Password is', password
    
    if check_ipv4_validity(ipv4) and host_is_up(ipv4):
       excute_command(ipv4,username,password,cmd_file) 
    else:
        print "This ip address %s is invalid or not available" % ipv4
        print "------------------------------------------------------------------------------"
       
#Closing the input file
selected_input_file.close()
