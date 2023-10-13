#include <stdio.h>
#include <iostream>
#include <string.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <string>
#include <sstream>
#include <dirent.h>
#include <sys/stat.h>
#include <poll.h>
#include <vector>
#include <map>
#include <utility>
#include <getopt.h>
#include <fcntl.h>
#include <errno.h>
#include <math.h>
#include <iomanip>
#include <algorithm>

#define File 0
#define Dir 1
#define SIZE 1024

struct box
{
   short fileType;
   unsigned long long fileSize;
   char data[SIZE];
};

int sendAll(size_t size, char* src, struct pollfd& fd_info, std::map<int, sockaddr_in>& clients_info, std::map<int, std::string>& clientLastDir)
{
   int sockfd = fd_info.fd;

   int totalBytesSent = 0;
   int bytesSent = 0;

   while (totalBytesSent < size)
   {
      bytesSent = write(sockfd, src + totalBytesSent, size - totalBytesSent);

      if (bytesSent < 0)
      {
         std::cerr << "[-] ERROR: " << strerror(errno) << "\n";
         std::cout << "[+] Disconnected the client from " << inet_ntoa(clients_info[sockfd].sin_addr) << ":" << ntohs(clients_info[sockfd].sin_port) << "\n";
         clients_info.erase(sockfd);
         clientLastDir.erase(sockfd);
         close(sockfd);
         fd_info.fd = -1;
         return 1;
      }
      else if (bytesSent == 0)
      {
         std::cout << "[+] Client from " << inet_ntoa(clients_info[sockfd].sin_addr) << ":" << ntohs(clients_info[sockfd].sin_port) << " disconnected\n";
         clients_info.erase(sockfd);
         clientLastDir.erase(sockfd);
         close(sockfd);
         fd_info.fd = -1;
         return 1;
      }

      totalBytesSent += bytesSent;
   }

   return 0;
}

int receiveAll(size_t size, char* dest, struct pollfd& fd_info, std::map<int, sockaddr_in>& clients_info, std::map<int, std::string>& clientLastDir)
{
   int sockfd = fd_info.fd;

   int totalBytesReceived = 0;
   int bytesReceived = 0;

   while (totalBytesReceived < size)
   {
      bytesReceived = read(sockfd, dest + totalBytesReceived, size - totalBytesReceived);

      if (bytesReceived < 0)
      {
         std::cerr << "[-] ERROR: " << strerror(errno) << "\n";
         std::cout << "[+] Disconnected the client from " << inet_ntoa(clients_info[sockfd].sin_addr) << ":" << ntohs(clients_info[sockfd].sin_port) << "\n";
         clients_info.erase(sockfd);
         clientLastDir.erase(sockfd);
         close(sockfd);
         fd_info.fd = -1;
         return 1;
      }
      else if (bytesReceived == 0)
      {
         std::cout << "[+] Client from " << inet_ntoa(clients_info[sockfd].sin_addr) << ":" << ntohs(clients_info[sockfd].sin_port) << " disconnected\n";
         clients_info.erase(sockfd);
         clientLastDir.erase(sockfd);
         close(sockfd);
         fd_info.fd = -1;
         return 1;
      }

      totalBytesReceived += bytesReceived;
   }

   return 0;
}

std::string receive_file_name_of_get_command(struct pollfd& fd_info, std::map<int, sockaddr_in>& clients_info, std::map<int, std::string>& clientLastDir)
{

   char msg[sizeof(box)];
   bzero(msg, sizeof(msg));
   
   if (receiveAll(sizeof(msg), msg, fd_info, clients_info, clientLastDir) == 1)
   {
      return "Fail";
   }

   return std::string(msg);
}

void writeFile(struct pollfd& fd_info, std::map<int, sockaddr_in>& clients_info, std::map<int, std::string>& clientLastDir, std::string fileName, unsigned long long fileSize)
{  
   
   unsigned long long &bytesLeftToReceive = fileSize;

   char cwd[PATH_MAX];
   getcwd(cwd, PATH_MAX);

   std::string newName = std::string(cwd) + "/copy_" + std::string(fileName);
   
   FILE* f = fopen(newName.c_str(), "wb");
   if (f == NULL)
   {
      std::cerr << "[-] ERROR: Can't create new file\n";
      std::cerr << "[-] ERROR: " << strerror(errno) << "\n";
      fclose(f);

      clients_info.erase(fd_info.fd);
      close(fd_info.fd);
      fd_info.fd = -1;
      return;
   }

   char receiveBuffer[SIZE];
   bzero(receiveBuffer, sizeof(receiveBuffer));

   int bytesToReceive = -1;
   
   while(bytesLeftToReceive > 0)
   {
      bytesToReceive = std::min<unsigned long long>(bytesLeftToReceive, SIZE);
      
      if (receiveAll(bytesToReceive, receiveBuffer, fd_info, clients_info, clientLastDir) == 1)
      {
         return;
      }

      fwrite(receiveBuffer, 1, bytesToReceive, f);

      bzero(receiveBuffer, SIZE);

      bytesLeftToReceive = bytesLeftToReceive - bytesToReceive;

   }

   fclose(f);
}

void writeDir(struct pollfd& fd_info, std::map<int, sockaddr_in>& clients_info, std::map<int, std::string>& clientLastDir)
{
   
   char msg[sizeof(box)];
   box receiver;

   bzero(&receiver, sizeof(box));
   bzero(msg, sizeof(msg));
   
   if (receiveAll(sizeof(msg), msg, fd_info, clients_info, clientLastDir) == 1)
   {
      return;
   }

   if (strcmp(msg, "success") != 0)
   {
      return;
   }

   if (receiveAll(sizeof(msg), msg, fd_info, clients_info, clientLastDir) == 1)
   {
      return;
   }

   memcpy(&receiver, msg, sizeof(box));
   
   if (receiver.fileType == File)
   {
      writeFile(fd_info, clients_info, clientLastDir, std::string(receiver.data), receiver.fileSize);

      bzero(&receiver, sizeof(box));
      bzero(msg, sizeof(msg));

      return;
   }
   else // Case the file is Directory
   {

      char beginCWD[PATH_MAX];

      if (getcwd(beginCWD, PATH_MAX) == NULL)
      {
         std::cerr << "[-] ERROR: " << strerror(errno) << "\n";
         clients_info.erase(fd_info.fd);
         close(fd_info.fd);
         fd_info.fd = -1;
         return;
      }

      std::string newDirName = "copy_" + std::string(receiver.data);

      mkdir(newDirName.c_str(), 0777);

      if (chdir(newDirName.c_str()) == -1)
      {
         std::cerr << "[-] ERROR: " << strerror(errno) << "\n";
         clients_info.erase(fd_info.fd);
         close(fd_info.fd);
         fd_info.fd = -1;
         return;
      }

      
      int loopFlag = -1; 
      
      if (receiveAll(sizeof(int), (char*)&loopFlag, fd_info, clients_info, clientLastDir) == 1)
      {
         return;
      }


      while (loopFlag == 1)
      {
         writeDir(fd_info, clients_info, clientLastDir);
         if (receiveAll(sizeof(int), (char*)&loopFlag, fd_info, clients_info, clientLastDir) == 1)
         {
            return;
         }
      }

      if (chdir(beginCWD) == -1)
      {
         std::cerr << "[-] ERROR: " << strerror(errno) << "\n";
         clients_info.erase(fd_info.fd);
         close(fd_info.fd);
         fd_info.fd = -1;
         return;
      }
   }
   
}

void sendFile(std::string fileName, struct pollfd& fd_info, std::map<int, sockaddr_in>& clients_info, std::map<int, std::string>& clientLastDir)
{

   FILE* f = fopen(fileName.c_str(), "rb");
   if (f == NULL)
   {
      std::cerr << "[-] ERROR: Can't open filename " << fileName << "\n";
      std::cerr << "[-] ERROR: " << strerror(errno) << "\n";
      fclose(f);

      clients_info.erase(fd_info.fd);
      close(fd_info.fd);
      fd_info.fd = -1;
      return;
   }

   char sendBuffer[SIZE];
   bzero(sendBuffer, sizeof(sendBuffer));

   int bytesToSend = -1;
   int bytesReadFromFile = -1;
   while ((bytesReadFromFile = fread(sendBuffer, 1, SIZE, f)) > 0)
   {
      bytesToSend = std::min(bytesReadFromFile, SIZE);

      if (sendAll(bytesToSend, sendBuffer, fd_info, clients_info, clientLastDir) == 1)
      {
         return;
      }
      
      bzero(sendBuffer, SIZE);
   }

   fclose(f);
}

void sendDir(std::string fileName, struct pollfd& fd_info, std::map<int, sockaddr_in>& clients_info, std::map<int, std::string>& clientLastDir)
{  
   char msg[sizeof(box)];
   box sender;

   bzero(&sender, sizeof(box));
   bzero(msg, sizeof(msg));

   // Get the current working directory
   char begin_cwd[PATH_MAX];
   if (getcwd(begin_cwd, PATH_MAX) == NULL)
   {
      std::cerr << "[-] ERROR: " << strerror(errno) << "\n";
      clients_info.erase(fd_info.fd);
      close(fd_info.fd);
      fd_info.fd = -1;
      return;
   }

   // Get the information of the file including file type and file size
   struct stat fileInfo;
   if (stat(fileName.c_str(), &fileInfo) == -1)
   {
      std::cerr << "[-] ERROR: fail to get file state\n";
      std::cerr << "[-] ERROR: " << strerror(errno) << "\n";
      printf("---%s/%s---\n", begin_cwd, fileName.c_str());

      strncpy(msg, strerror(errno), strlen(strerror(errno))+1);
      if (sendAll(sizeof(msg), msg, fd_info, clients_info, clientLastDir) == 1)
      {
         return;
      }
      return;
   }
   else
   {
      strncpy(msg, "success", strlen("success")+1);

      if (sendAll(sizeof(msg), msg, fd_info, clients_info, clientLastDir) == 1)
      {
         return;
      }
   }

   bzero(msg, sizeof(msg));

   if (S_ISREG(fileInfo.st_mode))
   {
      sender.fileType = File;
      sender.fileSize = fileInfo.st_size;
      strncpy(sender.data, fileName.c_str(), fileName.size()+1);
      memcpy(msg, &sender, sizeof(box));

      if (sendAll(sizeof(msg), msg, fd_info, clients_info, clientLastDir) == 1)
      {
         return;
      }

      sendFile(fileName, fd_info, clients_info, clientLastDir);

      bzero(msg, sizeof(msg));
      bzero(&sender, sizeof(box));

      return;
   }
   else // Case: the file is Directory
   {

      sender.fileType = Dir;
      sender.fileSize = fileInfo.st_size;
      strncpy(sender.data, fileName.c_str(), fileName.size()+1);
      memcpy(msg, &sender, sizeof(box));
      
      if (sendAll(sizeof(msg), msg, fd_info, clients_info, clientLastDir) == 1)
      {
         return;
      }
      
      DIR* dir = opendir(fileName.c_str());
      if (dir == NULL)
      {
         std::cout << "dirName = -----/" << fileName << "\\----\n";
         std::cerr << "[-] ERROR: " << strerror(errno) << "\n";
         closedir(dir);

         clients_info.erase(fd_info.fd);
         close(fd_info.fd);
         fd_info.fd = -1;
         return;
      }

      if (chdir(fileName.c_str()) == -1)
      {
         std::cerr << "[-] ERROR: " << strerror(errno) << "\n";
         closedir(dir);
         
         clients_info.erase(fd_info.fd);
         close(fd_info.fd);
         fd_info.fd = -1;
         return;
      }

      struct dirent* entry;
      int loopFlag = -1;
      while ((entry = readdir(dir)) != NULL)
      {
         if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0)
         {  
            continue;
         }
         
         loopFlag = 1;

         if (sendAll(sizeof(int), (char*)&loopFlag, fd_info, clients_info, clientLastDir) == 1)
         {
            return;
         }
         
         
         sendDir(std::string(entry->d_name), fd_info, clients_info, clientLastDir);
      }

      loopFlag = 0;

      if (sendAll(sizeof(int), (char*)&loopFlag, fd_info, clients_info, clientLastDir) == 1)
      {
         return;
      }

      if (chdir(begin_cwd) == -1)
      {
         closedir(dir);
         
         clients_info.erase(fd_info.fd);
         close(fd_info.fd);
         fd_info.fd = -1;
         return;
      }

      closedir(dir);
   }

}

void putServer(struct pollfd& fd_info, std::map<int, sockaddr_in>& clients_info, std::map<int, std::string>& clientLastDir)
{
   writeDir(fd_info, clients_info, clientLastDir);
}

void getServer(struct pollfd& fd_info, std::map<int, sockaddr_in>& clients_info, std::map<int, std::string>& clientLastDir)
{
   std::string fileName = receive_file_name_of_get_command(fd_info, clients_info, clientLastDir);
   
   sendDir(fileName, fd_info, clients_info, clientLastDir);

}

void listServer(struct pollfd& fd_info, std::map<int, sockaddr_in>& clients_info, std::map<int, std::string>& clientLastDir) 
{ 
   int sockfd = fd_info.fd;

   char cwd[PATH_MAX];
   
   if (getcwd(cwd, PATH_MAX) == NULL)
   {
      std::cerr << "[-] ERROR: " << strerror(errno) << "\n";
      
      clients_info.erase(fd_info.fd);
      close(fd_info.fd);
      fd_info.fd = -1;
      return;
   }
   std::cout << cwd << std::endl;

   DIR* directory = opendir(cwd);
   if (directory == NULL) 
   {
      std::cout << "[-] Error on opening directory\n";
      std::cerr << "[-] ERROR: " << strerror(errno) << "\n";
      closedir(directory);
         
      clients_info.erase(fd_info.fd);
      close(fd_info.fd);
      fd_info.fd = -1;
      return;
   } 

   std::stringstream res;
   struct dirent* entry;
   while((entry = readdir(directory)) != NULL) 
   {
      if (entry->d_name[0] == '.')
      {
         continue;
      }
      std::string file_path =  std::string(cwd) + "/" + std::string(entry->d_name);
      struct stat file_info;
       
      if (stat(file_path.c_str(), &file_info) < 0) 
      {
         std::cerr << "[-] ERROR: Unable to get the size of the file\n";
         closedir(directory);
         
         clients_info.erase(fd_info.fd);
         close(fd_info.fd);
         fd_info.fd = -1;
         return;
      }

      if (entry->d_type == DT_REG) 
      {
         res << "-" << "       " << std::setw(20) << std::left << entry->d_name << std::setw(10) << std::right << file_info.st_size << std::endl;
      } 
      else if (entry->d_type == DT_DIR) 
      {
         res << "d" << "       " << std::setw(20) << std::left << entry->d_name << std::setw(10) << std::right << "-" << std::endl;
      }
   }

   if (closedir(directory) == 1) 
   {
      std::cout << "[-] Error on closing directory\n";
   }

   int bytesLeftToSend = res.str().size() + 1;

   if (sendAll(sizeof(int), (char*)&bytesLeftToSend, fd_info, clients_info, clientLastDir) == 1)
   {
      return;
   }

   int totalBytesSent = 0;
   int bytesSent = 0;
   int bytesToSend = -1;
   int offset = 0;
   while (bytesLeftToSend > 0)
   {  
      bytesToSend = std::min(SIZE, bytesLeftToSend);

      while (totalBytesSent < bytesToSend)
      {
         bytesSent = write(sockfd, res.str().c_str() + totalBytesSent + offset, bytesToSend - totalBytesSent);

         if (bytesSent <= 0)
         {
            std::cerr << "[-] ERROR: " << strerror(errno) << "\n";
         
            clients_info.erase(fd_info.fd);
            close(fd_info.fd);
            fd_info.fd = -1;
            return;
         }

         totalBytesSent += bytesSent;
      }

      bytesSent = 0;
      totalBytesSent = 0;

      bytesLeftToSend = bytesLeftToSend - bytesToSend;
      offset += bytesToSend;
   }
}

void changeDirServer(std::string root, struct pollfd& fd_info, std::map<int, sockaddr_in>& clients_info, std::map<int, std::string>& clientLastDir) 
{
   
   char msg[sizeof(box)];
   box receiver;

   bzero(&receiver, sizeof(box));
   bzero(msg, sizeof(msg));

   if (receiveAll(sizeof(msg), msg, fd_info, clients_info, clientLastDir) == 1)
   {
      return;
   }

   memcpy(&receiver, msg, sizeof(box));

   std::string dir_name = std::string(receiver.data);

   char cwd[PATH_MAX];
   if (getcwd(cwd, PATH_MAX) == NULL)
   {
      std::cerr << "[-] ERROR: " << strerror(errno) << "\n";
      
      clients_info.erase(fd_info.fd);
      close(fd_info.fd);
      fd_info.fd = -1;
      return;
   }

   std::string currentDir(cwd);

   std::string newDir = currentDir + "/" + dir_name;
  

   bzero(msg, sizeof(msg));
   char resolvedPath[PATH_MAX];
   if (realpath(newDir.c_str(), resolvedPath) == NULL)
   {

      strncpy(msg, strerror(errno), strlen(strerror(errno))+1);
      if (sendAll(sizeof(msg), msg, fd_info, clients_info, clientLastDir) == 1)
      {
         return;
      }

      return;
   }

   std::string resolvedDir(resolvedPath);

   if (resolvedDir.find(root) == 0)
   {
      if (chdir(resolvedDir.c_str()) == -1)
      {
         std::cerr << "[-] ERROR: " << strerror(errno) << "\n";

         clients_info.erase(fd_info.fd);
         close(fd_info.fd);
         fd_info.fd = -1;
         return;
      }

      strncpy(msg, "success", strlen("success")+1);
      if (sendAll(sizeof(msg), msg, fd_info, clients_info, clientLastDir) == 1)
      {
         return;
      }

      clientLastDir[fd_info.fd] = resolvedDir;
   }
   else
   {
      strncpy(msg, "You do not have privilege to access this directory", strlen("You do not have privilege to access this directory")+1);
      if (sendAll(sizeof(msg), msg, fd_info, clients_info, clientLastDir) == 1)
      {
         return;
      }
   }

}

int main(int argc, char *argv[]) 
{
   int opt;
   int port_num = -1;
   std::string root = "";
   struct option long_options[] = {
      {"port", required_argument, NULL, 'p'},
      {"root", required_argument, NULL, 'r'},
      {"help", no_argument, NULL, 'h'},
      {0, 0, 0, 0}
   };

   while ((opt = getopt_long(argc, argv, "hp:r:", long_options, NULL)) != -1)
   {
      switch (opt)
      {
         case 'h':
            std::cout << "[+] Usage: ./fileName [OPTIONS]\n"
                      << "[+] Description: Execute command and Return result to the client.\n"
                      << "[+] Options:\n"
                      << "             -h, --help: Display the usage of the program.\n"
                      << "             -p, --port: Specify the port number the server uses to receive connections from clients.\n"
                      << "             -r, --root: Specify the root directory of the Server. The program only allows the client to access files in this directory and its subdirectory.\n"
                      << "[+] Command:\n"
                      << "              1. ls: list all files in the current directory.\n"
                      << "              2. cd: change the current working directory to the subdirectory of the root directory.\n"
                      << "              3. get <filename>: allow the user to download a file or directory named <filename> from the Server.\n"
                      << "              4. put <filename>: allow the user to upload a file or directory named <filename> to the current directory.\n"
                      << "              5. exit: disconnect the client.\n";
            exit(0);
            break;
      
         case 'p':
            port_num = atoi(optarg);
            break;
      
         case 'r':
            root = std::string(optarg);
            if (chdir(root.c_str()) == -1)
            {
               std::cerr << "[-] ERROR: " << strerror(errno) << "\n";
               exit(1);
            }
            break;

         default:
            exit(1);
            break;
      }
   }

   if (port_num == -1)
   {
      std::cerr << "Option -p/--port are required\n";
      exit(1);
   }

   if (root == "")
   {
      std::cerr << "Option -r/--root are required\n";
      exit(1);
   }

   // Create a listening socket
   int listeningSockfd;
   listeningSockfd = socket(AF_INET, SOCK_STREAM, 0);
   if (listeningSockfd < 0) 
   {
      std::cerr << "[-] ERROR: Can't create a socket for listening\n";
      exit(1);
   }
   

   // Bind the IP address and port to a socket
   sockaddr_in serv_addr;
   serv_addr.sin_family = AF_INET;
   serv_addr.sin_port = htons(port_num);
   serv_addr.sin_addr.s_addr = INADDR_ANY;

   if (bind(listeningSockfd, (sockaddr*) &serv_addr, sizeof(serv_addr)) < 0) 
   {
      std::cerr << "[-] ERROR: Can't bind the IP address and port of the server to a socket\n";
      exit(1);
   }

   // Mark this socket is for listening
   if (listen(listeningSockfd, 5) < 0) 
   {
      std::cerr <<"[-] ERROR: Can't mark the socket for listening\n";
      exit(1);
   }
   std::cout << "[*] Start server successfully in " << inet_ntoa(serv_addr.sin_addr) << ":" << ntohs(serv_addr.sin_port) << std::endl;
   
   // List of tracking socket descriptor for reading 
   std::vector<struct pollfd> readfds;
   readfds.push_back({listeningSockfd, POLLIN, 0});

   std::map<int, sockaddr_in> clients_info;
   std::map<int, std::string> clientLastDir;

   char cmdReceiveBuffer[sizeof(box)];
   bzero(cmdReceiveBuffer, SIZE);

   int totalBytesReceived = 0;
   int bytesReceived = 0;

   while (true)
   {
      std::vector<struct pollfd> copy = readfds;
      // Wait until an I/O event occurs 
      std::cout << "i'm Polling\n";
      if (poll(&copy[0], copy.size(), -1) < 0)
      {
         std::cerr << "[-] ERROR: Fail on tracking the client\n";
         exit(1);
      }
      
      /*********************************************************************/
      /* Find the descriptors that ready for reading                       */ 
      /* and determine whether it's the listening or the active connection */
      /*********************************************************************/
      for (int i = 0; i < copy.size(); i++)
      {
         
         // No I/O event occurs at this socket
         if (copy[i].revents == 0)
         {  
            continue;
         } 
         
         // There are ERROR at this socket
         if (copy[i].revents != POLLIN)
         {
            //std::cerr << "[-] ERROR: on fd#" << copy[i].fd << ". revents = " << copy[i].revents << std::endl;
            std::cerr << "[-] ERROR: " << strerror(errno) << "\n";
            clients_info.erase(readfds[i].fd);
            close(readfds[i].fd);
            readfds[i].fd = -1;
            continue;
         }

         // An I/O event occurs at listening socket
         if (copy[i].fd == listeningSockfd)
         {
            // Initilize place for client info
            int newClientSockfd;
            sockaddr_in cli_addr;
            socklen_t cli_len = sizeof(cli_addr);

            // Accept a new connection
            newClientSockfd = accept(listeningSockfd, (struct sockaddr*) &cli_addr, &cli_len);
           
            if (newClientSockfd < 0)
            {
               std::cerr << "[-] ERROR: Can't connect to the " << inet_ntoa(cli_addr.sin_addr) << ":" << ntohs(cli_addr.sin_port) << "\n";
               exit(1);
            }

            // Save the base working directory of client
            clientLastDir.insert(std::make_pair(newClientSockfd, root));

            // Save the info of client
            clients_info.insert(std::make_pair(newClientSockfd, cli_addr));
            std::cout << "[+] New client connect from " << inet_ntoa(cli_addr.sin_addr) << ":" << ntohs(cli_addr.sin_port) << std::endl;

            // Add the new connection to the tracking list  
            readfds.push_back({newClientSockfd, POLLIN, 0});
            continue;
         }

         chdir(clientLastDir[readfds[i].fd].c_str());
         
         // Receive command from client
         if (receiveAll(SIZE, cmdReceiveBuffer, readfds[i], clients_info, clientLastDir) == 1)
         {
            continue;
         }


         if (strcmp(cmdReceiveBuffer, "put") == 0)
         {
            bzero(cmdReceiveBuffer, SIZE);
            putServer(readfds[i], clients_info, clientLastDir);
            continue;
         }

         if (strcmp(cmdReceiveBuffer, "get") == 0)
         {
            bzero(cmdReceiveBuffer, SIZE);
            getServer(readfds[i], clients_info, clientLastDir);
            continue;
         }

         if (strcmp(cmdReceiveBuffer, "ls") == 0)
         {
            bzero(cmdReceiveBuffer, SIZE);
            listServer(readfds[i], clients_info, clientLastDir);
            continue;
         }

         if (strcmp(cmdReceiveBuffer, "cd") == 0)
         {
            bzero(cmdReceiveBuffer, SIZE);
            changeDirServer(root, readfds[i], clients_info, clientLastDir);
            continue;
         }

         if (strcmp(cmdReceiveBuffer, "exit") == 0)
         {
            bzero(cmdReceiveBuffer, SIZE);
            std::cout << "[+] Client from " << inet_ntoa(clients_info[readfds[i].fd].sin_addr) << ":" << ntohs(clients_info[readfds[i].fd].sin_port) << " disconnected\n";
            clients_info.erase(readfds[i].fd);
            clientLastDir.erase(readfds[i].fd);
            close(readfds[i].fd);
            readfds[i].fd = -1;
            continue;
         }

      }
   }
   
   for (int i = 0; i < readfds.size(); i++)
   {
      if (readfds[i].fd > 0)
      {
         close(readfds[i].fd);
      }
   }

   return 0;

}



