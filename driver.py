#coding:utf-8
'''
树莓派WiFi无线视频小车机器人驱动源码
作者：liuviking
版权所有：小R科技（深圳市小二极客科技有限公司）；WIFI机器人网论坛 www.wifi-robots.com
本代码可以自由修改，但禁止用作商业盈利目的！
本代码已申请软件著作权保护，如有侵权一经发现立即起诉！
'''
import os
from socket import *
from time import ctime
import binascii
import RPi.GPIO as GPIO
import time
import threading
from smbus import SMBus
import cv2
import numpy as np
from subprocess import call

XRservo = SMBus(1)
#print ('....WIFIROBOTS START!!!...')
global Path_Dect_px
Path_Dect_px = 320
global Path_Dect_on
Path_Dect_on = 0

#######################################
#############信号引脚定义##############
#######################################
GPIO.setmode(GPIO.BCM)

########LED口定义#################
LED0 = 10
LED1 = 9
LED2 = 25

########电机驱动接口定义#################
ENA = 13	#//L298使能A
ENB = 20	#//L298使能B
IN1 = 19	#//电机接口1
IN2 = 16	#//电机接口2
IN3 = 21	#//电机接口3
IN4 = 26	#//电机接口4

########舵机接口定义#################

########超声波接口定义#################
ECHO = 4	#超声波接收脚位  
TRIG = 17	#超声波发射脚位

########红外传感器接口定义#################
IR_R = 18	#小车右侧巡线红外
IR_L = 27	#小车左侧巡线红外
IR_M = 22	#小车中间避障红外
IRF_R = 23	#小车跟随右侧红外
IRF_L = 24	#小车跟随左侧红外
global Cruising_Flag
Cruising_Flag = 0	#//当前循环模式
global Pre_Cruising_Flag
Pre_Cruising_Flag = 0 	#//预循环模式

global RevStatus
RevStatus = 0
global TurnAngle
TurnAngle=0;
global Golength
Golength=0
buffer = ['00','00','00','00','00','00']
global motor_flag
motor_flag=1


global left_speed
global right_speed
global left_speed_hold
global right_speed_hold
left_speed=100
right_speed=100
#######################################
#########管脚类型设置及初始化##########
#######################################
GPIO.setwarnings(False)

#########led初始化为000##########
GPIO.setup(LED0,GPIO.OUT,initial=GPIO.HIGH)
GPIO.setup(LED1,GPIO.OUT,initial=GPIO.HIGH)
GPIO.setup(LED2,GPIO.OUT,initial=GPIO.HIGH)

#########电机初始化为LOW##########
GPIO.setup(ENA,GPIO.OUT,initial=GPIO.LOW)
ENA_pwm=GPIO.PWM(ENA,1000) 
ENA_pwm.start(0) 
ENA_pwm.ChangeDutyCycle(100)
GPIO.setup(IN1,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(IN2,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(ENB,GPIO.OUT,initial=GPIO.LOW)
ENB_pwm=GPIO.PWM(ENB,1000) 
ENB_pwm.start(0) 
ENB_pwm.ChangeDutyCycle(100)
GPIO.setup(IN3,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(IN4,GPIO.OUT,initial=GPIO.LOW)



#########红外初始化为输入，并内部拉高#########
GPIO.setup(IR_R,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(IR_L,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(IR_M,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(IRF_R,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(IRF_L,GPIO.IN,pull_up_down=GPIO.PUD_UP)



##########超声波模块管脚类型设置#########
GPIO.setup(TRIG,GPIO.OUT,initial=GPIO.LOW)#超声波模块发射端管脚设置trig
GPIO.setup(ECHO,GPIO.IN,pull_up_down=GPIO.PUD_UP)#超声波模块接收端管脚设置echo



####################################################
##函数名称 Open_Light()
##函数功能 开大灯LED0
##入口参数 ：无
##出口参数 ：无
####################################################
def	Open_Light():#开大灯LED0
	GPIO.output(LED0,False)#大灯正极接5V  负极接IO口
	time.sleep(1)


####################################################
##函数名称 Close_Light()
##函数功能 关大灯
##入口参数 ：无
##出口参数 ：无
####################################################
def	Close_Light():#关大灯
	GPIO.output(LED0,True)#大灯正极接5V  负极接IO口
	time.sleep(1)
	
####################################################
##函数名称 init_light()
##函数功能 流水灯
##入口参数 ：无
##出口参数 ：无
####################################################
def	init_light():#流水灯
	for i in range(1, 5):
		GPIO.output(LED0,False)#流水灯LED0
		GPIO.output(LED1,False)#流水灯LED1
		GPIO.output(LED2,False)#流水灯LED2
		time.sleep(0.5)
		GPIO.output(LED0,True)#流水灯LED0
		GPIO.output(LED1,False)#流水灯LED1
		GPIO.output(LED2,False)#流水灯LED2
		time.sleep(0.5)
		GPIO.output(LED0,False)#流水灯LED0
		GPIO.output(LED1,True)#流水灯LED1
		GPIO.output(LED2,False)#流水灯LED2
		time.sleep(0.5)
		GPIO.output(LED0,False)#流水灯LED0
		GPIO.output(LED1,False)#流水灯LED1
		GPIO.output(LED2,True)#流水灯LED2
		time.sleep(0.5)
		GPIO.output(LED0,False)#流水灯LED0
		GPIO.output(LED1,False)#流水灯LED1
		GPIO.output(LED2,False)#流水灯LED2
		time.sleep(0.5)
		GPIO.output(LED0,True)#流水灯LED0
		GPIO.output(LED1,True)#流水灯LED1
		GPIO.output(LED2,True)#流水灯LED2
		
########## Signal delivery ###########################

def	Delivery_Light():# all leds blinking fast
	GPIO.output(LED0,False) # ON
	GPIO.output(LED1,False)
	GPIO.output(LED2,False)
	time.sleep(0.25)
	GPIO.output(LED0,True)#OFF
	GPIO.output(LED1,True)
	GPIO.output(LED2,True)
	time.sleep(0.25)
	
##########机器人方向控制###########################
def Motor_Forward():
	#print ('motor forward')
	GPIO.output(ENA,True)
	GPIO.output(ENB,True)
	GPIO.output(IN1,True)
	GPIO.output(IN2,False)
	GPIO.output(IN3,True)
	GPIO.output(IN4,False)
	GPIO.output(LED1,False)#LED1亮
	GPIO.output(LED2,False)#LED1亮
	
def Motor_Backward():
	#print ('motor_backward')
	GPIO.output(ENA,True)
	GPIO.output(ENB,True)
	GPIO.output(IN1,False)
	GPIO.output(IN2,True)
	GPIO.output(IN3,False)
	GPIO.output(IN4,True)
	GPIO.output(LED1,True)#LED1灭
	GPIO.output(LED2,False)#LED2亮
	
def Motor_TurnLeft():
	#print ('motor_turnleft')
	GPIO.output(ENA,True)
	GPIO.output(ENB,True)
	GPIO.output(IN1,True)
	GPIO.output(IN2,False)
	GPIO.output(IN3,False)
	GPIO.output(IN4,True)
	GPIO.output(LED1,False)#LED1亮
	GPIO.output(LED2,True) #LED2灭
def Motor_TurnRight():
	#print 'motor_turnright'
	GPIO.output(ENA,True)
	GPIO.output(ENB,True)
	GPIO.output(IN1,False)
	GPIO.output(IN2,True)
	GPIO.output(IN3,True)
	GPIO.output(IN4,False)
	GPIO.output(LED1,False)#LED1亮
	GPIO.output(LED2,True) #LED2灭
def Motor_Stop():
	#print 'motor_stop'
	GPIO.output(ENA,False)
	GPIO.output(ENB,False)
	GPIO.output(IN1,False)
	GPIO.output(IN2,False)
	GPIO.output(IN3,False)
	GPIO.output(IN4,False)
	GPIO.output(LED1,True)#LED1灭
	GPIO.output(LED2,True)#LED2亮

##########Motor control from NN###########################
def Motor(r_speed, l_speed):
	#print 'motor control from NN'
	ENA_Speed(l_speed)
##	ENA_pwm.ChangeDutyCycle(l_speed)
	ENB_Speed(r_speed)
##	ENB_pwm.ChangeDutyCycle(r_speed)
	GPIO.output(ENA,True)
	GPIO.output(ENB,True)
	GPIO.output(IN1,True) #traction only in front wheels
	GPIO.output(IN2,False) 
	GPIO.output(IN3,True)  #traction only in front wheels
	GPIO.output(IN4,False) 
	GPIO.output(LED1,False)#ONLY LED1 ON when navigating
	GPIO.output(LED2,True)
##########机器人方向校准（模式中使用）###########################
def forward():
	global motor_flag
	if motor_flag == 1:
		Motor_Forward()
	elif motor_flag == 2:
		Motor_Forward()
	elif motor_flag == 3:
		Motor_Backward()
	elif motor_flag == 4:
		Motor_Backward()
	elif motor_flag == 5:
		Motor_TurnLeft()
	elif motor_flag == 6:
		Motor_TurnLeft()
	elif motor_flag == 7:
		Motor_TurnRight()
	elif motor_flag == 8:
		Motor_TurnRight()
def back():
	global motor_flag
	if motor_flag == 1:
		Motor_Backward()
	elif motor_flag == 2:
		Motor_Backward()
	elif motor_flag == 3:
		Motor_Forward()
	elif motor_flag == 4:
		Motor_Forward()
	elif motor_flag == 5:
		Motor_TurnRight()
	elif motor_flag == 6:
		Motor_TurnRight()
	elif motor_flag == 7:
		Motor_TurnLeft()
	elif motor_flag == 8:
		Motor_TurnLeft()
		
def left():
	global motor_flag
	if motor_flag == 1:
		Motor_TurnLeft()
	elif motor_flag == 2:
		Motor_TurnRight()
	elif motor_flag == 3:
		Motor_TurnLeft()
	elif motor_flag == 4:
		Motor_TurnRight()
	elif motor_flag == 5:
		Motor_Forward()
	elif motor_flag == 6:
		Motor_Backward()
	elif motor_flag == 7:
		Motor_Forward()
	elif motor_flag == 8:
		Motor_Backward()

def right():
	global motor_flag
	if motor_flag == 1:
		Motor_TurnRight()
	elif motor_flag == 2:
		Motor_TurnLeft()
	elif motor_flag == 3:
		Motor_TurnRight()
	elif motor_flag == 4:
		Motor_TurnLeft()
	elif motor_flag == 5:
		Motor_Backward()
	elif motor_flag == 6:
		Motor_Forward()
	elif motor_flag == 7:
		Motor_Backward()
	elif motor_flag == 8:
		Motor_Forward()


def ENA_Speed(EA_num):
	global left_speed
	left_speed=EA_num
	#print 'EA_A改变啦 %d '%EA_num
	ENA_pwm.ChangeDutyCycle(EA_num)

def ENB_Speed(EB_num):
	global right_speed
	right_speed=EB_num
	#print 'EB_B改变啦 %d '%EB_num
	ENB_pwm.ChangeDutyCycle(EB_num)
	
##########机器人速度控制###########################	
##函数功能 ：舵机控制函数
##入口参数 ：ServoNum(舵机号)，angle_from_protocol(舵机角度)
##出口参数 ：无
####################################################
def Angle_cal(angle_from_protocol):
	angle=hex(eval('0x'+angle_from_protocol))
	angle=int(angle,16)
	if angle > 160:
		angle=160
	elif angle < 15:
		angle=15
	return angle
	
def SetServoAngle(ServoNum,angle_from_protocol):
	GPIO.output(LED0,False)
	GPIO.output(LED1,True)
	GPIO.output(LED2,False)
	time.sleep(0.01)
	GPIO.output(LED0,True)
	GPIO.output(LED1,True)
	GPIO.output(LED2,True)
	if ServoNum== 1:
		XRservo.XiaoRGEEK_SetServo(0x01,Angle_cal(angle_from_protocol))
		return
	elif ServoNum== 2:
		XRservo.XiaoRGEEK_SetServo(0x02,Angle_cal(angle_from_protocol))
		return
	elif ServoNum== 3:
		XRservo.XiaoRGEEK_SetServo(0x03,Angle_cal(angle_from_protocol))
		return
	elif ServoNum== 4:
		XRservo.XiaoRGEEK_SetServo(0x04,Angle_cal(angle_from_protocol))
		return
	elif ServoNum== 5:
		XRservo.XiaoRGEEK_SetServo(0x05,Angle_cal(angle_from_protocol))
		return
	elif ServoNum== 6:
		XRservo.XiaoRGEEK_SetServo(0x06,Angle_cal(angle_from_protocol))
		return
	elif ServoNum== 7:
		XRservo.XiaoRGEEK_SetServo(0x07,Angle_cal(angle_from_protocol))
		return
	elif ServoNum== 8:
		XRservo.XiaoRGEEK_SetServo(0x08,Angle_cal(angle_from_protocol))
		return
	else:
		return

############Camera angle
def Angle_H_camera(angle):

##	if angle > 270:
##		angle=270
##	elif angle < 90:
##		angle=90
	return angle

def Angle_V_camera(angle):

	if angle > 160:
		angle=160
	elif angle < 15:
		angle=15
	return angle


def SetCameraAngleH(angle):
	GPIO.output(LED0,False)
	GPIO.output(LED1,True)
	GPIO.output(LED2,False)
	time.sleep(0.01)
	GPIO.output(LED0,True)
	GPIO.output(LED1,True)
	GPIO.output(LED2,True)
	
	XRservo.XiaoRGEEK_SetServo(0x07,Angle_H_camera(angle))
	
	return

def SetCameraAngleV(angle):
	GPIO.output(LED0,False)
	GPIO.output(LED1,True)
	GPIO.output(LED2,False)
	time.sleep(0.01)
	GPIO.output(LED0,True)
	GPIO.output(LED1,True)
	GPIO.output(LED2,True)
	
	XRservo.XiaoRGEEK_SetServo(0x08,Angle_V_camera(angle))
	
	return
	
####################################################
##函数名称 ：Avoiding()
##函数功能 ：红外避障函数
##入口参数 ：无
##出口参数 ：无
####################################################
def	Avoiding(): #红外避障函数
	if GPIO.input(IR_M) == False:
		Motor_Stop()
		time.sleep(0.1)
		return

####################################################
##函数名称 TrackLine()
##函数功能 巡黑线模式
##入口参数 ：无
##出口参数 ：无
####################################################
def TrackLine():
	if (GPIO.input(IR_L) == False)&(GPIO.input(IR_R) == False): #黑线为高，地面为低
		forward()
		return
	elif (GPIO.input(IR_L) == False)&(GPIO.input(IR_R) == True):
		right()
		return
	elif (GPIO.input(IR_L) == True)&(GPIO.input(IR_R) == False):
		left()
		return
	elif (GPIO.input(IR_L) == True)&(GPIO.input(IR_R) == True): #两侧都碰到黑线
		Motor_Stop()
		return

####################################################
##函数名称 Follow()
##函数功能 跟随模式
##入口参数 ：无
##出口参数 ：无
####################################################
def Follow(): 
	if(GPIO.input(IR_M) == True): #中间传感器OK
		if(GPIO.input(IRF_L) == False)&(GPIO.input(IRF_R) == False):	#俩边同时探测到障碍物
			Motor_Stop()			#停止 
		if(GPIO.input(IRF_L) == False)&(GPIO.input(IRF_R) == True):		#左侧障碍物
			right()		#右转 
		if(GPIO.input(IRF_L) == True)& (GPIO.input(IRF_R) == False):		#右侧障碍物
			left()		#左转
		if(GPIO.input(IRF_L) == True)& (GPIO.input(IRF_R) == True):		#无任何障碍物
			forward()			#直行 
	else:
		Motor_Stop()


####################################################
##函数名称 ：Get_Distence()
##函数功能 超声波测距，返回距离（单位是厘米）
##入口参数 ：无
##出口参数 ：无
####################################################
def	Get_Distence():
	time.sleep(0.1)
	GPIO.output(TRIG,GPIO.HIGH)
	time.sleep(0.000015)
	GPIO.output(TRIG,GPIO.LOW)
	while not GPIO.input(ECHO):
				pass
	t1 = time.time()
	while GPIO.input(ECHO):
				pass
	t2 = time.time()
	time.sleep(0.1)
	return (t2-t1)*340/2*100

####################################################
##函数名称 AvoidByRadar()
##函数功能 超声波避障函数
##入口参数 ：无
##出口参数 ：无
####################################################
def	AvoidByRadar(distance):
	dis = int(Get_Distence())
	if(distance<20):
		distance = 20					#限定最小避障距离为20cm
	if((dis>1)&(dis < distance)):		#避障距离值(单位cm)，大于1是为了避免超声波的盲区
		Motor_Stop()
	
		
def	Avoid_wave():
	dis = Get_Distence()
	if dis<20:
		Motor_Stop()
	else:
		forward()

####################################################
##函数名称 
##函数功能 Route() 路径规划
##入口参数 ：无
##出口参数 ：无
####################################################
def Route():
	global RevStatus
	global TurnAngle
	global Golength
	global left_speed
	global right_speed
	global left_speed_hold
	global right_speed_hold
	while RevStatus !=0 :
		#print 'RevStatus==== %d ' %RevStatus
		TurnA=float(TurnAngle*6)/1000
		Golen=float(Golength*10)/1000
		#print 'TurnAngle====== %f ' %TurnA
		#print 'Golength======= %f ' %Golen
		#ENA_Speed(85)
		#ENB_Speed(85)
		if RevStatus==1:
			left()
			time.sleep(TurnA)
			Motor_Stop()
			forward()
			time.sleep(Golen)
			Motor_Stop()
			RevStatus = 0
			tcpCliSock.send("\xFF")
			time.sleep(0.005)
			tcpCliSock.send("\xA8")
			time.sleep(0.005)
			tcpCliSock.send("\x00")
			time.sleep(0.005)
			tcpCliSock.send("\x00")
			time.sleep(0.005)
			tcpCliSock.send("\xFF")
			time.sleep(0.01)
		elif RevStatus==2:
			right()
			time.sleep(TurnA)
			Motor_Stop()
			forward()
			time.sleep(Golen)
			Motor_Stop()
			RevStatus = 0
			tcpCliSock.send("\xFF")
			time.sleep(0.005)
			tcpCliSock.send("\xA8")
			time.sleep(0.005)
			tcpCliSock.send("\x00")
			time.sleep(0.005)
			tcpCliSock.send("\x00")
			time.sleep(0.005)
			tcpCliSock.send("\xFF")
			time.sleep(0.01)
		#ENA_Speed(left_speed_hold)
		#ENB_Speed(right_speed_hold)
####################################################
##函数名称 Send_Distance()
##函数功能 ：超声波距离PC端显示
##入口参数 ：无
##出口参数 ：无
####################################################
def	Send_Distance():
	dis_send = int(Get_Distence())
	#dis_send = str("%.2f"%dis_send)
	if dis_send < 255:
		#print 'Distance: %d cm' %dis_send
		tcpCliSock.send("\xFF")
		time.sleep(0.005)
		tcpCliSock.send("\x03")
		time.sleep(0.005)
		tcpCliSock.send("\x00")
		time.sleep(0.005)
		tcpCliSock.send(chr(dis_send))
		time.sleep(0.005)
		tcpCliSock.send("\xFF")
		time.sleep(0.1)


####################################################
##函数名称 Cruising_Mod()
##函数功能 ：模式切换函数
##入口参数 ：无
##出口参数 ：无
####################################################
def	Cruising_Mod(func):
	##print 'into Cruising_Mod-01'
	global Pre_Cruising_Flag
	#print 'Pre_Cruising_Flag %d '%Pre_Cruising_Flag
	
	global Cruising_Flag
	##print 'Cruising_Flag %d '%Cruising_Flag
	while True:
		if (Pre_Cruising_Flag != Cruising_Flag):			
			if (Pre_Cruising_Flag != 0):
				Motor_Stop()
			Pre_Cruising_Flag = Cruising_Flag
			##print 'Pre_Cruising_Flag = Cruising_Flag == 0'
		if(Cruising_Flag == 1):		#进入红外跟随模式
			Follow()
		elif (Cruising_Flag == 2):	#进入红外巡线模式
			TrackLine()
		elif (Cruising_Flag == 3):	#进入红外避障模式
			Avoiding()
		elif (Cruising_Flag == 4):	#进入超声波壁障模式##
			Avoid_wave()
		elif (Cruising_Flag == 5):	#进入超声波测距模式
			Send_Distance()
		elif (Cruising_Flag == 6):	#进入超声波壁障模式
			AvoidByRadar(15)
		elif (Cruising_Flag == 7):
			Route()
		elif (Cruising_Flag == 8):	#退出摄像头循迹或进入调试模式
			time.sleep(3)
			#os.system('sh start_mjpg_streamer.sh')
			call("sh start_mjpg_streamer.sh &",shell=True)
			Cruising_Flag = 0
		elif (Cruising_Flag == 9):	#进入摄像头循迹操作
			Path_Dect()
		elif (Cruising_Flag == 0):
			RevStatus=0
		else:
			time.sleep(0.001)
		time.sleep(0.001)
####################################################
##函数名称 Path_Dect()
##函数功能 ：模式切换函数
##入口参数 ：FF130800FF，摄像头调试，FF130801FF开始摄像头循迹
##出口参数 
#int Path_Dect_px 	平均像素坐标
#int Path_Dect_on	1:开始循迹，0停止循迹
####################################################
def	Path_Dect():
	global Path_Dect_px
	global Path_Dect_on
	while (Path_Dect_on):
		if Path_Dect_px < 260:
			#print("turn left")
			Motor_TurnLeft()
		elif Path_Dect_px> 420:
			#print("turn right")
			Motor_TurnRight()
		else :
			#print("go stright")
			Motor_Forward()
		time.sleep(0.007)
		Motor_Stop()
		time.sleep(0.006)
####################################################
##函数名称 Path_Dect_img_processing()
##函数功能 ：模式切换函数
##入口参数 ：FF130800FF，摄像头调试，FF130801FF开始摄像头循迹
##出口参数 
#int Path_Dect_px 	平均像素坐标
#int Path_Dect_on	1:开始循迹，0调试模式/停止循迹
####################################################
def	Path_Dect_img_processing(func):
	global Path_Dect_px
	global Path_Dect_on
	Path_Dect_fre_count = 0
	Path_Dect_px_sum = 0
	Path_Dect_cap = 0
	#print("into theads Path_Dect_img_processing")
	while True:
		if(Path_Dect_on):
			if(Path_Dect_cap == 0):
				cap = cv2.VideoCapture(0)
				Path_Dect_cap = 1
			else:
				Path_Dect_fre_count+=1
				ret,frame = cap.read()	#capture frame_by_frame
				gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY) #get gray img
				ret,thresh1=cv2.threshold(gray,70,255,cv2.THRESH_BINARY)	#binaryzation 二值化
				for j in range(0,640,5):
					if thresh1[240,j] == 0:
						Path_Dect_px_sum = Path_Dect_px_sum + j
				Path_Dect_px = Path_Dect_px_sum>>5
				Path_Dect_px_sum = 0
				Path_Dect_fre_count = 0
		elif(Path_Dect_cap):
			Motor_Stop()
			time.sleep(0.001)
			Path_Dect_cap = 0
			cap.relese()
		time.sleep(0.1)
####################################################
## capture image and send to NN

####################################################  		
def	Start_Video_capture():
        global video_captured
        video_captured = cv2.VideoCapture(0)
        video_captured.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 304)
        video_captured.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 228)
        #video_captured.set(cv2.cv.CV_CAP_PROP_WHITE_BALANCE_U, 0.0)
        #video_captured.set(cv2.cv.CV_CAP_PROP_WHITE_BALANCE_V, 0.0)
        
        
def	Img_processing():
	global video_captured
	#print("Img_processing")

	ret,frame = video_captured.read()	#capture frame_by_frame
	#gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY) #get gray img
	#ret,thresh1=cv2.threshold(gray,70,255,cv2.THRESH_BINARY)	#binaryzation 二值化
	return frame
				
def	Stop_Video_capture():
        global video_captured
        video_captured.release()
		
####################################################
##函数名称 Communication_Decode()
##函数功能 ：通信协议解码
##入口参数 ：无
##出口参数 ：无
####################################################    
def Communication_Decode():
	global RevStatus
	global TurnAngle
	global Golength
	global Pre_Cruising_Flag
	global Cruising_Flag
	global motor_flag
	global left_speed
	global right_speed
	global left_speed_hold
	global right_speed_hold
	global Path_Dect_on
	#print 'Communication_decoding...'
	if buffer[0]=='00':
		if buffer[1]=='01':				#前进
			Motor_Forward()
		elif buffer[1]=='02':			#后退
			Motor_Backward()
		elif buffer[1]=='03':			#左转
			Motor_TurnLeft()
		elif buffer[1]=='04':			#右转
			Motor_TurnRight()
		elif buffer[1]=='00':			#停止
			Motor_Stop()
		else:
			Motor_Stop()
	elif buffer[0]=='02':
		if buffer[1]=='01':#左速度
			speed=hex(eval('0x'+buffer[2]))
			speed=int(speed,16)
			ENA_Speed(speed)
		elif buffer[1]=='02':#右侧速度
			speed=hex(eval('0x'+buffer[2]))
			speed=int(speed,16)
			ENB_Speed(speed)
	elif buffer[0]=='01':
		if buffer[1]=='01':#1号舵机驱动
			SetServoAngle(1,buffer[2])
		elif buffer[1]=='02':#2号舵机驱动
			SetServoAngle(2,buffer[2])
		elif buffer[1]=='03':#3号舵机驱动
			SetServoAngle(3,buffer[2])
		elif buffer[1]=='04':#4号舵机驱动
			SetServoAngle(4,buffer[2])
		elif buffer[1]=='05':#5号舵机驱动
			SetServoAngle(5,buffer[2])
		elif buffer[1]=='06':#6号舵机驱动
			SetServoAngle(6,buffer[2])
		elif buffer[1]=='07':#7号舵机驱动
			SetServoAngle(7,buffer[2])
		elif buffer[1]=='08':#8号舵机驱动
			SetServoAngle(8,buffer[2])
		else:
			print ('舵机角度大于170')
	elif buffer[0]=='13':
		if buffer[1]=='01':
			Cruising_Flag = 1#进入红外跟随模式
			#print 'Cruising_Flag红外跟随模式 %d '%Cruising_Flag
		elif buffer[1]=='02':#进入红外巡线模式
			Cruising_Flag = 2
			#print 'Cruising_Flag红外巡线模式 %d '%Cruising_Flag
		elif buffer[1]=='03':#进入红外避障模式
			Cruising_Flag = 3
			#print 'Cruising_Flag红外避障模式 %d '%Cruising_Flag
		elif buffer[1]=='04':#进入超声波壁障模式
			Cruising_Flag = 4
			#print 'Cruising_Flag超声波壁障 %d '%Cruising_Flag
		elif buffer[1]=='05':#进入超声波距离PC显示
			Cruising_Flag = 5
			#print 'Cruising_Flag超声波距离PC显示 %d '%Cruising_Flag
		elif buffer[1]=='06':
			Cruising_Flag = 6
			#print 'Cruising_Flag超声波遥控壁障 %d '%Cruising_Flag
		elif buffer[1]=='07':
			left_speed_hold=left_speed
			right_speed_hold=right_speed
			tcpCliSock.send("\xFF")
			time.sleep(0.005)
			tcpCliSock.send("\xA8")
			time.sleep(0.005)
			tcpCliSock.send("\x00")
			time.sleep(0.005)
			tcpCliSock.send("\x00")
			time.sleep(0.005)
			tcpCliSock.send("\xFF")
			time.sleep(0.005)
			Cruising_Flag = 7
		elif buffer[1]=='08':
			if buffer[2]=='00':#Path_Dect 调试模式
				Path_Dect_on = 0
				Cruising_Flag = 8
				#print 'Cruising_Flag Path_Dect调试模式 %d '%Cruising_Flag
				#os.system('sh start_mjpg_streamer.sh')
			elif buffer[2]=='01':#Path_Dect 循迹模式
				#os.system('sh stop_mjpg_streamer.sh')
				call("sh stop_mjpg_streamer.sh &",shell=True)
				time.sleep(2)
				Path_Dect_on = 1
				Cruising_Flag = 9
				#print 'Cruising_Flag Path_Dect循迹模式 %d '%Cruising_Flag
		elif buffer[1]=='00':
			RevStatus=0
			Cruising_Flag = 0
			#print 'Cruising_Flag正常模式 %d '%Cruising_Flag
		#else:
			#Cruising_Flag = 0
	elif buffer[0]=='a0':
		RevStatus=2
		Tangle=hex(eval('0x'+buffer[1]))
		Tangle=int(Tangle,16)
		TurnAngle=Tangle
		Golen=hex(eval('0x'+buffer[2]))
		Golen=int(Golen,16)
		Golength=Golen
	elif buffer[0]=='a1':
		RevStatus=1
		Tangle=hex(eval('0x'+buffer[1]))
		Tangle=int(Tangle,16)
		TurnAngle=Tangle
		Golen=hex(eval('0x'+buffer[2]))
		Golen=int(Golen,16)
		Golength=Golen
	elif buffer[0]=='40':
		temp=hex(eval('0x'+buffer[1]))
		temp=int(temp,16)
		#print 'mode_flag====== %d '%temp
		motor_flag=temp
	elif buffer[0]=='32':		#存储角度
		XRservo.XiaoRGEEK_SaveServo()
	elif buffer[0]=='33':		#读取角度
		XRservo.XiaoRGEEK_ReSetServo()
	elif buffer[0]=='04':		#开关灯模式 FF040000FF开灯  FF040100FF关灯
		if buffer[1]=='00':
			Open_Light()
		elif buffer[1]=='01':
			Close_Light()
		else:
			print ('error1 command!')
	elif buffer[0]=='05':		#读取电压 FF050000FF
		if buffer[1]=='00':
			Vol = XRservo.XiaoRGEEK_ReadVol()
			#print 'Read_Voltage %d '%Vol
		else:
			print ('error2 command!')
	elif buffer[0]=='06':		#读取脉冲 FF060000FF读取脉冲1号  FF060100FF读取脉冲2号
		if buffer[1]=='00':
			Speed1 = XRservo.XiaoRGEEK_SpeedCounter1()
			#print 'Read_Voltage %d '%Speed1
		elif buffer[1]=='01':
			Speed2 = XRservo.XiaoRGEEK_SpeedCounter2()
			#print 'Read_Voltage %d '%Speed2
		else:
			print ('error3 command!')
	else:
		print ('error4 command!')




init_light()
##Open_Light()
##time.sleep(2)
##Close_Light()
##time.sleep(2)

SetCameraAngleV(45)
SetCameraAngleH(10)
print('camera front')

time.sleep(2)
Motor(80,80)
time.sleep(2)
Motor(30,30)
print('forward 30')
time.sleep(10)
Motor(30,60)
print('turn 30 60')
time.sleep(2)
Motor(60,30)
print('turn 60 30')
time.sleep(2)
Motor(50,50)
print('fordward 40 40')
time.sleep(5)
Motor(80,80)
time.sleep(2)
Motor_Stop()

Start_Video_capture()
img = Img_processing()
cv2.imwrite("test.jpg", img)
cv2.imshow("imag",  img)
cv2.waitKey(0)
cv2.destroyAllWindows()

for i in range(1, 10):
    Delivery_Light()


    

