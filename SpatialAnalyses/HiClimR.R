library(HiClimR)

region = 'Northern' #'WY' 'Northern'

stats = list('Greatest_ten') # 'Greatest_ten'
#stats = ('99.5th Percentile', '99.9th Percentile', '99.99th Percentile', '97th Percentile', '99th Percentile', '95th Percentile') 
#ems = list('04', '05')
ems = list('01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15')
#ems = list('01')
# Number of clusters
num_clusters_list = list(2,3, 4, 5,10)

for (num_clusters in num_clusters_list){
  for (stat in stats){
    for (em in ems){
            print (em)
            #filepath = sprintf("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/HiClimR_inputdata/%s/%s/em%s.csv", region, stat, em)
             filepath = sprintf("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/HiClimR_inputdata/%s/%s/em%s.csv", region, stat, em)
            # Read in data
            df <- read.csv(file = filepath)
            
            # Create vectors with lons and lats
            lats <- df[['lat']]
            lons <- df[['lon']]
            
            # Remove lat and long from the dataframe
            drops <- c("lat","lon")
            df = df[ , !(names(df) %in% drops)]
            
            #df = df[,1:2]
            
            # Create vector from the dataframe
            vect = as.vector(t(df))
            # Create matrix from the vector
            new_matrix = matrix(data = vect, nrow = length(lats), byrow = TRUE)
            
            ## Single-Variate Hierarchical Climate Regionalization
            y <- HiClimR(new_matrix, lon = lons, lat = lats, lonStep = 1, latStep = 1, geogMask = TRUE,
                    continent = "Europe", meanThresh = 0, varThresh = 0, detrend = TRUE,
                    standardize = TRUE, nPC = NULL, method = "ward", hybrid = FALSE, kH = NULL, 
                    members = NULL, nSplit = 1, upperTri = TRUE, verbose = TRUE, 
                    validClimR = TRUE, k = num_clusters, minSize = 1, alpha = 0.01, 
                    plot = FALSE, colPalette = NULL, hang = -1, labels = FALSE)
            
            
            regions = y["region"]
            regions_values = as.numeric(unlist(regions))
            regions_df <- data.frame(regions_values, lats, lons)
            
            # Save to file
            
            if (!(file.exists(sprintf("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/HiClimR_outputdata/%s/%s/%s clusters", region, stat, num_clusters)))) 
            {  print ("Directory does not exist")
              dir.create(sprintf("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/HiClimR_outputdata/%s/%s/%s clusters", region, stat, num_clusters), recursive = TRUE)
              print("Directory created")
            }
            
            print("Here")
            output_filepath = sprintf("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/HiClimR_outputdata/%s/%s/%s clusters/em%s.csv", region, stat,  num_clusters, em)
            print("Here")
            unlink(output_filepath)
            write.csv(regions_df, output_filepath, row.names = FALSE)
            
    }
  }
}
 

#################################
# 
# em = '04'
# filepath = sprintf("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/DataforR/WY/%s/em%s.csv", stat, em)
# filepath = sprintf("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/DataforR/Northern/%s/em%s.csv", stat, em)
# 
# # Read in data
# df <- read.csv(file = filepath)
# 
# # Create vectors with lons and lats
# lats <- df[['lat']]
# lons <- df[['lon']]
# 
# # Remove lat and long from the dataframe
# drops <- c("lat","lon")
# df = df[ , !(names(df) %in% drops)]
# 
# #df = df[,1:2]
# 
# # Create vector from the dataframe
# vect = as.vector(t(df))
# # Create matrix from the vector
# new_matrix = matrix(data = vect, nrow = length(lats), byrow = TRUE)
# 
# ## Use Ward's method
# y <- HiClimR(new_matrix, lon = lons, lat = lats, lonStep = 1, latStep = 1, geogMask = TRUE,
#         continent = "Europe", meanThresh = 0, varThresh = 0, detrend = TRUE,
#         standardize = TRUE, nPC = NULL, method = "ward", hybrid = FALSE, kH = NULL, 
#         members = NULL, nSplit = 1, upperTri = TRUE, verbose = TRUE, 
#         validClimR = TRUE, k = num_clusters, minSize = 1, alpha = 0.01, 
#         plot = TRUE, colPalette = NULL, hang = -1, labels = FALSE)
# 
# ## Use data splitting for big data
# y <- HiClimR(new_matrix, lon = lons, lat = lats, lonStep = 1, latStep = 1, geogMask = FALSE,
#              continent = "Europe", meanThresh = 0, varThresh = 0, detrend = TRUE,
#              standardize = TRUE, nPC = NULL, method = "ward", hybrid = TRUE, kH = NULL,
#              members = NULL, nSplit = 10, upperTri = TRUE, verbose = TRUE,
#              validClimR = TRUE, k = num_clusters, minSize = 1, alpha = 0.01,
#              plot = TRUE, colPalette = NULL, hang = -1, labels = FALSE)
# 
# ## Use hybrid Ward-Regional method
# y <- HiClimR(new_matrix, lon = lons, lat = lats, lonStep = 1, latStep = 1, geogMask = FALSE,
#              continent = "Europe", meanThresh = 0, varThresh = 0, detrend = TRUE,
#              standardize = TRUE, nPC = NULL, method = "ward", hybrid = TRUE, kH = NULL,
#              members = NULL, nSplit = 1, upperTri = TRUE, verbose = TRUE,
#              validClimR = TRUE, k = num_clusters, minSize = 1, alpha = 0.01,
#              plot = TRUE, colPalette = NULL, hang = -1, labels = FALSE)
# 
# 
# z <- validClimR(y, k = 12, minSize = 25, alpha = 0.5,
#                 plot = TRUE, colPalette = NULL)
# ## The optimal number of clusters, including small clusters
# k <- length(z$clustFlag)
# 
# RegionsMap <- matrix(y$region, nrow = length(unique(y$coords[, 1])), byrow = TRUE)
# colPalette <- colorRampPalette(c("#00007F", "blue", "#007FFF", "cyan",
#                                  "#7FFF7F", "yellow", "#FF7F00", "red", "#7F0000"))
# image(unique(y$coords[, 1]), unique(y$coords[, 2]), RegionsMap
#       
#       , col = colPalette(ks))
# ## Visualization for gridded or ungridded data
# plot(y$coords[, 1], y$coords[, 2], col = colPalette(max(Regions, na.rm = TRUE))[y$region],
#      pch = 15, cex = 1)
# 
# 
# 
# 
# ## Generate a random matrix with the same number of rows
# x2 <- matrix(rnorm(nrow(df) * 100, mean=0, sd=1), nrow(df), 20)
# ## Multivariate Hierarchical Climate Regionalization
# y <- HiClimR(x2, lon = lons, lat = lats, lonStep = 1, latStep = 1, geogMask = TRUE,
#              continent = "Europe", meanThresh = 0, varThresh = 0, detrend = TRUE,
#              standardize = TRUE, nPC = NULL, method = "ward", hybrid = FALSE, kH = NULL, 
#              members = NULL, nSplit = 1, upperTri = TRUE, verbose = TRUE, 
#              validClimR = TRUE, k = num_clusters, minSize = 1, alpha = 0.01, 
#              plot = TRUE, colPalette = NULL, hang = -1, labels = FALSE)
# 
# 
# 
# #jpeg('Outputs/HiClimR/WY/em01.jpg')
# 
# 
# #####################
# library(HiClimR)
# setwd("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/")
# 
# # Number of clusters
# num_clusters = 10
# 
# em = '01'
# #stat = '99th Percentile'
# stat = 'Mean'
# #stat = 'Max'
# 
# filepath = sprintf("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/DataforR/WY/%s/em%s.csv", stat, em)
# 
# # Read in data
# df2 <- read.csv(file = filepath)
# #df2 <- df2[1:400,]
# 
# # Create vectors with lons and lats
# lats <- df2[['lat']]
# lons <- df2[['lon']]
# 
# # Remove lat and long from the dataframe
# drops <- c("lat","lon")
# df2 = df2[ , !(names(df2) %in% drops)]
# 
# #df = df[,1:2]
# 
# # Create vector from the dataframe
# vect2 = as.vector(t(df2))
# # Create matrix from the vector
# new_matrix2 = matrix(data = vect2, nrow = length(lats), byrow = TRUE)
# 
# ## Single-Variate Hierarchical Climate Regionalization
# y <- HiClimR(new_matrix2, lon = lons, lat = lats, lonStep = 1, latStep = 1, geogMask = FALSE,
#         meanThresh = 0, varThresh = 0, detrend = TRUE,
#         standardize = TRUE, nPC = NULL, method = "ward", hybrid = FALSE, kH = NULL, 
#         members = NULL, nSplit = 1, upperTri = TRUE, verbose = TRUE, 
#         validClimR = TRUE, k = num_clusters, minSize = 1, alpha = 0.01, 
#         plot = TRUE, colPalette = NULL, hang = -1, labels = FALSE)
# 
# HiClimR(new_matrix2, lon = lons, lat = lats, lonStep = 1, latStep = 1, geogMask = FALSE,
#         meanThresh = 0, varThresh = 0, detrend = TRUE,
#         standardize = TRUE, nPC = NULL, method = "ward", hybrid = FALSE, kH = NULL, 
#         members = NULL, nSplit = 1, upperTri = TRUE, verbose = TRUE, 
#         validClimR = TRUE, k = num_clusters, minSize = 1, alpha = 0.01, 
#         plot = TRUE, colPalette = NULL, hang = -1, labels = FALSE)
# 
# 
# 
# 
# 
# 
# 
# 
# 
