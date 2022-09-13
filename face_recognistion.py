import cv2, smtplib, threading, pywhatkit, awscli, time,Training_model,getpass,subprocess
import Training_model
from email.mime.text import MIMEText


# creates SMTP session
smtp = smtplib.SMTP('smtp.gmail.com', 587)
# start TLS for security
smtp.starttls()
sender_email_id=input("Enter sender's email ID for notification : ")
sender_email_id_password=getpass.getpass()
receiver_email_id=input("Enter reciever's email for notification : ")
phone=input("enter your number to get alert : ")

# create a function to send mail
def call_mail(name):
    smtp.login(sender_email_id, sender_email_id_password)
    content="ALERT: {} face was detected".format(name)
    msg = MIMEText(content)
    msg['Subject'] = 'Alert Notification'
    msg['From'] = sender_email_id
    msg['To'] = receiver_email_id
    smtp.sendmail(sender_email_id, receiver_email_id, msg.as_string())
    #smtp.quit()
    print("call_mail function called")

def call_mail2():
    time.sleep(180)
    ec2_ip_fetch='aws ec2 describe-instances --query "Reservations[*].Instances[*].PublicIpAddress" --output=text --profile umang'
    ip=subprocess.getoutput(ec2_ip_fetch)
    #smtp.login(sender_email_id, sender_email_id_password)
    content="ALERT: We started streaming the suspected person live on below url:- {}:5000".format(ip)
    msg = MIMEText(content)
    msg['Subject'] = 'Alert Notification'
    msg['From'] = sender_email_id
    msg['To'] = receiver_email_id
    smtp.sendmail(sender_email_id, receiver_email_id, msg.as_string())
    smtp.quit()


#create a fnction to send text message via whatsapp
def call_text(msg,hours,minutes):
    pywhatkit.sendwhatmsg(phone, msg, hours,minutes)
    
    

face_classifier = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

def face_detector(img, size=0.5):
    
    # Convert image to grayscale
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray, 1.3, 5)
    if faces is ():
        return img, []
    
    
    for (x,y,w,h) in faces:
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,255),2)
        roi = img[y:y+h, x:x+w]
        roi = cv2.resize(roi, (200, 200))
    return img, roi

#To get current time
t = time.localtime()
current_time = time.strftime("%H:%M", t)
hours, minutes = map(int, current_time.split(':'))
minutes=minutes+2

# Open Webcam
cap = cv2.VideoCapture(0)
i=0
j=0
while True:
    

    ret, frame = cap.read()
    
    image, face = face_detector(frame)
    
    try:
        face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

        # Pass face to prediction model
        # "results" comprises of a tuple containing the label and the confidence value
        results = Training_model.Umang_model.predict(face)
        # harry_model.predict(face)
        
        if results[1] < 500:
            confidence = int( 100 * (1 - (results[1])/400) )
            display_string = str(confidence) + '% Confident it is User'
            
        cv2.putText(image, display_string, (100, 120), cv2.FONT_HERSHEY_COMPLEX, 1, (255,120,150), 2)
        
        if confidence > 86:
            name1 = "umang"
            i=i+1
            cv2.putText(image, "Hey {}".format(name1), (250, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 2)
            cv2.imshow('Face Recognition', image )
            if(i==1):
                msg="{} 's face was detected".format(name1)
                print("known face detected")
                tr = threading.Thread(target=call_mail, args=(name1+'s',))
                tr.start()
                tr2 = threading.Thread(target=call_text, args=(msg,hours,minutes))
                tr2.start()
                print("success")
                   
        
        elif confidence > 10 and confidence < 70:
            hour2, minutes2 =map(int, current_time.split(':'))
            minutes2=minutes2 + 2
            j=j+1
            cv2.putText(image, "I dont know, how r u", (250, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,255), 2)
            cv2.imshow('Face Recognition', image )
            if(j==1):
                msg2="Suspicious face was detected"
                t1 = threading.Thread(target=call_mail, args=('Suspected',))
                t1.start()
                t2 = threading.Thread(target=call_text, args=(msg2,hour2,minutes2))
                t2.start()
                
                t3 = threading.Thread(target=awscli.aws)
                t3.start()
                print("\n Unknown face detected, We are now deploying a live streaming server on AWS and will be streaming him live soon....!!!")
                t4=threading.Thread(target=call_mail2)
                t4.start()
                print("\n Program exited wait for stream to start!")
                cap.release()
                cv2.destroyAllWindows()
                break

            
            
    except:
        cv2.putText(image, "No Face Found", (220, 120) , cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,255), 2)
        cv2.putText(image, "looking for face", (250, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,255), 2)
        cv2.imshow('Face Recognition', image )
        pass
        
    if cv2.waitKey(1) == 13: #13 is the Enter Key
        break
        
cap.release()
cv2.destroyAllWindows()     