#ifndef EXECUTOR_H
#define EXECUTOR_H

#include "reader_lib/reader.h"
#include "stack.h"

class Executor {
public:
   using Token = std::pair<Reader::Operator, Reader::Multi_type>;

   Executor  (Reader& reader, Stack& stack);
   ~Executor ();

   void run ();

private:
   // void out_str   (std::string str) const;
   // void out_int   (int value) const;
   // void out_float (double val) const;
   // void out_bool  (bool val) const;

   void in_int   () const;
   void in_float () const;
   void in_bool  () const;

private:
   using oprt = Reader::Operator;

   void calc_unary    (oprt op);
   void calc_binary   (oprt op);

   //TODO: переглянь, чи так я передаю
   std::pair<Reader::Operator, std::variant<int, double, bool>> get_rval (Token right_token);
   void label_declare ();

   void in     (oprt in_type);
   void out    (oprt out_type);
   void jump   (oprt jump_type);
   void assign ();

   size_t m_current_code_place;
   Reader& m_reader;
   Stack& m_stack;
   std::map<std::string, std::pair<std::variant<int, double, bool>, oprt>> m_var_table;


   std::ios_base::fmtflags m_old_cout;
};



#endif //EXECUTOR_H
