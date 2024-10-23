def a():
    print("a")
    return False

def b():
    print("b")
    return True

if not a() and not b():
    print("oh")