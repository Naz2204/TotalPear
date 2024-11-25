class A:
    def __init__(self): pass
    def a(self):
        A.a.a = 'A'
        print("A.a.a = ", A.a.a)

a = A()
a.a()