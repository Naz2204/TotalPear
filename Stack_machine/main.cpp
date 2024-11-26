#include <iostream>
#include <vector>
#include "reader.h"
#include <fstream>

int main () {
    Reader r(std::ifstream("test.postfix"));

    return 0;
}
