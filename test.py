# problem: find 1 or 2 consecutive numbers that are divisible by 3 and add those numbers up
n = "439" #ans is 51=3+9+39
print([int(a[0]) for a in [[int(n[i:i+j]) for i in range(len(n)) if i+j<=len(n) and int(n[i:i+j])%3==0] for j in range(1,3)]])

'''
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