from flask import Flask, redirect, render_template, request, url_for, send_from_directory
import os
import cv2
import numpy as np
import imutils
from pprint import pprint
from werkzeug.utils import secure_filename

app = Flask(__name__)
if __name__ == "__main__":
    app.run(host='0.0.0.0')

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)),"static/img/uploads")
app.config["DEBUG"] = True
app.config["IMAGE_UPLOADS"] = UPLOAD_FOLDER
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG"]
comments = []

#check if uploaded image is supported
def allowed_image(filename):
    if not "." in filename:
        return False
    ext = filename.rsplit(".", 1)[1]
    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False
#find playing field
def findFieldCnt(cnts):
    primaryCnt=[]
    global rect
    global box
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.015 * peri, True)
        hull = cv2.convexHull(c)
        hullArea = cv2.contourArea(hull)
        (x, y, w, h) = cv2.boundingRect(approx)
        aspectRatio = w / float(h)
        if hullArea>20000 and aspectRatio>0.95 and aspectRatio<1.05:
            rect = cv2.minAreaRect(approx)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            primaryCnt=c
            #cv2.drawContours(image2,[box],0,(0,0,255),8)
            break
    if primaryCnt==[]:
        print("No playing field detected")
    return primaryCnt
#warp cropped image to bounding box
def warpCropimage(img, rect):
    width = int(rect[1][0])
    height = int(rect[1][1])
    angle =round(int(rect[2]),-1)
    #print(rect,angle)
    src_pts = box.astype("float32")
    # corrdinate of the points in box points after the rectangle has been straightened
    dst_pts = np.array([[0, height-1],
                        [0, 0],
                        [width-1, 0],
                        [width-1, height-1]], dtype="float32")

    # the perspective transformation matrix
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    # directly warp the rotated rectangle to get the straightened rectangle
    warped = cv2.warpPerspective(img, M, (width, height))
    #rotate picture if angle is weird
    if angle!=0.0:
        warped=cv2.rotate(warped, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return warped
#find numbers (color)
def findVerticals(warped_img,rotation):
    # find the colors within the specified boundaries and apply mask
    vnmbrs=[]
    global height
    global width
    warped_img=imutils.rotate(warped_img,rotation)
    #cv2.imshow("test",cv2.resize(warped_img, (0,0), fx=0.2, fy=0.2))
    vmask = np.zeros(warped_img.shape[:2],np.uint8)
    hmask = np.zeros(warped_img.shape[:2],np.uint8)
    height = warped_img.shape[0]
    width = warped_img.shape[1]
    #build columns, apply mask
    for i in range(0,5):
        vmask[int(height*0.02):int(height*0.96),int(width*0.14+int(i*width*0.16)):int(width*0.23+int(i*width*0.16))]=255
        masked_image=cv2.bitwise_and(warped_img,warped_img,mask = vmask)
        #build rows, apply mask
        for j in range(0,5):
            submask=masked_image
            if i in (0,4):
                #print("klein")
                #cv2.rectangle(img_croped, (int(width*0.1),int(height*0.05+int(j*height*0.19))),(int(width*0.9),int(height*0.24+int(j*height*0.19))),(0,0,255), 10)
                hmask[int(height*0.05+int(j*height*0.19)):int(height*0.24+int(j*height*0.19)),int(width*0.1):int(width*0.9)]=255
            elif i in (1,3):
                #print("medium")
                #cv2.rectangle(img_croped, (int(width*0.1),int(height*0.14+int(j*height*0.19))),(int(width*0.9),int(height*0.34+int(j*height*0.19))),(255,0,0), 10)
                hmask[int(height*0.14+int(j*height*0.19)):int(height*0.34+int(j*height*0.19)),int(width*0.1):int(width*0.9)]=255
            else:
                #print("gross")
                #cv2.rectangle(img_croped, (int(width*0.1),int(height*0.05+int(j*height*0.19))),(int(width*0.9),int(height*0.24+int(j*height*0.19))),(0,0,255), 10)
                hmask[int(height*0.05+int(j*height*0.19)):int(height*0.24+int(j*height*0.19)),int(width*0.1):int(width*0.9)]=255
            submask=cv2.bitwise_and(submask,submask,mask = hmask)
            #print(str(i+1)+"/"+str(j+1)+" = "+str(checkForNumber(submask)))
            vnmbrs.append([i,j,checkForNumber(submask,rotation)])
            hmask = np.zeros(warped_img.shape[:2],np.uint8)
        #cv2.rectangle(img_croped, (int(width*0.14+int(i*width*0.16)),int(height*0.02)),(int(width*0.23+int(i*width*0.16)),int(height*0.96)),(0,255,0), 10)
        vmask = np.zeros(warped_img.shape[:2],np.uint8)
    return vnmbrs
#check for Number in masked image fragment
def checkForNumber(masked_img,i):
    if i==0:
        results=[9,5,1]
        threshold=width*4
        mask_1 = cv2.inRange(masked_img, np.array([70, 200, 200], dtype = "uint8"), np.array([150, 255, 255], dtype = "uint8")) #9
        mask_2 = cv2.inRange(masked_img, np.array([150, 100, 0], dtype = "uint8"), np.array([210, 190, 30], dtype = "uint8"))#5
        mask_3 = cv2.inRange(masked_img, np.array([120, 120, 120], dtype = "uint8"), np.array([230, 230, 200], dtype = "uint8"))#1
    if i==60:
        results=[7,6,2]
        threshold=width*2.5
        mask_1 = cv2.inRange(masked_img, np.array([60, 150, 130], dtype = "uint8"), np.array([130, 255, 190], dtype = "uint8")) #7
        mask_2 = cv2.inRange(masked_img, np.array([25, 25, 100], dtype = "uint8"), np.array([80, 80, 255], dtype = "uint8"))#6
        mask_3 = cv2.inRange(masked_img, np.array([175, 175, 190], dtype = "uint8"), np.array([240, 240, 240], dtype = "uint8"))#2
    if i==-60:
        results=[8,4,3]
        threshold=width*2.5
        mask_1 = cv2.inRange(masked_img, np.array([20, 100, 180], dtype = "uint8"), np.array([80, 200, 255], dtype = "uint8")) #8
        mask_2 = cv2.inRange(masked_img, np.array([200, 160, 0], dtype = "uint8"), np.array([255, 230, 50], dtype = "uint8"))#4
        mask_3 = cv2.inRange(masked_img, np.array([160, 100, 190], dtype = "uint8"), np.array([230, 160, 255], dtype = "uint8"))#3
    # debug = cv2.bitwise_and(masked_img, masked_img, mask = mask_3)
    # cv2.imshow("test",cv2.resize(debug, (0,0), fx=0.2, fy=0.2))
    # cv2.waitKey(0)
    cnts = cv2.findContours(mask_1.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:2]
    hullArea=0
    for c in cnts:
        hull = cv2.convexHull(c)
        hullArea = hullArea+cv2.contourArea(hull)
        if hullArea>threshold:
            return results[0]
            break
    cnts2 = cv2.findContours(mask_2.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cnts2 = imutils.grab_contours(cnts2)
    cnts2 = sorted(cnts2, key = cv2.contourArea, reverse = True)[:2]
    hullArea=0
    for x in cnts2:
        hull = cv2.convexHull(x)
        hullArea = hullArea+cv2.contourArea(hull)
        if hullArea>threshold:
            return results[1]
            break
    cnts3 = cv2.findContours(mask_3.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cnts3 = imutils.grab_contours(cnts3)
    cnts3 = sorted(cnts3, key = cv2.contourArea, reverse = True)[:3]
    hullArea=0
    for y in cnts3:
        hull = cv2.convexHull(y)
        hullArea = hullArea+cv2.contourArea(hull)
        if hullArea>threshold:
            return results[2]
            break
#find consecutive rows
def findCompleteRows(array,orientation):
    completeRows=[]
    #pprint(array)
    if (array[1][2]!=None and array[1][2]==array[2][2]==array[3][2]):
        #print("Row of "+str(array[1][2]) + " detected")
        completeRows.append([orientation,0,array[1][2],int(3*array[1][2])])
    if (array[5][2]!=None and array[5][2]==array[6][2]==array[7][2]==array[8][2]):
         #print("Row of "+str(array[5][2]) + " detected")
         completeRows.append([orientation,1,array[5][2],int(4*array[5][2])])
    if (array[10][2]!=None and array[10][2]==array[11][2]==array[12][2]==array[13][2]==array[14][2]):
          #print("Row of "+str(array[10][2]) + " detected")
          completeRows.append([orientation,2,array[10][2],int(5*array[10][2])])
    if (array[15][2]!=None and array[15][2]==array[16][2]==array[17][2]==array[18][2]):
         #print("Row of "+str(array[16][2]) + " detected")
         completeRows.append([orientation,3,array[16][2],int(4*array[16][2])])
    if (array[21][2]!=None and array[21][2]==array[22][2]==array[23][2]):
         #print("Row of "+str(array[22][2]) + " detected")
         completeRows.append([orientation,4,array[22][2],int(3*array[22][2])])
    return completeRows
#draw bounding boxes
def drawBoxes(rows,img_croped):
    font = cv2.FONT_HERSHEY_DUPLEX
    for r in rows:
        for s in r:
            if s[0]=="Diagonal1":
                box = cv2.boxPoints(((width*0.27+int(s[1]*width*0.12),height*0.27+int(s[1]*height*0.12)), (width*0.09, height*0.98), 60))
                box = np.int0(box)
                cv2.drawContours(img_croped,[box],0,(0,0,255),8)
                #cv2.putText(img_croped, str(s[3]), (int(width*0.9),int(height*0.8)+int(s[1]*height*0.03)), font, 3, (0,0,255),5)
                continue
            if s[0]=="Diagonal2":
                box = cv2.boxPoints(((width*0.4+int(s[1]*width*0.06),height*0.85-int(s[1]*height*0.16)), (width*0.09, height*0.98), -60))
                box = np.int0(box)
                cv2.drawContours(img_croped,[box],0,(255,255,0),8)
                #cv2.putText(img_croped, str(s[3]), (int(width*0.9),int(height*0.05)+int(s[1]*height*0.03)), font, 3, (255,255,0),5)
                continue
            cv2.rectangle(img_croped, (int(width*0.14+int(s[1]*width*0.16)),int(height*0.02)),(int(width*0.23+int(s[1]*width*0.16)),int(height*0.96)),(0,255,0), 10)
            #cv2.putText(img_croped, str(s[3]), (int(width*0.16+int(s[1]*width*0.16)), int(height*0.94)), font, 3, (0,255,0),5)
    return(img_croped)
#print results
def printResults(rows):
    sum=0
    for r in rows:
        for s in r:
            print s
            sum=sum+s[3]
    print("Total sum: "+str(sum))
    return sum


@app.route("/")
def index():
    return render_template("upload_image.html")

@app.route("/upload-image", methods=["GET", "POST"])
def upload_image():
    if request.method == "POST":
        if request.files:
            image = request.files["image"]
            if image.filename == "":
                print("No filename")
                return redirect(request.url)
            if allowed_image(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config["IMAGE_UPLOADS"], filename))
                image2 = cv2.imread(os.path.join(app.config["IMAGE_UPLOADS"], filename))

                print("Image saved: "+filename)
                # find the colors within the specified boundaries and apply mask
                lower = np.array([30, 10, 0], dtype = "uint8")
                upper = np.array([255, 80, 50], dtype = "uint8")
                mask = cv2.inRange(image2, lower, upper)
                output = cv2.bitwise_and(image2, image2, mask = mask)
                rows = []

                #detect 10 largest contours in blue filter mask
                cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
                cnts = imutils.grab_contours(cnts)
                cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]

                # loop over our contours and crop image to roi
                fieldCnt=findFieldCnt(cnts)
                if fieldCnt==[]:
                    return render_template("success.html", filename=filename)
                img_croped = warpCropimage(image2, rect)
                verts=findVerticals(img_croped,0)
                diags1=findVerticals(img_croped,60)
                diags2=findVerticals(img_croped,-60)
                rows.append(findCompleteRows(verts,"Vertical"))
                rows.append(findCompleteRows(diags1,"Diagonal1"))
                rows.append(findCompleteRows(diags2,"Diagonal2"))
                sum=printResults(rows)
                img_croped=drawBoxes(rows,img_croped)
                cropped_filename=(filename.rsplit(".", 1)[0]+"_cropped.jpg")
                cv2.imwrite(os.path.join(UPLOAD_FOLDER,cropped_filename),img_croped)

                #redirect to success page
                return render_template("success.html", filename=cropped_filename, sum=sum, rows=rows)
            else:
                print("That file extension is not allowed")
                return redirect(request.url)
    return render_template("upload_image.html")

@app.route('/show/<filename>')
def uploaded_file(filename):
    filename = 'http://127.0.0.1:5000/uploads/' + filename
    print(filename)
    return render_template("upload_image.html")

@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
