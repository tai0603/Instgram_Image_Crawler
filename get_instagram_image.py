import os
import sys
import time
import requests
import keyboard
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('-enable-webgl')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
browser = webdriver.Chrome('./chromedriver', chrome_options = chrome_options)
url = 'https://www.instagram.com/'

# ------ 前往該網址 ------
browser.get(url)

# ------ 填入帳號與密碼 ------
WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.NAME, 'username')))
# ------ 網頁元素定位 ------
username_input = browser.find_elements_by_name('username')[0]
password_input = browser.find_elements_by_name('password')[0]
print("Inputing username and password...")

# ------ 輸入帳號密碼 ------
username_input.send_keys("IG帳號")
password_input.send_keys("密碼")

# ------ 登入 ------
WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="loginForm"]/div/div[3]/button/div')))
# ------ 網頁元素定位 ------
login_click = browser.find_elements_by_xpath('//*[@id="loginForm"]/div/div[3]/button/div')[0]
# ------ 點擊登入鍵 ------
login_click.click()

try:
	# ------ 不儲存登入資料 ------
	WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/section/main/div/div/div/div/button')))
	# ------網頁元素定位 ------
	store_click = browser.find_elements_by_xpath('//*[@id="react-root"]/section/main/div/div/div/div/button')[0]
	# ------ 點擊不儲存鍵 ------
	store_click.click()
except:
	pass
try:
	# ------ 不開啟通知 ------
	WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div/div/div/div[3]/button[2]')))
	# ------ 網頁元素定位 ------                                                                                                    
	notification_click = browser.find_elements_by_xpath('/html/body/div[4]/div/div/div/div[3]/button[2]')[0]
	# ------ 點擊不開啟通知 ------
	notification_click.click()
except:
	browser.close()
	sys.exit(1)

while True:
	# ------ 輸入要抓取的使用者ID ------
	userid = input('INPUT USER ID: ')

	profile_url = url + userid

	# ------ 前往該網址 ------
	browser.get(profile_url)

	# ------ 判斷帳號有無貼文或是否是私人帳號 ------
	soup = BeautifulSoup(browser.page_source,"lxml")
	no_posts_yet = soup.find(class_ = 'Igw0E rBNOH eGOV_ _4EzTm') # 沒有貼文
	private_account = soup.find(class_ = '_4Kbb_ _54f4m') # 私人帳號

	if (no_posts_yet == None) and (private_account == None): # 有貼文且有追蹤
		# ------ 儲存圖片的資料夾 ------
		downloads_folder = './Downloads/'
		if os.path.exists(downloads_folder) == False:
			os.makedirs(downloads_folder)

		folder_path = downloads_folder + userid + '/'
		if os.path.exists(folder_path) == False:
			os.makedirs(folder_path)

		all_posts_url = []
		last_height = browser.execute_script('return document.body.scrollHeight')

		# 網頁下刷新讀取全部貼文資料
		while True:
			soup = BeautifulSoup(browser.page_source,"lxml")
			post_frame = soup.find_all(class_ = 'v1Nh3 kIKUG _bz0w')
			for i in post_frame:
				try:
					post_url = i.a.get('href')
					if (post_url != None) & (post_url not in all_posts_url):
						all_posts_url.append(post_url)
				except:
					pass

			browser.execute_script('window.scrollTo(0, document.body.scrollHeight);') # 網頁下滑

			time.sleep(3)

			new_height = browser.execute_script('return document.body.scrollHeight')
			if new_height == last_height: # 網頁滑到最底
				break
			last_height = new_height

		img_url = []
		lost_url = []
		p = 0

		for i in range(len(all_posts_url)):
			browser.get(url + all_posts_url[i])

			# 刷新html
			try:
				soup = BeautifulSoup(browser.page_source,"lxml")
				WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.CLASS_NAME, 'ltEKP')))
			except:
				print('Stop in here: ' + url + all_posts_url[i])
				lost_url.append('Stop in here: ' + url + all_posts_url[i])

			if (soup.find(class_="Ckrof") != None):
				button = 1
				while(button != None): # 如果下一頁按鈕存在
					soup = BeautifulSoup(browser.page_source,"lxml")
					time.sleep(1)
					# 取得網頁元素框架
					img_frame = soup.find_all(class_="Ckrof")
					# 找圖片連結
					for i in img_frame:
						try:
							# 下載圖片
							new_img = i.img.get('src')
							if (new_img != None) & (new_img not in img_url):
								img_url.append(new_img)
								html = requests.get(new_img)
								img_name = folder_path + str(p + 1) +'.jpg'
								p += 1
								with open(img_name, 'wb') as file:
									file.write(html.content)
								file.close()
						except:
							pass

					# 尋找下一頁按紐
					try:
						WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.CLASS_NAME, '_6CZji')))
						button = browser.find_elements_by_class_name('_6CZji')[0]
						button.click()
					except:
						button = None

			else: # 如果有沒有下一頁(單張圖片或影片)
				# 取得網頁元素框架
				soup = BeautifulSoup(browser.page_source,"lxml")
				img_frame = soup.find(class_="KL4Bh")
				# 取得圖片連結
				try:
					# 下載圖片
					new_img = img_frame.img.get('src')
					if (new_img != None) & (new_img not in img_url):
						img_url.append(new_img)
						html = requests.get(new_img)
						img_name = folder_path + str(p + 1) +'.jpg'
						p += 1
						with open(img_name, 'wb') as file:
							file.write(html.content)
						file.close()
				except:
					pass

				time.sleep(15)

		if len(lost_url) > 0:
			with open('lost_post.txt', 'w+') as f:
				for i in lost_post:
					f.write(i + '\n')

		print('Download Finish!!!')

	elif (no_posts_yet != None) and (private_account == None):
		print('This account is private.')

	elif (no_posts_yet == None) and (private_account != None):
		print('No Posts Yet')