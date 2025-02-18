# Exam for Python Lab – Duration: 6 Hours

## Question 1:

Build a CLI (Command Line Interface) program using Python (2 or 3) that allows users to view and browse information about existing exploits on exploit-db.com. Requirements:

### 1. Parameters passed through arguments:

- **Parameter –exploit**: Fetch the content of an exploit from exploit-db (a sample code for handling this is provided), save it locally, and open it using the operating system's default reader. The user can input either the exploit ID (e.g., 1234) or the full URL (e.g., exploit-db.com/exploits/1234). Use **only regex** (no if statements, replace, etc.) to process the input and extract the ID value. Note: If the exploit already exists locally, open the file directly without sending a request to exploit-db.com.

- **Parameter –page**: Return the results of exploits stored in the corresponding page. The structure organizes 5 exploits per page. Pages are numbered starting from 0. Exploits are sorted in ascending order by ID.

- **Parameter –search**: Search for a keyword in the content of stored exploits. Use **only regex** (no find, search, etc.) to process the search within the exploit content. For example, if the user searches for “here we go”, the program should return exploits containing at least one of the words “here”, “we”, or “go”.

- **Parameter –help**: Return usage instructions. If the user provides incorrect or no parameters, the help page should also be returned.

The priority order for processing functions is: **exploit > page > search**. If the user inputs multiple parameters, only the highest-priority function will be processed.

After processing one function, the program should exit. The user must input parameters again to perform the next function. Handle exceptions to avoid printing unnecessary errors during usage. Organize the source code to be clear and easy to read.

### 2. Data Storage Organization

- Use a file-based system to store data.
- Each exploit will be saved in a file with the format `[ID].txt`.
- All exploits will be stored in a folder named “exploit-db”. This folder should be located in the same directory as the program file.
- Do not use any additional files or databases to store the database for the page functionality. Handle this functionality programmatically.

### 3. Application Demo

[Download the demo here](https://drive.google.com/file/d/1_kZ0DLms8ycAX6Rw2_U4q4wUDyC6vygN/) (Download if you cannot view it online).

### 4. Base Code

```python
import requests
import html

path = './exploit-db'

def exploit_func(id):
    # id = '1234'
    url = 'https://exploit-db.com/exploits/{}'.format(id)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    res = requests.get(url, headers=headers)

    exploit = res.text[res.text.find('<code>'): res.text.find('</code>')]
    exploit = html.unescape(exploit[exploit.find("'>") + 2:])
    print(exploit)

def page_func(id):
    return

def search_func(keyword):
    return

if __name__ == '__main__':
    exploit_func(exploit)
    page_func(page)
    search_func(search)
