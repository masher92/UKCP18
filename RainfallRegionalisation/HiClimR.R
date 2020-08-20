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
 

