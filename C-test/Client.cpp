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
#include <getopt.h>
#include <math.h>
#include <map>
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

int sendAll(size_t size, char* src, int sockfd)
{
   int totalBytesSent = 0;
   int bytesSent = 0;

   while (totalBytesSent < size)
   {
      bytesSent = write(sockfd, src + totalBytesSent, size - totalBytesSent);

      if (bytesSent < 0)
      {
         std::cerr << "[-] ERROR: " << strerror(errno) << "\n";
         close(sockfd);
         std::cout << "[+] Disconnected the server\n";
         return 1;
      }
      else if (bytesSent == 0)
      {
         close(sockfd);
         std::cout << "[+] Server disconnected\n";
         return 1;
      }

      totalBytesSent += bytesSent;
   }

   return 0;
}

int receiveAll(size_t size, char* dest, int sockfd)
{
   int totalBytesReceived = 0;
   int bytesReceived = 0;
   
   while (totalBytesReceived < size)
   {
      bytesReceived = read(sockfd, dest + totalBytesReceived, size - totalBytesReceived);

      if (bytesReceived < 0)
      {
         std::cerr << "[-] ERROR: " << strerror(errno) << "\n";
         close(sockfd);
         std::cout << "[+] Disconnected the server\n";
         return 1;
      }
      else if (bytesReceived == 0)
      {
         close(sockfd);
         std::cout << "[+] Server disconnected\n";
         return 1;
      }

      totalBytesReceived += bytesReceived;
   }

   return 0;
}

void send_file_name_of_get_command(std::string fileName, int sockfd)
{
   char msg[sizeof(box)];
   bzero(msg, sizeof(msg));

   strncpy(msg, fileName.c_str(), fileName.size()+1);

   if (sendAll(sizeof(msg), msg, sockfd) == 1)
   {
      return;
   }
}

void sendFile(std::string fileName, int sockfd)
{
   FILE* f = fopen(fileName.c_str(), "rb");
   if (f == NULL)
   {
      std::cerr << "[-] ERROR: Can't open filename " << fileName << "\n";
      std::cerr << "[-] ERROR: " << strerror(errno) << "\n";
      close(sockfd);
      fclose(f);
      exit(1);
   }

   char sendBuffer[SIZE];
   bzero(sendBuffer, sizeof(sendBuffer));

   int bytesToSend = -1;
   int bytesReadFromFile = -1;
   
   while ((bytesReadFromFile = fread(sendBuffer, 1, SIZE, f)) > 0)
   {
      bytesToSend = std::min(bytesReadFromFile, SIZE);

      if (sendAll(bytesToSend, sendBuffer, sockfd) == 1)
      {
         return;
      }
      
      bzero(sendBuffer, SIZE);
      
   }

   fclose(f);

   
}

int sendDir(std::string fileName, int sockfd)
{  
   char msg[sizeof(box)];
   box sender;

   bzero(&sender, sizeof(box));
   bzero(msg, sizeof(msg));

   // Get the current working directory
   char begin_cwd[PATH_MAX];
   getcwd(begin_cwd, PATH_MAX);

   // Get the information of the file including file type and file size
   struct stat fileInfo;
   if (stat(fileName.c_str(), &fileInfo) == -1)
   {
      
      std::cerr << "[-] ERROR: " << strerror(errno) << "\n";
      
      strncpy(msg, strerror(errno), strlen(strerror(errno))+1);
      if (sendAll(sizeof(msg), msg, sockfd) == 1)
      {
         return 1;
      }
      return 1;
   }

   else
   {
      strncpy(msg, "success", strlen("success")+1);

      if (sendAll(sizeof(msg), msg, sockfd) == 1)
      {
         return 1;
      }
   }

   if (S_ISREG(fileInfo.st_mode))
   {
      sender.fileType = File;
      sender.fileSize = fileInfo.st_size;
      strncpy(sender.data, fileName.c_str(), fileName.size()+1);
      memcpy(msg, &sender, sizeof(box));

      if (sendAll(sizeof(msg), msg, sockfd) == 1)
      {
         return 1;
      }

      sendFile(fileName, sockfd);

      bzero(msg, sizeof(msg));
      bzero(&sender, sizeof(box));

      return 0;
   }
   else // Case: the file is Directory
   {

      sender.fileType = Dir;
      sender.fileSize = fileInfo.st_size;
      strncpy(sender.data, fileName.c_str(), fileName.size()+1);
      memcpy(msg, &sender, sizeof(box));

      if (sendAll(sizeof(msg), msg, sockfd) == 1)
      {
         return 1;
      }


      DIR* dir = opendir(fileName.c_str());
      if (dir == NULL)
      {
         
         std::cerr << "[-] ERROR: " << strerror(errno) << "\n";
        
         closedir(dir);
         
         return 1;
      }

      chdir(fileName.c_str());

      struct dirent* entry;
      int loopFlag = -1;
      while ((entry = readdir(dir)) != NULL)
      {
         if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0)
         {  
            continue;
         }
         
         loopFlag = 1;

         if (sendAll(sizeof(int), (char*)&loopFlag, sockfd) == 1)
         {
            return 1;
         }
         
         if (sendDir(std::string(entry->d_name), sockfd) == 1)
         {
            return 1;
         }
      }

      loopFlag = 0;
      if (sendAll(sizeof(int), (char*)&loopFlag, sockfd) == 1)
      {
         return 1;
      }

      chdir(begin_cwd);
      closedir(dir);
      return 0;
   }

}

void writeFile(int sockfd, std::string fileName, unsigned long long fileSize)
{  
   unsigned long long bytesLeftToReceive = fileSize;

   char cwd[PATH_MAX];
   getcwd(cwd, PATH_MAX);

   std::string newName = std::string(cwd) + "/copy_" + std::string(fileName);
   
   FILE* f = fopen(newName.c_str(), "wb");
   if (f == NULL)
   {
      std::cerr << "[-] ERROR: Can't create new file\n";
      std::cerr << "[-] ERROR: " << strerror(errno) << "\n";
      fclose(f);
      exit(1);
   }

   char receiveBuffer[SIZE];
   bzero(receiveBuffer, sizeof(receiveBuffer));

   int bytesToReceive = -1;
   
   while(bytesLeftToReceive > 0)
   {
      bytesToReceive = std::min<unsigned long long>(bytesLeftToReceive, SIZE);
      
      if (receiveAll(bytesToReceive, receiveBuffer, sockfd) == 1)
      {
         return;
      }

      fwrite(receiveBuffer, 1, bytesToReceive, f);

      bzero(receiveBuffer, SIZE);

      bytesLeftToReceive = bytesLeftToReceive - bytesToReceive;

   }

   fclose(f);

   
}

int writeDir(int sockfd)
{

   char msg[sizeof(box)];
   box receiver;

   bzero(&receiver, sizeof(box));
   bzero(msg, sizeof(msg));
   
   if (receiveAll(sizeof(msg), msg, sockfd) == 1)
   {
      return 1;
   }

   if (strcmp(msg, "success") != 0)
   {
      printf("[-] ERROR: %s\n", msg);
      return 1;
   }
   
   
   bzero(msg, sizeof(msg));

   if (receiveAll(sizeof(msg), msg, sockfd) == 1)
   {
      return 1;
   }

   memcpy(&receiver, msg, sizeof(box));
   
   if (receiver.fileType == File)
   {
      
      writeFile(sockfd, std::string(receiver.data), receiver.fileSize);

      bzero(&receiver, sizeof(box));
      bzero(msg, sizeof(msg));

      return 0;
   }
   else // Case the file is Directory
   {
      
      char beginCWD[PATH_MAX];
      getcwd(beginCWD, PATH_MAX);

      std::string newdirName = "copy_" + std::string(receiver.data);

      mkdir(newdirName.c_str(), 0777);
      
      chdir(newdirName.c_str());

      int loopFlag = -1; 

      if (receiveAll(sizeof(int), (char*)&loopFlag, sockfd) == 1)
      {
         return 1;
      }

      while (loopFlag == 1)
      {
         if (writeDir(sockfd) == 1)
         {
            return 1;
         }

         if (receiveAll(sizeof(int), (char*)&loopFlag, sockfd) == 1)
         {
            return 1;
         }

      }

      chdir(beginCWD);

      return 0;
   }
}

void putClient(std::string fileName, int sockfd)
{
   std::cout << "[+] Wait ...\n";
   if (sendDir(fileName, sockfd) == 1)
   {
      std::cout << "[-] ERROR: Fail to upload " << fileName << "\n";
      return;
   }
   std::cout << "[+] Upload " << fileName << " 100%\n";
}

void getClient(std::string fileName, int sockfd)
{
   std::cout << "[+] Wait ...\n";

   send_file_name_of_get_command(fileName, sockfd);

   if (writeDir(sockfd) == 1)
   {
      std::cout << "[-] ERROR: Fail to download " << fileName << "\n";
      return;
   }

   std::cout << "[+] Download " << fileName << " 100%\n";
}

void listClient(int sockfd)
{

   int bytesLeftToReceive = 0;

   if (receiveAll(sizeof(int), (char*)&bytesLeftToReceive, sockfd) == 1)
   {
      return;
   }

   char receiveBuffer[SIZE];
   bzero(receiveBuffer, SIZE);

   int bytesToReceive = -1;
   while (bytesLeftToReceive > 0)
   {
      bytesToReceive = std::min(SIZE, bytesLeftToReceive);

      if (receiveAll(bytesToReceive, receiveBuffer, sockfd) == 1)
      {
         return;
      }

      std::cout << std::string(receiveBuffer, 0, bytesToReceive);

      bzero(receiveBuffer, SIZE);

      bytesLeftToReceive = bytesLeftToReceive - bytesToReceive;
   }

}

void changeDirClient(std::string dirName, int sockfd)
{
   char msg[sizeof(box)];
   box sender;

   bzero(&sender, sizeof(box));
   bzero(msg, sizeof(msg));

   sender.fileType = Dir;
   sender.fileSize = dirName.size() + 1;
   strncpy(sender.data, dirName.c_str(), sender.fileSize);

   memcpy(msg, &sender, sizeof(box));

   if (sendAll(sizeof(msg), msg, sockfd) == 1)
   {
      return;
   }

   bzero(msg, sizeof(msg));

   if (receiveAll(sizeof(msg), msg, sockfd) == 1)
   {
      return;
   }

   if (strcmp(msg, "success") != 0)
   {
      printf("[-] ERROR: %s\n", msg);
   }
   
}

int main(int argc, char *argv[])
{  
   int opt;
   int port_num = -1;
   std::string ip = "";
   struct option long_options[] = {
      {"port", required_argument, NULL, 'p'},
      {"ip", required_argument, NULL, 'i'},
      {"help", no_argument, NULL, 'h'},
      {0, 0, 0, 0}
   };

   while ((opt = getopt_long(argc, argv, "hp:i:", long_options, NULL)) != -1)
   {
      switch (opt)
      {
         case 'h':
            std::cout << "[+] Usage: ./fileName [OPTIONS]\n"
                      << "[+] Description: Execute command and Return result to the client.\n"
                      << "[+] Options:\n"
                      << "             -h, --help: Display the usage of the program.\n"
                      << "             -p, --port: Specify the port number the server uses to receive connections from clients.\n"
                      << "             -i, --ip: Specify the ip address of the Server that the client uses to send request.\n"
                      << "[+] Command:\n"
                      << "              1. ls: list all files in the current directory.\n"
                      << "              2. cd: change the current working directory to the subdirectory of the root directory.\n"
                      << "              3. get <filename>: download a file or directory named <filename> from the Server and store at the current working directory.\n"
                      << "              4. put <filename>: upload a file or directory named <filename> to the current directory at the server side.\n"
                      << "              5. exit: allow the user to end the program.\n";
              
            exit(0);
            break;

         case 'p':
            port_num = atoi(optarg);
            break;
         
         case 'i':
            ip = std::string(optarg);
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

   if (ip == "")
   {
      std::cerr << "Option -i/--ip are required\n";
      exit(1);
   }

   // Get info of server
   struct addrinfo hint, *p;

   bzero(&hint, sizeof(struct addrinfo));
   hint.ai_family = AF_INET;
   hint.ai_socktype = SOCK_STREAM;
   hint.ai_protocol = 0;
   hint.ai_flags = 0;
   
   int s = getaddrinfo(ip.c_str(), std::to_string(port_num).c_str(), &hint, &p);
   
   if (s != 0)
   {
      std::cerr << "[-] ERROR: " << gai_strerror(s) << "\n";
      exit(1);
   }
   
   // Creat a socket
   int sockfd = socket(AF_INET, SOCK_STREAM, 0);
   if (sockfd < 0) 
   {
      std::cerr << "[-] Error: Can't create a socket\n";
      exit(1);
   }
   
   // Get the server info 
   sockaddr *serv_addr;
   bool connect_flag = false;
   for (p; p != NULL; p = p->ai_next)
   {
      serv_addr = p->ai_addr;

      // Connect to server
      if (connect(sockfd, serv_addr, p->ai_addrlen) != -1)
      {  connect_flag = true;
         
         break; // connect successfully
      }
   }
   
   if (!connect_flag)
   {
      std::cerr << "[-] ERROR: Can't connect to the server\n";
      exit(1);
   }



   // Send and receive data from the server
   std::string userInput;

   char cmdSendBuffer[SIZE];
   bzero(cmdSendBuffer, SIZE);


   do
   {
      // Promt the user for message
      std::cout << ">";
      getline(std::cin, userInput);

      if (userInput.size() == 0)
      {
         continue;
      }

      // Send the cmd to the server
      std::stringstream ss(userInput);
      std::string cmd, arg = {"", ""};

      ss >> cmd;
      strncpy(cmdSendBuffer, cmd.c_str(), cmd.size()+1);

      if (cmd == "put")
      {
         
         ss >> arg;
         
         if (arg == "")
         {
            std::cout << "[-] The \"put\" command requires an argument - file name\n";
            continue;
         }

         if (sendAll(SIZE, cmdSendBuffer, sockfd) == 1)
         {
            exit(1);
         }

         bzero(cmdSendBuffer, SIZE);

         putClient(arg, sockfd);

      }

      else if (cmd == "get")
      {

         ss >> arg;

         if (arg == "")
         {
            std::cout << "[-] The \"get\" command requires an argument - file name\n";
            continue;
         }

         if (sendAll(SIZE, cmdSendBuffer, sockfd) == 1)
         {
            exit(1);
         }
         
         bzero(cmdSendBuffer, SIZE);

         getClient(arg, sockfd);

      }

      else if (cmd == "ls")
      {
         ss >> arg;
         if (arg != "")
         {
            std::cout << "[-] The \"ls\" command doesn't require argument\n";
            continue;
         }

         if (sendAll(SIZE, cmdSendBuffer, sockfd) == 1)
         {
            exit(1);
         }

         bzero(cmdSendBuffer, SIZE);

         listClient(sockfd);

      }

      else if (cmd == "cd")
      {
         ss >> arg;

         if (sendAll(SIZE, cmdSendBuffer, sockfd) == 1)
         {
            exit(1);
         }

         bzero(cmdSendBuffer, SIZE);

         changeDirClient(arg, sockfd);
         
      }
      else if (cmd == "exit")
      {
         ss >> arg;
         if (arg != "")
         {
            std::cout << "[-] The \"exit\" command doesn't require argument\n";
            continue;
         }

         if (sendAll(SIZE, cmdSendBuffer, sockfd) == 1)
         {
            exit(1);
         }

         bzero(cmdSendBuffer, SIZE);

         return 0;

      }

      else
      {
         printf("[-] Unsupported Command\n");
      }

   } while (true);

   // Close the socket
   close(sockfd);

   return 0;

}