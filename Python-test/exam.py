import requests
import html
import re
import os
import argparse
import subprocess
import sys

path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"exploit-db")
# Check whether the specified path exists or not
isExist = os.path.exists(path)
if not isExist:
   # Create a new directory because it does not exist
   os.makedirs(path)
   
list_file = os.listdir(path) # list of file [ID].txt in exploit-db dir
list_id = sorted([i[:-4 ] for i in list_file], key=int) # list ID of [ID].txt   


# write a subclass MyArgumentParser inherit from the ArgumentParser class of the argparse module
# then overwrite the error method to print the help page every time an error raise
class MyArgumentParser(argparse.ArgumentParser):

    def error(self, message):
        raise ValueError(message)

def open_file(filename): #open file by its default
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])

def exploit_func(id):# get exploit from dir \exploit-db or exploit-db.com then print the content of the file
    #id = '1234'
    
    if str(id) in list_id:# if id in dir exploit-db -> open
        
        open_file(os.path.join(path, f"{id}.txt"))
            
    else: # if id not in dir exploit-db -> make request to exploit-db.com ,then store the content in [ID].txt at \exploit-db
        
        # make request
        url = 'https://exploit-db.com/exploits/{}'.format(id)
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        res= requests.get(url, headers = headers)
        exploit = res.text[res.text.find('<code') : res.text.find('</code>')]
        exploit = html.unescape(exploit[exploit.find('">') +2 :])
        
        # check if there is an exploit with passed id
        if exploit != "":  
            # store content to file
            with open(r'{}//{}.txt'.format(path, id), "w") as f:
                f.write(exploit)
            f.close()
        
            # open file by default text editor 
            open_file(os.path.join(path, f"{id}.txt"))
            
        else: # an exploit with passed id does not exist
            print("404 Page Not Found")
        
        
        
def page_func(id):# print the exploits at page i
    
    id  = int(id)
    
    # group each 5 exploit into 1 block 
    i=0
    pages=[]
    
    while i<len(list_id):
        pages.append(list_id[i:i+5])
        i+=5
    the_number_of_page = len(pages)
    # if the exploit-db directory is empty, print "There are no file in ./exploit-db"
    # elif the id is out of range, print "There are no such page with the id = "
    # else print the page
    if the_number_of_page == 0:
        print("There are no file in ./exploit-db")
        
    elif the_number_of_page <= id:
        print(f"There are only {the_number_of_page} page starting from 0")
        
    else:
        [print(exploit) for exploit in pages[id]]



def search_func(keyword): #find the file satisfied the constrain
    
    count = 0 # the number of valid file
    
    words = "|".join(keyword.strip().split(" ")) # a list of key word
    
    #creat a pattern for re.findall() method 
    Pattern = '(?<=\s)(?:{})(?=\s)'.format(words)
    
    #find the file that one of the key word occurs
    for file in list_file:
        # open each file and search the word 
        # store result in res variable
        # if res is None, that is, no keyword in that file --> skip
        # else print the result
        
        with open('{}//{}'.format(path, file), 'r') as f:
                data = f.read()
        f.close()
        
        res = re.findall(Pattern, data) 
        
        if res:
            count += 1
            print(f"./exploit-db/{file}")
            
    if count == 0: # no file is found with the keyword
        print(f"Cannot find {keyword}")   
    
    
if __name__ == '__main__':
    
    parser = MyArgumentParser(description="------------------------Python Exam---------------------------------------")
    parser.add_argument('-e', '--exploit', metavar="", type = str, help='exploit ID, the argument must be an int number or a URL: https://exploit-db.com/exploits/id')
    parser.add_argument('-p', '--page', metavar="", type = str, help='get page, the argument must be an int')
    parser.add_argument('-s', '--search', metavar="", type = str, help='Search keyword')

    try:
        arg = parser.parse_args()
    
        if arg.exploit != None:
            res = re.findall(r'(?<=^https:\/\/exploit-db\.com\/exploits\/)\d+$|^\d+$', arg.exploit) # find the id of the exploit in term of list --> example: [1]
            id = res[0] # get the id
            exploit_func(id) # print the content of the exploit
            
        elif arg.page != None:
            res = re.findall(r'^\d+$',arg.page) # find the index of the page in term of list --> example: [1] 
            page_index = res[0] # get the page index
            page_func(page_index) # print all the exploits in the i_page 
            
        elif arg.search != None: 
            search_func(arg.search) # print all the file that the kword occurs
        
        else: 
            parser.print_help()
            
    except Exception:
        parser.print_help()