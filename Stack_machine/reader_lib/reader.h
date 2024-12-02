#ifndef READER_H
#define READER_H


#include <fstream>
#include <list>
#include <vector>
#include <map>
#include <variant>



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
    static Multi_type str_to_multi_type (Reader::Operator type, std::string&& str);
    static Type str_to_type (const std::string& str);
};


#endif //READER_H
