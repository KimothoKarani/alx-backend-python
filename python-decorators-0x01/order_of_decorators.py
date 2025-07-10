def decorator1(func):
    def wrapper(*args, **kwargs):
        print("Before decorator1")
        result = func(*args, **kwargs)
        print("After decorator1")
        return result
    return wrapper

def decorator2(func):
    def wrapper(*args, **kwargs):
        print("Before decorator2")
        result = func(*args, **kwargs)
        print("After decorator2")
        return result
    return wrapper


@decorator1
@decorator2
def say_hello():
    print("Hello!")

say_hello()