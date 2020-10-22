#############################################
# Set up environment
#############################################
# Load in required packages
library(HiClimR)
library(dplyr)

# Specify the region for which the analysis will be conducted
region = 'Northern' #'WY' 'Northern'

# Specify lists with:
# stats: The stats to attempt regionalise with
# ems: the ensemble members with which to attempt the regionalisation
# num_clusters_list: the numbers of clusters to try splitting the region into

stats = list('Wethours/jja_p99_wh') # 'Greatest_ten'
#stats = ('99.5th Percentile', '99.9th Percentile', '99.99th Percentile', '97th Percentile', '99th Percentile', '95th Percentile') 

# Give the list of ensemble members
#ems = list('01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13','15')
ems = list('09')
# Number of clusters
num_clusters_list = list(2,3,4,5,10)


#############################################
# Find clusters
#############################################
# Loop through the different numbers of clusters, stats and ensemble members
for (num_clusters in num_clusters_list){
  for (stat in stats){
    for (em in ems){
            print (em)
            # Create the filepath
            filepath = sprintf("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/Regionalisation/HiClimR_inputdata/%s/%s/em_%s.csv", region, stat, em)
            
            # Read in data
            df <- read.csv(file = filepath)
            
            # Create coordinates as a string
            coordinates <- paste(as.character(round(df$lat, 2)), ",", as.character(round(df$lon, 2)))
            
            # Create vectors with lons and lats
            lats <- df[['lat']]
            lons <- df[['lon']]

            # Remove lat and long from the dataframe (not sure why there are 2 variables of lat/long)
            drops <- c("lat","lon", "lat.1", "lon.1", "mask")
            df = df[ , !(names(df) %in% drops)]
            
            # Testing whether sorting makes a difference - it does
            #new_matrix <- t(apply(df, 1, sort))
            
            
            #df$MeanRainfall <- rowMeans(df[2:20], na.rm=TRUE)
            #new_df <- rbind(yearlyvalues$MeanRainfall, df$Mean.Rainfall)
            #yearlyvalues <- yearlyvalues[,c("lat.1", "lon.1", "MeanRainfall")]
            #df <- yearlyvalues
            
            # Create vector from the dataframe containing the variables to regionalise on
            vect = as.vector(t(df))
            # Create matrix from the vector
            # Set the coordinate strings as the dimnames
            new_matrix = matrix(data = vect, nrow = length(lats), byrow = TRUE,
                                dimnames = list(coordinates))
            
            
            ## Conduct single-Variate Hierarchical Climate Regionalization
            y <- HiClimR(new_matrix, lon = lons, lat = lats, lonStep = 1, latStep = 1, geogMask = TRUE,
                    continent = "Europe", meanThresh = 0, varThresh = 0, detrend = TRUE,
                    standardize = TRUE, nPC = NULL, method = "ward", hybrid = FALSE, kH = NULL, 
                    members = NULL, nSplit = 1, upperTri = TRUE, verbose = TRUE, 
                    validClimR = TRUE, k = num_clusters, minSize = 1, alpha = 0.01, 
                    plot = FALSE, colPalette = NULL, hang = -1, labels = FALSE)
            
            # Get the cluster codes and save to a dataframe alongside the lat and long values
            regions = y["region"]
            regions_values = as.numeric(unlist(regions))
            regions_df <- data.frame(regions_values, lats, lons)
            
            # Save to file
            if (!(file.exists(sprintf("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/Regionalisation/HiClimR_outputdata/%s/%s/%s clusters", region, stat, num_clusters)))) 
            {  print ("Directory does not exist")
              dir.create(sprintf("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/Regionalisation/HiClimR_outputdata/%s/%s/%s clusters", region, stat, num_clusters), recursive = TRUE)
              print("Directory created")
            }
            
            print("Here")
            output_filepath = sprintf("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/Regionalisation/HiClimR_outputdata/%s/%s/%s clusters/em%s.csv", region, stat,  num_clusters, em)
            print("Here")
            unlink(output_filepath)
            write.csv(regions_df, output_filepath, row.names = FALSE)
    }
  }
}
 

