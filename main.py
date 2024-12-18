from Syntaxer.reverse import main_revers as translator_run
from Lexer.lexer import main_lexer as lexer_run
import subprocess
import os

def lexing ():
    lexer_run()

def run ():
    translator_run()

if __name__ == '__main__':
    translator_run()
    subprocess.run("ilasm test.il", cwd="Generated", shell=True)
    subprocess.run("clear", shell=True)
    subprocess.run("test.exe", cwd="Generated", shell=True)