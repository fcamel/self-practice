#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>

#include <string>

// Get the path of the executable file of current process.
// This is useful if you want to load files located in the
// same directory of the executable file.
void GetExecutableDirectory(std::string& dir)
{
  const char* exe = "/proc/self/exe";
  char path[1024];
  ssize_t len = readlink(exe, path, sizeof(path));
  if (len == -1) {
    dir = "";
    return;
  }
  path[len] = '\0';

  dir = path;
  size_t pos = dir.rfind('/');
  if (pos != std::string::npos && pos < dir.size()) {
    dir.erase(pos, dir.size() - pos);
  }
}

int main(int argc, char** argv)
{
  char* path = NULL;
  path = get_current_dir_name();
  printf("cwd: %s\n", path);
  free(path);

  printf("argv[0]: %s\n", argv[0]);

  std::string execDir;
  GetExecutableDirectory(execDir);
  printf("binary directory: %s\n", execDir.c_str());

  return 0;
}
