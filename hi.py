class A:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def change(self, x):
        self.x = x

    def set(self, x):
        self.x = x

    def print(self):
        print(f"Result: {self.x}")

def foo(aa):
    aa = 99999

a = 5
foo(a)
print(a)