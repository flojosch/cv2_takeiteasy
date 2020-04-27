# Welcome to cv2_takeiteasy
A simple take it easy board game sum using Python &amp; cv2
The Ravensburger&trade;  Take It Easy&trade; board game is fun - but summing up the totals isn't. This little Python script does the job using OpenCV.

## Get started
You need:
* Python 2.7 +
* cv2
* imutils
* numpy
* flask
* pprint

You will get the best results with **high resolution, top-view pictures** and **good lightning conditions**. Also keep in mind that the board should be completely visible. To get started, export the flask app:
```python
export FLASK_APP=tie.py
```
and start it:
```python
python -m flask run
```

You should see a simple upload page. JPG & PNG files are supported.
You will see the total sum + complete row information. Row + total sums will also be printed to the terminal. 

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
![example output image](https://github.com/flojosch/cv2_takeiteasy/blob/master/examples/example_2.png)
