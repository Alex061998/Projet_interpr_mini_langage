# -----------------------------------------------------------------------------
# calc.py
#
# Expressions arithmétiques sans variables
# -----------------------------------------------------------------------------
import ply.lex as lex
import util_fonctions as uf
from genereTreeGraphviz2 import printTreeGraph
import ply.yacc as yacc

reserved = {
    'print': 'PRINT',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'for': 'FOR',
    'function': 'FUNCTION'
}

tokens = ['NUMBER', 'MINUS',
          'PLUS', 'TIMES', 'DIVIDE',
          'LPAREN', 'RPAREN', 'AND', 'OR',
          'TRUE', 'FALSE', 'SEMICOLON', 'NAME',
          'AFFECT', 'INF', 'SUP', 'EQUALS', 'LACCOLADE', 'RACCOLADE',
          'VIRG', 'GUILLEMET', 'PLUSPLUS', 'MINUSMINUS', 'PLUSAFFECT', 'MINUSAFFECT']

tokens = tokens + list(reserved.values())

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE')
)


# Tokens
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LACCOLADE = r'\{'
t_RACCOLADE = r'\}'
t_AND = r'&'
t_OR = r'\|'
t_FALSE = r'F'
t_TRUE = r'T'
t_SEMICOLON = r';'
t_AFFECT = r'='
t_EQUALS = r'=='
t_INF = r'<'
t_SUP = r'>'
t_VIRG = r','
t_GUILLEMET = r'"'
t_PLUSPLUS = r'\++'
t_MINUSMINUS = r'--'
t_PLUSAFFECT = r'\+='
t_MINUSAFFECT = r'-='


def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'NAME')    # Check for reserved words
    return t


# def t_DECFUNC(t):
#     r'function'
#     t.type = reserved.get(t.value, 'DECFUNC')    # Check for reserved words
#     return t


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


# Ignored characters
t_ignore = " \t"


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
lex.lex()


# Début d'exécution des règles
def p_start(p):
    'start : bloc'
    p[0] = ('START', p[1])
    print('Arbre de dérivation = ', p[1])
    printTreeGraph(p[1])
    print('CALC> ', uf.eval_Inst(p[1]))

# Excution des bloc ( soit print, soit affect pour le moment)


def p_bloc(p):
    '''bloc : bloc statement SEMICOLON 
    | statement SEMICOLON'''
    if len(p) == 4:
        p[0] = ('bloc', p[1], p[2])
    else:
        p[0] = ('bloc', p[1], 'Empty')

# Affiche la valeur d'une expression


def p_print(p):
    '''statement : PRINT LPAREN multiExpr RPAREN'''
    # print(p[3])
    p[0] = ('print', p[3])

# Fait un une affection d'une expression dans une variable


def p_affect(p):
    'statement : NAME AFFECT expression'
    p[0] = ('affect', p[1], p[3])


def p_condition_if(p):
    '''statement : IF LPAREN expression RPAREN LACCOLADE bloc RACCOLADE
    | IF LPAREN expression RPAREN LACCOLADE bloc RACCOLADE ELSE LACCOLADE bloc RACCOLADE'''
    if len(p) == 8:
        p[0] = ('if', p[3], p[6])
    else:
        p[0] = ('if', p[3], p[6], 'else', p[10])


def p_boucle_while(p):
    'statement : WHILE LPAREN expression RPAREN LACCOLADE bloc RACCOLADE'
    p[0] = ('while', p[3], p[6])


def p_boucle_for(p):
    '''statement : FOR LPAREN statement SEMICOLON expression SEMICOLON statement RPAREN LACCOLADE bloc RACCOLADE'''
    p[0] = ('for', p[3], p[5], p[7], p[10])


def p_mutiple_names(p):
    '''multiname : NAME VIRG multiname
    | NAME'''
    if len(p) == 4:
        p[0] = ('multiname', p[1], p[3])
    else:
        p[0] = ('multiname', p[1])


def p_multiExpr_names(p):
    '''multiExpr : expression VIRG multiExpr
    | expression'''
    if len(p) == 4:
        p[0] = ('multiExpr', p[1], p[3])
    else:
        p[0] = ('multiExpr', p[1])


def p_function(p):
    '''statement : FUNCTION NAME LPAREN RPAREN LACCOLADE bloc RACCOLADE
    | FUNCTION NAME LPAREN multiname RPAREN LACCOLADE bloc RACCOLADE'''
    if len(p) == 7:
        p[0] = ('function', p[2], p[6])
    else:
        p[0] = ('function', p[2], p[4], p[7])


def p_call_func(p):
    '''statement : NAME LPAREN RPAREN'''
    p[0] = ('call', p[1], 'Empty')


def p_call_param_func(p):
    '''statement : NAME LPAREN multiExpr RPAREN'''
    if len(p) == 5:
        p[0] = ('callParam', p[1], p[3])

# Opération


def p_expression_binop_plus(p):
    'expression : expression PLUS expression'
    p[0] = ('+', p[1], p[3])


def p_expression_binop_times(p):
    'expression : expression TIMES expression'
    p[0] = ('*', p[1], p[3])


def p_expression_binop_divide_and_minus(p):
    '''expression : expression MINUS expression
                                | expression DIVIDE expression'''
    if p[2] == '-':
        p[0] = ('-', p[1], p[3])
    else:
        p[0] = ('/', p[1], p[3])


def p_expression_binop_bool(p):
    ''' expression : expression AND expression  
    | expression OR expression '''
    if p[2] == '&':
        p[0] = ('&', p[1], p[3])
    else:
        p[0] = ('|', p[1], p[3])


def p_expression_binop_comparison(p):
    '''expression : expression INF expression
                                | expression SUP expression'''
    if p[2] == '<':
        p[0] = ('<', p[1], p[3])
    else:
        p[0] = ('>', p[1], p[3])

# incrementation et affectation i++, i+=1;


def p_incrementation(p):
    '''expression : NAME PLUSPLUS 
    | NAME PLUSAFFECT expression
    | NAME MINUSMINUS 
    | NAME MINUSAFFECT expression'''
    if p[2] == '++':
        p[0] = ('incPlus', p[1])
    elif p[2] == '+=':
        p[0] = ('incExpr', p[1], p[3])
    elif p[2] == '--':
        p[0] = ('decMinus', p[1])
    elif p[2] == '-=':
        p[0] = ('decExpr', p[1], p[3])


def p_expression_binop_equals(p):
    '''expression : expression EQUALS expression'''
    p[0] = ('==', p[1], p[3])

# Element terminaux


def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]


def p_expression_number(p):
    'expression : NUMBER'
    p[0] = p[1]


def p_expression_name(p):
    '''expression : NAME
    | GUILLEMET NAME GUILLEMET'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]


def p_expression_true(p):
    'expression : TRUE'
    p[0] = True


def p_expression_false(p):
    'expression : FALSE'
    p[0] = False


def p_error(p):
    print("Syntax error at '%s'" % p.value)


yacc.yacc()


# s = input('calc > ')
# s = 'a = (1+1)+1;'
# s = 'print(1+2);a=2;print(a);'
# s='print(1+2);x=4;x=x+1;print(x);'
#s = 'if(2<4){print(2*3);print(3);};'
#s = 'x=1;print(x);'
#s = 'x=1;x=x+1;x=x+1;print(x);'
#s = 'x=2;while(x<5){x=x+1;print(x);};'
# s = 'for(x=0;x<11;x=x+1;){print(x);};'
# s = 'for(i=0; i<10; i=i+1){print(i);};'
s = 'function carre(a,b){print(a*b);};for(i=0;i<5;i=i+1){print(i);carre(i,i);};'
# s = 'a=2;print(a*a);'
# s = 'carre(a){print(a);};carre(2);'
# s = 'carre(a,b){a=1;b=2;print(a+b);};carre(2,1);'
# s = 'carre();'
# s = 'carre(a,b);'
# s = 'carre(a){a=2;print(a);};carre(1);'
# s = 'carre(a){a=2;print(a);};carre(1);'
#s = 'function carre(){print(2);};for(i=0;i<10;i=i+1){carre();};'
#s = 'while(5){print(1);};'
# s = 'x=5;while(x<8){print(2+9);};'
#s = 'x=1+2;print(x);'
#s = 'x=0; print(x+=2);'
#s = 'x=0; print(x++);'
#s = 'if(2<0){print("x");} else{ print("a");};'
#s = 'print(1+2,"toto", 3+4);'
#s= 'print(1+2);'
yacc.parse(s)
