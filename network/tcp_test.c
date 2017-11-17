#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <arpa/inet.h>
#include <netinet/tcp.h>
#include <unistd.h>
#include <stdbool.h>
#include <stdlib.h>
#include <errno.h>
#include <math.h>

#define ERROR() {\
  printf("error: line %d: %s (%d)\n", __LINE__, strerror(errno), errno);\
  exit(1);\
}

#define VERBOSE

typedef struct Config {
  bool no_delay;
  bool quickack;
  bool cork;
  bool msg_more;
} Config;

void help(char *prog) {
  printf("%s <is_server> <ip:port> <config>\n", prog);
}

/* Example of config:

no_delay 0
quickack 0
cork 0
msg_more 0
send 1000
n_chunk 100
round 100
*/
int parse_config(char* filename, Config* config, int* send_bytes, int* n_chunk, int* round) {
  if (!filename || !config || !send_bytes || !n_chunk || !round)
    return 0;

  FILE* fr = fopen(filename, "r");
  if (!fr) {
    printf("Failed to read file: %s\n", filename);
    return 0;
  }

  char buf[1024];
  char key[1024];
  int value = 0;
  while (1) {
    if (!fgets(buf, sizeof(buf), fr))
      return 1;

    if (sscanf(buf, "%s%d", key, &value) == 2) {
      if (strcmp(key, "no_delay") == 0) {
        config->no_delay = value;
      } else if (strcmp(key, "quickack") == 0) {
        config->quickack = value;
      } else if (strcmp(key, "cork") == 0) {
        config->cork = value;
      } else if (strcmp(key, "msg_more") == 0) {
        config->msg_more = value;
      } else if (strcmp(key, "send") == 0) {
        *send_bytes = value;
      } else if (strcmp(key, "n_chunk") == 0) {
        *n_chunk = value;
      } else if (strcmp(key, "round") == 0) {
        *round = value;
      } else {
        printf("Skip unknown key: %s\n", key);
      }
    } else {
      printf("Invalid format: %s\n", buf);
      return 1;
    }
  }

  fclose(fr);
  return 1;
}

void show_mss(int sock) {
  int value = -1;
  int length = sizeof(value);
  if (getsockopt(sock, IPPROTO_TCP, TCP_MAXSEG, &value, &length) == -1)
    ERROR();
  printf("MSS=%d\n", value);
}

void config_socket(int sock, Config config) {
  show_mss(sock);

  int value = config.no_delay ? 1 : 0;
  if (setsockopt(sock, IPPROTO_TCP, TCP_NODELAY, &value, sizeof(value)) == -1)
    ERROR();

  value = config.quickack ? 1 : 0;
  if (setsockopt(sock, IPPROTO_TCP, TCP_QUICKACK, &value, sizeof(value)) == -1)
    ERROR();

  value = config.cork ? 1 : 0;
  if (setsockopt(sock, IPPROTO_TCP, TCP_CORK, &value, sizeof(value)) == -1)
    ERROR();
}

// Let data = |bytes| - 1 '0' and one '1'.
// Split |data| into |n_chunk| chunks and send each chunk separatedly. into |n_chunk| chunks and send each chunk separatedly.
void send_data(int sock, Config config, int bytes, int n_chunk) {
#ifdef VERBOSE
  printf("send_data: will send %d bytes in %d chunks\n", bytes, n_chunk);
#endif

  if (bytes <= 0)
    return;

  int base = (int)ceil(bytes / (float)n_chunk);
  char* buf = (char*)malloc(base);
  memset(buf, '0', base);
  int flag = config.msg_more ? MSG_MORE : 0;
  while (bytes > base) {
    int sent = send(sock, buf, base, flag);
    if (sent == -1)
      ERROR();
    bytes -= sent;
  }
  buf[bytes - 1] = '1';
  if (send(sock, buf, bytes, 0) == -1)
    ERROR();

  free(buf);
}

bool recv_data(int sock) {
  while (true) {
    char buf[1024];
    int n = recv(sock, buf, sizeof(buf) , 0);

#ifdef VERBOSE
    printf("recv %d bytes, the last byte is %c\n", n, n > 0 ? buf[n - 1] : ' ');
#endif

    if (n < 0)
      ERROR();

    if (n == 0)
      return false;

    if (buf[n - 1] == '1') {
      return true;
    }
  }
}

// Send data |round| rounds. In each ruond, send |send_bytes| - 1 '0' and one '1'.
// In each round, split the data into |n_chunk| chunks and send them separatedly.
void do_server(char* ip, int port, Config config, int send_bytes, int n_chunk, int round) {
  int server_socket = socket(AF_INET , SOCK_STREAM , 0);
  if (server_socket == -1)
    ERROR();

  config_socket(server_socket, config);

  struct sockaddr_in server_addr;
  server_addr.sin_family = AF_INET;
  server_addr.sin_addr.s_addr = INADDR_ANY;
  server_addr.sin_port = htons(port);

  if (setsockopt(server_socket, SOL_SOCKET, SO_REUSEADDR, &(int){1}, sizeof(int)) == -1)
    ERROR();

  if (bind(server_socket, (struct sockaddr *)&server_addr , sizeof(server_addr)) < 0)
    ERROR();

  listen(server_socket , 1);

  struct sockaddr_in client_addr;
  int size = sizeof(client_addr);
  int client_socket = accept(server_socket, (struct sockaddr *)&client_addr, (socklen_t*)&size);
  if (client_socket < 0)
    ERROR();

  show_mss(client_socket);

  struct timeval begin, end;
  gettimeofday(&begin, NULL);
  for (int i = 0; i < round; i++) {
    send_data(client_socket, config, send_bytes, n_chunk);
    recv_data(client_socket);
  }
  gettimeofday(&end, NULL);
  double seconds = (end.tv_sec - begin.tv_sec) + (end.tv_usec - begin.tv_usec) / 1e6;
  printf("server: send + recv time in seconds: %.3f\n", seconds);

  show_mss(client_socket);

  close(server_socket);
}

// Keep receiving data. After receiving '1', send |send_bytes| - 1 '0' and 1 '1' to the server.
void do_client(char* ip, int port, Config config, int send_bytes, int n_chunk) {
  int client_socket = socket(AF_INET, SOCK_STREAM , 0);
  if (client_socket == -1)
    ERROR();

  config_socket(client_socket, config);

  struct sockaddr_in server_addr;
  server_addr.sin_addr.s_addr = inet_addr(ip);
  server_addr.sin_family = AF_INET;
  server_addr.sin_port = htons(port);

  if (connect(client_socket, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
    printf("ip=%s, port=%d", ip, port);
    ERROR();
  }

  struct timeval begin, end;
  gettimeofday(&begin, NULL);
  while (recv_data(client_socket)) {
    send_data(client_socket, config, send_bytes, n_chunk);
  }
  gettimeofday(&end, NULL);
  double seconds = (end.tv_sec - begin.tv_sec) + (end.tv_usec - begin.tv_usec) / 1e6;
  printf("client: recv + send time in seconds: %.3f\n", seconds);

  close(client_socket);
}

int main(int argc, char *argv[]) {
  if (argc != 4) {
    help(argv[0]);
    return 0;
  }

  bool is_server = atoi(argv[1]);
  char ip[1024] = {0};
  int port = 0;
  char tmp[1024];
  strcpy(tmp, argv[2]);
  strcpy(ip, strtok(tmp, ":"));
  port = atoi(strtok(NULL, ":"));

  int send_bytes = 0;
  int n_chunk = 0;
  int round = 0;
  Config config;
  if (!parse_config(argv[3], &config, &send_bytes, &n_chunk, &round)) {
    help(argv[0]);
    return 1;
  }

  printf("server=%s:%d, pid=%d\n", ip, port, getpid());
  printf("config: no_delay=%d, quickack=%d, cork=%d, msg_more=%d, send=%d %d %d\n\n",
         config.no_delay, config.quickack, config.cork, config.msg_more, send_bytes, n_chunk, round);

  if (is_server) {
    do_server(ip, port, config, send_bytes, n_chunk, round);
  } else {
    do_client(ip, port, config, send_bytes, n_chunk);
  }

  return 0;
}
