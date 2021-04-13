### Multi-variate Analysis
#### Examining relationship between catchment rainfall (FEH13) and catchment descriptors

For FEH13 precipitation with a 25h duration and 10 year return period:

<ins> Pearson's R Correlation Coefficient </ins>  

The Pearson's R correlation coefficient quantifies how strongly two variables are related. The correlation between various catchment descriptors and the 10 year return period 25 hour duration rainfall amount is shown below.

| Variable   | Correlation |
|------------|-------|
| Northing   | 0.9   |
| SAAR       | 0.81  |
| ALTBAR     | 0.67  |
| DPSBAR     | 0.6   |
| Easting    | -0.52 |
| PROPWET    | 0.49  |
| FARL       | -0.34 |
| BFIHOST    | -0.3  |
| URBEXT2000 | 0.15  |
| AREA       | -0.1  |
| LDP        | -0.02 |

<ins> Linear Regression </ins>  
The relationship between a response variable (y) and a predictor variable (x) can also be described as the regression of y on x, and can be represented in a regression equation.

The R2 coefficient of determination is a statistical measure of how well the regression predictions approximate the real data points. The R2 value is equivalent to the square of the Pearson's R correlation coefficient (e.g. 0.9*0.9 = 0.81).

The adjusted R2 is a modified version of R-squared that has been adjusted for the number of predictors in the model. The adjusted R-squared increases when the new term improves the model more than would be expected by chance. It decreases when a predictor improves the model by less than expected. Typically, the adjusted R-squared is positive, not negative. It is always lower than the R-squared (this is because adding more variables always increases the R2).

<p align="center">
  <img src="Figs/ols_Northing.png" width="500"  />  
<p align="center"> Northing <p align="center">

<p align="center">
  <img src="Figs/ols_saar.png" width="500"  />  
<p align="center"> SAAR <p align="center">

<p align="center">
  <img src="Figs/ols_altbar.png" width="500"  />  
<p align="center"> ALTBAR <p align="center">

<ins> Mutlivariate Linear Regression </ins>  
The univariate models above help to understand the variables which alone are best at describing the response variable. However, generally, most response variables depend on multiple predictor variables in a complex manner. A multiple regression can be performed to show the effect of each variable in the equation, after controlling for all the other variables in the equation (rather than only examining the relationship between a pair variables at a time). Basically, trying to ascertain which combination of predictor variables best explains the response variable.

<p align="center">
<img src="Figs/ols_northing_saar.png" width="500"  />  
<p align="center"> Northing and SAAR <p align="center">

<p align="center">
  <img src="Figs/ols_altbar_northing.png" width="500"  />  
<p align="center"> Northing and ALTBAR <p align="center">

Northing had the highest R2 value in a univariate analysis. However, including either SAAR or ALTBAR increases the adjusted R2 value, indicating that whilst both SAAR and ALTBAR are strongly correlated with Northing, there is an influence of both which is not adequately captured through just including Northing.

<p align="center">
<img src="Figs/ols_saar_altbar.png" width="500"  />  
<p align="center"> SAAR and ALTBAR <p align="center">

The adjusted R2 value for SAAR and ALTBAR is higher than when either of these two variables were used alone in a univariate analysis. However, the adjusted R2 value is lower than when Northing alone was used. This indicates that Northing has an important influence on rainfall that is not related to its relationship with either SAAR or ALTBAR.

<p align="center">
<img src="Figs/ols_saar_altbar_northing.png" width="500"  />  
<p align="center"> Northing, SAAR and ALTBAR <p align="center">

Including all three variables, the adjusted R2 value (0.888) is lower than when just Northing and SAAR were used (0.895), and only marginally higher than when Northing and ALTBAR were used (0.884). This indicates that the inclusion of either SAAR or ALTBAR as a third variable does not improve the model.

Significant values indicate that neither SAAR or ALTBAR are significant variables;  However, previously have showed that both of them improve on using just Northing alone!?

HOWEVER:

Including ALL the variables, leads to the highest adjusted R2 value. Despite this, various variables have a non-Significant p value.

<p align="center">
<img src="Figs/ols_allvars.png" width="500"  />  
<p align="center"> Northing, SAAR and ALTBAR <p align="center">

But, removing these non-significant variables leads to a lower adjusted R2 score. This could be because whilst the response variable is not significantly dependent upon these predictor variables (and altering them won't have a significant impact), they may still have a minor and insignificant correlation with the response variable and so cause an increase in the R2 value.

<p align="center">
<img src="Figs/ols_allvars_remove_nonsig.png" width="500"  />  
<p align="center"> Northing, SAAR and ALTBAR <p align="center">


### Adjusted R2 values

dfdd

<p align="center">
<img src="Figs/ols_pairwiseadjR2.png" width="650"  />  
<p align="center">  <p align="center">
