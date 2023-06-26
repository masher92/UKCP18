# Examples here: https://www.gis-blog.com/eva-intro-2/

library (extRemes)
library(xts)
library(tidyquant)
library(dplyr)

# Create path to file
filepath <- "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Scripts/UKCP18/Outputs/TimeSeries_csv/Armley/2.2km/EM01_1980-2001.csv"
# Read in data
file <- read.csv(file = filepath)

# Create column containing just the year 
file$year <- format(as.Date(file$Date_Formatted), format = "%Y")

# Remove rows with emty year (because of February problem)
file <- na.omit(file) 

# Find the biggest value in each year
annual_max = file %>% group_by(year) %>% summarise(max = max(Precipitation..mm.hr.))

#
annual_maxs = as.vector(annual_max$max)
annual_max_df <- annual_max$max


# Summary
summary(annual_maxs)

##############  maximum-likelihood fitting of the GEV distribution
fit_mle <- fevd(as.vector(annual_max$max), method = "MLE", type="GEV")
# Diagnostic plots
plot(fit_mle)
# Plot a specific diagnostic plot
plot(fit_mle, type = 'density')
rl_mle <- return.level(fit_mle, conf = 0.05, return.period= c(2,5,10,20,50,100))

# Examine confidence intervals
ci(fit_mle,type="parameter")

##############   fitting of GEV distribution based on L-moments estimation
fit_lmom <- fevd(as.vector(annual_max$max), method = "Lmoments", type="GEV")
# diagnostic plots - all
plot(fit_lmom)
# Plot a specific diagnostic plot
plot(fit_lmom, type = 'Zplot')
# return levels:
rl_lmom <- return.level(fit_lmom, conf = 0.05, return.period= c(2,5,10,20,50,100,200, 500, 1000))

# return level plots
par(mfcol=c(1,2))
# return level plot w/ MLE
plot(fit_mle, type="rl",
     main="Return Level Plot for Bärnkopf w/ MLE",
     ylim=c(0,200), pch=16)
loc <- as.numeric(return.level(fit_mle, conf = 0.05,return.period=100))
segments(100, 0, 100, loc, col= 'midnightblue',lty=6)
segments(0.01,loc,100, loc, col='midnightblue', lty=6)

# return level plot w/ LMOM
plot(fit_lmom, type="rl",
     main="Return Level Plot for Bärnkopf w/ L-Moments",
     ylim=c(0,200))
loc <- as.numeric(return.level(fit_lmom, conf = 0.05,return.period=100))
segments(100, 0, 100, loc, col= 'midnightblue',lty=6)
segments(0.01,loc,100, loc, col='midnightblue', lty=6)

# comparison of return levels
results <- t(data.frame(mle=as.numeric(rl_mle),
                        lmom=as.numeric(rl_lmom)))
colnames(results) <- c(2,5,10,20,50,100)
round(results,1)

#### Checking for trend
# https://www.gis-blog.com/eva-intro-4/
library(extRemes)
library(xts)
library(ggplot2)
Kendall::MannKendall(annual_max_df)
ams_df <- fortify(annual_max)
colnames(ams_df)[1] <- "date"
summary(lm(max~date, data=ams_df))

p <- ggplot(ams_df, aes(x = date, y = max, group = 1)) + geom_point() + geom_line()
p + stat_smooth(method = "lm", formula = y ~ x, size = 1)


# maximum likelihood estimation
mle_trend <- fevd(x = annual_max, data = ams_df, location.fun=~date, method = "MLE", type="GEV")
rl_trend <- return.level(mle_trend, conf = 0.05, return.period= c(2,5,10,20,50,100))

# return level plot
plot(mle_trend, type="rl", main="Return Level Plot for Bärnkopf w/ MLE")




