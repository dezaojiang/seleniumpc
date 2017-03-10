#-*- coding: utf-8 -*-
#!/usr/bin/env python

import os, re, selenium, time, autoit, datetime, PIL.ImageGrab, traceback
from selenium.webdriver.common.keys import Keys as Key

class Driver(object):
    def __init__(self):
        self._name = None
        self._executor = None
        self._browser = None
        self._proxy = None
        self._option = list()
        self._log = None
        self._delay = 0.7
        self._driver = None
        self._handle = None

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, name):
        if not ((type(name) is str) and (name.strip().lower() in ['chrome', 'ff', 'ie'])):
            raise Exception('pass name as str(chrome/ff/ie)!')
        self._name = name.strip().lower()

    @property
    def executor(self):
        return self._executor
    @executor.setter
    def executor(self, executor):
        if not ((type(executor) is str) and (executor.strip().endswith('.exe')) and (os.path.isfile(path = executor.strip().decode(encoding = 'UTF-8', errors = 'strict')))):
            raise Exception('pass executor as str(executor_path)!')
        self._executor = executor.strip().decode(encoding = 'UTF-8', errors = 'strict')

    @property
    def browser(self):
        return self._browser
    @browser.setter
    def browser(self, browser):
        if not ((type(browser) is str) and (browser.strip().endswith('.exe')) and (os.path.isfile(path = browser.strip().decode(encoding = 'UTF-8', errors = 'strict')))):
            raise Exception('pass browser as str(browser_path)!')
        self._browser = browser.strip().decode(encoding = 'UTF-8', errors = 'strict')

    @property
    def proxy(self):
        return self._proxy
    @proxy.setter
    def proxy(self, proxy):
        if not ((type(proxy) is str) and (len(re.findall(pattern = '^\s*[a-z0-9A-Z.-_]+:\d{1,5}\s*$', string = proxy, flags = 0)) == 1) and (1 <= int((re.findall(pattern = '^\s*[a-z0-9A-Z.-_]+:(\d{1,5})\s*$', string = proxy, flags = 0))[0]) <= 65535)):
            raise Exception('pass proxy as str(address:port)!')
        self._proxy = proxy.strip()

    @property
    def option(self):
        return self._option
    @option.setter
    def option(self, option):
        if not ((type(option) is str) and (len(option.strip()) > 0)):
            raise Exception('pass option as str(len>0)!')
        if option.strip() not in self._option:
            self._option.append(option.strip())

    @property
    def log(self):
        return self._log
    @log.setter
    def log(self, path):
        self._log = Log(path = path, driver = self)

    @property
    def delay(self):
        return self._delay
    @delay.setter
    def delay(self, delay):
        if not (type(delay) is int and delay > 0):
            raise Exception('pass delay as float(>0)/int(>0)!')
        self._delay = delay / 1000

    def launch(self):
        if (self._name is None) or ((self._name == 'chrome') and (not ((self._executor is not None) and (self._browser is not None) and (self._log is not None)))):
            raise Exception('name/executor/browser/log not pass!')
        elif (self._name is None) or ((self._name == 'ff') and (not ((self._browser is not None) and (self._log is not None)))):
            raise Exception('name/browser/log not pass!')
        elif (self._name is None) or ((self._name == 'ie') and (not ((self._executor is not None) and (self._log is not None)))):
            raise Exception('name/executor/log not pass!')

        capability = dict()
##        capability['javascriptEnabled'] = True
        capability['unexpectedAlertBehaviour'] = 'ignore'
        capability['ignoreProtectedModeSettings'] = True
        if self._proxy is not None:
            capability['proxy'] = {'proxyType': 'MANUAL', 'httpProxy': self._proxy, 'sslProxy': self._proxy, 'ftpProxy': self._proxy}
            capability['ie.usePerProcessProxy'] = True
        capability['chromeOptions'] = dict()
        capability['chromeOptions']['binary'] = self._browser
        capability['chromeOptions']['prefs'] = {'download' : {'prompt_for_download' : True}} #force chrome to prompt for download
        if len(self._option) > 0:
            capability['chromeOptions']['args'] = self._option
            capability['ie.forceCreateProcessApi'] = True
            capability['ie.browserCommandLineSwitches'] = ' '.join(self._option)

        self._log.ignite(ignite = 'Driver.launch()')
        try:
            self._log.clause(clause = 'name = ' + self._name + ', executor = ' + (self._executor if self._executor is not None else 'none') + ', browser = ' + (self._browser if self._browser is not None else 'none') + ', proxy = ' + (self._proxy if self._proxy is not None else 'none') + ', option = ' + (' '.join(self._option) if len(self._option) > 0 else 'none') + ', log = ' + self._log._log.name.encode(encoding = 'UTF-8', errors = 'strict'))

            if self._name == 'chrome':
##                self._driver = selenium.webdriver.chrome.webdriver.WebDriver(executable_path = self._executor, desired_capabilities = capability, service_args = ['--verbose']) #debug
                self._driver = selenium.webdriver.chrome.webdriver.WebDriver(executable_path = self._executor, desired_capabilities = capability)
            elif self._name == 'ff':
                binary = selenium.webdriver.firefox.firefox_binary.FirefoxBinary(firefox_path = self._browser)
                binary.command_line = self._option
                profile = selenium.webdriver.firefox.firefox_profile.FirefoxProfile()
                profile.default_preferences['browser.download.useDownloadDir'] = False #force ff to prompt for download
##                profile.default_preferences['browser.link.open_newwindow'] = 3 #force ff to open new window in tab, but would crash test run
                self._driver = selenium.webdriver.firefox.webdriver.WebDriver(capabilities = capability, firefox_profile = profile, firefox_binary = binary)
            else:
##                self._driver = selenium.webdriver.ie.webdriver.WebDriver(executable_path = self._executor, capabilities = capability, log_level = 'trace') #debug
                self._driver = selenium.webdriver.ie.webdriver.WebDriver(executable_path = self._executor, capabilities = capability)


            if (self._name == 'chrome') and (('incognito' in self._option) or ('-incognito' in self._option) or ('--incognito' in self._option)):
                self._driver.get(url = 'chrome://extensions-frame')
                if self._driver.find_element_by_xpath(xpath = "//span[@class='extension-title'][text()='Chrome Automation Extension']/parent::div/parent::div[@class='extension-details']//label[@class='incognito-control']/input[@type='checkbox']").is_selected() is False:
                    self._driver.find_element_by_xpath(xpath = "//span[@class='extension-title'][text()='Chrome Automation Extension']/parent::div/parent::div[@class='extension-details']//label[@class='incognito-control']/input[@type='checkbox']").click()

            self._driver.maximize_window()

            self._log.effect(effect = 'driver launch')
        except Exception as e:
            self._log.error(error = e)
            raise e

    def quit(self):
        self._log.ignite(ignite = 'Driver.quit()')
        try:
            self._log.clause(clause = 'none')

            self._driver.quit()

            self._log.effect(effect = 'driver quit')

            self._log._log.close()
        except Exception as e:
            self._log.error(error = e)

            self._log._log.close()

            raise e

    def open(self, url):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Driver.open()')
        try:
            if not ((type(url) is str) and (len(url.strip()) > 0)):
                raise Exception('pass url as str(len>0)')

            self._log.clause(clause = 'url = ' + url.strip())

            self._driver.get(url = url.strip().decode(encoding = 'UTF-8', errors = 'strict'))

##            if self._name != 'ie':
##                self._handle = self._driver.current_window_handle
            self._handle = self._driver.current_window_handle

            self._log.effect(effect = 'url open')
        except Exception as e:
            self._log.error(error = e)
            raise e

    def refresh(self):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Driver.refresh()')
        try:
            self._log.clause(clause = 'none')

            self._driver.refresh()

            self._log.effect(effect = 'webpage refresh')
        except Exception as e:
            self._log.error(error = e)
            raise e

    def back(self):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Driver.back()')
        try:
            self._log.clause(clause = 'none')

            self._driver.back()

            self._log.effect(effect = 'webpage back')
        except Exception as e:
            self._log.error(error = e)
            raise e

    def forward(self):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Driver.forward()')
        try:
            self._log.clause(clause = 'none')

            self._driver.forward()

            self._log.effect(effect = 'webpage forward')
        except Exception as e:
            self._log.error(error = e)
            raise e

    def close(self):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Driver.close()')
        try:
            self._log.clause(clause = 'none')

            if len(self._driver.window_handles) == 1:
                raise Exception('close last webpage!')

            self._driver.close()
            self._driver._switch_to.window(window_name = self._driver.window_handles[-1])

            self._log.effect(effect = 'webpage close')
        except Exception as e:
            self._log.error(error = e)
            raise e

    def find(self, tag = '*', attribute = list(), text = list()):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Driver.find()')
        try:
            if (not (type(tag) is str) and (len(tag.strip()) > 0)) or ((type(attribute) is not list) and (not isinstance(attribute, Attribute))) or ((type(text) is not list) and (not isinstance(text, Text))):
                raise Exception('pass tag/attribute/text as str(len>0)/Attribute()/Text()!')

            xpath = '//' + tag

            if type(attribute) is not list:
                attribute = [attribute]

            for i in attribute:
                if not isinstance(i, Attribute):
                    raise Exception('pass attribute as list(Attribute())!')

                if i._strict is True:
                    xpath += "[@" + i._key + "='" + i._value + "']"
                else:
                    xpath += "[contains(@" + i._key + ",'" + i._value + "')]"

            if type(text) is not list:
                text = [text]

            for i in text:
                if not isinstance(i, Text):
                    raise Exception('pass text as list(Text())!')

                if i._strict is True:
                    xpath += "[text()='" + i._text + "']"
                else:
                    xpath += "[contains(text(),'" + i._text + "')]"

            self._log.clause(clause = 'xpath = ' + xpath)

            element = self._driver.find_elements_by_xpath(xpath = xpath.decode(encoding = 'UTF-8', errors = 'strict'))
            if not ((type(element) is list) and (len(element) > 0)):
                raise Exception('find element = 0!')

##            self._driver.execute_script('arguments[0].scrollIntoView(true)', element[0])

            self._log.effect(effect = 'find element = ' + str(len(element)))

            return list(Element(element = i, driver = self) for i in element)
        except Exception as e:
            self._log.error(error = e)
            raise e

    def framein(self, element):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Driver.framein()')
        try:
            if not isinstance(element, Element):
                raise Exception('pass element as Element()!')

            tag = element._element.tag_name
            if type(tag) is unicode:
                tag = tag.encode(encoding = 'UTF-8', errors = 'strict')
            if not ((tag is not None) and ('frame' in tag)):
                raise Exception('pass element as Element(<frame>)!')

            self._log.clause(clause = 'Element()')

            self._driver._switch_to.frame(frame_reference = element._element)

            self._log.effect(effect = 'frame in')
        except Exception as e:
            self._log.error(error = e)
            raise e

    def frameout(self):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Driver.frameout()')
        try:
            self._log.clause(clause = 'none')

            self._driver._switch_to.default_content()

            self._log.effect(effect = 'frame out')
        except Exception as e:
            self._log.error(error = e)
            raise e

    def type(self, key):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Driver.type()')
        try:
            if not (((type(key) is list) and (len(key) > 0)) or (type(key) is int) or ((type(key) is str) and (len(key) > 0)) or ((type(key) is unicode) and (key in selenium.webdriver.common.keys.Keys.__dict__.values()))):
                raise Exception('pass key as int()/str(len>0)/Key()!')

            if type(key) is not list:
                key = [key]

            number = len(self._driver.window_handles)

            action = selenium.webdriver.common.action_chains.ActionChains(driver = self._driver)
            clause = ''
            for i in key:
                if not ((type(i) is int) or ((type(i) is str) and (len(i) > 0)) or ((type(i) is unicode) and (i in selenium.webdriver.common.keys.Keys.__dict__.values()))):
                    raise Exception('pass key as list(int()/str(len>0)/Key())!')

                action.send_keys(i)
                if type(i) is int:
                    clause += str(i)
                elif type(i) is unicode:
                    clause += i.encode(encoding = 'unicode-escape', errors = 'strict')
                else:
                    clause += i

            self._log.clause(clause = 'key = ' + clause)

##            if self._name != 'ie':
##                self._handle = self._driver.current_window_handle
            self._handle = self._driver.current_window_handle

            action.perform()

            #Element.click() would typically open a new window, and rarely Driver.type() would open a new window either
            if self._name == 'ie':
                try:
                    if len(self._driver.window_handles) > number:
                        self._driver._switch_to.window(window_name = self._driver._driver.window_handles[-1])

                        self._driver.maximize_window()
                except selenium.common.exceptions.UnexpectedAlertPresentException:
                    pass
                except selenium.common.exceptions.NoSuchWindowException:
                    pass
            elif len(self._driver.window_handles) > number:
                self._driver._switch_to.window(window_name = self._driver._driver.window_handles[-1])

            self._log.effect(effect = 'key type')
        except Exception as e:
            self._log.error(error = e)
            raise e

    def modifierdown(self, modifier):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Driver.modifierdown()')
        try:
            if not ((type(modifier) is unicode) and (modifier in selenium.webdriver.common.keys.Keys.__dict__.values())):
                raise Exception('pass modifier as Key()!')

            self._log.clause(clause = 'modifier = ' + modifier.encode(encoding = 'unicode-escape', errors = 'strict'))

            selenium.webdriver.common.action_chains.ActionChains(driver = self._driver).key_down(value = modifier, element = None).perform()

            self._log.effect(effect = 'modifier down')
        except Exception as e:
            self._log.error(error = e)
            raise e

    def modifierup(self, modifier):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Driver.modifierup()')
        try:
            if not ((type(modifier) is unicode) and (modifier in selenium.webdriver.common.keys.Keys.__dict__.values())):
                raise Exception('pass modifier as Key()!')

            self._log.clause(clause = 'modifier = ' + modifier.encode(encoding = 'unicode-escape', errors = 'strict'))

            selenium.webdriver.common.action_chains.ActionChains(driver = self._driver).key_up(value = modifier, element = None).perform()

            self._log.effect(effect = 'modifier up')
        except Exception as e:
            self._log.error(error = e)
            raise e

    def alert(self, accept = True, send = None, timeout = 7000):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Driver.alert()')
        try:
            if ((send is not None) and (type(send) is not str)) or ((type(send) is str) and (len(send) == 0)) or (not (type(timeout) is int) and (timeout > 0)):
                raise Exception('pass send/timeout as str(len>0)/int(>0)!')

            self._log.clause(clause = 'accept = ' + str(accept) + ', send = ' + str(send) + ', timeout = ' + str(timeout))

            end = time.time() + timeout / 1000
            while time.time() < end:
                try:
                    alert = self._driver._switch_to.alert
                except Exception as e:
                    if time.time() < end:
                        time.sleep(0.7)
                    else:
                        raise e
                else:
                    break

            text = alert.text
            if type(text) is unicode:
                text = text.encode(encoding = 'UTF-8', errors = 'strict')

            if send is not None:
                alert.send_keys(keysToSend = send.decode(encoding = 'UTF-8', errors = 'strict'))

            if accept is True:
                #accept the Alert would automatically switch Driver from current Alert back to last window
                alert.accept()
            else:
                #accept the Alert would not switch Driver back to last window, thus add one more manual step to do the switch action
                alert.dismiss()
                self._driver._switch_to.window(window_name = self._driver.window_handles[-1])

            self._log.effect(effect = 'alert text = ' + (text if text is not None else 'none'))

            return text
        except Exception as e:
            self._log.error(error = e)
            raise e

    def upload(self, path, timeout = 7000):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Driver.upload()')
        try:
            if not ((type(path) is str) and (os.path.isfile(path = path.strip().decode(encoding = 'UTF-8', errors = 'strict'))) and (type(timeout) is int) and (timeout > 0)):
                raise Exception('pass path/timeout as str(file_path)/int(>0)!')

            self._log.clause(clause = 'path = ' + path.strip() + ', timeout = ' + str(timeout))

            if self._name == 'chrome':
                title = u'打开'
            elif self._name == 'ff':
                title = u'文件上载'
            else:
                title = u'选择要加载的文件'

            autoit.win_wait(title = title, timeout = timeout / 1000)
            window = autoit.win_get_handle(title = title)
            edit = autoit.control_get_handle(hwnd = window, control = 'Edit1')
            button = autoit.control_get_handle(hwnd = window, control = 'Button1')
            autoit.control_set_text_by_handle(hwnd = window, h_ctrl = edit, control_text = path.strip().replace('/', '\\').decode(encoding = 'UTF-8', errors = 'strict'))
            time.sleep(0.7)
            autoit.control_click_by_handle(hwnd = window, h_ctrl = button)

            self._log.effect(effect = 'file upload')
        except Exception as e:
            self._log.error(error = e)
            raise e

    def download(self, path, timeout = 7000):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Driver.download()')
        try:
            if not ((type(path) is str) and (len(path.strip()) > 0) and (type(timeout) is int) and (timeout > 0)):
                raise Exception('pass path/timeout as str(file_path)/int(>0)!')

            self._log.clause(clause = 'path = ' + path.strip() + ', timeout = ' + str(timeout))

            if self._name == 'chrome':
                title = u'另存为'
                autoit.win_wait(title = title, timeout = timeout / 1000)
                window = autoit.win_get_handle(title = title)
                edit = autoit.control_get_handle(hwnd = window, control = 'Edit1')
                combo = autoit.control_get_handle(hwnd = window, control = 'ComboBox2')
                button = autoit.control_get_handle(hwnd = window, control = 'Button1')
                if os.path.isfile(path = path.strip().decode(encoding = 'UTF-8', errors = 'strict')):
                    os.remove(path.strip().decode(encoding = 'UTF-8', errors = 'strict'))
                elif not os.path.exists(path = re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0].decode(encoding = 'UTF-8', errors = 'strict')):
                    os.makedirs(name = re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0].decode(encoding = 'UTF-8', errors = 'strict'), mode = 0777)
                time.sleep(0.7)
                autoit.control_set_text_by_handle(hwnd = window, h_ctrl = edit, control_text = path.strip().replace('/', '\\').decode(encoding = 'UTF-8', errors = 'strict'))
                time.sleep(0.7)
                autoit.control_click_by_handle(hwnd = window, h_ctrl = combo)
                time.sleep(0.7)
                autoit.control_send_by_handle(hwnd = window, h_ctrl = combo, send_text = '{DOWN}{ENTER}', mode = 0)
                time.sleep(0.7)
                autoit.control_click_by_handle(hwnd = window, h_ctrl = button)

                time.sleep(0.7)
##                autoit.win_wait_close_by_handle(handle = window, timeout = timeout / 1000)
                autoit.win_wait_close(title = title, timeout = timeout / 1000)

                self._log.effect(effect = 'download file')
##                self._driver._switch_to.window(window_name = self._handle)

            elif self._name == 'ff':
                title = '[CLASS:MozillaDialogClass]'
                autoit.win_wait_active(title = title, timeout = timeout / 1000)
                time.sleep(0.7)
                autoit.send(send_text = '{LEFT}{ALTDOWN}s{ALTUP}{ENTER}', mode = 0)

                title = u'输入要保存的文件名…'
                autoit.win_wait(title = title, timeout = timeout / 1000)
                window = autoit.win_get_handle(title = title)
                edit = autoit.control_get_handle(hwnd = window, control = 'Edit1')
                button = autoit.control_get_handle(hwnd = window, control = 'Button1')
                if not os.path.exists(path = re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0].decode(encoding = 'UTF-8', errors = 'strict')):
                    os.makedirs(name = re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0].decode(encoding = 'UTF-8', errors = 'strict'), mode = 0777)
                time.sleep(0.7)
                autoit.control_set_text_by_handle(hwnd = window, h_ctrl = edit, control_text = path.strip().replace('/', '\\').decode(encoding = 'UTF-8', errors = 'strict'))
                time.sleep(0.7)
                autoit.control_click_by_handle(hwnd = window, h_ctrl = button)

                title1 = u'确认另存为'
                try:
                    autoit.win_wait(title = title1, timeout = timeout / 1000)
                except:
                    pass
                else:
                    window1 = autoit.win_get_handle(title = title1)
                    button1 = autoit.control_get_handle(hwnd = window1, control = 'Button1')
                    time.sleep(0.7)
                    autoit.control_click_by_handle(hwnd = window1, h_ctrl = button1)

                time.sleep(0.7)
##                autoit.win_wait_close_by_handle(handle = window, timeout = timeout / 1000)
                autoit.win_wait_close(title = title, timeout = timeout / 1000)

                self._log.effect(effect = 'download file')
##                self._driver._switch_to.window(window_name = self._handle)

            else:
                title = u'文件下载 - 安全警告'
                autoit.win_wait(title = title, timeout = timeout / 1000)
                window = autoit.win_get_handle(title = title)
                button = autoit.control_get_handle(hwnd = window, control = 'Button2')
                time.sleep(0.7)
                autoit.control_click_by_handle(hwnd = window, h_ctrl = button)

                title = u'另存为'
                autoit.win_wait(title = title, timeout = timeout / 1000)
                window = autoit.win_get_handle(title = title)
                edit = autoit.control_get_handle(hwnd = window, control = 'Edit1')
                button = autoit.control_get_handle(hwnd = window, control = 'Button1')
                if not os.path.exists(path = re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0].decode(encoding = 'UTF-8', errors = 'strict')):
                    os.makedirs(name = re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0].decode(encoding = 'UTF-8', errors = 'strict'), mode = 0777)
                time.sleep(0.7)
                autoit.control_set_text_by_handle(hwnd = window, h_ctrl = edit, control_text = path.strip().replace('/', '\\').decode(encoding = 'UTF-8', errors = 'strict'))
                time.sleep(0.7)
                autoit.control_click_by_handle(hwnd = window, h_ctrl = button)

                title1 = u'确认另存为'
                try:
                    autoit.win_wait(title = title1, timeout = timeout / 1000)
                except:
                    pass
                else:
                    window1 = autoit.win_get_handle(title = title1)
                    button1 = autoit.control_get_handle(hwnd = window1, control = 'Button1')
                    time.sleep(0.7)
                    autoit.control_click_by_handle(hwnd = window1, h_ctrl = button1)

##                title2 = '[ClASS:#32770]'
##                autoit.win_wait_active(title = title2, timeout = timeout / 1000)
##                time.sleep(0.7)
##                autoit.send(send_text = '{ALTDOWN}{SPACE}{ALTUP}n', mode = 0)

                time.sleep(0.7)
##                autoit.win_wait_close_by_handle(handle = window, timeout = timeout / 1000)
                autoit.win_wait_close(title = title, timeout = timeout / 1000)

                self._log.effect(effect = 'download file')
##                try:
##                    self._driver._switch_to.alert.dismiss()
##                except selenium.common.exceptions.NoAlertPresentException:
##                    pass
##                except selenium.common.exceptions.NoSuchWindowException:
##                    pass

            self._driver._switch_to.window(window_name = self._handle)
        except Exception as e:
            self._log.error(error = e)
            raise e

    def title(self):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Driver.title()')
        try:
            self._log.clause(clause = 'none')

            title = self._driver.title
            if type(title) is unicode:
                title = title.encode(encoding = 'UTF-8', errors = 'strict')

            self._log.effect(effect = 'webpage title = ' + (title if title is not None else 'none'))

            return title
        except Exception as e:
            self._log.error(error = e)
            raise e

    def url(self):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Driver.url()')
        try:
            self._log.clause(clause = 'none')

            url = self._driver.current_url
            if type(url) is unicode:
                url = url.encode(encoding = 'UTF-8', errors = 'strict')

            self._log.effect(effect = 'webpage url = ' + (url if url is not None else 'none'))

            return url
        except Exception as e:
            self._log.error(error = e)
            raise e







class Element(object):
    def __init__(self, element, driver):
        if not ((isinstance(element, selenium.webdriver.remote.webelement.WebElement)) and (isinstance(driver, Driver))):
            raise Exception('pass element/driver as WebElement()/Driver()!')
        self._element = element
        self._driver = driver

    def find(self, tag = '*', attribute = list(), text = list()):
        time.sleep(self._driver._delay)
        self._driver._log.ignite(ignite = 'Element.find()')
        try:
            if (not (type(tag) is str) and (len(tag.strip()) > 0)) or ((type(attribute) is not list) and (not isinstance(attribute, Attribute))) or ((type(text) is not list) and (not isinstance(text, Text))):
                raise Exception('pass tag/attribute/text as str(len>0)/Attribute()/Text()!')

            xpath = './/' + tag

            if type(attribute) is not list:
                attribute = [attribute]

            for i in attribute:
                if not isinstance(i, Attribute):
                    raise Exception('pass attribute as list(Attribute())!')

                if i._strict is True:
                    xpath += "[@" + i._key + "='" + i._value + "']"
                else:
                    xpath += "[contains(@" + i._key + ",'" + i._value + "')]"

            if type(text) is not list:
                text = [text]

            for i in text:
                if not isinstance(i, Text):
                    raise Exception('pass text as list(Text())!')

                if i._strict is True:
                    xpath += "[text()='" + i._text + "']"
                else:
                    xpath += "[contains(text(),'" + i._text + "')]"

            self._driver._log.clause(clause = 'xpath = ' + xpath)

            element = self._element.find_elements_by_xpath(xpath = xpath.decode(encoding = 'UTF-8', errors = 'strict'))
            if not ((type(element) is list) and (len(element) > 0)):
                raise Exception('find element = 0!')

##            self._driver._parent.execute_script('arguments[0].scrollIntoView(true)', element[0])

            self._driver._log.effect(effect = 'find element = ' + str(len(element)))

            return list(Element(element = i, driver = self._driver) for i in element)
        except Exception as e:
            self._driver._log.error(error = e)
            raise e

    def parent(self):
        time.sleep(self._driver._delay)
        self._driver._log.ignite(ignite = 'Element.parent()')
        try:
            xpath = './/parent::node()'

            self._driver._log.clause(clause = 'xpath = ' + xpath)

            element = self._element.find_element_by_xpath(xpath = xpath.decode(encoding = 'UTF-8', errors = 'strict'))

##            self._element._parent.execute_script('arguments[0].scrollIntoView(true)', element)

            self._driver._log.effect(effect = 'parent find')

            return Element(element = element, driver = self._driver)
        except Exception as e:
            self._driver._log.error(error = e)
            raise e

    def hover(self, x = 0, y = 0):
        time.sleep(self._driver._delay)
        self._driver._log.ignite(ignite = 'Element.hover()')
        try:
            if not ((type(x) is int) and (type(y) is int)):
                raise Exception('pass x/y as int()!')

            self._driver._log.clause(clause = 'x = ' + str(x) + ', y = ' + str(y))

            end = time.time() + 7
            while time.time() < end:
                try:
                    if self._element.is_displayed() is True:
                        break
                    elif time.time() < end:
                        time.sleep(0.7)
                    else:
                        raise Exception('element not display!')
                except Exception as e:
                    if time.time() < end:
                        time.sleep(0.7)
                    else:
                        raise e

##            self._element._parent.execute_script('arguments[0].scrollIntoView(true)', self._element)

            selenium.webdriver.common.action_chains.ActionChains(driver = self._element._parent).move_to_element_with_offset(to_element = self._element, xoffset = self._element.size['width'] / 2 + x, yoffset = self._element.size['height'] / 2 - y).perform()

            self._driver._log.effect(effect = 'mouse hover')
        except Exception as e:
            self._driver._log.error(error = e)
            raise e

    def click(self, x = 0, y = 0):
        time.sleep(self._driver._delay)
        self._driver._log.ignite(ignite = 'Element.click()')
        try:
            if not ((type(x) is int) and (type(y) is int)):
                raise Exception('pass x/y as int()!')

            self._driver._log.clause(clause = 'x = ' + str(x) + ', y = ' + str(y))

            end = time.time() + 7
            while time.time() < end:
                try:
                    if self._element.is_displayed() is True:
                        break
                    elif time.time() < end:
                        time.sleep(0.7)
                    else:
                        raise Exception('element not display!')
                except Exception as e:
                    if time.time() < end:
                        time.sleep(0.7)
                    else:
                        raise e

            number = len(self._driver._driver.window_handles)

##            if self._driver._name != 'ie':
##                self._driver._handle = self._driver._driver.current_window_handle
            self._driver._handle = self._driver._driver.current_window_handle

##            self._element._parent.execute_script('arguments[0].scrollIntoView(true)', self._element)

            if x == 0 and y == 0:
                self._element.click()
            else:
##                selenium.webdriver.common.action_chains.ActionChains(driver = self._element._parent).move_to_element_with_offset(to_element = self._element, xoffset = self._element.size['width'] / 2 + x, yoffset = self._element.size['height'] / 2 - y).click(on_element = None).perform()
                selenium.webdriver.common.action_chains.ActionChains(driver = self._element._parent).move_to_element_with_offset(to_element = self._element, xoffset = self._element.size['width'] / 2 + x, yoffset = self._element.size['height'] / 2 - y).click_and_hold(on_element = None).release(on_element = None).perform()

            #Element.click() would typically open a new window
            if self._driver._name == 'ie':
                #ie treats HTML prompt and download dialog as Alerts
                try:
                    if len(self._driver._driver.window_handles) > number:
                        self._driver._driver._switch_to.window(window_name = self._driver._driver.window_handles[-1])

                        self._driver._driver.maximize_window()
                #while an Alert is activated, WebDriver.window_handles() would raise UnexpectedAlertPresentException
                except selenium.common.exceptions.UnexpectedAlertPresentException:
                    pass
                #while an Alert is activated, WebDriver.current_window_handle() would raise NoSuchWindowException
                except selenium.common.exceptions.NoSuchWindowException:
                    pass
                #the moment HTML prompt pops up/download dialog pops up/file has been downloaded and being moved from temp folder to destination folder, the Alert is activated
            elif len(self._driver._driver.window_handles) > number:
                #chrome & ff treat HTML prompt and download dialog as normal windows
                self._driver._driver._switch_to.window(window_name = self._driver._driver.window_handles[-1])

            self._driver._log.effect(effect = 'mouse click')
        except Exception as e:
            self._driver._log.error(error = e)
            raise e

    def mousedown(self, x = 0, y = 0):
        time.sleep(self._driver._delay)
        self._driver._log.ignite(ignite = 'Element.mousedown()')
        try:
            if not ((type(x) is int) and (type(y) is int)):
                raise Exception('pass x/y as int()!')

            self._driver._log.clause(clause = 'x = ' + str(x) + ', y = ' + str(y))

            end = time.time() + 7
            while time.time() < end:
                try:
                    if self._element.is_displayed() is True:
                        break
                    elif time.time() < end:
                        time.sleep(0.7)
                    else:
                        raise Exception('element not display!')
                except Exception as e:
                    if time.time() < end:
                        time.sleep(0.7)
                    else:
                        raise e

##            self._element._parent.execute_script('arguments[0].scrollIntoView(true)', self._element)

            selenium.webdriver.common.action_chains.ActionChains(driver = self._element._parent).move_to_element_with_offset(to_element = self._element, xoffset = self._element.size['width'] / 2 + x, yoffset = self._element.size['height'] / 2 - y).click_and_hold(on_element = None).perform()

            self._driver._log.effect(effect = 'mouse down')
        except Exception as e:
            self._driver._log.error(error = e)
            raise e

    def mouseup(self, x = 0, y = 0):
        time.sleep(self._driver._delay)
        self._driver._log.ignite(ignite = 'Element.mouseup()')
        try:
            if not ((type(x) is int) and (type(y) is int)):
                raise Exception('pass x/y as int()!')

            self._driver._log.clause(clause = 'x = ' + str(x) + ', y = ' + str(y))

            end = time.time() + 7
            while time.time() < end:
                try:
                    if self._element.is_displayed() is True:
                        break
                    elif time.time() < end:
                        time.sleep(0.7)
                    else:
                        raise Exception('element not display!')
                except Exception as e:
                    if time.time() < end:
                        time.sleep(0.7)
                    else:
                        raise e

##            self._element._parent.execute_script('arguments[0].scrollIntoView(true)', self._element)

            selenium.webdriver.common.action_chains.ActionChains(driver = self._element._parent).move_to_element_with_offset(to_element = self._element, xoffset = self._element.size['width'] / 2 + x, yoffset = self._element.size['height'] / 2 - y).release(on_element = None).perform()

            self._driver._log.effect(effect = 'mouse up')
        except Exception as e:
            self._driver._log.error(error = e)
            raise e

    def clear(self):
        time.sleep(self._driver._delay)
        self._driver._log.ignite(ignite = 'Element.clear()')
        try:
            self._driver._log.clause(clause = 'none')

            end = time.time() + 7
            while time.time() < end:
                try:
                    if self._element.is_displayed() is True:
                        break
                    elif time.time() < end:
                        time.sleep(0.7)
                    else:
                        raise Exception('element not display!')
                except Exception as e:
                    if time.time() < end:
                        time.sleep(0.7)
                    else:
                        raise e

##            self._element._parent.execute_script('arguments[0].scrollIntoView(true)', self._element)

            self._element.clear()

            self._driver._log.effect(effect = 'content clear')
        except Exception as e:
            self._driver._log.error(error = e)
            raise e

    def send(self, send):
        time.sleep(self._driver._delay)
        self._driver._log.ignite(ignite = 'Element.send()')
        try:
            if not ((type(send) is str) and (len(send) > 0)):
                raise Exception('pass send as str(len>0)!')

            end = time.time() + 7
            while time.time() < end:
                try:
                    if self._element.is_displayed() is True:
                        break
                    elif time.time() < end:
                        time.sleep(0.7)
                    else:
                        raise Exception('element not display!')
                except Exception as e:
                    if time.time() < end:
                        time.sleep(0.7)
                    else:
                        raise e

            self._driver._log.clause(clause = 'send = ' + send)

            number = len(self._driver._driver.window_handles)

##            if self._driver._name != 'ie':
##                self._driver._handle = self._driver._driver.current_window_handle
            self._driver._handle = self._driver._driver.current_window_handle

##            self._element._parent.execute_script('arguments[0].scrollIntoView(true)', self._element)

            self._element.send_keys(send.decode(encoding = 'UTF-8', errors = 'strict'))

            #Element.click() would typically open a new window, and rarely Element.send() would open a new window either
            if self._driver._name == 'ie':
                try:
                    if len(self._driver._driver.window_handles) > number:
                        self._driver._driver._switch_to.window(window_name = self._driver._driver.window_handles[-1])

                        self._driver._driver.maximize_window()
                except selenium.common.exceptions.UnexpectedAlertPresentException:
                    pass
                except selenium.common.exceptions.NoSuchWindowException:
                    pass
            elif len(self._driver._driver.window_handles) > number:
                self._driver._driver._switch_to.window(window_name = self._driver._driver.window_handles[-1])

            self._driver._log.effect(effect = 'line send')
        except Exception as e:
            self._driver._log.error(exception = e)
            raise e

    def waitexist(self, tag = '*', attribute = list(), text = list(), timeout = 7000):
        time.sleep(self._driver._delay)
        self._driver._log.ignite(ignite = 'Element.waitexist()')
        try:
            if (not (type(tag) is str) and (len(tag.strip()) > 0)) or ((type(attribute) is not list) and (not isinstance(attribute, Attribute))) or ((type(text) is not list) and (not isinstance(text, Text))) or (not (type(timeout) is int) and (timeout > 0)):
                raise Exception('pass tag/attribute/text/timeout as str(len>0)/Attribute()/Text()/int(>0)!')

            xpath = './/' + tag

            if type(attribute) is not list:
                attribute = [attribute]

            for i in attribute:
                if not isinstance(i, Attribute):
                    raise Exception('pass attribute as list(Attribute())!')

                if i._strict is True:
                    xpath += "[@" + i._key + "='" + i._value + "']"
                else:
                    xpath += "[contains(@" + i._key + ",'" + i._value + "')]"

            if type(text) is not list:
                text = [text]

            for i in text:
                if not isinstance(i, Text):
                    raise Exception('pass text as list(Text())!')

                if i._strict is True:
                    xpath += "[text()='" + i._text + "']"
                else:
                    xpath += "[contains(text(),'" + i._text + "')]"

            self._driver._log.clause(clause = 'xpath = ' + xpath)

            end = time.time() + timeout / 1000
            while time.time() < end:
                try:
                    self._element.find_element_by_xpath(xpath = xpath.decode(encoding = 'UTF-8', errors = 'strict'))
                except Exception as e:
                    if time.time() < end:
                        time.sleep(0.7)
                    else:
                        raise e
                else:
                    break

            self._driver._log.effect(effect = 'element exist')
        except Exception as e:
            self._driver._log.error(error = e)
            raise e

    def waitextinct(self, tag = '*', attribute = list(), text = list(), timeout = 7000):
        time.sleep(self._driver._delay)
        self._driver._log.ignite(ignite = 'Element.waitextinct()')
        try:
            if (not (type(tag) is str) and (len(tag.strip()) > 0)) or ((type(attribute) is not list) and (not isinstance(attribute, Attribute))) or ((type(text) is not list) and (not isinstance(text, Text))) or (not (type(timeout) is int) and (timeout > 0)):
                raise Exception('pass tag/attribute/text/timeout as str(len>0)/Attribute()/Text()/int(>0)!')

            xpath = './/' + tag

            if type(attribute) is not list:
                attribute = [attribute]

            for i in attribute:
                if not isinstance(i, Attribute):
                    raise Exception('pass attribute as list(Attribute())!')

                if i._strict is True:
                    xpath += "[@" + i._key + "='" + i._value + "']"
                else:
                    xpath += "[contains(@" + i._key + ",'" + i._value + "')]"

            if type(text) is not list:
                text = [text]

            for i in text:
                if not isinstance(i, Text):
                    raise Exception('pass text as list(Text())!')

                if i._strict is True:
                    xpath += "[text()='" + i._text + "']"
                else:
                    xpath += "[contains(text(),'" + i._text + "')]"

            self._driver._log.clause(clause = 'xpath = ' + xpath)

            end = time.time() + timeout / 1000
            while time.time() < end:
                try:
                    self._element.find_element_by_xpath(xpath = xpath.decode(encoding = 'UTF-8', errors = 'strict'))
                except Exception as e:
                        break
                else:
                    if time.time() < end:
                        time.sleep(0.7)
                    else:
                        raise e

            self._driver._log.effect(effect = 'element extinct')
        except Exception as e:
            self._driver._log.error(error = e)
            raise e

    def tag(self):
        time.sleep(self._driver._delay)
        self._driver._log.ignite(ignite = 'Element.tag()')
        try:
            self._driver._log.clause(clause = 'none')

            tag = self._element.tag_name
            if type(tag) is unicode:
                tag = tag.encode(encoding = 'utf-8', errors = 'strict')

            self._driver._log.effect(effect = 'element tag = ' + (tag if tag is not None else 'none'))

            return tag
        except Exception as e:
            self._driver._log.error(error = e)
            raise e

    def attribute(self, key):
        time.sleep(self._driver._delay)
        self._driver._log.ignite(ignite = 'Element.attribute()')
        try:
            if not ((type(key) is str) and (len(key.strip()) > 0)):
                raise Exception('pass key as str(len>0)!')

            self._driver._log.clause(clause = 'key = ' + key.strip())

            value = self._element.get_attribute(name = key.strip().decode(encoding = 'UTF-8', errors = 'strict'))
            if type(value) is unicode:
                value = value.encode(encoding = 'utf-8', errors = 'strict')

            self._driver._log.effect(effect = 'attibute [' + key.strip() + '] = ' + (value if value is not None else 'none'))

            return value
        except Exception as e:
            self._driver._log.error(error = e)
            raise e

    def text(self):
        time.sleep(self._driver._delay)
        self._driver._log.ignite(ignite = 'Element.text()')
        try:
            self._driver._log.clause(clause = 'none')

            text = self._element.text
            if type(text) is unicode:
                text = text.encode(encoding = 'utf-8', errors = 'strict')

            self._driver._log.effect(effect = 'element text = ' + (text if text is not None else 'none'))

            return text
        except Exception as e:
            self._driver._log.error(error = e)
            raise e

    def width(self):
        time.sleep(self._driver._delay)
        self._driver._log.ignite(ignite = 'Element.width()')
        try:
            self._driver._log.clause(clause = 'none')

            width = self._element.size['width']

            self._driver._log.effect(effect = 'element width = ' + (str(width) if width is not None else 'none'))

            return width
        except Exception as e:
            self._driver._log.error(error = e)
            raise e

    def height(self):
        time.sleep(self._driver._delay)
        self._driver._log.ignite(ignite = 'Element.height()')
        try:
            self._driver._log.clause(clause = 'none')

            height = self._element.size['height']

            self._driver._log.effect(effect = 'element height = ' + (str(height) if height is not None else 'none'))

            return height
        except Exception as e:
            self._driver._log.error(error = e)
            raise e

    def isdisplay(self):
        time.sleep(self._driver._delay)
        self._driver._log.ignite(ignite = 'Element.isdisplay()')
        try:
            self._driver._log.clause(clause = 'none')

            result = self._element.is_displayed() if True is True else False

            self._driver._log.effect(effect = 'element isdisplay = ' + ('true' if result else 'false'))

            return result
        except Exception as e:
            self._driver._log.error(error = e)
            raise e

    def isselect(self):
        time.sleep(self._driver._delay)
        self._driver._log.ignite(ignite = 'Element.isselect()')
        try:
            self._driver._log.clause(clause = 'none')

            result = self._element.is_selected() if True is True else False

            self._driver._log.effect(effect = 'element isselect = ' + ('true' if result else 'false'))

            return result
        except Exception as e:
            self._driver._log.error(error = e)
            raise e

    def isenable(self):
        time.sleep(self._driver._delay)
        self._driver._log.ignite(ignite = 'Element.isenable()')
        try:
            self._driver._log.clause(clause = 'none')

            result = self._element.is_enabled() if True is True else False

            self._driver._log.effect(effect = 'element isenable = ' + ('true' if result else 'false'))

            return result
        except Exception as e:
            self._driver._log.error(error = e)
            raise e







class Attribute(object):
    def __init__(self, key, value, strict = True):
        if (not (type(key) is str) and (len(key.strip()) > 0)) or ((type(value) is str) and (len(value) == 0)):
            raise Exception('pass key/value as str(len>0)!')

        self._key = key
        self._value = value
        self._strict = strict







class Text(object):
    def __init__(self, text, strict = True):
        if not ((type(text) is str) and len(text) > 0):
            raise Exception('pass text as str(len>0)!')

        self._text = text
        self._strict = strict







class Log(object):
    def __init__(self, path, driver):
        if not ((type(path) is str) and (len(re.findall(pattern = '^\s*(.+[/\\\])(.*)\s*$', string = path, flags = 0)) == 1) and (len(re.findall(pattern = '^\s*(.+[/\\\])(.*)\s*$', string = path, flags = 0)[0]) == 2) and (len(re.findall(pattern = '^\s*(.+[/\\\])(.*)\s*$', string = path, flags = 0)[0][1].strip()) > 0) and (isinstance(driver, Driver))):
            raise Exception('pass path/driver as str(log_path)/Driver()!')

        if not os.path.exists(path = re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0].decode(encoding = 'UTF-8', errors = 'strict')):
            os.makedirs(name = re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0].decode(encoding = 'UTF-8', errors = 'strict'), mode = 0777)

        self._log = open(name = (re.findall(pattern = '^\s*(.+[/\\\])(.*)\s*$', string = path, flags = 0)[0][0] + re.findall(pattern = '^\s*(.+[/\\\])(.*)\s*$', string = path, flags = 0)[0][1].strip()).decode(encoding = 'UTF-8', errors = 'strict'), mode = 'w+', buffering = 0)
        self._driver = driver
        self._count = 1

    def ignite(self, ignite):
        self._log.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') + '\tDEF IGNITE:\t' + ignite)
        self._log.write('\n')

    def clause(self, clause):
        self._log.write('\t' * 4 + 'DEF CLAUSE:\t' + clause)
        self._log.write('\n')

    def effect(self, effect):
        self._log.write('\t' * 4 + 'DEF EFFECT:\t' + effect)
        self._log.write('\n' * 2)

    def error(self, error):
        PIL.ImageGrab.grab(bbox=None).save(fp = (self._log.name + '.' + str(self._count).zfill(7) + '.jpg').encode(encoding = 'UTF-8', errors = 'strict'), format = 'JPEG')

##        try:
##            self._driver._driver.quit()
##        except:
##            pass

        if isinstance(error, selenium.common.exceptions.WebDriverException):
            message = error.msg
        else:
            message = error.message

        self._log.write('DEF EXCEPTION:\t' + message)
        self._log.write('\n')
        self._log.write('DEF TRACEBACK:')
        self._log.write('\n')
        self._log.writelines(traceback.format_stack(f = None, limit = None))
        self._log.write('DEF SCREENSHOT:\t' + self._log.name + '.' + str(self._count).zfill(7) + '.jpg')
        self._log.write('\n' * 2)
        self._count += 1

##        self._log.close()