#ifndef READER_H
#define READER_H


#include <fstream>
#include <list>
#include <vector>
#include <map>
#include <variant>
/*
    OP_UMINUS            = "op_uminus",            "uminus"
    OP_INPUT_INT         = "op_input_in",          "input_in"
    OP_INPUT_FLOAT       = "op_input_float",       "input_float"
    OP_INPUT_BOOL        = "op_input_bool",        "input_bool"
    OP_OUT_STR           = "op_out_str",           "out_str"
    OP_OUT_INT           = "op_out_int",           "out_int"
    OP_OUT_FLOAT         = "op_out_float",         "out_float"
    OP_OUT_BOOL          = "op_out_bool",          "out_bool"
    OP_JMP               = "op_jmp",               "jmp"
    OP_JT                = "op_jt",                "jt"
    OP_JF                = "op_jf",                "jf"

    OP_ASSIGN = "op_assign", "="
    OP_PLUS = "op_plus", "+"
    OP_MINUS = "op_minus", "-"
    OP_MULTI = "op_multi", "*"
    OP_DIVIDE = "op_divide", "/"
    OP_POWER = "op_power", "^"

    # Logical
    OP_AND = "op_and", "and"
    OP_OR = "op_or", "or"
    OP_NOT = "op_not", "not"

    # Comparison
    OP_EQUAL = "op_equal", "=="
    OP_NOT_EQUAL = "op_not_equal", "!="
    OP_BIGGER_EQUAL = "op_bigger_equal", ">="
    OP_LESS_EQUAL = "op_less_equal", "<="
    OP_LESS = "op_less", "<"
    OP_BIGGER = "op_bigger", ">"

 */


class Reader {
public:
    enum class Operator  {
        L_VALUE       = 0,
        R_VALUE       = 1,
        LABEL         = 2,
        INT           = 3,
        REAL          = 4,
        STR           = 5,
        BOOLEAN       = 6,

        LABEL_DECLARE = 7,

        INPUT_INT     = 8,
        INPUT_FLOAT   = 9,
        INPUT_BOOL    = 10,

        OUT_STR       = 11,
        OUT_INT       = 12,
        OUT_FLOAT     = 13,
        OUT_BOOL      = 14,

        JMP           = 15,
        JT            = 16,
        JF            = 17,

        ASSIGN        = 18,
        UMINUS        = 19,
        PLUS          = 20,
        MINUS         = 21,
        MULTI         = 22,
        DIVIDE        = 23,
        POWER         = 24,
        AND           = 25,
        OR            = 26,
        NOT           = 27,
        EQUAL         = 28,
        NOT_EQUAL     = 29,
        BIGGER_EQUAL  = 30,
        LESS_EQUAL    = 31,
        LESS          = 32,
        BIGGER        = 33,
    };

    enum class Type {
        INT     = static_cast<int>(Operator::INT),
        REAL    = static_cast<int>(Operator::REAL),
        BOOLEAN = static_cast<int>(Operator::BOOLEAN),
    };

    using Multi_type = std::variant<std::string, int, bool, double>;

    // ---
    explicit Reader (std::ifstream&& file_in);
    ~Reader ();

    // ---
    const std::vector<std::pair<Operator, Multi_type>>& get_code () const;
    const std::map<std::string, int>& get_labels () const;
    const std::list<std::pair<std::string, Type>>& get_variables () const;

private:
    std::ifstream m_file_in;

    std::vector<std::pair<Operator, Multi_type>> m_code;
    std::map<std::string, int> m_labels;
    std::list<std::pair<std::string, Type>> m_variables;

    // ---
    void fill_tables ();

    // ---
    static Operator str_to_op (const std::string& str);
    static Multi_type str_to_multi_type (Reader::Operator type, const std::string&& str);
    static Type str_to_type (const std::string& str);
};


#endif //READER_H
