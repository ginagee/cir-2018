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
import numpy as np
import threading

import RPi.GPIO as GPIO
import time
from smbus import SMBus
import cv2
from subprocess import call

XRservo = SMBus(1)
print ('....Loading drivers...')




####################################################
##函数名称 TurnOn_Light()
##函数功能 开大灯LED0
##入口参数 ：无
##出口参数 ：无
####################################################
def	turnOn_Light():#开大灯LED0
	global LED0
	GPIO.output(LED0,False)#大灯正极接5V  负极接IO口
	time.sleep(1)


####################################################
##函数名称 TurnOff_Light()
##函数功能 关大灯
##入口参数 ：无
##出口参数 ：无
####################################################
def	turnOff_Light():#关大灯
	global LED0
	GPIO.output(LED0,True)#大灯正极接5V  负极接IO口
	time.sleep(1)
	

		
########## Signal delivery ###########################

def	delivery_Light():# all leds blinking fast
	global LED0
	global LED1
	global LED2
    motor(0, 0)
	for repeat in range(0,20):
		GPIO.output(LED0,False) # ON
		GPIO.output(LED1,False)
		GPIO.output(LED2,False)
		time.sleep(0.25)
		GPIO.output(LED0,True)#OFF
		GPIO.output(LED1,True)
		GPIO.output(LED2,True)
		time.sleep(0.25)


##########Motor control from NN###########################
def motor(r_speed, l_speed):
	global ENA
	global ENB
	global IN1
	global IN2
	global IN3
	global IN4
	global LED1
	global LED2

	print 'motor control from NN left speed: ' + l_speed + ' right speed:' + r_speed
	ENA_Speed(l_speed)
	ENB_Speed(r_speed)
	GPIO.output(ENA,True)
	GPIO.output(ENB,True)
	GPIO.output(IN1,True) #traction only in front wheels
	GPIO.output(IN2,False) 
	GPIO.output(IN3,True)  #traction only in front wheels
	GPIO.output(IN4,False) 
	GPIO.output(LED1,False)#ONLY LED1 ON when navigating
	GPIO.output(LED2,True)


def motor_linear_action_to_rl(action):

	r,l = 0

	if action == 1:
		r = 80
		l = 80
	elif action == 2:
		r = 50
		l = 50
	elif action == 3:
		r = 80
		l = 0
	elif action == 4:
		r = 80
		l = 40
	elif action == 5:
		r = 80
		l = 80
	elif action == 6:
		r = 40
		l = 80
	elif action == 7:
		r = 0
		l = 80

	#if action < 2:
	#	r = 80/action
	#	l = 80/action
	#else:
	#	r = 80 * (1 - mod(action/5))
	#	l = 80 * (mod(action/5))
	return r,l

def motor_move (action):							##This is what we call from the real world(?)
	r,l = motor_linear_action_to_lr(action)
	motor(r,l)

#This are duplicated...

def ENA_Speed(EA_num):
	ENA_pwm.ChangeDutyCycle(EA_num)

def ENB_Speed(EB_num):

	ENB_pwm.ChangeDutyCycle(EB_num)



############ Camera angle  ##########

def setCameraAngleH(angle):
	
	XRservo.XiaoRGEEK_SetServo(0x07,Angle_H_camera(angle))
	
	return

def setCameraAngleV(angle):
	
	XRservo.XiaoRGEEK_SetServo(0x08,Angle_V_camera(angle))
	
	return

#####  Start video #####
def	start_Video_capture(Wres = 304, Hres = 228):
        global video_captured_nn
        video_captured_nn = cv2.VideoCapture(0)
        video_captured_nn.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, Wres)
        video_captured_nn.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, Hres)
        #video_captured.set(cv2.cv.CV_CAP_PROP_WHITE_BALANCE_U, 0.0)
        #video_captured.set(cv2.cv.CV_CAP_PROP_WHITE_BALANCE_V, 0.0)
        
        
def	img_processing():
	global video_captured_nn
	#print("Img_processing")

	ret,frame = video_captured_nn.read()	#capture frame_by_frame
	#gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY) #get gray img
	#ret,thresh1=cv2.threshold(gray,70,255,cv2.THRESH_BINARY)	#binaryzation 二值化
	return frame
				
def	stop_Video_capture():
        global video_captured_nn
        video_captured_nn.release()





    

