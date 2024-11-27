#include "stack.h"

Stack::Stack() {
    m_stack.reserve(100);
}

void Stack::push(code_entry&& entry) {
    m_stack.emplace_back(std::move(entry));
}

Stack::code_entry Stack::pop() {
    if (m_stack.size() == 0) throw std::runtime_error("Exhausted stack");

    auto result = m_stack.back();
    m_stack.pop_back();
    return result;
}
