//
// Created by Nazar on 26.11.2024.
//

#ifndef STACK_H
#define STACK_H
#include <string>
#include <vector>


class Stack {
    public:
        void push (const std::pair<std::string, std::string>&);
        std::pair<std::string, std::string>& pop();

    private:
        std::vector<std::pair<std::string, std::string>> stack;
};

#endif //STACK_H
