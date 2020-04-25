# Welcome to cv2_takeiteasy
A simple take it easy board game sum using Python &amp; cv2
The Ravensburger&trade;  Take It Easy&trade; board game is fun - but summing up the totals isn't. This little Python script does the job using OpenCV.

## Get started
You need:
* Python 2.7 +
* cv2
* imutils
* numpy
* pprint

You will get the best results with **high resolution, top-view pictures** and **good lightning conditions**. Also keep in mind that the board should be completely visible. Simple choose the picture you want to analyze using 
```python
#Import test picture
image = cv2.imread("test1.jpg")
```
and run the script. Row + total sums will be printed to the terminal. 

```
['Vertical', 2, 9, 45]
['Diagonal1', 0, 2, 6]
['Diagonal1', 2, 6, 30]
['Diagonal1', 4, 7, 21]
['Diagonal2', 0, 3, 9]
['Diagonal2', 2, 8, 40]
['Diagonal2', 3, 4, 16]
['Diagonal2', 4, 3, 9]
Total sum: 176
```
In addition, a cropped, scaled down picture of the board is shown.
![example output image](https://github.com/flojosch/cv2_takeiteasy/blob/master/examples/cropped_screenshot_25.04.2020.png)
