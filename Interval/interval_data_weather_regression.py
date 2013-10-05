import numpy as np

##weather regression analysis

#get x

x=[1,2,3,4,5]


#get y

y=[2,5,7,9,13]

## Get fit

R2=np.corrcoef(x,y)[0][1]**2

print "The R^2 Coeff is: "+str(R2)

## Save Results

##Gap was ... 3 Hours
##Duration Was ... 4 Hours

## Example, it is 3 o' clock in the afternoon, n hours ago the previous k
## hours had an average temp of 90, now the usage for 15 minutes is 150 kwh.
## In the next 15 minutes, the usage was 160, the average temp was 92.

## In order for this to work well, I will need to get average occupancy
## profiles either from the building, or from ASHRAE. Otherwise, the usage
## could start to decrease not because the temperature is driving it,
## but because the occupancy is.

## Perhaps it would be best to first try out the "Getting similar days"
## thing. I'm still going to use python though. Because fuck this shit.
