from os import walk

f = []
layer = 1
w = walk("C:/Users/skuma807/Project Core/Test Project/")
for (dirpath, dirnames, filenames) in w:
    
    f.extend(dirnames)
    print(dirpath)
    print(filenames)
    #break
    layer += 1