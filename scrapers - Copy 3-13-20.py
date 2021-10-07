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
from bs4 import BeautifulSoup

from anticaptcha import api_key

num_pool = 20

def check_website(url, proxies, row, password, log=None):
    if '.etix.' in url:
        return Etix(url, proxies, row, log, password)
    elif '.eventbrite.' in url:
        return Eventbrite(url, proxies, row, log, password)
    elif '.ticketfly.' in url:
        return TicketFly(url, proxies, row, log, password)
    elif '.frontgatetickets.' in url:
        return FrontGate(url, proxies, row, log, password)
    elif '.ticketweb.' in url:
        return TicketWeb(url, proxies, row, log, password)


class Scraper(object):

    def __init__(self, url, proxies, row, log, password):
        self.log = log
        self.ticket_url = url
        self.ticket_row = row
        self.password = password
        with open(proxies, 'r') as f:
            self.proxies = f.read().split('\n')

    def input_password(self, driver):
        pass

    def log_message(self, msg):
        pass

    def check_ticket_qty(self):
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
        if user_agent:
            chrome_options.add_argument('--user-agent=%s' % user_agent)
        try:
            driver = webdriver.Chrome('chromedriver', chrome_options=chrome_options)
        except Exception as E:
            # print('Error ', E)
            return self.open_driver()

        # Check if it's working
        driver.get('https://www.google.com/')
        try:
            driver.find_element_by_xpath('//*[@id="tsf"]/div[2]/div/div[3]/center/input[1]')
        except:
            driver.quit()
            return self.open_driver()
        return driver


class Etix(Scraper):

    def input_password(self, driver):
        if self.password:
            driver.find_element_by_xpath('//*[@placeholder="Password"]').send_keys(self.password)

    def get_qty(self, box_id):
        # qty = 0
        driver = self.open_driver()
        driver.get(self.ticket_url)
        time.sleep(2)
        self.input_password(driver)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        sold_out = soup.find('h2', {'class': 'header-message'})
        if sold_out:
            if 'sold out' in sold_out.text.lower():
                driver.quit()
                return 0
        if soup.find('div', {'class': 'callout error emphasize'}):
            driver.quit()
            print(0, 'Tickets added...')
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
                print(0, 'Tickets added...')
                return 0
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            try:
                id = soup.find('form', {'name': 'frmPickTicket'}).find_all('select')[int(self.ticket_row) - 1]['id']
            except:
                print(0, 'Tickets added...')
                return 0

        opt = driver.find_elements_by_xpath('//*[@id="{}"]/option'.format(id))[-1]
        opt_qty = int(opt.get_attribute('value'))
        opt.click()
        if soup.find('div', {'class': 'g-recaptcha'}):
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
            time.sleep(1)

        try:
            driver.find_element_by_xpath('//button[@type="submit"]').click()
        except:
            print(0, 'Tickets added....')
            driver.quit()
            return 0

        time.sleep(0.5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        error = soup.find('div', {'class': 'callout error emphasize'})
        if error:
            if 'Tickets Currently Not Available' in error.text:
                print(0, 'Tickets added...')
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
                driver.find_element_by_xpath('//button[@type="submit"]').click()
                time.sleep(0.5)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                error = soup.find('div', {'class': 'validationError error'})
                if error:
                    if num_of_options == index:
                        driver.quit()
                        return 0
                    continue
                else:
                    break

        driver.quit()
        print(opt_qty, 'Tickets added')
        return opt_qty  # driver

    def check_ticket_qty(self):
        driver = self.open_driver()
        if '?method=switchSelectionMethod&selection_method=byBest' not in self.ticket_url:
            if '?' in self.ticket_url:
                self.ticket_url += "&method=switchSelectionMethod&selection_method=byBest"
            else:
                self.ticket_url += '?method=switchSelectionMethod&selection_method=byBest'
        driver.get(self.ticket_url)
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

            # CHECK CAPTCHA
            # if soup.find('div', {'class': 'g-recaptcha'}):
            #     print('Captcha')
            #     driver.quit()
            #     return 'Captcha', False
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
                    r = p.map(self.get_qty, list(range(20)))
                    for q in r:
                        loop_qty += q
                qty += loop_qty
                print('Total QTY:', qty)
                if loop_qty == 0:
                    break
                time.sleep(3)

            # with Pool(8) as p:
            #     r = p.map(self.get_qty, list(range(20)))
            #     results = [x for x in r]
            #     #drivers = [x[1] for x in r]

            # qty = 0
            # for q in results:
            #     qty += q
            # for driver in drivers:
            #     try:
            #         driver.find_element_by_xpath('//*[@id="cartForm"]/div[2]/div[1]/a').click()
            #     except:
            #         pass
            #     driver.quit()
            return qty, timer_run_out


class Eventbrite(Scraper):

    def input_password(self, driver):
        if self.password:
            driver.find_element_by_xpath('//*[@data-automation="order-box-enter-promo"]').click()
            driver.find_element_by_id('promo-access-code-input').send_keys(self.password)
            driver.find_element_by_xpath('//*[@type="submit"]').click()
            time.sleep(2)


    def get_qty(self, _id):
        driver = self.open_driver(headless=True)
        self.drivers.append(driver)
        driver.get(self.ticket_url)
        time.sleep(3)
        self.input_password(driver)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        try:
            opt = driver.find_elements_by_xpath('//*[@id="{}"]/option'.format(_id))[-1]
        except IndexError:
            print('0 Tickets added')
            driver.quit()
            return 0
        opt_qty = int(opt.get_attribute('value'))
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
        time.sleep(1)

        try:
            driver.find_element_by_xpath('//*[@type="submit"]').click()
        except:
            print('0 Tickets added')
            driver.quit()
            return 0
        time.sleep(1)

        # if self.wait_for_element(driver, 'time_left'):
        #     pass
        #     print('time_left found')
        # else:
        #     print('time_left not found')
        #     opt_qty = 0
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
        time.sleep(3)
        main_id = driver.find_element_by_tag_name('body').get_attribute('data-event-id')
        xpath = '//*[@id="eventbrite-widget-modal-{}"]'.format(main_id)
        try:
            iframe = driver.find_element_by_xpath(xpath)
        except:
            print('0 Tickets added', 'btn')
            driver.quit()
            return 0

        driver.switch_to.frame(iframe)
        #self.input_password(driver)


        try:
            opt = driver.find_elements_by_class_name('tiered-ticket-display-content-root')[int(self.ticket_row)-1]
            opt = opt.find_elements_by_tag_name('option')[-1]
        except IndexError:
            try:
                opt = driver.find_elements_by_class_name('eds-card-list__item')[int(self.ticket_row)-1]
                opt = opt.find_elements_by_tag_name('option')[-1]
            except IndexError:
                print('0 Tickets added', 'idx')
                driver.quit()
                return 0
        opt_qty = int(opt.get_attribute('value'))
        opt.click()

        time.sleep(1)

        try:
            driver.find_element_by_xpath('//*[@data-automation="eds-modal__primary-button"]').click()
        except:
            print('0 Tickets added', 'btn')
            driver.quit()
            return 0
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        alert = soup.find('div', {'class': 'eds-notification-bar__content'})
        if alert:
            if 'The tickets you selected are no longer available' in alert.text:
                print('0 Tickets added')
                driver.quit()
                return 0

        # if self.wait_for_element(driver, 'time_left'):
        #     pass
        #     print('time_left found')
        # else:
        #     print('time_left not found')
        #     opt_qty = 0
        # opt_qty = 0
        # if self.wait_for_element(driver, 'time_left'):
        #     soup = BeautifulSoup(driver.page_source, 'html.parser')
        #     try:
        #         opt_qty = int(soup.find('td', {'class': 'quantity_td'}).text.strip())
        #     except AttributeError:
        #         pass

        driver.quit()
        print(opt_qty, 'Tickets added')
        return opt_qty

    def check_ticket_qty(self):
        driver = self.open_driver()

        self.drivers = []

        if '?' in self.ticket_url:
            self.ticket_url = self.ticket_url[:self.ticket_url.find('?')]
        if '#tickets' not in self.ticket_url:
            self.ticket_url += '#tickets'
        driver.get(self.ticket_url)
        time.sleep(3)
        self.input_password(driver)


        _id = driver.find_element_by_tag_name('body').get_attribute('data-event-id')
        xpath = '//*[@id="eventbrite-widget-modal-{}"]'.format(_id)
        try:
            iframe = driver.find_element_by_xpath(xpath)
            driver.switch_to.frame(iframe)
            new_style = True
        except selenium.common.exceptions.NoSuchElementException:
            new_style = False

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        if not new_style:
            try:
                _id = soup.find_all('select')[int(self.ticket_row) - 1]['id']
            except IndexError:
                driver.quit()
                print('No tickets available')
                return '-', False
        else:
            try:
                _id = soup.find_all('div', {'class': 'tiered-ticket-quantity-select eds-g-cell eds-text-color--grey-800 eds-ticket-card-content__quantity-selector'})[int(self.ticket_row) - 1]['data-automation']
            except IndexError:
                try:
                    _id = soup.find_all('select', {'name': 'ticket-quantity-selector'})[int(self.ticket_row) - 1]['data-automation']
                except IndexError:
                    driver.quit()
                    print('No tickets available')
                    return '-', False




        driver.quit()

        timer_run_out = False
        num_pool = 20
        lst = [_id for x in range(num_pool)]
        qty = 0
        oldtime = time.time()

        if new_style:
            func = self.get_qty_new
        else:
            func = self.get_qty

        while True:
            if time.time() - oldtime >= 480:
                break
            loop_qty = 0
            with Pool(num_pool) as p:
                r = p.map(func, lst)
                for q in r:
                    loop_qty += q
            qty += loop_qty
            print('Total QTY:', qty)
            if loop_qty == 0:
                break
            time.sleep(3)


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


        if self.wait_for_element(driver, '/html/body/div[10]/div/div/div[1]/div[2]/h2', By.XPATH):
            qty = max_amount

        driver.quit()
        print(qty, 'Tickets added')
        return qty

    def check_new_style(self, driver):
        pass



    def check_ticket_qty(self):
        driver = self.open_driver()
        self.input_password(driver)
        driver.get(self.ticket_url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        ticket = soup.find('form', {'id': 'cart_tickets_form'}).find_all('div', {'class': 'ticket-price-section'})[
            int(self.ticket_row) - 1]
        spinner = ticket.find('div', {'class': 'number-spinner'})


        #driver.switch_to.frame(iframe)



        try:
            max_amount = spinner.find('input')['data-quantityarray']
        except:
            driver.quit()
            print("No tickets available")
            return '-', False
        max_amount = ast.literal_eval(max_amount)[-1]
        driver.quit()


        timer_run_out = False
        num_pool = 20
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
            qty += loop_qty
            print('Total QTY:', qty)
            if loop_qty == 0:
                break
            time.sleep(3)

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
        self.input_password(driver)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        sold_out = soup.find('div', {'class': 'section section-status theme-mod eventStatusCustomMessage'})
        if sold_out:
            if 'This screening is currently sold out' in sold_out.text.strip():
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
            site_key = '6LfW2FYUAAAAAJmlXoUhKpxRo7fufecPstaxMMvn'
            client = AnticaptchaClient(api_key)
            task = NoCaptchaTaskProxylessTask(self.ticket_url, site_key)
            job = client.createTask(task)
            print("Waiting to solution by Anticaptcha workers")
            job.join()
            # Receive response
            response = job.get_solution_response()
            print("Received solution", response)
            driver.execute_script('document.getElementById("g-recaptcha-response").innerHTML = "%s"' % response)
            time.sleep(1)


        driver.find_element_by_id('edp_checkout_btn').click()

        if self.wait_for_element(driver, '/html/body/div[1]/header/div/div/ul/li/p[2]', By.XPATH):
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            try:
                qty = int(soup.find('p', {'class': 'small tickets-sum'}).text.split(' ')[0].strip())
            except AttributeError:
                driver.quit()
                return self.get_qty(x)
        driver.quit()
        print(qty, 'Tickets added')
        return qty


    def check_ticket_qty(self):
        if '?' in self.ticket_url:
            self.ticket_url = self.ticket_url[:self.ticket_url.find('?')]

        driver = self.open_driver()
        driver.get(self.ticket_url)
        self.input_password(driver)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # captcha = soup.find('div', {'class': 'g-recaptcha'})
        # if captcha:
        #     driver.quit()
        #     return 'CAPTCHA', False


        sold_out = soup.find('div', {'class': 'section section-status theme-mod eventStatusCustomMessage'})
        if sold_out:
            if 'This screening is currently sold out' in sold_out.text.strip():
                driver.quit()
                print('0 Tickets added')
                return 0, False
        driver.quit()
        num_pool = 20
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
            qty += loop_qty
            print('Total QTY:', qty)
            if loop_qty == 0:
                break
            time.sleep(3)

        print('total qty', qty)
        return qty, timer_run_out

class TicketFly(Scraper):

    def input_password(self, driver):
        if self.password:
            driver.find_element_by_id('promoCode').send_keys(self.password)
            driver.find_element_by_id('applyPromoCode').click()

    def get_qty(self, max_amount):
        if max_amount == 0:
            print('0 Tickets added')
            return 0
        driver = self.open_driver()
        try:
            driver.get(self.ticket_url)
        except:
            driver.quit()
            return self.get_qty(max_amount)
        self.input_password(driver)
        if not self.wait_for_element(driver, 'productsDiv'):
            driver.quit()
            return self.get_qty(max_amount)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        info = soup.find('section', {'class': 'info'})
        if info:
            if 'Off Sale' in info.text:
                print('0 Tickets added')
                driver.quit()
                return 0
        product = soup.find('div', {'name': 'product-{}'.format(int(self.ticket_row)-1)})
        if product is None:
            driver.quit()
            return self.get_qty(max_amount)
        sold_out = product.find('span', {'class': 'sold-out'})
        if sold_out:
            if 'None Available' in sold_out.text:
                print('0 Tickets added')
                driver.quit()
                return 0

        try:
            inpt = driver.find_element_by_name('productRequestForms[{}].quantity'.format(int(self.ticket_row)-1))
        except:
            driver.quit()
            return self.get_qty(max_amount)
        max_amount = int(inpt.get_attribute('max'))


        i = 0
        while True:
            if i > 10:
                break


            for i in range(max_amount):
                try:
                    driver.find_element_by_xpath(
                        '//*[@id="productsDiv"]/div[{}]/div[3]/p/button[2]'.format(self.ticket_row)).click()
                except:
                    driver.find_element_by_xpath(
                            '//*[@id="productsDiv"]/div[{}]/div[2]/p/button[2]'.format(self.ticket_row)).click()


                # prds.find_elements_by_xpath("//button[contains(text(), '+')]")[int(self.ticket_row)-1].click()
            if 'true' in re.search('enableCaptcha: (true|false),', str(soup)).group(0):

                driver.find_element_by_id('bestSeats').click()
                client = AnticaptchaClient(api_key)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                iframe = soup.find('iframe')['src'].replace('https://www.google.com/recaptcha/api2/anchor?ar=1&k=','')
                site_key = iframe[:iframe.find('&')]
                site_key = '6LfKUB0UAAAAALUrUue3Jsb5skcZD1UCpFQxwr9e'
                try:
                    task = NoCaptchaTaskProxylessTask(self.ticket_url, site_key)
                    job = client.createTask(task)
                    print("Waiting to solution by Anticaptcha workers")
                    job.join()
                    # Receive response
                    response = job.get_solution_response()
                    print("Received solution", response)
                    # Inject response in webpage
                    driver.execute_script('document.getElementById("g-recaptcha-response").innerHTML = "%s"' % response)
                    # Wait a moment to execute the script (just in case).
                    time.sleep(1)
                    # Press submit button
                    driver.find_element_by_id('securityCheck').click()
                except Exception as e:
                    print(e)
                    print('0 Tickets added')
                    driver.quit()
                    return 0
            else:
                driver.find_element_by_id('bestSeats').click()
            time.sleep(1.5)



            error = soup.find('section', {'class': 'error'})
            if error:
                if "We're sorry, but there aren't enough available" in error.text:
                    max_amount -= 1
                    i += 1
                    continue
                    # driver.quit()
                    # return self.get_qty(max_amount - 1)
            break

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        try:
            qty = soup.find('div', {'class': 'ticket-qty'}).text.strip()
        except AttributeError:
            print('0 Tickets added')
            driver.quit()
            return 0
        qty = int(qty.split('x')[0].strip())
        print(qty, 'Tickets added')
        driver.quit()
        return qty

    def check_ticket_qty(self):
        driver = self.open_driver()
        if '?' in self.ticket_url:
            self.ticket_url = self.ticket_url[:self.ticket_url.find('?')]
        driver.get(self.ticket_url)
        self.input_password(driver)
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        info = soup.find('section', {'class': 'info'})
        if info:
            if 'Off Sale' in info.text:
                print('Sold out')
                driver.quit()
                return 'Off Sale', None

        #if 'true' in re.search('enableCaptcha: (true|false),', str(soup)).group(0):
            # print("CAPTCHA EVENT - can't retrieve quantity...")
            # driver.quit()
            # return "CAPTCHA", None




        ticket_row = soup.find('div', {'class': 'product-{}'.format(int(self.ticket_row)-1)})
        sold_out = ticket_row.find('span', {'class': 'sold-out'})
        if sold_out:
            if 'None Available' in sold_out.text:
                print('No tickets available')
                driver.quit()
                return '-'

        max_amount = soup.find('div', {'id': 'productsDiv'}).find('span', {'class': 'quantity-warning'}).text.strip()
        max_amount = int(max_amount.split(' ')[0].strip())
        driver.quit()


        timer_run_out = False
        num_pool = 20
        lst = [max_amount for x in range(num_pool)]
        qty = 0
        oldtime = time.time()
        while True:
            if time.time() - oldtime >= 600:
                timer_run_out = True
                break
            loop_qty = 0
            with Pool(num_pool) as p:
                r = p.map(self.get_qty, lst)
                not_zeros = 0
                for q in r:
                    if q != 0:
                        not_zeros +=1
                    loop_qty += q
            qty += loop_qty
            print('Total QTY:', qty)
            if not_zeros == 1:
                break
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
