
# Difference between single array elements
lst1 = [1.1,1.5,1.4,1.8]
k = 0.4

for i in lst1[:-1]:
    for j in lst1[1:]:
        val1 = round((i-j),2)
        if abs(val1) == k:
            print(True, i, j)

print("***********")
for i in range(1, len(lst1)):
    if abs(round(lst1[i] - lst1[i-1],2)) == k:
        print(True, lst1[i], lst1[i-1])


print("***********")
for x, y in zip(lst1[0:-1:], lst1[1::]):
    if abs(round((y-x),2)) == k:
        print(True, x, y)

print("***********")

sub = 0
for i in range(len(lst1)):
    if sub!=0:
        sub = abs(lst1[i]- sub)
        if round(sub,2) == k:
            print(True)
    else:
        sub = abs(lst1[i]-lst1[i+1])
        if round(sub,2) == k:
            print(True)