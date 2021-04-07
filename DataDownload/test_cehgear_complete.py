import os
for year in range(1990, 2015):#
    for month in range(1, 12):
      month = str(month).zfill(2) 
      pattern = os.path.join(r'/nfs/a319/gy17m2a/CEH-GEAR/CEH-GEAR-1hr_{}{}.nc')
      if os.path.exists(pattern.format(year, month)):
              print ("File " + pattern.format(year, month) + ' exists')
      #print(pattern.format(year, month))
      if not os.path.exists(pattern.format(year, month)):
              print ("File " + pattern.format(year, month) + ' does not exist')