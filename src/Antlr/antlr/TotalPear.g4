grammar TotalPear;

program: statementList EOF;

statementList: statementLine+;

statementLine: initDeclare
             | statementLocal;

statementLocal: assign
              | print
              | cycleDo
              | cycleWhile
              | cycleFor
              | conditionalIf
              | conditionalFlags
              | conditionalSwitch;

initDeclare: type IDENTIFIER ('=' (expression | inputStatement))? ';';

expression: mathPolynomial
          | logicalExpression;

mathPolynomial: mathMonomial (('+' | '-') mathMonomial)*;

mathMonomial: mathPrimary1 (('*' | '/') mathPrimary1)*;

mathPrimary1: ('-')* mathPrimary2;

mathPrimary2: mathPrimary3 ('^' mathPrimary1)?;

mathPrimary3: IDENTIFIER
            | uint
            | ufloat
            | '(' mathPolynomial ')';

logicalExpression: logical2 ('or' logical2)*;

logical2: logical3 ('and' logical3)*;

logical3: ('not')* logical4;

logical4: IDENTIFIER
        | comparison
        | bool
        | '(' logicalExpression ')';

comparison: '|' (mathPolynomial ('>' | '<' | '>=' | '<=' | '==' | '!=') mathPolynomial
                |logicalExpression ('==' | '!=') logicalExpression)'|';

assign: assignStatement ';';
assignStatement: IDENTIFIER  '=' (inputStatement | expression);

print: 'print' '(' printList ')' ';';
printList: printable (',' printable)*;
printable: STRING | expression;

inputStatement: inputType '(' STRING? ')';

cycleWhile: 'while' logicalExpression body;

body: '{' statementLocal* '}';

cycleFor: 'for' '(' assignStatement ';' logicalExpression ';' assignStatement ')' body;

cycleDo: 'do' body 'while' logicalExpression ';';

conditionalFlags: 'flagIf' flagList flagBody+;

flagList: '[' flagDeclare (',' flagDeclare)* ']';

flagDeclare: flag ':' logicalExpression;

flag: '#' IDENTIFIER;

flagBody: flag ':' body;

conditionalIf: 'if' logicalExpression body elif* else?;

elif: 'elif' logicalExpression body;

else: 'else' body;

conditionalSwitch: 'switch' mathPolynomial '{' case+ default? '}';

case: 'case' ('-')? (uint | ufloat) ':' body;

default: 'default' ':' body;


// -------------------------------------

inputType:  INPUT_TYPE;
bool:       BOOL;
type:       TYPE;
uint:       UNSIGNED_INTEGER;
ufloat:     UNSIGNED_FLOAT;

// -------------------------------------



STRING: '"' (LETTER | CHAR_SYMBOL | DIGIT | '\\n')* '"';

COMMENT: '//' (LETTER | DIGIT | CHAR_SYMBOL)* NEW_LINE -> skip;

INPUT_TYPE: 'inputInt' | 'inputFloat' | 'inputBool';

//COMPARISON_OP: '>'
//             | '<'
//             | '>='
//             | '<='
//             | '=='
//             | '!=';

BOOL: 'true' | 'false';
TYPE: 'int'
    | 'float'
    | 'bool';

IDENTIFIER: LETTER_FOR_IDENT (LETTER_FOR_IDENT | DIGIT)*;

LETTER_FOR_IDENT: LETTER | '$' | '_';

UNSIGNED_INTEGER: DIGIT_STRING;

UNSIGNED_FLOAT: DIGIT_STRING '.' DIGIT_STRING;

DIGIT_STRING: DIGIT+;

DIGIT: [0-9];

LETTER: [a-zA-Z];

WS : [ \t\n\r]+ -> skip;

CHAR_SYMBOL: ':' | ';'  | '\''  | '@' | '|' | '#' | '~'
           | '`' | '!'  | '$'  | '%' | '^' | '&' | '*'
           | '('  | ')' | '-' | '=' | '_'  | '+' | '\t'
           | ' ' | '<' | '>' | '.' | ','  | '['
           | ']'  | '{' | '}' | '?' | '/' | '\\\\';


NEW_LINE: '\n';
