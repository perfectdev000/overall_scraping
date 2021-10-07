import ast
import os
import re
import zipfile
import random
import time
from multiprocessing.pool import Pool

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask
from capmonster_python import *
from bs4 import BeautifulSoup

from anticaptcha import api_key
from anticaptcha import capmonster_api_key

num_pool = 2

def check_website(url, proxies, row, password, log=None):
    if '.etix.' in url:
        return Etix(url, proxies, row, log, password)
    elif '.eventbrite.' in url:
        return Eventbrite(url, proxies, row, log, password)
    elif '.bigtickets.' in url:
        return BigTicket(url, proxies, row, log, password)
    elif '.frontgatetickets.' in url:
        return FrontGate(url, proxies, row, log, password)
    elif '.ticketweb.' in url:
        return TicketWeb(url, proxies, row, log, password)
    elif 'seetickets.us' in url:  
        return SeeTickets(url, proxies, row, log, password)
    elif 'showclix.' in url:  
        return Showclix(url, proxies, row, log, password)

class Scraper(object):

    def __init__(self, url, proxies, row, log, password):
        self.log = log
        self.ticket_url = url
        self.ticket_row = row
        self.password = password
        with open("proxies_storm.txt", 'r') as f:
            self.proxies = f.read().split('\n')

    def input_password(self, driver):
        pass

    def log_message(self, msg):
        pass

    def check_ticket_qty(self, cap):
        pass

    def wait_for_element(self, driver, element, type=By.ID):
        try:
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((type, element))
            )
        except:
            return False
        finally:
            return True
    #TODO
    def open_driver(self, use_proxy=False,
                    user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36.',
                    headless=False):
        random_proxy = random.choice(self.proxies)
        auth, ip_port = random_proxy.split('@')
        user, pwd = auth.split(':')
        ip, port = ip_port.split(':')
        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """

        background_js = """
        var config = {
                mode: "fixed_servers",
                rules: {
                  singleProxy: {
                    scheme: "http",
                    host: "%s",
                    port: parseInt(%s)
                  },
                  bypassList: ["localhost"]
                }
              };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """ % (ip, port, user, pwd)
        chrome_options = webdriver.ChromeOptions()
        if headless:
            pass
            # chrome_options.add_argument('--headless')
        
        if use_proxy:
            pluginfile = 'proxy_auth_plugin.zip'
            with zipfile.ZipFile(pluginfile, 'w') as zp:
                zp.writestr("manifest.json", manifest_json)
                zp.writestr("background.js", background_js)
            chrome_options.add_extension(pluginfile)
            time.sleep(2)
        if user_agent:
            chrome_options.add_argument('--user-agent=%s' % user_agent)
        try:
            driver = webdriver.Chrome('chromedriver', chrome_options=chrome_options)
        except Exception as E:
            return self.open_driver()

        # Check if it's working
        driver.get('https://www.google.com/')
        try:
            driver.find_element_by_id("L2AGLb").click()
            time.sleep(0.5)
        except:
            pass
        try:
            driver.find_element_by_css_selector('input[name="q"]')
        except:
            driver.quit()
            return self.open_driver()
        return driver


class Etix(Scraper):

    def input_password(self, driver):
        if self.password:
            driver.find_elements_by_xpath('//*[@placeholder="Password"]')[int(self.ticket_row) - 1].send_keys(self.password)
    
    def get_qty(self, box_id):
        driver = self.open_driver()            
        driver.get(self.ticket_url)
        self.input_password(driver)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        sold_out = soup.find('h2', {'class': 'header-message'})
        if sold_out:
            # sold_out  ticktes
            if 'sold out' in sold_out.text.lower():
                driver.quit()
                return 0

        if soup.find('p', {'class': 'callout error'}):
            driver.quit()
            print('session expried')
            return 0

        if soup.find('//*[@id="view"]/div[3]'):
            driver.quit()
            print('Tickets is ended')
            return 0

        if soup.find('div', {'class': 'callout error emphasize'}):
            driver.quit()
            print('Can\'t scrap! It\' sold out all')
            return 0

        try:
            id = soup.find('form', {'name': 'frmPickTicket'}).find_all('select')[int(self.ticket_row) - 1]['id']
            tab_click = False

        except:
            tab_click = True
            try:
                driver.find_element_by_xpath('//*[@id="ticket-type"]/li[2]/a').click()
            except:
                driver.quit()
                print(0, '2Tickets added...')
                return 0
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            try:
                id = soup.find('form', {'name': 'frmPickTicket'}).find_all('select')[int(self.ticket_row) - 1]['id']
            except:
                print(0, '3Tickets added...')
                return 0

        opt = driver.find_elements_by_xpath('//*[@id="{}"]/option'.format(id))[-1]
        opt_qty = int(opt.get_attribute('value'))
        opt.click()
        
        if soup.find('div', {'class': 'g-recaptcha'}):
          if self.cap == "Capmonster":# solve this capmonster
            capmonster = NoCaptchaTaskProxyless(client_key=capmonster_api_key)
            taskId = capmonster.createTask(website_key='6LdoyhATAAAAAFdJKnwGwNBma9_mKK_iwaZRSw4j', website_url=self.ticket_url)
            print("Waiting to solution by capmonster workers")
            try:
                response = capmonster.joinTaskResult(taskId=taskId)
            except:
                print(0, 'Tickets added....')
                driver.quit()
                return 0
          else:
            # solve this anticapcha
            client = AnticaptchaClient(api_key)
            task = NoCaptchaTaskProxylessTask(self.ticket_url, '6LdoyhATAAAAAFdJKnwGwNBma9_mKK_iwaZRSw4j')
            try:
                job = client.createTask(task)
                print("Waiting to solution by Anticaptcha workers")
                job.join()
                # Receive response
                response = job.get_solution_response()
            except:
                print(0, 'Tickets added....')
                driver.quit()
                return 0
          print("Received solution", response)
          driver.execute_script('document.getElementById("g-recaptcha-response").innerHTML = "%s"' % response)
          driver.execute_script('document.getElementById("submitBtn").removeAttribute("disabled")')
          time.sleep(3)

        try:
            driver.find_element_by_id("allow_cookies").click()
            time.sleep(0.5)
            driver.find_element_by_name("addSeatBtn").click()
            time.sleep(0.5)
            # new_soup = BeautifulSoup(driver.page_source, 'html.parser')
            # if new_soup.find('iframe' , {'title':'recaptcha challenge'}):
            #     if self.cap == "Capmonster":# solve this capmonster
            #         capmonster = NoCaptchaTaskProxyless(client_key=capmonster_api_key)
            #         taskId = capmonster.createTask(website_key='6LdoyhATAAAAAFdJKnwGwNBma9_mKK_iwaZRSw4j', website_url=self.ticket_url)
            #         print("Waiting to solution by capmonster workers")
            #         try:
            #             response = capmonster.joinTaskResult(taskId=taskId)
            #         except:
            #             print(0, 'Tickets added....')
            #             driver.quit()
            #             return 0
            #     else:
            #         # solve this anticapcha
            #         client = AnticaptchaClient(api_key)
            #         task = NoCaptchaTaskProxylessTask(self.ticket_url, '6LdoyhATAAAAAFdJKnwGwNBma9_mKK_iwaZRSw4j')
            #         try:
            #             job = client.createTask(task)
            #             print("Waiting to solution by Anticaptcha workers")
            #             job.join()
            #             # Receive response
            #             response = job.get_solution_response()
            #         except:
            #             print(0, 'Tickets added....')
            #             driver.quit()
            #             return 0
            #     print("Received solution", response)
            #     print('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<b')
            #     time.sleep(3000)
            
            new_soup = BeautifulSoup(driver.page_source, 'html.parser')
            if new_soup.find('div', {'class': 'validationError error'}):
                driver.quit()
                print('amount miss selected')
                return 0 
            if new_soup.find('div', {'class': 'callout error'}):
                driver.quit()
                print('you due to the high volume of requests for the same seats')
                return 0 
        
        except Exception as e:
            print(e)
            print(0, '4Tickets added....')
            driver.quit()
            return 0

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        error = soup.find('div', {'class': 'callout'})
        if error:
            if 'Tickets Currently Not Available' in error.text:
                print(0, '5Tickets added...')
                driver.quit()
                return 0
        error = soup.find('div', {'class': 'validationError error'})

        num_of_options = len(driver.find_elements_by_xpath('//*[@id="{}"]/option'.format(id)))
        if error:
            error_txt = error.text.strip()
            index = 1
            while True:
                # TODO Localize if error
                if tab_click:
                    driver.find_element_by_xpath('//*[@id="ticket-type"]/li[2]/a').click()
                    soup = BeautifulSoup(driver.page_source, 'html.parser')

                opt = driver.find_elements_by_xpath('//*[@id="{}"]/option'.format(id))[-1 - index]
                index += 1
                opt_qty = int(opt.get_attribute('value'))
                if opt_qty == 0:
                    driver.quit()
                    return 0
                opt.click()
                driver.find_element_by_xpath('//*[@id="view"]/div[5]/form/div[2]/button').click()
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                error = soup.find('div', {'class': 'validationError error'})
                if error:
                    if num_of_options == index:
                        driver.quit()
                        return 0
                    continue
                else:
                    break
        time.sleep(3)           
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        opt_qty = len(soup.find('table', {'class':'table table--bordered table-shopping-cart'}).findChildren(['tbody', 'tr']))-2
        
        driver.quit()
        print(opt_qty, 'Tickets added')
        return opt_qty  # driver

    def check_ticket_qty(self, cap):
        self.cap = cap
        driver = self.open_driver()
        if '?method=switchSelectionMethod&selection_method=byBest' not in self.ticket_url:
            if '?' in self.ticket_url:
                self.ticket_url += "&method=switchSelectionMethod&selection_method=byBest"
            else:
                self.ticket_url += '?method=switchSelectionMethod&selection_method=byBest'
        driver.get(self.ticket_url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        if 'Public Onsale Begins:' in soup.text.strip():
            print('this tickets has special date')
            driver.quit()
            return '-', False
        if self.wait_for_element(driver, 'view'):
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            view = soup.find('div', {'id': 'view'}).text.strip()
            if 'Tickets Currently Not Available' in view:
                print('no tickets available')
                driver.quit()
                return 0

            sold_out = soup.find('h2', {'class': 'header-message'})
            if sold_out:
                if 'sold out' in sold_out.text.lower():
                    driver.quit()
                    return 0
                        
            driver.quit()
            qty = 0
            timer_run_out = False
            oldtime = time.time()
            next_cycle = True
            while True:
                if time.time() - oldtime >= 600:
                    timer_run_out = True
                    break
                loop_qty = 0
                with Pool(num_pool) as p:
                    r = p.map(self.get_qty, list(range(20)))
                    for q in r:
                        loop_qty += q
                        if q==0:
                            next_cycle = False

                qty += loop_qty
                print('Total QTY:', qty)
                if next_cycle ==False:
                        break
                if loop_qty == 0:
                    break

            return qty, timer_run_out

class Eventbrite(Scraper):
    def input_password(self, driver):
        if self.password:
            driver.find_element_by_xpath('//*[@data-automation="promo-code-form-link"]').click()
            driver.find_element_by_id('promo-code-field').send_keys(self.password)
            time.sleep(0.5)
            driver.find_element_by_xpath('//span[@class="eds-field-styled__aside eds-field-styled__aside-suffix"]/button').click()

    def get_qty(self, _id):
        print('eventbrite type1')
        driver = self.open_driver(headless=True)
        self.drivers.append(driver)
        driver.get(self.ticket_url)
        self.input_password(driver)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        if soup.find('span', {'class':'ticket-status eds-text-color--ui-600 eds-text-bm ticket-status--no-wrap eds-text--right'}):
            print('tickets is unavaliable1')
            driver.quit()
            return 0

        if soup.find('span', {'class':'micro-ticket-box__status js-micro-ticket-box-status l-pad-hor-2 hide-small hide-medium'}):
            print('tickets is unavaliable1 casue of scrap')
            driver.quit()
            return 0
        
        try:
            opt = driver.find_elements_by_xpath('//*[@id="{}"]/option'.format(_id))[-1]
        except IndexError:
            print('0 Tickets added')
            driver.quit()
            return 0
        
        opt_qty = int(opt.get_attribute('value'))
        # time.sleep(3000)
        try:
            opt.click()
        except:
            driver.find_element_by_xpath('//*[@id="event-page"]/main/div[1]/div[2]/div/div[2]/div[2]/div/div[3]/div/div/div/div/form/span/span/button').click()
            time.sleep(1)
            try:
                opt = driver.find_elements_by_xpath('//*[@id="{}"]/option'.format(_id))[-1]
            except IndexError:
                print('0 Tickets added')
                driver.quit()
                return 0
            opt.click()
        try:
            driver.find_element_by_xpath('//*[@type="submit"]').click()
            time.sleep(0.5)
            new_soup = BeautifulSoup(driver.page_source, 'html.parser')
            if new_soup.find('div', {'class':'eds-notification-bar__content-child'}):
                print('tickets is sold out cause of scrap!!! or The tickets you selected are no longer available!!')
                driver.quit()
                return 0
        except:
            print('0 Tickets added')
            driver.quit()
            return 0

        opt_qty = 0
        if self.wait_for_element(driver, 'time_left'):
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            try:
                opt_qty = int(soup.find('td', {'class': 'quantity_td'}).text.strip())
            except AttributeError:
                pass

        driver.quit()
        print(opt_qty, 'Tickets added')
        return opt_qty

    def get_qty_new(self, _id):
        driver = self.open_driver(headless=True)
        self.drivers.append(driver)
        driver.get(self.ticket_url)
        time.sleep(0.5)

        main_id = driver.find_element_by_tag_name('body').get_attribute('data-event-id')
        xpath = '//*[@id="eventbrite-widget-modal-{}"]'.format(main_id)
        try:
            iframe = driver.find_element_by_xpath(xpath)
        except:
            print('0 Tickets added and can\'t open the iframe')
            driver.quit()
            return 0
            
        driver.switch_to.frame(iframe)
        
        page_content = BeautifulSoup(driver.page_source, 'html.parser')
        if page_content.find('div', {'class':'eds-text-hs eds-text-color--grey-800 eds-l-pad-top-2 eds-text--center'}):
            print('unvisable iframe')
            driver.quit()
            return 0

        self.input_password(driver)
        
        page_content = BeautifulSoup(driver.page_source, 'html.parser')
        if self.opt_len > len(page_content.find_all('select')):
                print('0 Tickets added', '+++++this ticket row is sold out')
                driver.quit()
                return 0

        # one_row = page_content.find('span', {'class':'ticket-status eds-text-color--ui-600 eds-text-bm ticket-status--no-wrap eds-text--right'})
        # if one_row:
        #     if 'Unavailable' in one_row.text.strip():
        #         driver.quit()
        #         print('tickets is Unavaiable or sold out1')
        #         return 0
        #     if 'Sales ended' in one_row.text.strip():
        #         driver.quit()
        #         print('tickets is Unavaiable or sold out2')
        #         return 0
        
        time.sleep(2)
        
        try:
            opt = driver.find_elements_by_class_name('tiered-ticket-display-content-root')[int(self.ticket_row)-1]
            # try:
            #     opt = opt.find_elements_by_tag_name('option')[-1]
            # except:
            #     print('0 Tickets added', 'unvisable button and tickets')
            #     driver.quit()
            #     return 0

        except IndexError:
            try:
                time.sleep(3)
                opt = driver.find_elements_by_class_name('eds-card-list__item')[int(self.ticket_row)-1]
                try:
                    opt = opt.find_elements_by_tag_name('option')[-1]
                except:
                    print('0 Tickets added', 'unvisable button and tickets')
                    driver.quit()
                    return 0
            except IndexError:
                print('0 Tickets added', 'idx')
                driver.quit()
                return 0
        
        opt_qty = int(opt.get_attribute('value'))
        # print(f'>>>>>>>>>>>>>>>{opt_qty}')
        # time.sleep(3000)
        if opt_qty == 1:
            print('this thread is ignored cause of ticket number is 1')
            driver.quit()
            return 0
        
        opt.click()

        try:
            driver.find_element_by_xpath('//*[@data-automation="eds-modal__primary-button"]').click()
        except:
            print('0 Tickets added', 'btn disabled cause of sold out')
            driver.quit()
            return 0

        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        alert = soup.find('div', {'class': 'eds-notification-bar__content'})
        if alert:
            if 'The tickets you selected are no longer available' in alert.text:
                print('0 Tickets added', 'show the read alert')
                driver.quit()
                return 0

            if 'The seats you selected aren\'t available next to each other.' in alert.text:
                print('0 Tickets added', 'show the read alert')
                driver.quit()
                return 0      

            if 'Your requested ticket quantity exceeds the number provided by your promotional code.' in alert.text:
                print('you request many tickets using promo code')
                driver.quit()
                return 0
        else:
            pass       
        # print(f'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>{opt_qty}')
        # time.sleep(3000)
        driver.quit()
        print(opt_qty, 'Tickets added')
        return opt_qty

    def check_ticket_qty(self, cap):
        driver = self.open_driver()
        self.drivers = []

        if '?' in self.ticket_url:
            self.ticket_url = self.ticket_url[:self.ticket_url.find('?')]
        if '#tickets' not in self.ticket_url:
            self.ticket_url += '#tickets'
        driver.get(self.ticket_url)

        _id = driver.find_element_by_tag_name('body').get_attribute('data-event-id')
        xpath = '//*[@id="eventbrite-widget-modal-{}"]'.format(_id)
        
        try:
            iframe = driver.find_element_by_xpath(xpath)
            driver.switch_to.frame(iframe)
            self.input_password(driver)
            new_style = True
            print('eventbrite type2')
        except selenium.common.exceptions.NoSuchElementException:
            new_style = False
            print('eventbrite type1')

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        length = len(soup.find_all('select'))
        self.opt_len = length
        if soup.find('span', {'class':'micro-ticket-box__status js-micro-ticket-box-status l-pad-hor-2 hide-small hide-medium'}):
            driver.quit()
            print('tickets is Unavailable')
            return '-', False
        if not new_style:
            try:
                _id = soup.find_all('select')[int(self.ticket_row) - 1]['id']
            except Exception as e:
                print(e)
                driver.quit()
                print('No tickets available')
                return '-', False
        else:
            try:
                _id = soup.find_all('select')[int(self.ticket_row) - 1]['id']
            except IndexError:
                try:
                    _id = soup.find_all('select', {'name': 'ticket-quantity-selector'})[int(self.ticket_row) - 1]['data-automation']
                except Exception as e:
                    try:
                        _id = soup.find_all('div', {'class': 'tiered-ticket-quantity-select eds-g-cell eds-text-color--grey-800 eds-ticket-card-content__quantity-selector'})[int(self.ticket_row) - 1]['data-automation']
                    except:
                        driver.quit()
                        print('No tickets available')
                        return '-', False
        driver.quit()

        timer_run_out = False
        num_pool = 10
        lst = [_id for x in range(num_pool)]
        qty = 0
        oldtime = time.time()
        next_cycle = True

        if new_style:
            func = self.get_qty_new
        else:
            func = self.get_qty
        while True:
            if time.time() - oldtime >= 480:
                break
            loop_qty = 0
            if func==0:
                print("ticket amount is 0")
                break
            with Pool(num_pool) as p:  
                r = p.map(func, lst)
                for q in r:
                    loop_qty += q
                    if q==0:
                        next_cycle = False
                
            qty += loop_qty
            print('Total QTY:', qty)
            if next_cycle == False:
                break
            if loop_qty == 0:
                break
            time.sleep(2)

        print('total qty', qty)
        return qty, timer_run_out

class FrontGate(Scraper):

    def input_password(self, driver):
        if self.password:
            self.ticket_url += '/passcode/' + self.password
        #     driver.find_element_by_id('txt-passcode').send_keys(self.password)
        #     driver.find_element_by_id('btn-passcode').click()

    def get_qty(self, max_amount):
        qty = 0
        driver = self.open_driver()
        self.input_password(driver)
        driver.get(self.ticket_url)

        for i in range(max_amount):
            try:
                driver.find_element_by_xpath('//*[@id="cart_tickets_form"]/div[1]/div[{}]/div/div[4]/div[1]/button[2]'.format(self.ticket_row)).click()
            except selenium.common.exceptions.NoSuchElementException:
                driver.quit()
                print(qty, 'Tickets added')
                return qty

        driver.find_element_by_id('btn-add-cart').click()

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        captcha = soup.find('div', {'id': 'google_captcha'})
        if captcha:
          if self.cap=="Capmonster":
            # using capmonster
            driver.execute_script('document.getElementById("div-btn-modal-submit").removeAttribute("disabled")')
            capmonster = NoCaptchaTaskProxyless(client_key=capmonster_api_key)
            taskId = capmonster.createTask(website_key='6Lev0AsTAAAAALtgxP66tIWfiNJRSNolwoIx25RU', website_url=self.ticket_url)
            print("Waiting to solution by capmonster workers")
            response = capmonster.joinTaskResult(taskId=taskId)
            print("Received solution", response)
            driver.execute_script('document.getElementById("g-recaptcha-response").innerHTML = "%s"' % response)
            time.sleep(1)
            driver.find_element_by_id('div-btn-modal-submit').click()
          else:
            # using anti_captcha
            driver.execute_script('document.getElementById("div-btn-modal-submit").removeAttribute("disabled")')
            client = AnticaptchaClient(api_key)
            task = NoCaptchaTaskProxylessTask(self.ticket_url, '6Lev0AsTAAAAALtgxP66tIWfiNJRSNolwoIx25RU')
            job = client.createTask(task)
            print("Waiting to solution by Anticaptcha workers")
            job.join()
            response = job.get_solution_response()
            print("Received solution", response)
            driver.execute_script('document.getElementById("g-recaptcha-response").innerHTML = "%s"' % response)
            time.sleep(1)
            driver.find_element_by_id('div-btn-modal-submit').click()
        
        time.sleep(1)
        print('click the add tickets')
        try:
            driver.find_element_by_class_name('eds-btn eds-btn--button eds-btn--fill').click()
        except:
            pass
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        try:
            error_box = soup.find('div', {'class':'div-add-cart-message'})
            
            if 'Unable to cart' in error_box.text.strip():
                print('amount miss selected')
                driver.quit()
                return 0
        except:
            pass

        if self.wait_for_element(driver, '//*[@id="cart-success-header"/h2]', By.XPATH):
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            real_amount = soup.find('span', {'class': 'cartTotal badge'}).decode_contents()
            qty = int(real_amount)
            # print(f"succesed>>>>>>>>>>{real_amount}")
            time.sleep(3)

        driver.quit()
        print(qty, 'Tickets added')
        return qty

    def check_new_style(self, driver):
        pass

    def check_ticket_qty(self, cap):
        print(cap)
        self.cap = cap
        driver = self.open_driver()
        driver.get(self.ticket_url)
        try: 
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            has_date = soup.find('div',{'class':'onSaleDate'})
            if 'On Sale' in has_date.text.strip():
                print('this tickets has special sale data')
                driver.quit()
                return '-', False
        except:
            pass
        self.input_password(driver)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        ticket = soup.find('form', {'id': 'cart_tickets_form'}).find_all('div', {'class': 'ticket-price-section'})[
            int(self.ticket_row) - 1]
        spinner = ticket.find('div', {'class': 'number-spinner'})

        #driver.switch_to.frame(iframe)
        try:
            max_amount = spinner.find('input')['data-quantityarray']
        except:
            driver.quit()
            print("unavailable or sold out")
            return '-', False
        max_amount = ast.literal_eval(max_amount)[-1]
        driver.quit()
        
        timer_run_out = False
        # num_pool = 2
        lst = [max_amount for x in range(num_pool)]
        qty = 0
        oldtime = time.time()
        while True:
            if time.time() - oldtime >= 900:
                timer_run_out = True
                break
            loop_qty = 0
            with Pool(num_pool) as p:
                r = p.map(self.get_qty, lst)
                for q in r:
                    loop_qty += q
                    if q==0:
                        print("the tickets is sold out by scrap")
                        break
            qty += loop_qty
            print('Total QTY:', qty)
            if loop_qty == 0:
                break
            time.sleep(2)

        print('total qty', qty)
        return qty, timer_run_out

class TicketWeb(Scraper):

    def input_password(self, driver):
        if self.password:
            driver.find_element_by_id('edp_accessCodeTxt').send_keys(self.password)
            driver.find_element_by_id('edp_accessCodeBtn').click()
    def get_qty(self, x):
        qty = 0
        driver = self.open_driver()
        driver.get(self.ticket_url)
        # self.input_password(driver)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        sold_out = soup.find('div', {'class': 'section section-status theme-mod eventStatusCustomMessage'})
        if sold_out:
            if 'This screening is currently sold out' in sold_out.text.strip():
                driver.quit()
                print('0 Tickets added')
                return 0
        
        no_tickets_available = soup.find('ul', {'class': 'status-info sold-out theme-primary-color'})
        if no_tickets_available:
            if 'Sorry, there are currently no tickets  available through TicketWeb.' in no_tickets_available.text.strip():
                driver.quit()
                print('0 Tickets added')
                return 0

        ticket = soup.find_all('div', {'class': 'action-select'})[int(self.ticket_row)-1]
        max_amount = int(ticket.find('div', {'class': 'value-select'})['limit'])
        for i in range(max_amount):
            driver.find_elements_by_xpath('//a[@ng-click="plus()"]')[int(self.ticket_row)-1].click()
            #driver.find_element_by_xpath('//*[@id="{}"]/div/div/div/a[2]'.format(ticket_id)).click()

        captcha = soup.find('div', {'class': 'g-recaptcha'})
        if captcha:
          if self.cap == 'Capmonster':
            capmonster = NoCaptchaTaskProxyless(client_key=capmonster_api_key)
            taskId = capmonster.createTask(website_key='6LfQ2VYUAAAAACEJaznob8RVoWsBEFTec2zDPJwv', website_url=self.ticket_url)
            print("Waiting to solution by capmonster workers")
            try:
                response = capmonster.joinTaskResult(taskId=taskId)
            except:
                print(0, 'Tickets added....')
                driver.quit()
                return 0
          else:
            site_key = '6LfQ2VYUAAAAACEJaznob8RVoWsBEFTec2zDPJwv'
            client = AnticaptchaClient(api_key)
            task = NoCaptchaTaskProxylessTask(self.ticket_url, site_key)
            job = client.createTask(task)
            print("Waiting to solution by Anticaptcha workers")
            job.join()
            # Receive response
            response = job.get_solution_response()
        print("Received solution", response)
        driver.execute_script('document.getElementById("g-recaptcha-response").innerHTML = "%s"' % response)
        time.sleep(2)


        driver.find_element_by_id('edp_checkout_btn').click()
        time.sleep(1)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        if soup.find('div', {'class' : 'error-message theme-mod-bd theme-error-color ng-scope'}):
            print('the tickets amount is limited')
            driver.quit()
            return 0

        if self.wait_for_element(driver, '/html/body/div[1]/header/div/div/ul/li/p[2]', By.XPATH):
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            if soup.find('ul', {'class':'status-info sold-out theme-primary-color'}):
                driver.quit()
                return 0
            if 'This event is sold out' in soup.text.strip():
                driver.quit()
                print('It can not get the tickets cause of sold_out')
            
            try:
                qty = int(soup.find('p', {'class': 'small tickets-sum'}).text.split(' ')[0].strip())
            except AttributeError:
                driver.quit()
                return self.get_qty(x)
        driver.quit()
        print(qty, 'Tickets added')
        return qty


    def check_ticket_qty(self, cap):
        print(cap)
        if '?' in self.ticket_url:
            self.ticket_url = self.ticket_url[:self.ticket_url.find('?')]
        self.cap = cap
        driver = self.open_driver()
        driver.get(self.ticket_url)
        # self.input_password(driver)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # captcha = soup.find('div', {'class': 'g-recaptcha'})
        # if captcha:
        #     driver.quit()
        #     return 'CAPTCHA', False


        sold_out = soup.find('div', {'class': 'section section-status theme-mod eventStatusCustomMessage'})
        if sold_out:
            if 'This screening is currently sold out' in sold_out.text.strip():
                driver.quit()
                print('It can not get the tickets cause of sold out')

        no_tickets_available = soup.find('ul', {'class': 'status-info sold-out theme-primary-color'})
        if no_tickets_available:
            if 'Sorry, there are currently no tickets  available through TicketWeb.' in no_tickets_available.text.strip():
                driver.quit()
                print('It can not get the tickets cause of no_tickets_available')
                return '-'
            if 'This event is sold out' in no_tickets_available.text.strip():
                driver.quit()
                print('It can not get the tickets cause of sold_out')
                return '-'
        
        driver.quit()
        num_pool=10
        lst = [x for x in range(num_pool)]
        qty = 0
        oldtime = time.time()
        timer_run_out = False
        while True:
            if time.time() - oldtime >= 600:
                timer_run_out = True
                break
            loop_qty = 0
            with Pool(num_pool) as p:
                r = p.map(self.get_qty, lst)
                for q in r:
                    loop_qty += q
                    if q ==0 :
                        print("the tickets sold out by scrap!")
                        break
            qty += loop_qty
            print('Total QTY:', qty)
            if loop_qty == 0:
                break
            time.sleep(3)

        print('total qty', qty)
        return qty, timer_run_out

class BigTicket(Scraper):

    def get_qty(self, max_amount):
        driver = self.open_driver()
        driver.get(self.ticket_url) 

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        try:
            buy_now = soup.find('button', {'class': 'btn btn-primary btn-lg btn-sticky-panel'})
            if 'BUY NOW' in buy_now.text:
                print("enter the buy now area")
                buy_button_elements = driver.find_element_by_class_name('btn-sticky-panel')
                driver.execute_script("arguments[0].click();", buy_button_elements)
                time.sleep(0.5)
        except Exception as e:
            print(e)
            # can't find the select tag
            driver.quit()
            print(0, 'Tickets added...')
            return 0
        
        #click the max value and get value
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        try: 
            if 'The maximum number of attendees for this event has been reached' in soup.find('form', {'name': 'EventForm'}).decode_contents():
                print("Ticket's number is maximum")
                driver.quit()
                return 0
            select_name = soup.find('form', {'name': 'EventForm'}).find_all('select')[int(self.ticket_row) - 1]['name']
            opt = driver.find_elements_by_xpath('//*[@name="{}"]/option'.format(select_name))[-1]
            opt_qty = int(opt.get_attribute('value'))
            opt.click()
        except Exception as e:
            print("Can't find the row")
            driver.quit()
            return '-'
        #click checkout
        try:
            check_out = driver.find_element_by_class_name('btn-submit')
            driver.execute_script("arguments[0].click();", check_out)
            try:
                time.sleep(0.5)
                driver.find_element_by_xpath('//*[@id="modal-liability-waiver"]/div/div/div[3]/div/a[1]').click()
                driver.find_element_by_xpath('//*[@id="formCarousel"]/div/div[1]/div[1]/a[2]').click()
            except Exception as e:
                pass
        except Exception as e:
            print(0, 'Tickets added....')
            driver.quit()
            return 0  

        time.sleep(0.5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        real_amount = 0
        try:
            show_counter = soup.find('div', {'class' : 'countdown-timer-clock'})
            if show_counter:
                try:
                    real_amount = soup.find('div' , {'class' : 'ticket-qty info'}).decode_contents() 
                except:
                    real_amount = soup.find('div' , {'class' : 'wrap ticket-number text-align-center'}).find_next('span').decode_contents() 
        except Exception as e:
            print(e)
            print('This is not current style')
            driver.quit()
            return 0
        real_amount = real_amount.replace('\n', '').replace('×', '').replace('  ', '')
        opt_qty = int( real_amount )
        driver.quit()
        print(opt_qty, 'Tickets added')
        return opt_qty

    def check_ticket_qty(self, cap):
        print(cap)
        driver = self.open_driver()
        driver.get(self.ticket_url)
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        try:
            no_seat = soup.find('div',{'class':'seats-ui-primary'})
            if 'No Map Seats Available.' in no_seat.text:
                print('no seat on this tickets')
                driver.quit()
                return '-'
        except:
            pass
        
        driver.quit()
        qty = 0
        timer_run_out = False
        oldtime = time.time()
        while True:
            if time.time() - oldtime >= 600:
                timer_run_out = True
                break
            loop_qty = 0
            with Pool(num_pool) as p:
                r = p.map(self.get_qty, list(range(num_pool)))
                for q in r:
                    loop_qty += q
            qty += loop_qty
            print('Total QTY:', qty)
            if loop_qty == 0:
                break
        
        return qty, timer_run_out

class SeeTickets(Scraper):
    # def input_password(self, driver):
    #     if self.password:
    #         driver.find_element_by_xpath('//*[@data-automation="order-box-enter-promo"]').click()
    #         driver.find_element_by_id('promo-access-code-input').send_keys(self.password)
    #         driver.find_element_by_xpath('//*[@type="submit"]').click()
    #         time.sleep(2)

    def get_qty(self, box_id):
        driver = self.open_driver()
        driver.get(self.ticket_url) 
        
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        try:
            id = soup.find('form', {'name': 'eventview'}).find_all('select')[int(self.ticket_row) - 1]['id']
        except:
            # can't find the select tag
            driver.quit()
            print(0, 'Tickets added...')
            return 0
        
        #click the max value and get value
        opt = driver.find_elements_by_xpath('//*[@id="{}"]/option'.format(id))[-1]
        opt_qty = int(opt.get_attribute('value'))
        opt.click()
        if self.wait_for_element(driver, 'container'):
        #click checkout
            try: 
                add_To_cart = driver.find_element_by_xpath('//*[@id="addtocartbnt"]')
                driver.execute_script("arguments[0].click();", add_To_cart)
            except Exception as e:
                print(e)
                pass
            time.sleep(4)
            try:
                driver.find_element_by_xpath('//*[@id="checkoutbnt"]').click()
            except:
                try:
                    checkout = driver.find_elements_by_xpath('//*[@id="checkoutbnt"]')
                    for x in range(0, len(checkout)):
                        driver.execute_script("arguments[0].click();", checkout[x])
                except Exception as e:
                    print(0, 'Tickets added....')
                    driver.quit()
                    return 0  
        time.sleep(4)
        
        try:
            driver.find_element_by_xpath('//*[@id="skipbutton"]').click()
        except:
            pass
        time.sleep(4)
        if self.wait_for_element(driver, 'loginsignup_pageV3'):
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            time.sleep(6)
            next_url = 'https://'+self.ticket_url.split('/')[2]+'/'+soup.find('a', {'class':'checkout-btn btn'})['href']
            driver.get(next_url)  
            try:
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                try_agian = soup.find('div',{'id':'purchasebutton'})
                if try_agian:
                    if 'TRY AGAIN' in try_agian.text:
                        print('can\'t check out')
                        driver.quit()
                        return 0
            except:
                print('This is not current style')
                driver.quit()
                return 0
        opt_qty = int(soup.find('div',{'class':'search-num-icon float-r'}).decode_contents())
        driver.quit()
        print(opt_qty, 'Tickets added')
        return opt_qty

    def check_ticket_qty(self, cap):
        driver = self.open_driver()
        driver.get(self.ticket_url)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        try:
            id = soup.find('form', {'name': 'eventview'}).find_all('select')[int(self.ticket_row) - 1]['id']
        except:
            # can't find the select tag
            driver.quit()
            print(0, 'Tickets added...')
            return 0
        
        driver.quit()
        qty = 0
        timer_run_out = False
        oldtime = time.time()
        while True:
            if time.time() - oldtime >= 600:
                timer_run_out = True
                break
            loop_qty = 0
            with Pool(num_pool) as p:
                r = p.map(self.get_qty, list(range(10)))
                for q in r:
                    loop_qty += q
            qty += loop_qty
            print('Total QTY:', qty)
            if loop_qty == 0:
                break
        
        return qty, timer_run_out

class Showclix(Scraper):
    def input_password(self, driver):
        if self.password:
            driver.find_element_by_id('promoCode').send_keys(self.password)
            driver.find_element_by_id('applyPromoCode').click()

    def get_qty(self, box_id):
        driver = self.open_driver()
        driver.get(self.ticket_url)
        time.sleep(2)
        # self.input_password(driver)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        try:
            id = soup.find('form', {'id': 'ticket-form'}).find_all('select')[int(self.ticket_row) - 1]['id']
        except:
            try:
                driver.find_element_by_xpath('//*[@id="{}"]/option]').click()
            except:
                driver.quit()
                print(0, 'Tickets added...')
                return 0
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            try:
                id = soup.find('form', {'name': 'frmPickTicket'}).find_all('select')[int(self.ticket_row) - 1]['id']
            except:
                print(0, 'Tickets added...')
                return 0
        try:
            opt = driver.find_elements_by_xpath('//*[@id="{}"]/option'.format(id))[-1]
        except:
            print('tickets is sold out or unavaible cause of scrap')
            driver.quit()
            return 0
        opt_qty = int(opt.get_attribute('value'))
        opt.click()
        # if soup.find('div', {'class': 'g-recaptcha'}):
        #     client = AnticaptchaClient(api_key)
        #     task = NoCaptchaTaskProxylessTask(self.ticket_url, '6LdoyhATAAAAAFdJKnwGwNBma9_mKK_iwaZRSw4j')
        #     try:
        #         job = client.createTask(task)
        #         print("Waiting to solution by Anticaptcha workers")
        #         job.join()
        #         # Receive response
        #         response = job.get_solution_response()
        #     except:
        #         print(0, 'Tickets added....')
        #         driver.quit()
        #         return 0
        #     print("Received solution", response)
        #     driver.execute_script('document.getElementById("g-recaptcha-response").innerHTML = "%s"' % response)
        #     driver.execute_script('document.getElementById("submitBtn").removeAttribute("disabled")')
        #     time.sleep(1)

        try:
            driver.find_element_by_xpath('//input[@type="submit"]').click()
        except:
            print(0, 'Tickets added....')
            driver.quit()
            return 0
        # time.sleep(3000)
        time.sleep(0.5)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        alert = soup.find('li', {'role': 'alert'})
        if alert:
            if 'Unable to reserve' in alert.text:
                print('amount is misselected')
                driver.quit()
                return 0
            if 'Your reservation has been cleared' in alert.test:
                print('Your reservation has been cleared')
                driver.quit()
                return 0
        # error = soup.find('div', {'class': 'validationError error'})
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        real_amount = soup.find('td',{'class': 'qty-td'}).text.strip()
        opt_qty = int(real_amount)

        driver.quit()
        print(opt_qty, 'Tickets added')
        return opt_qty  # driver

    def check_ticket_qty(self, cap):
        print(cap)
        driver = self.open_driver()
        driver.get(self.ticket_url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # sold_out or any event

        try:
            id = soup.find('form', {'id': 'ticket-form'}).find_all('select')[int(self.ticket_row) - 1]['id']
            tab_click = False
        except:
            tab_click = True
            try:
                driver.find_element_by_xpath('//*[@id={id}]').click()
            except:
                print('tickets is sold out cause of scrap')
                driver.quit()
                return '-', False
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            try:
                id = soup.find('form', {'name': 'frmPickTicket'}).find_all('select')[int(self.ticket_row) - 1]['id']
            except:
                print(0, 'Tickets added...')
                return 0

        opt = driver.find_elements_by_xpath('//*[@id="{}"]/option'.format(id))[-1]
        if opt.get_attribute('value')=="Sold Out":
            print('tickets is sold out cause of scrap')
            driver.quit()
            return '-', False

        # max_amount = soup.find('div', {'id': 'productsDiv'}).find('span', {'class': 'quantity-warning'}).text.strip()
        # max_amount = int(max_amount.split(' ')[0].strip())
        driver.quit()

        timer_run_out = False
        num_pool = 20
        qty = 0
        timer_run_out = False
        oldtime = time.time()
        while True:
            if time.time() - oldtime >= 600:
                timer_run_out = True
                break
            loop_qty = 0
            with Pool(num_pool) as p:
                r = p.map(self.get_qty, list(range(20)))
                for q in r:
                    loop_qty += q
            qty += loop_qty
            print('Total QTY:', qty)
            if loop_qty == 0:
                break
        time.sleep(3)

        print('total qty', qty)
        return qty, timer_run_out 

# if __name__ == "__main__":
#     proxies = r'D:\Programming\Work\Freelancer2\carrcocarr\low_price_warning\proxies.txt'
#     t = TicketFly('https://www.ticketfly.com/purchase/event/1822963', proxies, 1, None)
#     t.get_qty(10)
#
