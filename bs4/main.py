from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
from openpyxl import Workbook
import os
import requests
import shutil


class App:
    def __init__(self, username='josep.martorell.33', password='F0renXis1234****', target_username='sheilavamodel',
                 path='/home/jmartorell/Pictures/instagram'):
        self.username = username
        self.password = password
        self.target_username = target_username
        self.path = path
        self.driver = webdriver.Firefox(
            executable_path="/usr/local/bin/geckodriver")
        self.error = False
        self.main_url = 'https://www.instagram.com'
        self.all_images = []
        self.no_of_posts = 0
        self.driver.get(self.main_url)
        sleep(3)
        self.log_in()
        if self.error is False:
            self.sweep_box()
            self.shoot_target()
        if self.error is False:
            self.scroll_down()
        if self.error is False:
            if not os.path.exists(path):
                os.mkdir(path)
            self.download_images()
        sleep(3)
        # self.driver.close()

    def write_spreadsheet(self, images, caption_path):
        print('writing to excel ...')
        filepath = os.path.join(caption_path, 'subtitles.xlsx')
        workbook = Workbook()
        workbook.save(filepath)
        worksheet = workbook.active
        row = 1
        worksheet.cell(row=row, column=1).value = 'Image name'
        worksheet.cell(row=row, column=2).value = 'Subtitle'
        row += 1

        for index, image in enumerate(images):
            filename = 'image_' + str(index) + '.jpg'
            try:
                caption = image['alt']
            except KeyError:
                caption = 'No caption exists'
            worksheet.cell(row=row, column=1).value = filename
            worksheet.cell(row=row, column=2).value = caption
            row += 1

        workbook.save(filepath)  # save file
        workbook.close()

    def download_subtitles(self, images):
        subtitles_folder_path = os.path.join(self.path, 'subtitles')
        if not os.path.exists(subtitles_folder_path):
            os.mkdir(subtitles_folder_path)
        self.write_spreadsheet(images, subtitles_folder_path)

    def download_images(self):
        self.all_images = list(set(self.all_images))
        self.download_subtitles(self.all_images)
        print('Length of all images', len(self.all_images))
        for index, image in enumerate(self.all_images):
            filename = 'image_' + str(index) + '.jpg'
            image_path = os.path.join(self.path, filename)
            link = image['src']
            print('Downloading image', index)
            response = requests.get(link, stream=True)
            try:
                with open(image_path, 'wb') as file:
                    shutil.copyfileobj(response.raw, file)  # source -  destination
            except Exception as e:
                print(e)
                print('Could not download image number ', index)
                print('Image link -->', link)

    def scroll_down(self):
        try:
            print('starting automatic scroll ...')
            no_of_posts = self.driver.find_element_by_xpath('//span[text()=" posts"]').text
            no_of_posts = no_of_posts.replace(' posts', '')
            no_of_posts = str(no_of_posts).replace(',', '')  # 2,156 --> 2156
            self.no_of_posts = int(no_of_posts)
            if self.no_of_posts > 12:
                no_of_scrolls = int(self.no_of_posts / 12) + 3
                try:
                    for value in range(no_of_scrolls):
                        soup = BeautifulSoup(self.driver.page_source, 'lxml')
                        for image in soup.find_all('img'):
                            self.all_images.append(image)

                        self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                        sleep(2)
                except Exception as e:
                    self.error = True
                    print(e)
                    print('Some error occurred while trying to scroll down')
            sleep(10)
        except Exception as e:
            print('Could not find no of posts while trying to scroll down\n', e)
            self.error = True

    def shoot_target(self):
        try:
            print('shooting target ' + self.target_username + ' ...')
            search_bar = self.driver.find_element_by_xpath('//input[@placeholder="Search"]')
            search_bar.send_keys(self.target_username)
            target_profile_url = self.main_url + '/' + self.target_username + '/'
            self.driver.get(target_profile_url)
            sleep(3)

        except Exception as e:
            self.error = True
            print('Could not find search bar\n', e)

    def sweep_box(self):
        # reload page
        sleep(2)
        self.driver.get(self.driver.current_url)

        try:
            print('closing popup window ...')
            not_now_btn = self.driver.find_element_by_xpath(
                '//*[text()="Not Now"]')

            not_now_btn.click()
            sleep(1)
        except Exception as e:
            print(e)

    def close_settings_window_if_there(self):
        try:
            self.driver.switch_to.window(self.driver.window_handles[1])
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
        except Exception as e:
            print(e)

    def log_in(self, ):
        try:
            print('logging in with username and password ...')
            user_name_input = self.driver.find_element_by_xpath(
                '//input[@aria-label="Phone number, username, or email"]')
            user_name_input.send_keys(self.username)
            sleep(1)

            password_input = self.driver.find_element_by_xpath('//input[@aria-label="Password"]')
            password_input.send_keys(self.password)
            self.driver.implicitly_wait(100)

            user_name_input.submit()
            sleep(1)

            self.close_settings_window_if_there()
        except Exception as e:
            print('Some exception occurred while trying to find username or password field\n', e)
            self.error = True


if __name__ == '__main__':
    app = App()
