def is_prime(n):
    if n<=2:
        return(False)
    if n==2:
        return(True)
    if n==3:
        return(True)
    if n==5:
        return(True)
    if n%2 ==0:
        return(False)
    i=4
    while i<=(n/2):
        i=i+1
        if n%i==0:
            return(False)
        else:
            return(True)
#numb=int(input("enter number to check prime="))
#print(is_prime(numb))
k=200
for l in range(k):
    print(l," ",is_prime(l))
