from numpy import*
def montecarlo(num_samples):
    inside_circle=0
    for i in range(num_samples):
        x,y=random.uniform(-1,1,2)
        if ((x**2)+(y**2))<=1:        