## Visualising data distributions

There is no definitive distribution for a set of data.


<p align="center">
  <img src="Figs/Example_histogram.PNG" width="400" />
  <img src="Figs/Example_smoothedhistogram.PNG" width="400"/>
</p>
<p align="center"> Figure 1. Histogram (left) and smoothed density plot (right) <p align="center">

Histogram:
* Divide the data range into non-overlapping bins of same size
* For each bin, count the number of values that fall into that interval

Smoothed density plot:
* No sharp edges on interval boundaries; local peaks removed
* Scale on y-axis changed from counts to density

Assume we are constructing our plot from a list of observed values and that this list is only a subset of all values
If we had lots of values, we could make the bin size smaller and smaller, and the histogram would become more and more like a curve
BUT we don't have all the data, so can't make lots and lots of bins

The axis of a smoothed density plot is designed so that the area under the curve equals 1.

---
A PDF is the continuous version of the histogram with densities (imagine infantessimile small bin widths). It specifies how the probability density is spread out over the range of values that a random variable can take.

----
A PDF is constructed by drawing a smooth curve fit through the vertically nromalised histograms. You can tink of a PDF as the smooth limit of a vertically normalised histogram if there were millions of measurements and a huge number of bins. 
A histogram involves discrete data
A PDF involves continuous data (a smooth curve)
Usefulness of PDF:
We can find the probability that a value lies between a and b, by finding the area under the curve between a and b. 

---
https://machinelearningmastery.com/probability-density-estimation/
Probabiltiy density is the relationship between observations and their probability. 
The overall shape of the probability density is referred to as a probability distribution. 

For a random variable we do not know the probability distribution because we don't have access to all possible outcomes for a random variable. We just have a sample of observations. So, we must do probability density estimation. Using the observations in a sample to estimate the general density of probabilities beyond just the sample of data we have. 

Few steps in process of density estimation:
1st -- review the density of observations in the sample with a histogram. This may identify that the data follows a common and well-understood distribtuion. 

Histogram -- grouping the observations into bins and counting the number of events the fall into each bin. The counts of frequencies of observations in each bin are then plotted as a bar graph. The number of bins controls the coarseness of the distribution. 

---
Sparse data problem -- many events that are plausible in reality are not found in the data used to estimate probabilities.

----
Sometimes need to use bins of different widths ;;
When classes are allowed to vary in size we need to make some adjustments to the concept of a histogram. When classes have unequal widths the vertical axis must not represent frequency (number of occurrences) but frequency density (frequency divided by class width)

If data does not resemble a common probability distribution


---
- Histogram of frequency
- Convert to histogram of density
- COnvert from discrete to continuous distribution


--
If we had enough data we could continue to create histograms with smaller and smaller ranges to get a more refined picture of the distribution of the data.  

--
When grouping continuous data, it may be necessary to have different class widths if the data are not equally spaced out. When class widths are not equal the y-axis must be density.
Frequency density = frequency/class width.
----
The outout of a probability density function is not a probability. 
TO get the probabiltiy from a PDF we need to find the area under the curve
In continuous PDFs the probability of the random variable being equal to a specific outcome is 0. Can only talk about probbilities between two values. 

A probability distribution is a lit of outcomes and their associated probabilities
We can write small distributions with tables but with large distributions its easier to summarise with functions
