from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from config import username, password
from selenium.common.exceptions import NoSuchElementException

import time
import random
import requests
import os



class InstagramBot():

    def __init__(self,username,password):

        self.username = username
        self.password = password
        self.browser = webdriver.Chrome ('./chromedriver/chromedriver')

    def close_browser(self):

        self.browser.close()
        self.browser.quit()

    def login(self):

        browser = self.browser
        browser.get('https://www.instagram.com/')
        time.sleep(random.randrange(3, 5))

        username_input = browser.find_element_by_name("username")
        username_input.clear()
        username_input.send_keys(username)

        time.sleep(2)

        password_input = browser.find_element_by_name("password")
        password_input.clear()
        password_input.send_keys(password)

        password_input.send_keys(Keys.ENTER)

        time.sleep(10)

    def like_photo_by_hashtag(self, hashtag):

        browser = self.browser

        browser.get(f'https://www.instagram.com/explore/tags/{hashtag}/')
        time.sleep(5)

        for i in range(1, 4):
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.randrange(3, 5))

        hrefs = browser.find_elements_by_tag_name('a')

        posts_urls = [item.get_attribute('href') for item in hrefs if "/p/" in item.get_attribute('href')]
        print(posts_urls)

        for url in posts_urls:
            try:
                browser.get(url)
                time.sleep(3)
                like_button = browser.find_element_by_xpath(
                    '/html/body/div[1]/section/main/div/div[1]/article/div[3]/section[1]/span[1]/button').click()
                time.sleep(random.randrange(80, 100))
            except Exception as ex:
                print(ex)
                self.close_browser()

    #проверка существует ли элемент на странице по xpath

    def expath_exists(self, url):
        browser=self.browser
        try:
            browser.find_element_by_xpath(url)
            exist = True
        except NoSuchElementException:
            exist = False
        return exist

    #ставим лайк на пост по прямой ссылке

    def put_exactly_like(self,userpost):

        browser = self.browser
        browser.get(userpost)
        time.sleep(4)

        wrong_userpage = "/html/body/div[1]/section/main/div/h2"
        if self.expath_exists(wrong_userpage):
            print('Такого поста не существует, проверьте URL')
            self.close_browser()
        else:
            print('Пост найден, ставлю лайк!')
            time.sleep(2)

            like_button = '/html/body/div[1]/section/main/div/div[1]/article/div[3]/section[1]/span[1]/button'
            browser.find_element_by_xpath(like_button).click()

            print(f'лайк к посту: {username} поставлен!')
            time.sleep(2)
            self.close_browser()

    # собирем ссылки на все посты пользователя
    def get_all_posts_urls(self, userpage):

        browser = self.browser
        browser.get(userpage)
        time.sleep(3)

        wrong_userpage = "/html/body/div[1]/section/main/div/h2"
        if self.expath_exists(wrong_userpage):
            print('Такого пользователя не существует, проверьте URL')
            self.close_browser()
        else:
            print('Пользователь найден, ставлю лайки!')
            time.sleep(2)

            post_count = int(browser.find_element_by_xpath('/html/body/div[1]/section/main/div/header/section/ul/li[1]/span/span').text)
            loops_count = int(post_count / 12)
            print(loops_count)

            posts_urls = []
            print(posts_urls)
            for i in range(0, loops_count):
                hrefs = browser.find_elements_by_tag_name('a')
                hrefs = [item.get_attribute('href') for item in hrefs if "/p/" in item.get_attribute('href')]

                for href in hrefs:
                    posts_urls.append(href)

                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.randrange(3, 5))
                print(f'Итерация #{i}')

                file_name = userpage.split("/")[-2]

                with open(f'{file_name}.txt', 'a') as file:
                    for posts_url in posts_urls:
                        file.write(posts_url + "\n")

                set_posts_urls = list(set(posts_urls))

                with open(f'{file_name}_set.txt', 'a') as file:
                    for posts_url in set_posts_urls:
                        file.write(posts_url + "\n")

    # ставим лайки на всех постах указанной страницы
    def put_many_likes(self, userpage):

        browser = self.browser
        self.get_all_posts_urls(userpage)
        file_name = userpage.split("/")[-2]
        time.sleep(2)
        browser.get(userpage)
        time.sleep(3)


        with open(f'{file_name}_set.txt') as file:
            urls_list = file.readlines()

            for post_url in urls_list:
                try:
                    browser.get(post_url)

                    like_button = '/html/body/div[1]/section/main/div/div[1]/article/div[3]/section[1]/span[1]/button'
                    browser.find_element_by_xpath(like_button).click()
                    time.sleep(random.randrange(80, 100))
                    time.sleep(2)

                    print(f'лайк к посту: {post_url} поставлен!')

                except Exception as ex:
                    print(ex)
                    self.close_browser()


        self.close_browser()

    #скачиваем фото и видео с инстаграм
    def download_userpage_content(self, userpage):

        browser = self.browser
        self.get_all_posts_urls(userpage)
        file_name = userpage.split("/")[-2]
        time.sleep(2)
        browser.get(userpage)
        time.sleep(3)

        #создание папки с именем пользователя
        if os.path.exists(f'{file_name}'):
            print('Папка уже имеется')
        else:
            os.mkdir(file_name)


        img_and_video_src_urls = []

        with open(f'{file_name}_set.txt') as file:
            urls_list = file.readlines()

            for post_url in urls_list:
                try:
                    browser.get(post_url)
                    time.sleep(4)

                    img_src = '/html/body/div[1]/section/main/div/div[1]/article/div[2]/div/div/div[1]/img'
                    video_src = '/html/body/div[1]/section/main/div/div[1]/article/div[2]/div/div/div[1]/div/div/video'
                    post_id = post_url.split("/")[-2]

                    if self.expath_exists(img_src):
                        img_src_url = browser.find_element_by_xpath(img_src).get_attribute('src')
                        img_and_video_src_urls.append(img_src_url)

                        #save img
                        get_img = requests.get(img_src_url)
                        with open(f'{file_name}/{file_name}_{post_id}_img.jpg', 'wb') as img_file:
                            img_file.write(get_img.content)
                        time.sleep(2)


                    elif self.expath_exists(video_src):
                        video_src_url = browser.find_element_by_xpath(video_src).get_attribute('src')
                        img_and_video_src_urls.append(video_src_url)

                        #save video
                        get_video = requests.get(video_src_url, stream=True)
                        with open(f'{file_name}/{file_name}_{post_id}_video.mp4', 'wb') as video_file:
                            for chunk in get_video.iter_content(chunk_size=1024*1024):
                                if chunk:
                                    video_file.write(chunk)
                    else:
                        print("Error")
                        img_and_video_src_urls.append(f'{file_name}/{file_name}_{post_url}, нет ссыдки')

                    print(f'Контент из поста {post_url} успешно загружен!')



                except Exception as ex:
                    print(ex)
                    self.close_browser()

            self.close_browser()

        with open(f'{file_name}/{file_name}_img_and_video_src_urls.txt', 'a') as file:
            for i in img_and_video_src_urls:
                file.write(i + "\n")

    #подписка на всех подписчиков указанного профиля
    def get_all_followers(self, userpage):

        browser = self.browser
        browser.get(userpage)
        time.sleep(3)
        file_name = userpage.split('/')[-2]

        # создание папки с именем пользователя
        if os.path.exists(f'{file_name}'):
            print(f'Папка {file_name} уже имеется')
        else:
            print(f'Создаем папку для аккаунта {file_name}')
            os.mkdir(file_name)


        wrong_userpage = "/html/body/div[1]/section/main/div/h2"
        if self.expath_exists(wrong_userpage):
            print(f'Пользователя {file_name} не существует, проверьте URL')
            self.close_browser()
        else:
            print(f'Пользователь {file_name} найден, скачиваем ссылки!')
            time.sleep(2)

            followers_button = browser.find_element_by_xpath('/html/body/div[1]/section/main/div/header/section/ul/li[2]/a')

            followers_count = browser.find_element_by_xpath('/html/body/div[1]/section/main/div/header/section/ul/li[2]/a/span').get_property('title')

            if len(followers_count) > 3:
                followers_count = int(''.join(followers_count.split(',')))
                print(followers_count)


            else:
                followers_count = int(followers_count)
                print(f'Followers number: {followers_count}')
            time.sleep(4)

            loops_count = int(followers_count / 12)
            if loops_count > 100:
                loops_count = 100

            print(f'Число итераций: {loops_count}')
            time.sleep(3)

            followers_button.click()
            time.sleep(2)

            followers_ul = browser.find_element_by_xpath('/html/body/div[4]/div/div/div[2]')

            try:
                followers_urls = []

                for i in range(1, loops_count + 1):
                    browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", followers_ul)
                    time.sleep(random.randrange(2,4))
                    print(f'Итерация #{i}')

                all_urls_div = followers_ul.find_elements_by_tag_name('li')

                for url in all_urls_div:
                    url = url.find_element_by_tag_name('a').get_attribute('href')
                    followers_urls.append(url)

                #Сохраняем список подписчиков в файл
                with open(f'{file_name}/{file_name}.txt', 'a') as text_file:
                    for link in followers_urls:
                        text_file.write(link + '\n')


                with open(f'{file_name}/{file_name}.txt') as text_file:
                    users_urls = text_file.readlines()

                    for user in users_urls:
                        try:
                            try:
                                with open(f'{file_name}/{file_name}_subscribe_list.txt', 'r') as subscribe_list_file:
                                    lines = subscribe_list_file.readlines()
                                    if user in lines:
                                        print(f'Вы уже подписаны на {user}, давайте перейдем к слкдующему аккаунту!')
                                        continue

                            except Exception as ex:
                                print('Файл с ссылками уже создан')

                            browser = self.browser
                            browser.get(user)
                            page_owner = user.split('/')[-2]

                            if self.expath_exists('/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/a'):
                                print('Это ваш профиль, пропускаем итерацию')

                            elif self.expath_exists('/html/body/div[1]/section/main/div/header/section/div[1]/div[2]/div/span/span[1]/button/div/span'):
                                print(f'Вы уже подписаны на {page_owner}, пропускаем итерацию')

                            else:
                                time.sleep(random.randrange(2,6))

                                if self.expath_exists('/html/body/div[1]/section/main/div/div/article/div[1]/div/h2'):
                                    try:
                                        follow_button = browser.find_element_by_xpath('/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/button').click()
                                        print(f'Запросил подписку на пользователя {page_owner}, у него закрытый аккаунт')

                                    except Exception as ex:
                                        print(ex)

                                else:

                                    try:

                                        if self.expath_exists('/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/button'):
                                            follow_button = browser.find_element_by_xpath('/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/button').click()
                                            print(f'Подписка на {page_owner} прошла успешно')

                                        else:
                                            follow_button = browser.find_element_by_xpath('/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/span/span[1]/button').click()
                                            print(f'Подписка на {page_owner} прошла успешно')

                                    except Exception as ex:
                                        print(ex)

                                #Производим запись данных в файл
                                with open(f'{file_name}/{file_name}_subscribe_list.txt', 'a') as subscribe_list_file:
                                    subscribe_list_file.write(user)

                                time.sleep(random.randrange(40,120))




                        except Exception as ex:
                            print(ex)
                            self.close_browser()






            except Exception as ex:
                print(ex)
                self.close_browser()

        self.close_browser()



    #метод для отправки сообщений в директ
    def send_direct_message(self, username="", message=""):

        browser = self.browser
        time.sleep(random.randrange(2,4))

        direct_message_button = '/html/body/div[1]/section/nav/div[2]/div/div/div[3]/div/div[2]/a'

        if not self.expath_exists(direct_message_button):
            print('error')
            self.close_browser()
        else:
            direct_message = browser.find_element_by_xpath(direct_message_button).click()
            print('sending a message')
            time.sleep(random.randrange(2,4))

        #отключение всплывающего окна
        if self.expath_exists('/html/body/div[4]/div'):
            browser.find_element_by_xpath('/html/body/div[4]/div/div/div/div[3]/button[2]').click()
        time.sleep(random.randrange(2, 4))


        send_message_button = browser.find_element_by_xpath('/html/body/div[1]/section/div/div[2]/div/div/div[2]/div/button').click()
        time.sleep(random.randrange(2, 4))

        #вводим пользователя

        to_input = browser.find_element_by_xpath('/html/body/div[4]/div/div/div[2]/div[1]/div/div[2]/input')
        to_input.send_keys(username)
        time.sleep(random.randrange(2, 4))

        #выбор получателя
        user_list = browser.find_element_by_xpath('/html/body/div[4]/div/div/div[2]/div[2]/div[2]').find_element_by_xpath('/html/body/div[4]/div/div/div[2]/div[2]/div[1]/div/div[3]/button').click()
        time.sleep(random.randrange(2, 4))

        next_button = browser.find_element_by_xpath('/html/body/div[4]/div/div/div[1]/div/div[2]/div/button').click()
        time.sleep(random.randrange(2, 4))

        text_message_area = browser.find_element_by_xpath('/html/body/div[1]/section/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[2]/textarea')
        text_message_area.clear()
        text_message_area.send_keys(message)
        time.sleep(random.randrange(2,8))
        text_message_area.send_keys(Keys.ENTER)
        print(f'Сообщение для {username}б успешно отправлено!')

        self.close_browser()






my_bot = InstagramBot(username, password)
my_bot.login()
#my_bot.send_direct_message('oksanabilenka','Это тестовое сообщение')
my_bot.get_all_followers("https://www.instagram.com/mojodesserts/")







