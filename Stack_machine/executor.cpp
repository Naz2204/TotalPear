#include "executor.h"
#include <iomanip>
#include <iostream>
#include <limits>
#include <utility>
#include <math.h>
#include "reader_lib/reader.h"

Executor::Executor (Reader& reader, Stack& stack): m_reader{reader}, m_stack{stack} {
    m_current_code_place = 0;
    m_old_cout = std::cout.flags();
    std::cout << std::boolalpha;

    // make var table
    for (const auto&[var, type] : m_reader.get_variables()) {
        switch (type) {
            case Reader::Type::INT:
                m_var_table[var] = std::pair(0, oprt::INT);
                break;
            case Reader::Type::REAL:
                m_var_table[var] = std::pair(0.0, oprt::REAL);
                break;
            case Reader::Type::BOOLEAN:
                m_var_table[var] = std::pair(false, oprt::BOOLEAN);
                break;

        }
    }
}

Executor::~Executor () {
    std::cout.flags(m_old_cout);
}

void Executor::run () {
    size_t code_len = m_reader.get_code().size();
    while (m_current_code_place < code_len) {
        auto code_lexeme = m_reader.get_code()[m_current_code_place];
        m_current_code_place++;
        oprt lexeme_type = code_lexeme.first;
        //std::cout << static_cast<std::underlying_type<oprt>::type>(lexeme_type);
        switch (lexeme_type) {
            // pushable
            case oprt::INT:      case oprt::REAL:
            case oprt::BOOLEAN:
            // TODO: use index instead of string
            case oprt::STR:      case oprt::LABEL:
            case oprt::L_VALUE:  case oprt::R_VALUE:
                m_stack.push(std::move(code_lexeme));
                break;

            // in operator
            case oprt::INPUT_INT: case oprt::INPUT_BOOL:
            case oprt::INPUT_FLOAT:
                in(lexeme_type);
                break;

            // out operator
            case oprt::OUT_BOOL:  case oprt::OUT_INT:
            case oprt::OUT_FLOAT: case oprt::OUT_STR:
                out(lexeme_type);
                break;

            // jumps
            case oprt::JMP: case oprt::JF: case oprt::JT:
                jump(lexeme_type);
                break;

            // label declare
            case oprt::LABEL_DECLARE:
                label_declare();
                break;


            // assign
            case oprt::ASSIGN:
                assign();
                break;

            // math unary: UMINUS, NOT
            case oprt::UMINUS: case oprt::NOT:
                calc_unary(lexeme_type);
                break;

            // math binary: PLUS, MINUS, MULTI, DIVIDE, POWER, AND, OR,
            // EQUAL, NOT_EQUAL, BIGGER_EQUAL, LESS_EQUAL, LESS, BIGGER
            default:
                calc_binary(lexeme_type);
                break;

        }

    }
}

void Executor::in_int () const {
    int result = 0;
    std::cin >> result;
    while (not std::cin) {
        std::cin.clear();
        std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
        std::cout << "Incorrect input (expected integer)\nTry again: ";
        std::cin >> result;
    }
    m_stack.push(std::pair(oprt::INT, result));
}

void Executor::in_float () const {
    double result = 0;
    std::cin >> result;

    while (not std::cin) {
        std::cin.clear();
        std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
        std::cout << "Incorrect input (expected float point number)\nTry again: ";
        std::cin >> result;
    }
    m_stack.push(std::pair(oprt::REAL, result));
}

void Executor::in_bool () const {
    std::string result;
    std::cin >> result;

    while (not (result == "true" or result == "false" or result == "yes" or result == "no")) {
        std::cin.clear();
        std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
        std::cout << "Incorrect input (expected bool (true/false, yes/no))\nTry again: ";
        std::cin >> result;
    }
    m_stack.push(std::pair(oprt::BOOLEAN, result == "true" or result == "yes"));
}

void Executor::calc_unary (oprt op) {
    auto right_operand = m_stack.pop();
    Token right_token = std::get<Token>(right_operand);

    auto right_type_value_pair = get_rval(right_token);

    oprt right_type = right_type_value_pair.first;
    std::variant<int, double, bool> right_value = right_type_value_pair.second;

    if (op == oprt::UMINUS) {
        if (right_type == oprt::INT) {
            int result = - get<int>(right_value);
            m_stack.push(std::pair(oprt::INT, result));
        }
        else if (right_type == oprt::REAL) {
            double result = - get<double>(right_value);
            m_stack.push(std::pair(oprt::REAL, result));
        }
        else {
            throw std::runtime_error("Unexpected internal error Unsupported type for unary minus operation");
        }
    } else if (op == oprt::NOT) {
         bool result = !get<bool>(right_value);
         m_stack.push(std::pair(oprt::BOOLEAN, result));
    }else {
        throw std::runtime_error("Unexpected internal error (10)");
    }
}

std::pair<Reader::Operator, std::variant<int, double, bool>> Executor::get_rval(Token right_token) {
    oprt right_type = right_token.first;
    std::variant<int, double, bool> right_value;

    if (right_type == oprt::R_VALUE) {
        auto temp_search = m_var_table.at(std::get<std::string>(right_token.second));
        right_type  = temp_search.second;
        right_value = temp_search.first;
    } else {
        auto& temp_multi = right_token.second;
        if (std::holds_alternative<int>(temp_multi)) {
            right_value = std::get<int>(right_token.second);
        } else if (std::holds_alternative<double>(temp_multi)) {
            right_value = std::get<double>(right_token.second);
        } else if (std::holds_alternative<bool>(temp_multi)) {
            right_value = std::get<bool>(right_token.second);
        } else {
            throw std::runtime_error("Unexpected internal error (15)");
        }
    }
    return std::pair<Reader::Operator, std::variant<int, double, bool>>(right_type, right_value);
}

void Executor::calc_binary (oprt op) {
    auto right_operand = m_stack.pop();
    auto left_operand = m_stack.pop();

    Token right_token = std::get<Token>(right_operand);
    Token left_token = std::get<Token>(left_operand);

    auto right_type_value_pair = get_rval(right_token);
    oprt right_type = right_type_value_pair.first;
    std::variant<int, double, bool> right_value = right_type_value_pair.second;

    auto left_type_value_pair = get_rval(left_token);
    oprt left_type = left_type_value_pair.first;
    std::variant<int, double, bool> left_value = left_type_value_pair.second;

    oprt result_type;

    bool is_same = left_type == right_type;

    switch (op) {
        case oprt::PLUS: {
            if (is_same) {
                if (left_type == oprt::REAL) {
                    double result = get<double>(left_value) + get<double>(right_value);
                    result_type = oprt::REAL;
                    m_stack.push(std::pair(result_type, result));
                }
                else if (left_type == oprt::INT) {
                    int result = get<int>(left_value) + get<int>(right_value);
                    result_type = oprt::INT;
                    m_stack.push(std::pair(result_type, result));
                }
            }
            else {
                double result = 0;
                if (left_type == oprt::REAL) {
                    result = get<double>(left_value) + static_cast<double>(get<int>(right_value));
                }
                else if (left_type == oprt::INT) {
                    result = static_cast<double>(get<int>(left_value)) + get<double>(right_value);
                }
                else {
                    throw std::runtime_error("Unexpected internal error Unsupported type for plus");
                }
                result_type = oprt::REAL;
                m_stack.push(std::pair(result_type, result));
            }
            break;
        }
        case oprt::MINUS: {
            if (is_same) {
                if (left_type == oprt::REAL) {
                    double result = get<double>(left_value) - get<double>(right_value);
                    result_type = oprt::REAL;
                    m_stack.push(std::pair(result_type, result));
                }
                else if (left_type == oprt::INT) {
                    int result = get<int>(left_value) - get<int>(right_value);
                    result_type = oprt::INT;
                    m_stack.push(std::pair(result_type, result));
                }
            }
            else {
                double result = 0;
                if (left_type == oprt::REAL) {
                    result = get<double>(left_value) - static_cast<double>(get<int>(right_value));
                }
                else if (left_type == oprt::INT) {
                    result = static_cast<double>(get<int>(left_value)) - get<double>(right_value);
                }
                else {
                    throw std::runtime_error("Unexpected internal error Unsupported type for minus");
                }
                result_type = oprt::REAL;
                m_stack.push(std::pair(result_type, result));
            }
            break;
        }
        case oprt::MULTI: {
            if (is_same) {
                if (left_type == oprt::REAL) {
                    double result = get<double>(left_value) * get<double>(right_value);
                    result_type = oprt::REAL;
                    m_stack.push(std::pair(result_type, result));
                }
                else if (left_type == oprt::INT) {
                    int result = get<int>(left_value) * get<int>(right_value);
                    result_type = oprt::INT;
                    m_stack.push(std::pair(result_type, result));
                }
            }
            else {
                double result = 0.0;
                if (left_type == oprt::REAL) {
                    result = get<double>(left_value) * static_cast<double>(get<int>(right_value));
                }
                else if (left_type == oprt::INT) {
                    result = static_cast<double>(get<int>(left_value)) * get<double>(right_value);
                }
                else {
                    throw std::runtime_error("Unexpected internal error Unsupported type for multy");
                }
                result_type = oprt::REAL;
                m_stack.push(std::pair(result_type, result));
            }
            break;
        }
        case oprt::DIVIDE: {
            double result = 0;
            result_type = oprt::REAL;
            if (is_same) {
                if (left_type == oprt::REAL) {
                    if (get<double>(right_value) == 0.0) throw std::runtime_error("Divide by zero");
                    result = get<double>(left_value) / get<double>(right_value);
                }
                else if (left_type == oprt::INT) {
                    if (get<int>(right_value) == 0) throw std::runtime_error("Divide by zero");
                    result = static_cast<double>(get<int>(left_value)) / static_cast<double>(get<int>(right_value));
                }
            }
            else {
                if (left_type == oprt::REAL) {
                    if (get<int>(right_value) == 0) throw std::runtime_error("Divide by zero");
                    result = get<double>(left_value) / static_cast<double>(get<int>(right_value));
                }
                else if (left_type == oprt::INT) {
                    if (get<double>(right_value) == 0) throw std::runtime_error("Divide by zero");
                    result = static_cast<double>(get<int>(left_value)) / get<double>(right_value);
                }
                else {
                    throw std::runtime_error("Unexpected internal error Unsupported type for divide");
                }
            }
            m_stack.push(std::pair(result_type, result));
            break;
        }
        case oprt::POWER: {
            double result = 0;
            result_type = oprt::REAL;
            if (is_same) {
                if (left_type == oprt::REAL) {
                    result = pow(get<double>(left_value), get<double>(right_value));
                }
                else if (left_type == oprt::INT) {
                    result = pow(get<int>(left_value), get<int>(right_value));
                }
            } else {
                if (left_type == oprt::REAL) {
                    result = pow(get<double>(left_value), static_cast<double>(get<int>(right_value)));
                }
                else if (left_type == oprt::INT) {
                    result = pow(static_cast<double>(get<int>(left_value)), get<double>(right_value));
                }
                else {
                    throw std::runtime_error("Unexpected internal error Unsupported type for power");
                }
            }
            m_stack.push(std::pair(result_type, result));
            break;
        }
        case oprt::AND: {
            bool result;
            result_type = oprt::BOOLEAN;
            if (is_same and left_type == oprt::BOOLEAN) {
                result = get<bool>(left_value) && get<bool>(right_value);
            }
            else {
                throw std::runtime_error("Unexpected internal error Unsupported type for and");
            }
            m_stack.push(std::pair(result_type, result));
            break;
        }
        case oprt::OR: {
            bool result;
            result_type = oprt::BOOLEAN;
            if (is_same and left_type == oprt::BOOLEAN) {
                result = get<bool>(left_value) || get<bool>(right_value);
            }
            else {
                throw std::runtime_error("Unexpected internal error Unsupported type for or");
            }
            m_stack.push(std::pair(result_type, result));
            break;
        }
        case oprt::BIGGER: {
            bool result = false;
            result_type = oprt::BOOLEAN;
            if (is_same) {
                if (left_type == oprt::REAL) {
                    result = get<double>(left_value) > get<double>(right_value);
                }
                else if (left_type == oprt::INT) {
                    result = get<int>(left_value) > get<int>(right_value);
                }
            }
            else {
                if (left_type == oprt::REAL) {
                    result = get<double>(left_value) > static_cast<double>(get<int>(right_value));
                }
                else if (left_type == oprt::INT) {
                    result = static_cast<double>(get<int>(left_value)) > get<double>(right_value);
                }
                else {
                    throw std::runtime_error("Unexpected internal error Unsupported type for >");
                }
            }
            m_stack.push(std::pair(result_type, result));
            break;
        }
        case oprt::LESS: {
            bool result = false;
            result_type = oprt::BOOLEAN;
            if (is_same) {
                if (left_type == oprt::REAL) {
                    result = get<double>(left_value) < get<double>(right_value);
                }
                else if (left_type == oprt::INT) {
                    result = get<int>(left_value) < get<int>(right_value);
                }
            }
            else {
                if (left_type == oprt::REAL) {
                    result = get<double>(left_value) < static_cast<double>(get<int>(right_value));
                }
                else if (left_type == oprt::INT) {
                    result = static_cast<double>(get<int>(left_value)) < get<double>(right_value);
                }
                else {
                    throw std::runtime_error("Unexpected internal error Unsupported type for <");
                }
            }
            m_stack.push(std::pair(result_type, result));
            break;
        }
        case oprt::BIGGER_EQUAL: {
            bool result = false;
            result_type = oprt::BOOLEAN;
            if (is_same) {
                if (left_type == oprt::REAL) {
                    result = get<double>(left_value) >= get<double>(right_value);
                }
                else if (left_type == oprt::INT) {
                    result = get<int>(left_value) >= get<int>(right_value);
                }
            }
            else {
                if (left_type == oprt::REAL) {
                    result = get<double>(left_value) >= static_cast<double>(get<int>(right_value));
                }
                else if (left_type == oprt::INT) {
                    result = static_cast<double>(get<int>(left_value)) >= get<double>(right_value);
                }
                else {
                    throw std::runtime_error("Unexpected internal error Unsupported type for >=");
                }
            }
            m_stack.push(std::pair(result_type, result));
            break;
        }
        case oprt::LESS_EQUAL: {
            bool result = false;
            result_type = oprt::BOOLEAN;
            if (is_same) {
                if (left_type == oprt::REAL) {
                    result = get<double>(left_value) <= get<double>(right_value);
                }
                else if (left_type == oprt::INT) {
                    result = get<int>(left_value) <= get<int>(right_value);
                }
            }
            else {
                if (left_type == oprt::REAL) {
                    result = get<double>(left_value) <= static_cast<double>(get<int>(right_value));
                }
                else if (left_type == oprt::INT) {
                    result = static_cast<double>(get<int>(left_value)) <= get<double>(right_value);
                }
                else {
                    throw std::runtime_error("Unexpected internal error Unsupported type for <=");
                }
            }
            m_stack.push(std::pair(result_type, result));
            break;
        }
        case oprt::EQUAL: {
            bool result = false;
            result_type = oprt::BOOLEAN;
            if (is_same) {
                if (left_type == oprt::REAL) {
                    result = get<double>(left_value) == get<double>(right_value);
                }
                else if (left_type == oprt::INT) {
                    result = get<int>(left_value) == get<int>(right_value);
                }
                else if (left_type == oprt::BOOLEAN) {
                    result = get<bool>(left_value) == get<bool>(right_value);
                }
            }
            else {
                if (left_type == oprt::REAL) {
                    result = get<double>(left_value) == static_cast<double>(get<int>(right_value));
                }
                else if (left_type == oprt::INT) {
                    result = static_cast<double>(get<int>(left_value)) == get<double>(right_value);
                }
                else {
                    throw std::runtime_error("Unexpected internal error Unsupported type for ==");
                }
            }
            m_stack.push(std::pair(result_type, result));
            break;
        }
        case oprt::NOT_EQUAL: {
            bool result = false;
            result_type = oprt::BOOLEAN;
            if (is_same) {
                if (left_type == oprt::REAL) {
                    result = get<double>(left_value) != get<double>(right_value);
                }
                else if (left_type == oprt::INT) {
                    result = get<int>(left_value) != get<int>(right_value);
                }
                else if (left_type == oprt::BOOLEAN) {
                    result = get<bool>(left_value) != get<bool>(right_value);
                }
            }
            else {
                if (left_type == oprt::REAL) {
                    result = get<double>(left_value) != static_cast<double>(get<int>(right_value));
                }
                else if (left_type == oprt::INT) {
                    result = static_cast<double>(get<int>(left_value)) != get<double>(right_value);
                }
                else {
                    throw std::runtime_error("Unexpected internal error Unsupported type for !=");
                }
            }
            m_stack.push(std::pair(result_type, result));
            break;
        }
    }
}

void Executor::label_declare () {
    auto& label_table = m_reader.get_labels();
    auto jump_label = m_stack.pop();
}

void Executor::in (oprt in_type) {
    switch (in_type) {
        case oprt::INPUT_INT:
            in_int();
            return;
        case oprt::INPUT_FLOAT:
            in_float();
            return;
        case oprt::INPUT_BOOL:
            in_bool();
            return;
        default:
            throw std::runtime_error("Unexpected internal error (2)");
    }
}

void Executor::out (oprt out_type) {
    auto multi_opt = m_stack.pop();

    if (std::holds_alternative<int>(multi_opt)) {
        std::cout << std::get<int>(multi_opt);
    } else if (std::holds_alternative<Token>(multi_opt)) {
        Token buf = std::get<Token>(multi_opt);

        if (buf.first == oprt::R_VALUE) {
            auto temp = get_rval(buf);
            buf.first = temp.first;
            switch (temp.second.index()) {
                case 0:
                    buf.second = std::get<int>(temp.second);
                    break;
                case 1:
                    buf.second = std::get<double>(temp.second);
                    break;
                case 2:
                    buf.second = std::get<bool>(temp.second);
                    break;
            }
        }

        switch (buf.first) {
            case oprt::INT:
                std::cout << std::get<int>(buf.second) << std::flush;
                break;
            case oprt::REAL:
                std::cout << std::get<double>(buf.second) << std::flush;
                break;
            case oprt::BOOLEAN:
                std::cout << std::get<bool>(buf.second) << std::flush;
                break;
            case oprt::STR:
                std::cout << std::get<std::string>(buf.second) << std::flush;
                break;
            default:
                throw std::runtime_error("Unexpected internal error (Unsupported type for out)");

        }

    } else {
        throw std::runtime_error("Unexpected internal error (1)");
    }
}

void Executor::jump (oprt jump_type) {
    auto& label_table = m_reader.get_labels();
    auto jump_label = m_stack.pop();

    // --- Check conditional of JMP
    ////std::cout << "\nPizza: " << static_cast<std::underlying_type<oprt>::type>(jump_type) << "||\n";

    if (jump_type != oprt::JMP) {
        auto logical_expr = m_stack.pop();
        auto logical_token = std::get<Token>(logical_expr);
        bool logical_value = false;
        if (logical_token.first == oprt::R_VALUE) {
            auto temp = get_rval(logical_token);
            if (not std::holds_alternative<bool>(temp.second)) throw std::runtime_error("Unexpected internal error (13)");
            logical_value = std::get<bool>(temp.second);
        } else {
            if (not std::holds_alternative<bool>(logical_token.second)) throw std::runtime_error("Unexpected internal error (3)");
            logical_value = std::get<bool>(logical_token.second);
        }


        if (jump_type == oprt::JT and not logical_value) {
            return;
        } else if (jump_type == oprt::JF and logical_value) { // JF
            return;
        }
    }

    // --- Do jump

    if (std::get<Token>(jump_label).first != oprt::LABEL) {
        throw std::runtime_error("Unexpected internal error (4)");
    }

    auto token = std::get<Token>(jump_label).second;
    auto place_to_go_iter = label_table.find(std::get<std::string>(token));
    if (place_to_go_iter == label_table.end()) throw std::runtime_error("Unexpected internal error (5)");

    m_current_code_place = place_to_go_iter->second;
}

void Executor::assign () {
    auto right_operand = m_stack.pop();
    auto left_operand  = m_stack.pop();


    // ---

    Token left_token  = std::get<Token>(left_operand);
    Token right_token = std::get<Token>(right_operand);

    if (left_token.first != oprt::L_VALUE or
        not std::holds_alternative<std::string>(left_token.second) or
        not m_var_table.contains(std::get<std::string>(left_token.second))) {
        throw std::runtime_error("Unexpected internal error (6)");
    }

    // ---
    //FIXME тут похоже шо right_type заходить на перевірку неініцілізованим можливо треба замінити на right_token.first
    oprt right_type;
    std::variant<int, double, bool> right_value;
    if (right_type == oprt::R_VALUE) {
        auto temp_search = m_var_table.at(std::get<std::string>(right_token.second));
        right_type  = temp_search.second;
        right_value = temp_search.first;
    } else {
        right_type  = right_token.first;
        auto& temp_multi = right_token.second;
        if (std::holds_alternative<int>(temp_multi)) {
            right_value = std::get<int>(right_token.second);
        } else if (std::holds_alternative<double>(temp_multi)) {
            right_value = std::get<double>(right_token.second);
        } else if (std::holds_alternative<bool>(temp_multi)) {
            right_value = std::get<bool>(right_token.second);
        } else {
            throw std::runtime_error("Unexpected internal error (7)");
        }
    }

    std::string& left_var_str = std::get<std::string>(left_token.second);
    oprt left_type = m_var_table[left_var_str].second;

    bool is_same = left_type == right_type;
    bool is_float_to_int = left_type == oprt::INT  and right_type == oprt::REAL;
    bool is_int_to_float = left_type == oprt::REAL and right_type == oprt::INT;

    if (not (is_same or is_float_to_int or is_int_to_float)) {
        throw std::runtime_error("Unexpected internal error (8)");
    }

    // ---

    if (is_same) {
        m_var_table[left_var_str].first = right_value;
    } else if (is_float_to_int) {
        m_var_table[left_var_str].first = static_cast<int>(std::get<double>(right_value));
        m_var_table[left_var_str].first = static_cast<int>(std::get<double>(right_value));
    } else { // int_to_float
        m_var_table[left_var_str].first = static_cast<double>(std::get<int>(right_value));
    }
}
