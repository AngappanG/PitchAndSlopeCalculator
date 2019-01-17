from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .forms import CustomUserCreationForm
from PitchAndSlope.core.models import PortalUser
import base64
import cv2
import numpy as np
import PitchAndSlope.settings as settings
import re
import os
import img2pdf 
from PIL import Image 

def home(request):
    return render(request, 'core/home.html')

def userHome(request):
    if 'userName' in request.session:
        userName=request.session['userName']    
        if userName:
            request.session['userName']=userName
    if 'uploadedFile' in request.session:    
        uploadedUrl=request.session["uploadedFile"]
        if uploadedUrl:
            request.session['uploadedFile']=uploadedUrl
    if 'loggedIn' in request.session:
        loggedIn=request.session['loggedIn']
        if loggedIn:
            request.session['loggedIn']=loggedIn
            
    return render(request, 'core/home.html')

def uploadImage(request):
    if request.method == 'POST' and request.FILES['document']:
        myfile = request.FILES['document']
        fs = FileSystemStorage()
        imageName = settings.MEDIA_ROOT+"\\"+myfile.name
        if os.path.exists(imageName):
            os.remove(imageName)
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        request.session["uploadedFile"]=uploaded_file_url
        return render(request, 'core/viewImage.html', {
            'uploaded_file_url': uploaded_file_url
        })
    else:
        return render(request, 'core/home.html')


def processImage(request):
    loggedIn = request.POST.get('loggedIn')
    request.session["loggedIn"]=loggedIn
    image = request.POST.get('imageString')
    dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
    image_data = dataUrlPattern.match(image).group(2)
    image_data = image_data.encode()
    image_data = base64.b64decode(image_data)
    if 'userName' in request.session:
        userName=request.session['userName']   
    imageName = settings.MEDIA_ROOT+"\processedImage_"+userName+".png"
    pdfFileName = settings.MEDIA_ROOT+"\PDF\processedImage_"+userName+".pdf"
    if os.path.exists(imageName):
        os.remove(imageName)
    with open(imageName, "wb") as fh:
        fh.write(image_data)
        fh.close()
    detectPoints(imageName)
    saveAsPDF(imageName, pdfFileName)
    request.session["uploadedFile"]="/media/processedImage_"+userName+".png"
    request.session["slopeFile"]="/media/slopeAndPitch.png"
    request.session["pdfFile"]="/media/PDF/processedImage_"+userName+".pdf"
    return render(request, 'core/processedImage.html')

def viewImage(request):
    userName=request.session["userName"]
    if userName:
        request.session["userName"]=userName
    uploadedUrl=request.session["uploadedFile"]
    if uploadedUrl:
        request.session["uploadedFile"]=uploadedUrl
    else:
        uploadedUrl = request.POST.get('uploadedUrl')
        request.session["uploadedFile"]=uploadedUrl
    loggedIn=request.session["loggedIn"]
    if loggedIn:
        request.session["loggedIn"]=loggedIn
    else:
        loggedIn = request.POST.get('loggedIn')
        request.session["loggedIn"]=loggedIn
    
    return render(request, 'core/viewImage.html')

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            uploadedUrl = request.POST.get('uploadedUrl')
            if uploadedUrl:
                request.session["uploadedFile"]=uploadedUrl
            username = request.POST.get('userId')
            request.session["loggedIn"]="Yes"
            request.session["userName"]=username
            return render(request,'core/home.html',{'message':'User Created Successfully','color':'green'})
        else:
            return render(request, 'core/signup.html', {'form': form,'message':'Error in creating the user','color':'red'})
    else:
        form = CustomUserCreationForm()
        uploadedUrl = request.POST.get('uploadedUrl')
        if not uploadedUrl:
            uploadedUrl=request.session["uploadedFile"]
        return render(request, 'core/signup.html',{'form': form,'uploadedUrl':uploadedUrl})


def processLogin(request):
    if request.method == 'POST':
        username = request.POST.get('userId')
        password = request.POST.get('password')
        uploadedUrl = request.POST.get('uploadedUrl')
        if not uploadedUrl:
            uploadedUrl=request.session["uploadedFile"]
        if username and password:
            user = PortalUser.objects.filter(userId=username,password=password)
            if user:
                request.session["loggedIn"]="Yes"
                request.session["userName"]=username
                request.session["uploadedFile"]=uploadedUrl
                return render(request, 'core/viewImage.html', {'message':'Welcome '+username})
            else:
                return render(request, 'core/signup.html', {'message':'Invalid Username or password.','color':'red'}) 
        else:
            return render(request, 'core/signup.html', {'message':'Invalid Username or password.','color':'red'})
    else:
        return render(request, 'core/signup.html')

def logout(request):
    if 'userName' in request.session:
        userName=request.session['userName']
    
    return
    
def saveImage(request):
    if request.method == 'GET':
        return viewImage(request)
    elif request.method == 'POST':
        filename = request.POST['save_fname']
        image = request.POST['save_image']
        with open(filename, "wb") as fh:
            fh.write(base64.decodebytes(image))
        request.session["uploadedFile"]=filename
        return viewImage(request)

def detectPoints(imageName):
    img_rgb = cv2.imread(imageName)
    height, width = img_rgb.shape[:2]
    #for i in range(0,img_rgb.shape[0]):
        #for j in range(0,img_rgb.shape[1]):
            #pixel = img_rgb.item(i, j)
            #print(pixel
    points = [[0,0],[0,0],[0,0]]
    ptCnt = 0
    xRange = 0;
    yRange = 0;
    image_data = np.asarray(img_rgb)
    for i in range(len(image_data)):
        if(i > yRange):
            xRange = 0
        for j in range(len(image_data[0])):
            #Check for red pixel
            if(image_data[i][j][0]==0 and image_data[i][j][1]== 0 and image_data[i][j][2]==255):
                if((j > xRange) and i > yRange and ptCnt<3):
                    count = 0;
                    for x in range(i,i+10):
                        for y in range(j,j+10):
                            if(image_data[x][y][0]==0 and image_data[x][y][1]== 0 and image_data[x][y][2]==255):
                                count += 1; 
                            else:
                                break
                    
                    #to consider there is a group of red pixels around he current point
                    if count > 10:
                        if(ptCnt <= 2):
                            addPt = True
                            yPos = i;
                            for pt in points:
                                #skip the condition if there is no points identified earlier
                                if (pt[0] == 0 and pt[1] == 0):
                                    continue
                                #Add the point if it doesn't falling under the current dot region 
                                elif(pt[1]+15 < i or pt[0]+15 < j or pt[0]-15 > j):
                                    addPt = True
                                    if(pt[1]+15 > i):
                                        yPos = pt[1]
                                else:
                                    addPt = False
                            if(addPt == True):
                                if(yPos == i):
                                    points[ptCnt] = [j+5,i+5]
                                else:
                                    points[ptCnt] = [j+5,yPos]
                                ptCnt += 1
                                xRange = j+15
                                if(ptCnt==1):
                                    yRange = i+15
    points = tuple(points)
    print(points)
    x1 = points[0][0]
    x2 = points[1][0]
    x3 = points[2][0]
    y1 = points[0][1]
    y2 = points[1][1]
    y3 = points[2][1]
    minX = 0
    maxX = 0
    
    minY = 0
    maxY = 0
    
    if (x1 >= x2) and (x1 >= x3):
        maxX = x1
    elif (x2 >= x1) and (x2 >= x3):
        maxX = x2
    else:
        maxX = x3
        
    if (x1 <= x2) and (x1 <= x3):
        minX = x1
    elif (x2 <= x1) and (x2 <= x3):
        minX = x2
    else:
        minX = x3
        
    riseX = minX +int((maxX-minX)/2)
        
    if (y1 >= y2) and (y1 >= y3):
        maxY = y1
    elif (y2 >= y1) and (y2 >= y3):
        maxY = y2
    else:
        maxY = y3
        
    if (y1 <= y2) and (y1 <= y3):
        minY = y1
    elif (y2 <= y1) and (y2 <= y3):
        minY = y2
    else:
        minY = y3
    
    riseY = minY +int((maxY-minY)/2)
    
    slope = (maxY-minY)/(riseX - minX)
    #slopePt = (int(points[0][0]/2),int(points[1][1]/2))
    print("Slope of the house")
    print(slope)
    pitch = slope/2
    print("Pitch of the house")
    print(pitch)
    #i=0
    #while i < len(points)-1:
    #cv2.line(img_rgb, tuple(points[i]),tuple(points[i+1]), (0,255,255), 2)
    #i = i+1
    cv2.line(img_rgb, (minX,maxY),(riseX,minY), (0,255,255), 2)
    cv2.line(img_rgb, (minX,maxY),(maxX,maxY), (0,255,255), 2)
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.line(img_rgb, (riseX,minY),(riseX,maxY), (0,255,0), 2)
    cv2.putText(img_rgb,'Rise='+str(int(maxY-minY)),(riseX+2,riseY+2), font, 0.5,(255,255,0),2,cv2.LINE_AA)
    cv2.putText(img_rgb,'Run='+str(int((maxX-minX)/2)),(minX+5,maxY+20), font, 0.5,(255,255,0),2,cv2.LINE_AA)
    cv2.putText(img_rgb,'Span='+str(int(maxX-minX)),(minX+int((maxX-minX)/2),maxY+35), font, 0.5,(255,255,0),2,cv2.LINE_AA)
    cv2.putText(img_rgb,'Slope = (Rise/Run) = '+str("%.2f" % slope),(20,int((height/2)+30)), font, 0.5,(255,255,0),2,cv2.LINE_AA)
    cv2.putText(img_rgb,'Pitch = (Rise/Span) = '+str("%.2f" % pitch),(20,int((height/2)+50)), font, 0.5,(255,255,0),2,cv2.LINE_AA)
    cv2.imwrite(imageName,img_rgb)
    return
    

def saveAsPDF(imageName,pdfFileName):
  
    # storing image path 
    image = Image.open(imageName) 
    if os.path.exists(pdfFileName):
        os.remove(pdfFileName)
    # converting into chunks using img2pdf 
    pdf_bytes = img2pdf.convert(image.filename) 
      
    # writing pdf files with chunks 
    with open(pdfFileName, "wb") as fh:
        fh.write(pdf_bytes)
        fh.close()
    # closing image file 
    image.close() 
      
