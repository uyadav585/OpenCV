import socket,cv2, pickle,struct
import subprocess
import json
import time

from numpy import intp


# test
def aws():
    sg='aws ec2 create-security-group --group-name TeamZero --description "Give Description" --vpc-id vpc-595f9832 --profile umang'
    rule1='aws ec2 authorize-security-group-ingress --group-name TeamZero --protocol tcp --port 22 --cidr 0.0.0.0/0 --profile umang'
    rule2='aws ec2 authorize-security-group-ingress --group-name TeamZero --protocol tcp --port 5000 --cidr 0.0.0.0/0 --profile umang'
    rule3='aws ec2 authorize-security-group-ingress --group-name TeamZero --protocol tcp --port 1234 --cidr 0.0.0.0/0 --profile umang'
    o=subprocess.getoutput(sg)
    sg_id = json.loads(o)
    sg_id=sg_id.get('GroupId')

    subprocess.getoutput(rule1)
    subprocess.getoutput(rule2)
    subprocess.getoutput(rule3)

    ec2="aws ec2 run-instances --image-id ami-0c1a7f89451184c8b --instance-type t2.micro --security-group-ids {} --subnet-id subnet-910ee2fa --count 1 --key-name terraform_key --user-data=file://userData.txt --profile umang".format(sg_id)
    o=subprocess.getoutput(ec2)
    inst_id=json.loads(o)
    inst_id=inst_id.get('Instances')[0].get('InstanceId')

    vol="aws ec2 create-volume --size 5 --volume-type gp2 --availability-zone ap-south-1a --profile umang"
    o=subprocess.getoutput(vol)
    vol_id=json.loads(o)
    vol_id=vol_id.get('VolumeId')

    attach="aws ec2 attach-volume --volume-id {} --instance-id {} --device /dev/sdf --profile umang".format(vol_id,inst_id)
    time.sleep(60)
    o=subprocess.getoutput(attach)
    print(o)

    

    def send_vid():
            ec2_ip_fetch='aws ec2 describe-instances --query "Reservations[*].Instances[*].PublicIpAddress" --output=text --profile umang'
            ip=subprocess.getoutput(ec2_ip_fetch)
            print(ip)
            # create socket
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            host_ip = ip
            port = 1234
            s.connect((host_ip,port)) # a tuple
            vid=cv2.VideoCapture(0)
            while True:
                    img,frame = vid.read()
                    a = pickle.dumps(frame)
                    message = struct.pack("Q",len(a))+a
                    s.sendall(message)
                    #cv2.imshow("You",frame)
                    key = cv2.waitKey(1) & 0xFF
                    if key ==ord('q'):
                            s.close()
    time.sleep(180)
    send_vid()
        