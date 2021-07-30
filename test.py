

'''
a = [chr(i) for i in range(97,100)]
b = {i:ord(i)-96 for i in a}
print(b)

def f(a):
    return a+1

b = (1,)
b = f(1) if not b else b
print(b)



# correct_function_definition.py
def my_function(a, b, *args, **kwargs):
    print(a)
    print(b)
    print(args)
    print(kwargs)

def f(*args):
    print(None if not args else args)

f()
#my_function(1,2,3,4,c=5,d=6)
# sum_integers_args_3.py
def my_sum(*args):
    print(args)
    result = 0
    for x in args:
        result += x
    return result

list1 = [1, 2, 3]
list2 = [4, 5]
list3 = [6, 7, 8, 9]

print(my_sum(*list1, *list2, *list3))
a = *"abc"
print(a)
*a, = "RealPython"
print(a)
'''