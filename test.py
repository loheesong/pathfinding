from queue import PriorityQueue

customers = PriorityQueue() #we initialise the PQ class instead of using a function to operate upon a list. 
customers.put((2, 1))
customers.put((3, 2))
customers.put((1, 3))
customers.put((4, 4))

while not customers.empty():
    print(customers.get())