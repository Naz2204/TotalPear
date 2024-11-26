#include "reader.h"
#include <iostream>
#include "nlohmann/json.hpp"

using json = nlohmann::json;

Reader::Reader (std::ifstream&& file_in) : m_file_in{std::move(file_in)} {
   fill_tables();
}

Reader::~Reader () {
    m_file_in.close();
}

const std::vector<std::pair<Reader::Operator, Reader::Multi_type>>& Reader::get_code () const {
    return m_code;
}

const std::map<std::string, int>& Reader::get_labels () const {
    return m_labels;
}

const std::list<std::pair<std::string, Reader::Type>>& Reader::get_variables () const {
    return m_variables;
}

void Reader::fill_tables () {
    json j = json::parse(m_file_in);

    auto var_table   = (j["var_table"].template get<std::list<json>>());
    auto label_table = (j["label_table"].template get<std::list<json>>());
    auto code_table  = (j["code"].template get<std::list<json>>());

    // VAR TABLE
    size_t table_size = var_table.size();
    for (size_t i = 0; i < table_size; ++i) {
        auto temp = std::move(var_table.front());
        var_table.pop_front();

        m_variables.emplace_back(
            std::move(temp[0]. template get<std::string>()),
            str_to_type(temp[1].get_ref<const json::string_t&>().c_str())
        );
    }

    // LABEL TABLE
    table_size = label_table.size();
    for (size_t i = 0; i < table_size; ++i) {
        auto temp = std::move(label_table.front());
        label_table.pop_front();

        m_labels[std::move(temp[0]. template get<std::string>())] = temp[1]. template get<int>();
    }

    // CODE TABLE
    table_size = code_table.size();
    m_code.reserve(table_size);
    for (int i = 0; i < table_size; ++i) {
        auto temp = std::move(code_table.front());
        code_table.pop_front();

        Operator op = str_to_op(temp[1].get_ref<const json::string_t&>().c_str());
        m_code.emplace_back(
            op,
            str_to_multi_type(op, std::move(temp[0]. template get<std::string>()))
        );

    }

}

Reader::Multi_type Reader::str_to_multi_type (Reader::Operator type, const std::string&& str) {

    return {12};
}

Reader::Operator Reader::str_to_op (const std::string& str) {
    static const std::map<std::string, Operator> STR_TO_OP = {
        {"l-value",         Operator::L_VALUE},
        {"r-value",         Operator::R_VALUE},
        {"label",           Operator::LABEL},
        {"integer",         Operator::INT},
        {"real",            Operator::REAL},
        {"string",          Operator::STR},
        {"boolean",         Operator::BOOLEAN},
        {"label_declare",   Operator::LABEL_DECLARE},
        {"op_input_int",    Operator::INPUT_INT},
        {"op_input_float",  Operator::INPUT_FLOAT},
        {"op_input_bool",   Operator::INPUT_BOOL},
        {"op_out_str",      Operator::OUT_STR},
        {"op_out_int",      Operator::OUT_INT},
        {"op_out_float",    Operator::OUT_FLOAT},
        {"op_out_bool",     Operator::OUT_BOOL},
        {"op_jmp",          Operator::JMP},
        {"op_jt",           Operator::JF},
        {"op_jf",           Operator::JT},
        {"op_assign",       Operator::ASSIGN},
        {"op_uminus",       Operator::UMINUS},
        {"op_plus",         Operator::PLUS},
        {"op_minus",        Operator::MINUS},
        {"op_multi",        Operator::MULTI},
        {"op_divide",       Operator::DIVIDE},
        {"op_power",        Operator::POWER},
        {"op_and",          Operator::AND},
        {"op_or",           Operator::OR},
        {"op_not",          Operator::NOT},
        {"op_equal",        Operator::EQUAL},
        {"op_not_equal",    Operator::NOT_EQUAL},
        {"op_bigger_equal", Operator::BIGGER_EQUAL},
        {"op_less_equal",   Operator::LESS_EQUAL},
        {"op_less",         Operator::LESS},
        {"op_bigger",       Operator::BIGGER}
    };
    auto result = STR_TO_OP.find(str);
    if (result == STR_TO_OP.end()) throw std::runtime_error("Fatal error: Internal inconsistency");
    return result->second;
}

Reader::Type Reader::str_to_type (const std::string& str) {
    static const std::map<std::string, Type> STR_TO_TYPE = {
        {"integer", Type::INT},
        {"real",    Type::REAL},
        {"bool",  Type::BOOLEAN}
    };
    auto result = STR_TO_TYPE.find(str);

    if (result == STR_TO_TYPE.end()) throw std::runtime_error("Fatal error: Internal inconsistency");
    return result->second;
}
