#ifndef STACK_H
#define STACK_H

#include <optional>
#include <vector>
#include "reader.h"

class Stack {
public:
    using code_entry = std::variant<int, std::pair<Reader::Operator, Reader::Multi_type>>;

    Stack ();

    void push (code_entry&& entry);
    code_entry pop();

private:
    std::vector<code_entry> m_stack;
};

#endif //STACK_H
