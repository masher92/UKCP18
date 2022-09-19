Introduction
============

This script provides an R equivalence of the RandomForest algorithm in `LCC_Footfall.ipynb`, used in the predictive analysis of footfall datasets. The goal of this module is to compare the performance of the R version with the Python version, before its integration into a web-based tool designed for daily prediction of footfall data in Leeds City Centre.

This module jumped to the `Create Validation Data Set` section of the `LCC_Footfall.ipynb`. In other words, an already prepared dataset is used here.

``` r
#Importing cleaned (processed) datasets and preview
data <- read.table(file="//ds.leeds.ac.uk/staff/staff7/geomad/GitHub/lcc-footfall/Cleaned_Dataset/input_Dataset.csv", sep=",",head=TRUE)

#previewing first 5 rows and 5 columns of the dataset
head(data)[1:5,1:5]
```

    ##   InCount school_holiday uni_holiday bank_hols easter_sunday
    ## 1  115685              1           1         0             0
    ## 2  160658              1           1         1             0
    ## 3  165334              1           1         0             0
    ## 4  135127              0           1         0             0
    ## 5  148253              0           1         0             0

``` r
print(paste("Data summary: no. of rows = ",nrow(data),"; no. of column = ",ncol(data), sep = ""))
```

    ## [1] "Data summary: no. of rows = 2122; no. of column = 83"

``` r
#subsetting the predictors
Xfull <- subset(data, select=-c(InCount)) 
xname <- colnames(Xfull)

#subsetting the dependent variable (footfall count)
Yfull <-data[,1]
yname <- c("y")

#merge as dataframe
XYfull <- as.data.frame(cbind(Xfull, Yfull))
colnames(XYfull) <- c(xname, yname)

#partitioning the dataset into training and testing sets
set.seed(123)
inTraining <- createDataPartition(XYfull$y, p = .66666, list = FALSE)
training_set <- XYfull[inTraining,] 
testing_set  <- XYfull[-inTraining,]

#Run a k-fold cross validation using the "training_set" (66.66% partition). 
#Combine k-1 subsets in turns, and predict the last (kth) subset
#Each time, compute the Median R2, Median, and predictive accuracy.

#First, randomise the dataset
training_set<- training_set[sample(nrow(training_set)),]

folds <- cut(seq(1,nrow(training_set)), breaks=10, labels=FALSE)
training_set$holdoutpred <- rep(0,nrow(training_set)) #nrow(training)

k =10;

result_List <- matrix(0, k, 6)

for(i in 1:k){ # i = 1

  subset_train <- subset(training_set, select=-c(holdoutpred)) 
  train <- subset_train[(folds != i), ] #Set the training set nrow(train)
  validation <- subset_train[(folds == i), ] #Set the validation set, #nrow(validation)

  #using Regression method
  regre_model <- lm(y~.,data=train) 
  mse_1 <- mean(regre_model$residuals^2)
  r2_1 <- summary(regre_model)$adj.r.squared
  #newpred <- predict(regre_model, newdata=validation)
  #corr_acc_1 <- cor(data.frame(cbind(validation$y, newpred)))
  result_List[i,1] <- mse_1
  result_List[i,2] <- r2_1
  #result_List[i,3] <- corr_acc_1[1,2]

  ##Using randomForest algorithm
  randomForest <- randomForest(y ~., data=train)
  mse_2 <- mean(randomForest$mse)
  r2_2 <- mean(randomForest$rsq)
  #predict_Random <- predict(randomForest, validation)
  #corr_acc_2 <- cor(data.frame(cbind(validation$y, as.vector(predict_Random))))
  result_List[i,4] <- mse_2
  result_List[i,5] <- r2_2
  #result_List[i,6] <- corr_acc_2[1,2]

 }

#Feature importance.

print(paste("Regression: mse = ", mean(result_List[i,1]), "r2 = ", mean(result_List[i,2]), "pred_acc = ", mean(result_List[i,3])) )
```

    ## [1] "Regression: mse =  298662924.423021 r2 =  0.787098092834183 pred_acc =  0"

``` r
print(paste("RandomForest: mse = ", mean(result_List[i,4]), "r2 = ", mean(result_List[i,5]), "pred_acc = ", mean(result_List[i,6])) ) 
```

    ## [1] "RandomForest: mse =  301163799.369455 r2 =  0.798975561498177 pred_acc =  0"

``` r
#fgl.res <- tuneRF(subset(train, select=-c(y)), train[,ncol(train)], stepFactor=1.5)
#randomForest <- randomForest(y ~., data=train, importance=TRUE)
#importance(randomForest, type=1)[1:10,]
```

Hypterparameter tuning to be included....

Work in progress....
