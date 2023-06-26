library (extRemes)
library(xts)


filepath <- "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Scripts/UKCP18/Outputs/TimeSeries_csv/Armley/2.2km/EM01_1980-2001.csv"
file <- read.csv(file = filepath)

# Derive AMS for maximum precipitation
ams <- apply.yearly(file, max)

# Max-likelihood fitting of the GEV distribution
fit_mle <- fevd(as.vector(ams), method = 'MLE', type = 'GEV')
# Diagnostic plots
plot(fit_mle)
