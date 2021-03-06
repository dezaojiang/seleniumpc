#-*- coding: utf-8 -*-
#!/usr/bin/env python

import os, re, selenium, time, autoit, datetime, StringIO, PIL.ImageGrab, traceback
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
        self._frame = list()

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
        if not ((type(executor) is str) and (len(re.findall(pattern = '^.*[.]exe\s*$', string = executor, flags = re.IGNORECASE)) == 1) and (os.path.isfile(path = executor.strip().decode(encoding = 'utf_8', errors = 'strict')))):
            raise Exception('pass executor as str(executor_path)!')
        self._executor = executor.strip()

    @property
    def browser(self):
        return self._browser
    @browser.setter
    def browser(self, browser):
        if not ((type(browser) is str) and (len(re.findall(pattern = '^.*[.]exe\s*$', string = browser, flags = re.IGNORECASE)) == 1) and (os.path.isfile(path = browser.strip().decode(encoding = 'utf_8', errors = 'strict')))):
            raise Exception('pass browser as str(browser_path)!')
        self._browser = browser.strip()

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
            raise Exception('pass delay as int(>0)!')
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
            self._log.clause(clause = 'name = ' + self._name + ', executor = ' + (self._executor.replace('/', '\\') if self._executor is not None else 'none') + ', browser = ' + (self._browser.replace('/', '\\') if self._browser is not None else 'none') + ', proxy = ' + (self._proxy if self._proxy is not None else 'none') + ', option = ' + (' '.join(self._option) if len(self._option) > 0 else 'none') + ', log = ' + self._log._log.name.encode(encoding = 'utf_8', errors = 'strict'))

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

            #selenium extension is not enabled in chrome's incognito mode, then it would not be able to handle instructions in incognito mode either
            if (self._name == 'chrome') and (('incognito' in self._option) or ('-incognito' in self._option) or ('--incognito' in self._option)):
                self._driver.get(url = 'chrome://extensions-frame')
                if self._driver.find_element(by = 'xpath', value = "//input[@type='checkbox'][@focus-type='incognito'][@tabindex='0']").is_selected() is False:
                    self._driver.find_element(by = 'xpath', value = "//input[@type='checkbox'][@focus-type='incognito'][@tabindex='0']").click()
##                if self._driver.find_element(by = 'xpath', value = "//span[@class='extension-title'][text()='Chrome Automation Extension']/parent::div/parent::div[@class='extension-details']//label[@class='incognito-control']/input[@type='checkbox']").is_selected() is False:
##                    self._driver.find_element(by = 'xpath', value = "//span[@class='extension-title'][text()='Chrome Automation Extension']/parent::div/parent::div[@class='extension-details']//label[@class='incognito-control']/input[@type='checkbox']").click()

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

            self._driver.get(url = url.strip().decode(encoding = 'utf_8', errors = 'strict'))

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
            del self._frame[0::1]

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
                    xpath += '[@' + i._key + '=' + i._value + ']'
                else:
                    xpath += '[contains(@' + i._key + ',' + i._value + ')]'

            if type(text) is not list:
                text = [text]

            for i in text:
                if not isinstance(i, Text):
                    raise Exception('pass text as list(Text())!')

                if i._strict is True:
                    xpath += '[text()=' + i._text + ']'
                else:
                    xpath += '[contains(text(),' + i._text + ')]'

            self._log.clause(clause = 'xpath = ' + xpath)

            element = self._driver.find_elements(by = 'xpath', value = xpath.decode(encoding = 'utf_8', errors = 'strict'))
            if not ((type(element) is list) and (len(element) > 0)):
                raise Exception('find element = 0!')

##            self._driver.execute_script(script = 'arguments[0].scrollIntoView(true)', element[0])

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
                tag = tag.encode(encoding = 'utf_8', errors = 'strict')
            if not ((tag is not None) and ('frame' in tag)):
                raise Exception('pass element as Element(<frame>)!')

            self._log.clause(clause = 'Element()')

            self._driver._switch_to.frame(frame_reference = element._element)
            self._frame.append(element._element)

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
                        self._driver._switch_to.window(window_name = self._driver.window_handles[-1])
                        del self._frame[0::1]

                        self._driver.maximize_window()
                except selenium.common.exceptions.UnexpectedAlertPresentException:
                    pass
                except selenium.common.exceptions.NoSuchWindowException:
                    pass
            elif len(self._driver.window_handles) > number:
                self._driver._switch_to.window(window_name = self._driver.window_handles[-1])
                del self._frame[0::1]

            self._log.effect(effect = 'key type')
        except Exception as e:
            self._log.error(error = e)
            raise e

    def modifierdown(self, modifier):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Driver.modifierdown()')
        try:
            if not (((type(modifier) is list) and (len(modifier) > 0)) or ((type(modifier) is unicode) and (modifier in selenium.webdriver.common.keys.Keys.__dict__.values()))):
                raise Exception('pass modifier as Key()!')

            if type(modifier) is not list:
                modifier = [modifier]

            action = selenium.webdriver.common.action_chains.ActionChains(driver = self._driver)
            clause = ''
            for i in modifier:
                if not ((type(i) is unicode) and (i in selenium.webdriver.common.keys.Keys.__dict__.values())):
                    raise Exception('pass modifier as list(Key())!')

                action.key_down(value = i, element = None)
                clause += i.encode(encoding = 'unicode-escape', errors = 'strict')

            self._log.clause(clause = 'modifier = ' + clause)

            action.perform()

            self._log.effect(effect = 'modifier down')
        except Exception as e:
            self._log.error(error = e)
            raise e

    def modifierup(self, modifier):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Driver.modifierup()')
        try:
            if not (((type(modifier) is list) and (len(modifier) > 0)) or ((type(modifier) is unicode) and (modifier in selenium.webdriver.common.keys.Keys.__dict__.values()))):
                raise Exception('pass modifier as Key()!')

            if type(modifier) is not list:
                modifier = [modifier]

            action = selenium.webdriver.common.action_chains.ActionChains(driver = self._driver)
            clause = ''
            for i in modifier:
                if not ((type(i) is unicode) and (i in selenium.webdriver.common.keys.Keys.__dict__.values())):
                    raise Exception('pass modifier as list(Key())!')

                action.key_up(value = i, element = None)
                clause += i.encode(encoding = 'unicode-escape', errors = 'strict')

            self._log.clause(clause = 'modifier = ' + clause)

            action.perform()

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
                text = text.encode(encoding = 'utf_8', errors = 'strict')

            if send is not None:
                alert.send_keys(keysToSend = send.decode(encoding = 'utf_8', errors = 'strict'))

            if accept is True:
                #accept the Alert would automatically switch Driver from current Alert back to last window
                alert.accept()
            else:
                #accept the Alert would not switch Driver back to last window, thus add one more manual step to do the switch action
                alert.dismiss()
                self._driver._switch_to.window(window_name = self._driver.window_handles[-1])
                del self._frame[0::1]

            self._log.effect(effect = 'alert text = ' + (text if text is not None else 'none'))

            return text
        except Exception as e:
            self._log.error(error = e)
            raise e

    def upload(self, path, timeout = 7000):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Driver.upload()')
        try:
            if not ((type(path) is str) and (os.path.isfile(path = path.strip().decode(encoding = 'utf_8', errors = 'strict'))) and (type(timeout) is int) and (timeout > 0)):
                raise Exception('pass path/timeout as str(file_path)/int(>0)!')

            self._log.clause(clause = 'path = ' + path.strip().replace('/', '\\') + ', timeout = ' + str(timeout))

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
            autoit.control_set_text_by_handle(hwnd = window, h_ctrl = edit, control_text = path.strip().replace('/', '\\').decode(encoding = 'utf_8', errors = 'strict'))
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
            if not ((type(path) is str) and (len(re.findall(pattern = '^\s*(.+[/\\\])(.*)\s*$', string = path, flags = 0)) == 1) and (len(re.findall(pattern = '^\s*(.+[/\\\])\s*(.*)\s*$', string = path, flags = 0)[0][1]) > 0) and (type(timeout) is int) and (timeout > 0)):
                raise Exception('pass path/timeout as str(file_path)/int(>0)!')

            self._log.clause(clause = 'path = ' + (re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0] + re.findall(pattern = '^\s*(.+[/\\\])\s*(.*)\s*$', string = path, flags = 0)[0][1]).replace('/', '\\') + ', timeout = ' + str(timeout))

            if self._name == 'chrome':
                title = u'另存为'
                autoit.win_wait(title = title, timeout = timeout / 1000)
                window = autoit.win_get_handle(title = title)
                edit = autoit.control_get_handle(hwnd = window, control = 'Edit1')
                combo = autoit.control_get_handle(hwnd = window, control = 'ComboBox2')
                button = autoit.control_get_handle(hwnd = window, control = 'Button1')
                if os.path.isfile(path = (re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0] + re.findall(pattern = '^\s*(.+[/\\\])\s*(.*)\s*$', string = path, flags = 0)[0][1]).decode(encoding = 'utf_8', errors = 'strict')):
                    os.remove((re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0] + re.findall(pattern = '^\s*(.+[/\\\])\s*(.*)\s*$', string = path, flags = 0)[0][1]).decode(encoding = 'utf_8', errors = 'strict'))
                elif not os.path.exists(path = re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0].decode(encoding = 'utf_8', errors = 'strict')):
                    os.makedirs(name = re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0].decode(encoding = 'utf_8', errors = 'strict'), mode = 0777)
                time.sleep(0.7)
                autoit.control_set_text_by_handle(hwnd = window, h_ctrl = edit, control_text = (re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0] + re.findall(pattern = '^\s*(.+[/\\\])\s*(.*)\s*$', string = path, flags = 0)[0][1]).replace('/', '\\').decode(encoding = 'utf_8', errors = 'strict'))
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
##                del self._frame[0::1]

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
                if not os.path.exists(path = re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0].decode(encoding = 'utf_8', errors = 'strict')):
                    os.makedirs(name = re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0].decode(encoding = 'utf_8', errors = 'strict'), mode = 0777)
                time.sleep(0.7)
                autoit.control_set_text_by_handle(hwnd = window, h_ctrl = edit, control_text = (re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0] + re.findall(pattern = '^\s*(.+[/\\\])\s*(.*)\s*$', string = path, flags = 0)[0][1]).replace('/', '\\').decode(encoding = 'utf_8', errors = 'strict'))
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
##                del self._frame[0::1]

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
                if not os.path.exists(path = re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0].decode(encoding = 'utf_8', errors = 'strict')):
                    os.makedirs(name = re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0].decode(encoding = 'utf_8', errors = 'strict'), mode = 0777)
                time.sleep(0.7)
                autoit.control_set_text_by_handle(hwnd = window, h_ctrl = edit, control_text = (re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0] + re.findall(pattern = '^\s*(.+[/\\\])\s*(.*)\s*$', string = path, flags = 0)[0][1]).replace('/', '\\').decode(encoding = 'utf_8', errors = 'strict'))
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
            del self._frame[0::1]
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
                title = title.encode(encoding = 'utf_8', errors = 'strict')

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
                url = url.encode(encoding = 'utf_8', errors = 'strict')

            self._log.effect(effect = 'webpage url = ' + (url if url is not None else 'none'))

            return url
        except Exception as e:
            self._log.error(error = e)
            raise e

    def shoot(self, path):
##        time.sleep(self._delay)
        self._log.ignite(ignite = 'Driver.shoot()')
        try:
            if not ((type(path) is str) and (len(re.findall(pattern = '^\s*(.+[/\\\])(.*[.]png)\s*$', string = path, flags = re.IGNORECASE)) == 1) and (len(re.findall(pattern = '^\s*(.+[/\\\])\s*(.*[.]png)\s*$', string = path, flags = re.IGNORECASE)[0][1]) > 0)):
                raise Exception('pass path as str(png_path)!')

            if not os.path.exists(path = re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0].decode(encoding = 'utf_8', errors = 'strict')):
                os.makedirs(name = re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0].decode(encoding = 'utf_8', errors = 'strict'), mode = 0777)

            self._log.clause(clause = 'path = ' + (re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0] + re.findall(pattern = '^\s*(.+[/\\\])\s*(.*[.]png)\s*$', string = path, flags = re.IGNORECASE)[0][1]).replace('/', '\\'))

            if self._name == 'chrome':
                self._driver._switch_to.default_content()

                full_height = self._driver.execute_script(script = 'return window.document.height')
                full_width = self._driver.execute_script(script = 'return window.document.width')
                screen_height = self._driver.execute_script(script = 'return window.document.documentElement.clientHeight')
                screen_width = self._driver.execute_script(script = 'return window.document.documentElement.clientWidth')

                memory = StringIO.StringIO(buf = '')
                full_image = PIL.Image.new(mode = 'RGB', size = (full_width, full_height), color = 0)

                for j in range(0, full_height / screen_height, 1):
                    y = screen_height * j
                    for i in range(0, full_width / screen_width, 1):
                        x = screen_width * i
                        self._driver.execute_script(script = ('window.scrollTo(%s, %s)' % (x, y)))
                        time.sleep(0.7)
                        memory.truncate(size = 0)
##                        memory.write(s = self._driver.get_screenshot_as_png())
                        memory.write(s = self._driver.get_screenshot_as_base64().decode(encoding = 'base64_codec', errors = 'strict'))
                        memory.seek(pos = 0, mode = 0)
                        screen_image = PIL.Image.open(fp = memory, mode = 'r')
                        full_image.paste(im = screen_image, box = (x, y), mask = None)
                    if screen_width * (i + 1) < full_width:
                        x = full_width - 1 - screen_width
                        self._driver.execute_script(script = ('window.scrollTo(%s, %s)' % (x, y)))
                        time.sleep(0.7)
                        memory.truncate(size = 0)
##                        memory.write(s = self._driver.get_screenshot_as_png())
                        memory.write(s = self._driver.get_screenshot_as_base64().decode(encoding = 'base64_codec', errors = 'strict'))
                        memory.seek(pos = 0, mode = 0)
                        screen_image = PIL.Image.open(fp = memory, mode = 'r')
                        full_image.paste(im = screen_image, box = (x, y), mask = None)
                if screen_height * (j + 1) < full_height:
                    y = full_height - 1 - screen_height
                    for i in range(0, full_width / screen_width, 1):
                        x = screen_width * i
                        self._driver.execute_script(script = ('window.scrollTo(%s, %s)' % (x, y)))
                        time.sleep(0.7)
                        memory.truncate(size = 0)
##                        memory.write(s = self._driver.get_screenshot_as_png())
                        memory.write(s = self._driver.get_screenshot_as_base64().decode(encoding = 'base64_codec', errors = 'strict'))
                        memory.seek(pos = 0, mode = 0)
                        screen_image = PIL.Image.open(fp = memory, mode = 'r')
                        full_image.paste(im = screen_image, box = (x, y), mask = None)
                    if screen_width * (i + 1) < full_width:
                        x = full_width - 1 - screen_width
                        self._driver.execute_script(script = ('window.scrollTo(%s, %s)' % (x, y)))
                        time.sleep(0.7)
                        memory.truncate(size = 0)
##                        memory.write(s = self._driver.get_screenshot_as_png())
                        memory.write(s = self._driver.get_screenshot_as_base64().decode(encoding = 'base64_codec', errors = 'strict'))
                        memory.seek(pos = 0, mode = 0)
                        screen_image = PIL.Image.open(fp = memory, mode = 'r')
                        full_image.paste(im = screen_image, box = (x, y), mask = None)

                full_image.save(fp = (re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0] + re.findall(pattern = '^\s*(.+[/\\\])\s*(.*[.]png)\s*$', string = path, flags = re.IGNORECASE)[0][1]).decode(encoding = 'utf_8', errors = 'strict'), format = 'PNG')
                memory.close()

                self._log.effect(effect = 'webpage shoot')

                for i in self._frame:
                    self._driver._switch_to.frame(frame_reference = i)

            else:
##                self._driver.get_screenshot_as_file(filename = (re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0] + re.findall(pattern = '^\s*(.+[/\\\])\s*(.*[.]png)\s*$', string = path, flags = re.IGNORECASE)[0][1]).decode(encoding = 'utf_8', errors = 'strict'))
                with open(name = (re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0] + re.findall(pattern = '^\s*(.+[/\\\])\s*(.*[.]png)\s*$', string = path, flags = re.IGNORECASE)[0][1]).decode(encoding = 'utf_8', errors = 'strict'), mode = 'wb+', buffering = 0) as f:
                    f.write(self._driver.get_screenshot_as_base64().decode(encoding = 'base64_codec', errors = 'strict'))

                self._log.effect(effect = 'webpage shoot')
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
                    xpath += '[@' + i._key + '=' + i._value + ']'
                else:
                    xpath += '[contains(@' + i._key + ',' + i._value + ')]'

            if type(text) is not list:
                text = [text]

            for i in text:
                if not isinstance(i, Text):
                    raise Exception('pass text as list(Text())!')

                if i._strict is True:
                    xpath += '[text()=' + i._text + ']'
                else:
                    xpath += '[contains(text(),' + i._text + ')]'

            self._driver._log.clause(clause = 'xpath = ' + xpath)

            element = self._element.find_elements(by = 'xpath', value = xpath.decode(encoding = 'utf_8', errors = 'strict'))
            if not ((type(element) is list) and (len(element) > 0)):
                raise Exception('find element = 0!')

##            self._driver._parent.execute_script(script = 'arguments[0].scrollIntoView(true)', element[0])

            self._driver._log.effect(effect = 'find element = ' + str(len(element)))

            return list(Element(element = i, driver = self._driver) for i in element)
        except Exception as e:
            self._driver._log.error(error = e)
            raise e

    def parent(self):
        time.sleep(self._driver._delay)
        self._driver._log.ignite(ignite = 'Element.parent()')
        try:
            xpath = './..'

            self._driver._log.clause(clause = 'xpath = ./..')

            element = self._element.find_element(by = 'xpath', value = xpath)

##            self._element._parent.execute_script(script = 'arguments[0].scrollIntoView(true)', element)

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
                    else:
                        raise Exception('element not display!')
                except Exception as e:
                    if time.time() < end:
                        time.sleep(0.7)
                    else:
                        raise e

##            self._element._parent.execute_script(script = 'arguments[0].scrollIntoView(true)', self._element)

            selenium.webdriver.common.action_chains.ActionChains(driver = self._element._parent).move_to_element_with_offset(to_element = self._element, xoffset = self._element.size['width'] / 2 + x, yoffset = self._element.size['height'] / 2 - y).perform()

            self._driver._log.effect(effect = 'mouse hover')
        except Exception as e:
            self._driver._log.error(error = e)
            raise e

    def click(self, x = 0, y = 0, count = 1):
        time.sleep(self._driver._delay)
        self._driver._log.ignite(ignite = 'Element.click()')
        try:
            if not ((type(x) is int) and (type(y) is int) and (type(count) is int) and (count > 0)):
                raise Exception('pass x/y/count as int()/int(>0)!')

            self._driver._log.clause(clause = 'x = ' + str(x) + ', y = ' + str(y) + ', count = ' + str(count))

            end = time.time() + 7
            while time.time() < end:
                try:
                    if self._element.is_displayed() is True:
                        break
                    else:
                        raise Exception('element not display!')
                except Exception as e:
                    if time.time() < end:
                        time.sleep(0.7)
                    else:
                        raise e

            number = len(self._element._parent.window_handles)

##            if self._driver._name != 'ie':
##                self._driver._handle = self._element._parent.current_window_handle
            self._driver._handle = self._element._parent.current_window_handle

##            self._element._parent.execute_script(script = 'arguments[0].scrollIntoView(true)', self._element)

            if x == 0 and y == 0:
                for i in range(0, count, 1):
                    self._element.click()
##                    time.sleep(0.17)
            else:
                action = selenium.webdriver.common.action_chains.ActionChains(driver = self._element._parent)
                action.move_to_element_with_offset(to_element = self._element, xoffset = self._element.size['width'] / 2 + x, yoffset = self._element.size['height'] / 2 - y)
                for i in range(0, count, 1):
##                    action.click(on_element = None)
                    action.click_and_hold(on_element = None).release(on_element = None)
                action.perform()

            #Element.click() would typically open a new window
            if self._driver._name == 'ie':
                #ie treats HTML prompt and download dialog as Alerts
                try:
                    if len(self._element._parent.window_handles) > number:
                        self._element._parent._switch_to.window(window_name = self._element._parent.window_handles[-1])
                        del self._driver._frame[0::1]

                        self._element._parent.maximize_window()
                #while an Alert is activated, WebDriver.window_handles() would raise UnexpectedAlertPresentException
                except selenium.common.exceptions.UnexpectedAlertPresentException:
                    pass
                #while an Alert is activated, WebDriver.current_window_handle() would raise NoSuchWindowException
                except selenium.common.exceptions.NoSuchWindowException:
                    pass
                #the moment HTML prompt pops up/download dialog pops up/file has been downloaded and being moved from temp folder to destination folder, the Alert is activated
            elif len(self._element._parent.window_handles) > number:
                #chrome & ff treat HTML prompt and download dialog as normal windows
                self._element._parent._switch_to.window(window_name = self._element._parent.window_handles[-1])
                del self._driver._frame[0::1]

            self._driver._log.effect(effect = 'mouse click = ' + str(count))
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
                    else:
                        raise Exception('element not display!')
                except Exception as e:
                    if time.time() < end:
                        time.sleep(0.7)
                    else:
                        raise e

##            self._element._parent.execute_script(script = 'arguments[0].scrollIntoView(true)', self._element)

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
                    else:
                        raise Exception('element not display!')
                except Exception as e:
                    if time.time() < end:
                        time.sleep(0.7)
                    else:
                        raise e

##            self._element._parent.execute_script(script = 'arguments[0].scrollIntoView(true)', self._element)

            selenium.webdriver.common.action_chains.ActionChains(driver = self._element._parent).move_to_element_with_offset(to_element = self._element, xoffset = self._element.size['width'] / 2 + x, yoffset = self._element.size['height'] / 2 - y).release(on_element = None).perform()

            self._driver._log.effect(effect = 'mouse up')
        except Exception as e:
            self._driver._log.error(error = e)
            raise e

    def mousepress(self, duration, x = 0, y = 0):
        time.sleep(self._driver._delay)
        self._driver._log.ignite(ignite = 'Element.mousepress()')
        try:
            if not ((type(duration) is int) and (duration > 0) and (type(x) is int) and (type(y) is int)):
                raise Exception('pass duration/x/y as int(>0)/int()!')

            self._driver._log.clause(clause = 'duration = ' + str(duration) + ', x = ' + str(x) + ', y = ' + str(y))

            end = time.time() + 7
            while time.time() < end:
                try:
                    if self._element.is_displayed() is True:
                        break
                    else:
                        raise Exception('element not display!')
                except Exception as e:
                    if time.time() < end:
                        time.sleep(0.7)
                    else:
                        raise e

##            self._element._parent.execute_script(script = 'arguments[0].scrollIntoView(true)', self._element)

            selenium.webdriver.common.action_chains.ActionChains(driver = self._element._parent).move_to_element_with_offset(to_element = self._element, xoffset = self._element.size['width'] / 2 + x, yoffset = self._element.size['height'] / 2 - y).perform()
            time.sleep(duration / 1000)
            selenium.webdriver.common.action_chains.ActionChains(driver = self._element._parent).release(on_element = None).perform()

            self._driver._log.effect(effect = 'mouse press = ' + str(duration))
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
                    else:
                        raise Exception('element not display!')
                except Exception as e:
                    if time.time() < end:
                        time.sleep(0.7)
                    else:
                        raise e

##            self._element._parent.execute_script(script = 'arguments[0].scrollIntoView(true)', self._element)

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
                    else:
                        raise Exception('element not display!')
                except Exception as e:
                    if time.time() < end:
                        time.sleep(0.7)
                    else:
                        raise e

            self._driver._log.clause(clause = 'send = ' + send)

            number = len(self._element._parent.window_handles)

##            if self._driver._name != 'ie':
##                self._driver._handle = self._element._parent.current_window_handle
            self._driver._handle = self._element._parent.current_window_handle

##            self._element._parent.execute_script(script = 'arguments[0].scrollIntoView(true)', self._element)

            self._element.send_keys(send.decode(encoding = 'utf_8', errors = 'strict'))

            #Element.click() would typically open a new window, and rarely Element.send() would open a new window either
            if self._driver._name == 'ie':
                try:
                    if len(self._element._parent.window_handles) > number:
                        self._element._parent._switch_to.window(window_name = self._element._parent.window_handles[-1])
                        del self._driver._frame[0::1]

                        self._element._parent.maximize_window()
                except selenium.common.exceptions.UnexpectedAlertPresentException:
                    pass
                except selenium.common.exceptions.NoSuchWindowException:
                    pass
            elif len(self._element._parent.window_handles) > number:
                self._element._parent._switch_to.window(window_name = self._element._parent.window_handles[-1])
                del self._driver._frame[0::1]

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
                    xpath += '[@' + i._key + '=' + i._value + ']'
                else:
                    xpath += '[contains(@' + i._key + ',' + i._value + ')]'

            if type(text) is not list:
                text = [text]

            for i in text:
                if not isinstance(i, Text):
                    raise Exception('pass text as list(Text())!')

                if i._strict is True:
                    xpath += '[text()=' + i._text + ']'
                else:
                    xpath += '[contains(text(),' + i._text + ')]'

            self._driver._log.clause(clause = 'xpath = ' + xpath)

            end = time.time() + timeout / 1000
            while time.time() < end:
                try:
                    if not isinstance(self._element.find_element(by = 'xpath', value = xpath.decode(encoding = 'utf_8', errors = 'strict')), selenium.webdriver.remote.webelement.WebElement):
                        raise Exception('element not exist!')
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
                    xpath += '[@' + i._key + '=' + i._value + ']'
                else:
                    xpath += '[contains(@' + i._key + ',' + i._value + ')]'

            if type(text) is not list:
                text = [text]

            for i in text:
                if not isinstance(i, Text):
                    raise Exception('pass text as list(Text())!')

                if i._strict is True:
                    xpath += '[text()=' + i._text + ']'
                else:
                    xpath += '[contains(text(),' + i._text + ')]'

            self._driver._log.clause(clause = 'xpath = ' + xpath)

            end = time.time() + timeout / 1000
            while time.time() < end:
                try:
                    if not isinstance(self._element.find_element(by = 'xpath', value = xpath.decode(encoding = 'utf_8', errors = 'strict')), selenium.webdriver.remote.webelement.WebElement):
                        raise
                except Exception:
                        break
                else:
                    if time.time() < end:
                        time.sleep(0.7)
                    else:
                        raise Exception('element not extinct!')

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
                tag = tag.encode(encoding = 'utf_8', errors = 'strict')

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

            value = self._element.get_attribute(name = key.strip().decode(encoding = 'utf_8', errors = 'strict'))
            if type(value) is unicode:
                value = value.encode(encoding = 'utf_8', errors = 'strict')

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
                text = text.encode(encoding = 'utf_8', errors = 'strict')

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

            width = self._element.size.get('width', None)

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

            height = self._element.size.get('height', None)

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

            result = self._element.is_displayed() is True

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

            result = self._element.is_selected() is True

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

            result = self._element.is_enabled() is True

            self._driver._log.effect(effect = 'element isenable = ' + ('true' if result else 'false'))

            return result
        except Exception as e:
            self._driver._log.error(error = e)
            raise e

    def shoot(self, path, left = 0, top = 0, right = 0, bottom = 0):
##        time.sleep(self._driver._delay)
        self._driver._log.ignite(ignite = 'Driver.shoot()')
        try:
            if not ((type(path) is str) and (len(re.findall(pattern = '^\s*(.+[/\\\])(.*[.]png)\s*$', string = path, flags = re.IGNORECASE)) == 1) and (len(re.findall(pattern = '^\s*(.+[/\\\])\s*(.*[.]png)\s*$', string = path, flags = re.IGNORECASE)[0][1]) > 0) and (type(left) is int) and (type(top) is int) and (type(right) is int) and (type(bottom) is int)):
                raise Exception('pass path/left/top/right/bottom as str(png_path)/int!')

            if not os.path.exists(path = re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0].decode(encoding = 'utf_8', errors = 'strict')):
                os.makedirs(name = re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0].decode(encoding = 'utf_8', errors = 'strict'), mode = 0777)

            self._driver._log.clause(clause = 'path = ' + (re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0] + re.findall(pattern = '^\s*(.+[/\\\])\s*(.*[.]png)\s*$', string = path, flags = re.IGNORECASE)[0][1]).replace('/', '\\') + ', left = ' + str(left) + ', top = ' + str(top) + ', right = ' + str(right) + ', bottom = ' + str(bottom))

            if self._driver._name == 'chrome':
                self._driver._driver._switch_to.default_content()

                full_height = self._driver._driver.execute_script(script = 'return window.document.height')
                full_width = self._driver._driver.execute_script(script = 'return window.document.width')
                screen_height = self._driver._driver.execute_script(script = 'return window.document.documentElement.clientHeight')
                screen_width = self._driver._driver.execute_script(script = 'return window.document.documentElement.clientWidth')

                memory = StringIO.StringIO(buf = '')
                full_image = PIL.Image.new(mode = 'RGB', size = (full_width, full_height), color = 0)

                for j in range(0, full_height / screen_height, 1):
                    y = screen_height * j
                    for i in range(0, full_width / screen_width, 1):
                        x = screen_width * i
                        self._driver._driver.execute_script(script = ('window.scrollTo(%s, %s)' % (x, y)))
                        time.sleep(0.7)
                        memory.truncate(size = 0)
##                        memory.write(s = self._driver._driver.get_screenshot_as_png())
                        memory.write(s = self._driver._driver.get_screenshot_as_base64().decode(encoding = 'base64_codec', errors = 'strict'))
                        memory.seek(pos = 0, mode = 0)
                        screen_image = PIL.Image.open(fp = memory, mode = 'r')
                        full_image.paste(im = screen_image, box = (x, y), mask = None)
                    if screen_width * (i + 1) < full_width:
                        x = full_width - 1 - screen_width
                        self._driver._driver.execute_script(script = ('window.scrollTo(%s, %s)' % (x, y)))
                        time.sleep(0.7)
                        memory.truncate(size = 0)
##                        memory.write(s = self._driver._driver.get_screenshot_as_png())
                        memory.write(s = self._driver._driver.get_screenshot_as_base64().decode(encoding = 'base64_codec', errors = 'strict'))
                        memory.seek(pos = 0, mode = 0)
                        screen_image = PIL.Image.open(fp = memory, mode = 'r')
                        full_image.paste(im = screen_image, box = (x, y), mask = None)
                if screen_height * (j + 1) < full_height:
                    y = full_height - 1 - screen_height
                    for i in range(0, full_width / screen_width, 1):
                        x = screen_width * i
                        self._driver._driver.execute_script(script = ('window.scrollTo(%s, %s)' % (x, y)))
                        time.sleep(0.7)
                        memory.truncate(size = 0)
##                        memory.write(s = self._driver._driver.get_screenshot_as_png())
                        memory.write(s = self._driver._driver.get_screenshot_as_base64().decode(encoding = 'base64_codec', errors = 'strict'))
                        memory.seek(pos = 0, mode = 0)
                        screen_image = PIL.Image.open(fp = memory, mode = 'r')
                        full_image.paste(im = screen_image, box = (x, y), mask = None)
                    if screen_width * (i + 1) < full_width:
                        x = full_width - 1 - screen_width
                        self._driver._driver.execute_script(script = ('window.scrollTo(%s, %s)' % (x, y)))
                        time.sleep(0.7)
                        memory.truncate(size = 0)
##                        memory.write(s = self._driver._driver.get_screenshot_as_png())
                        memory.write(s = self._driver._driver.get_screenshot_as_base64().decode(encoding = 'base64_codec', errors = 'strict'))
                        memory.seek(pos = 0, mode = 0)
                        screen_image = PIL.Image.open(fp = memory, mode = 'r')
                        full_image.paste(im = screen_image, box = (x, y), mask = None)

                left = left
                top = 0 - top
                right = right
                bottom = 0 - bottom
                for i in self._driver._frame:
                    left += i.location['x']
                    top += i.location['y']
                    right += i.location['x']
                    bottom += i.location['y']
                    self._driver._driver._switch_to.frame(frame_reference = i)

                left += self._element.location['x']
                top += self._element.location['y']
                right += self._element.location['x'] + self._element.size['width']
                bottom += self._element.location['y'] + self._element.size['height']

                element_image = full_image.crop(box = (left, top, right, bottom))
                element_image.save(fp = (re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0] + re.findall(pattern = '^\s*(.+[/\\\])\s*(.*[.]png)\s*$', string = path, flags = re.IGNORECASE)[0][1]).decode(encoding = 'utf_8', errors = 'strict'), format = 'PNG')
                memory.close()

                self._driver._log.effect(effect = 'element shoot')

            else:
                memory = StringIO.StringIO(buf = '')
##                memory.write(s = self._driver._driver.get_screenshot_as_png())
                memory.write(s = self._driver._driver.get_screenshot_as_base64().decode(encoding = 'base64_codec', errors = 'strict'))
                memory.seek(pos = 0, mode = 0)
                full_image = PIL.Image.open(fp = memory, mode = 'r')

                self._driver._driver._switch_to.default_content()
                left = left
                top = 0 - top
                right = right
                bottom = 0 - bottom
                for i in self._driver._frame:
                    left += i.location['x']
                    top += i.location['y']
                    right += i.location['x']
                    bottom += i.location['y']
                    self._driver._driver._switch_to.frame(frame_reference = i)

                left += self._element.location['x']
                top += self._element.location['y']
                right += self._element.location['x'] + self._element.size['width']
                bottom += self._element.location['y'] + self._element.size['height']

                element_image = full_image.crop(box = (left, top, right, bottom))
                element_image.save(fp = (re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0] + re.findall(pattern = '^\s*(.+[/\\\])\s*(.*[.]png)\s*$', string = path, flags = re.IGNORECASE)[0][1]).decode(encoding = 'utf_8', errors = 'strict'), format = 'PNG')
                memory.close()

                self._driver._log.effect(effect = 'element shoot')
        except Exception as e:
            self._driver._log.error(error = e)
            raise e







class Attribute(object):
    def __init__(self, key, value, strict = True):
        if (not (type(key) is str) and (len(key.strip()) > 0)) or ((type(value) is str) and (len(value) == 0)):
            raise Exception('pass key/value as str(len>0)!')

        self._key = key
        self._value = "'" + value + "'"
        self._strict = strict







class Text(object):
    def __init__(self, text, strict = True):
        if not ((type(text) is str) and len(text) > 0):
            raise Exception('pass text as str(len>0)!')

        self._text = "'" + text + "'"
        self._strict = strict







class Log(object):
    def __init__(self, path, driver):
        if not ((type(path) is str) and (len(re.findall(pattern = '^\s*(.+[/\\\])(.*)\s*$', string = path, flags = 0)) == 1) and (len(re.findall(pattern = '^\s*(.+[/\\\])(.*)\s*$', string = path, flags = 0)[0]) == 2) and (len(re.findall(pattern = '^\s*(.+[/\\\])\s*(.*)\s*$', string = path, flags = 0)[0][1]) > 0) and (isinstance(driver, Driver))):
            raise Exception('pass path/driver as str(log_path)/Driver()!')

        if not os.path.exists(path = re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0].decode(encoding = 'utf_8', errors = 'strict')):
            os.makedirs(name = re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0].decode(encoding = 'utf_8', errors = 'strict'), mode = 0777)

        self._log = open(name = (re.findall(pattern = '^\s*(.+[/\\\])(.*)\s*$', string = path, flags = 0)[0][0] + re.findall(pattern = '^\s*(.+[/\\\])\s*(.*)\s*$', string = path, flags = 0)[0][1]).decode(encoding = 'utf_8', errors = 'strict'), mode = 'w+', buffering = 0)
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
        PIL.ImageGrab.grab(bbox = None).save(fp = (self._log.name + '.' + str(self._count).zfill(7) + '.png').encode(encoding = 'utf_8', errors = 'strict'), format = 'PNG')

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
        self._log.write('DEF SCREENSHOT:\t' + self._log.name + '.' + str(self._count).zfill(7) + '.png')
        self._log.write('\n' * 2)
        self._count += 1

##        self._log.close()