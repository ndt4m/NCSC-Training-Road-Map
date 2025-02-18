# Exam

**Note:** The program must be coded in Linux OS.

## File Server and File Client

Develop two programs, **File Server** and **File Client**, using the C/C++ socket library  
([Socket Programming in C/C++](https://www.geeksforgeeks.org/socket-programming-cc/)),  
with the following requirements:

---

## File Server

### Requirements:
- Use **TCP sockets**.
- Accept the following command-line arguments:
  - `-h/--help`: Display the application's help message.
  - `-p/--port`: Specify the port number the server will use to accept client connections.
  - `-r/--root`: Define the root directory for the File Server.  
    The application **must only** access files within this directory and should not access  
    any other directories on the system.

### Responsibilities:
- Accept connection requests from clients.
- Handle and process an **unlimited number of clients simultaneously**,  
  supporting up to **1000 concurrent connections** while functioning normally.
- Receive, process, and respond to client requests.

### Supported Commands:
- `ls` - List all files in the current directory.  
  Similar to the Linux `ls` command but without displaying permissions.  
  It must distinguish between **files** and **directories**, displaying file sizes in bytes.
- `cd <directory>` - Navigate into subdirectories of the root directory,  
  similar to the Linux `cd` command.
- `get <filename>` - Download a **file** or **directory** `<filename>`.
- `put <filename>` - Upload a **file** or **directory** `<filename>`  
  to the currently selected directory.
- **Unsupported commands** must return the message:  
  `"Unsupported Command"`.

---

## File Client

### Requirements:
- Accept the following command-line arguments:
  - `-h/--help`: Display the application's help message.
  - `-i/--ip`: Specify the **IP address** of the File Server.
  - `-p/--port`: Specify the **port** the File Server is listening on.

### Responsibilities:
- Connect to the File Server.
- Accept user commands, send them to the File Server,  
  receive the response, and display it to the user.
- Support all commands provided by the File Server.

### Command Behavior:
- `get <filename>` - Download a **file** or **directory** `<filename>`  
  from the File Server and save it in the **current directory**.
- `put <filename>` - Read a **file** or **directory** `<filename>`  
  and upload it to the File Server.

---

## Example Usage

### Start the File Server:
```sh
$ ./server -p 5555 -r /tmp/fileserver/
[*] Start file server successfully in 0.0.0.0:5555
[+] New client connected from 192.168.1.130
