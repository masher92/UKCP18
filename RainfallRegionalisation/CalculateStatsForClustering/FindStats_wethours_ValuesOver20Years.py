stat = 'Wethours/wet_prop'
region = 'leeds-at-centre'
em = '01'
wet_prop = pd.read_csv("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/RainfallRegionalisation/HiClimR_inputdata/leeds-at-centre/Wethours/wet_prop/em_01.csv")
p95 = pd.read_csv("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/RainfallRegionalisation/HiClimR_inputdata/leeds-at-centre/Wethours/jja_p95_wh/em_01.csv")
wet_prop = pd.read_csv("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/RainfallRegionalisation/HiClimR_inputdata/leeds-at-centre/Wethours/wet_prop/em_01.csv")
p99 = pd.read_csv("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/RainfallRegionalisation/HiClimR_inputdata/leeds-at-centre/Wethours/jja_p99_wh/em_01.csv")


plt.scatter(p95['1981'], wet_prop['1981'], s=1.5)
plt.xlabel('Cell wet day proportion')
plt.ylabel('Cell P95')

for year in range(1981,2001):
    print(year)
    plt.scatter(p99[str(year)], wet_prop[str(year)], s=1.5)
    plt.xlabel('Cell wet day proportion')
    plt.ylabel('Cell P95')
    plt.show()
    
x = p95['1981']
y = wet_prop['1981']
z = np.polyfit(x, y, 1)
p = np.poly1d(z)
pylab.plot(x,p(x),"r--")
# the line equation:
print "y=%.6fx+(%.6f)"%(z[0],z[1])    