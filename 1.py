# -*- coding: UTF-8 -*-

import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import random
import requests
import base64
from PIL import Image
import logging

"""
@File    ：1.10
@Author  ：mark
"""

#########################
# 日志输出配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    filename='run.log',  # 输出到run.log文件
    filemode='a' # 追加模式
)
s = Service(executable_path=r'chromedriver.exe')
browser = webdriver.Chrome(service=s)
#########################

# 登入函数
def login():
    logging.info('正在打开页面')
    browser.get('https://qqvps.com/user/index/')
    browser.maximize_window()
    time.sleep(10)
    # ID定位用户名，密码输入框
    username = browser.find_element(By.XPATH,'//*[@id="L_email"]')
    password = browser.find_element(By.XPATH, '//*[@id="L_pass"]')
    username.send_keys('handuck@qq.com')
    password.send_keys('51349924')
    # Xpath定位登录按钮并点击
    home_state = browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div/ul/li[1]').text
    if home_state=='登入':
        logging.info('页面载入完成')

    else:
        logging.info('页面载入失败')
        time.sleep(3)
        logging.info('准备重新打开页面')
        login()
    sleep(random.random()*3)

# 保存验证码
def save_img():
    logging.info('正在保存验证码')
    browser.save_screenshot('page.png')# save_screenshot：将当前页面进行截图并保存下来
    code_img_ele = browser.find_element(By.XPATH,'//*[@id="captcha"]')# Xpath定位验证码图片的位置
    location = code_img_ele.location  # 验证码左上角的坐标x,y
    size = code_img_ele.size  # 验证码图片对应的长和宽
    # 得到左上角和右下角的坐标
    rangle = (
        int(location['x']), int(location['y']), int((location['x'] + size['width'])),
        int((location['y'] + size['height']))
    )
    image1 = Image.open('page.png')
    frame = image1.crop(rangle)# crop根据rangle元组内的坐标进行裁剪 裁剪出验证码区域
    frame.save('code.png')
    logging.info('验证码保存完毕')
    return

# 提交识别验证码
def submit_img():
    logging.info('正在识别验证码')
    # 将验证码提交给OCR识别
    with open('code.png', "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    url = 'https://api.apitruecaptcha.org/one/gettext'
    data = { 'userid':'euextend', 'apikey':'deJhWBaqgd6QDN4BqJGf',  'data':str(encoded_string)[2:-1]}
    r = requests.post(url = url, json = data)
    j = r.json()['result']
    logging.info('验证码：'+j)
    return(j)
# 输入验证码
def click_codeImg():
    time.sleep(5)
    logging.info('正在输入验证码')
    browser.find_element(By.XPATH, '//*[@id="L_vercode"]').send_keys(submit_img())
    time.sleep(2)
    logging.info('验证码输入完毕')
    browser.find_element(By.XPATH,'//*[@id="LAY_ucm"]/div/div/form/div[4]/button').click()
    logging.info('执行登入')
    time.sleep(10)
    user_state=browser.find_element(By.XPATH,'/html/body/div[2]/div/div[5]/div/div[2]/div[2]/div/div[1]').text
    if user_state=='我的会员信息':
        logging.info('登入成功')
    else:
        logging.info('登入失败，等待3秒重试')
        time.sleep(3)
        login()
    time.sleep(5)
# 签到操作
def click_in():
    # 判断签到状态
    logging.info('正在判断签到状态')
    try:
        browser.find_element(By.XPATH, '//*[@id="LAY_signin"]').text
        logging.info('未签到状态')
    except:
        logging.info('已签到，退出签到！')
        nomber_state=browser.find_element(By.XPATH, '/html/body/div[2]/div/div[5]/div/div[2]/div[1]/div/div/div/div[1]/span/cite').text
        logging.info('已连续签到：'+nomber_state+'天。')
        browser.save_screenshot('state.png')
        browser.quit()
        email()
    time.sleep(3)
    logging.info('执行签到操作')
    browser.find_element(By.XPATH,'//*[@id="LAY_signin"]').click()# 点击签到
    time.sleep(6)
    browser.refresh()
    time.sleep(6)
    click_in()

def email():
    sender = 'mark@myssr.pw'  # 这里就是你的QQ邮箱
    receiver = 'handuck@qq.com'  # 发给单人时的邮件接收邮箱

    smtpserver = "smtp.qq.com"  # 邮件服务器，如果是qq邮箱那就是这个了，其他的可以自行查找
    username = 'mark@myssr.pw'  # 这里还是你的邮箱
    password = '51349924Bb'  # 上面获取的SMTP授权码，相当于是一个密码验证

    msgRoot = MIMEMultipart('related')  # 邮件类型，如果要加图片等附件，就得是这个
    msgRoot['Subject'] = '签到日志'  # 邮件标题，以下设置项都很明了
    msgRoot['From'] = sender
    msgRoot['To'] = receiver  # 发给单人

    # 以下为邮件正文内容，含有一个居中的标题和一张图片
    jpg = MIMEText('<html><img src="cid:image1" alt="image1"></html>', 'html', 'gbk')
    # 如果有编码格式问题导致乱码，可以进行格式转换：
    # content = content.decode('utf-8').encode('gbk')
    msgRoot.attach(jpg)

    # 上面加的图片src必须是cid:xxx的形式，xxx就是下面添加图片时设置的图片id
    # 添加图片附件
    fp = open('state.png', 'rb')
    msgImage = MIMEImage(fp.read())
    fp.close()
    msgImage.add_header('Content-ID', 'image1')  # 这个id用于上面html获取图片
    msgRoot.attach(msgImage)

    ############
    ########
    fp1 = open('run.log', 'rb')
    run_log = MIMEText(fp1.read(), 'plain', 'gbk')
    fp1.close()
    run_log.add_header('Content-ID', 'txt1')
    msgRoot.attach(run_log)
    # 连接邮件服务器，因为使用SMTP授权码的方式登录，必须是465端口
    smtp = smtplib.SMTP_SSL('smtp.exmail.qq.com:465')
    smtp.login(username, password)
    smtp.sendmail(sender, receiver, msgRoot.as_string())
    smtp.quit()
    sys.exit()

def main():
    # 进入登录界面，输入账号密码
    login()
    # 保存页面截图，并根据坐标裁剪获取验证码图片
    save_img()
    # 将图片提交给超级鹰,获取返回的识别结果
    submit_img()
    # 在页面验证码上完成点击操作并登录
    click_codeImg()
    # 签到流程
    click_in()
    # 发送邮件
    email()
main()
