 #include <iostream>
 #include <vector>
 #include "reader_lib/reader.h"
 #include "stack.h"
 #include "executor.h"
 #include <fstream>

 int main () {
     Reader reader{std::ifstream("test.postfix")};
     Stack stack{};
     Executor exe{reader, stack};
     exe.run();

     return 0;
 }