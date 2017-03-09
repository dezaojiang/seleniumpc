#-*- coding: utf-8 -*-
#!/usr/bin/env python

from seleniumpc import Driver, Attribute, Text, Key
import time

def main():
    driver = Driver()

    #chrome
    driver.name = 'chrome'
    driver.executor = 'D:/seleniumpc/driver/chromedriver.exe'
    driver.browser = 'C:/Program Files (x86)/GoogleChromePortable/App/Google Chrome/chrome.exe'
##    driver.proxy = '127.0.0.1:8787'
    driver.option = '--incognito'
    driver.option = '--allow-outdated-plugins'
    driver.option = '--ignore-certificate-errors'
    driver.log = 'D:/seleniumpc/test/日志.log'
    driver.delay = 1.7

    #firefox
##    driver.name = 'ff'
##    driver.browser = 'C:/Program Files (x86)/Mozilla Firefox/firefox.exe'
####    driver.proxy = '127.0.0.1:8787'
##    driver.option = '-private-window'
##    driver.log = 'D:/seleniumpc/test/日志.log'
##    driver.delay = 1.7

    #ie
##    driver.name = 'ie'
##    driver.executor = 'D:/seleniumpc/driver/IEDriverServer.exe'
####    driver.proxy = '127.0.0.1:8787'
##    driver.option = '-private'
##    driver.log = 'D:/seleniumpc/test/日志.log'
##    driver.delay = 1.7

    #launch driver
    driver.launch()

    #basic navigation
    driver.open('http://www.w3school.com.cn/tiy/t.asp?f=html_a_target_framename')
    driver.switchframe(driver.find('iframe', Attribute('name', 'i'))[0])
    driver.back()
    time.sleep(1.7)
    driver.forward()
    time.sleep(1.7)
    driver.refresh()
    time.sleep(1.7)
    driver.find('*', [], Text('Preface'))[0].click()
    driver.close()
    driver.switchframe(driver.find('iframe', Attribute('name', 'i'))[0])
    driver.find('*', [], Text('Chapter 1'))[0].click()
    driver.close()
    driver.switchframe(driver.find('iframe', Attribute('name', 'i'))[0])
    driver.find('*', [], Text('Chapter 2'))[0].click()
    driver.close()
    driver.switchframe(driver.find('iframe', Attribute('name', 'i'))[0])
    driver.find('*', [], Text('Chapter 3'))[0].click()
    driver.close()
    time.sleep(7)

    #type input
    driver.open('http://www.w3school.com.cn/tiy/t.asp?f=html_form_submit')
    driver.switchframe(driver.find('iframe', Attribute('name', 'i'))[0])
    driver.find(attribute = Attribute('name', 'firstname'))[0].click()
    driver.modifierdown(Key.CONTROL)
    driver.type('a')
    driver.modifierup(Key.CONTROL)
    driver.type(Key.BACKSPACE)
    driver.type(['abc', 123, Key.ADD])
    driver.find(attribute = Attribute('name', 'lastname'))[0].clear()
    driver.find(attribute = Attribute('name', 'lastname'))[0].send('输入汉字\n')
    driver.switchout()
    time.sleep(7)

    #upload file, MAY BE INCOMPATIBLE WITH IE 8
    driver.open('https://encodable.com/uploaddemo/')
    if driver.name == 'ff':
        driver.find(attribute = Attribute('id', 'uploadname1'))[0].click(7) #on ff 21 click on the ement itself could not trigger upload, so add a little offset
    else:
        driver.find(attribute = Attribute('id', 'uploadname1'))[0].click()
    driver.upload('D:/seleniumpc/test/上传.jpg')
    time.sleep(7)

    #download file
    driver.open('https://cn.bing.com')
    driver.find(attribute = Attribute('title', '输入搜索词'))[0].send('下载')
    driver.find(attribute = Attribute('title', '搜索'))[0].click()
    driver.find(text = Text('点击下载'))[3].click()
    driver.download('D:/seleniumpc/test/下载.exe')
    time.sleep(7)

    #alert dialog
    driver.open('http://www.w3school.com.cn/tiy/loadtext.asp?f=hdom_prompt')
    driver.find('input', Attribute('value', '显示一个提示框'))[0].click()
    print driver.alert(False, '输入汉字')
    driver.find('input', Attribute('value', '显示一个提示框'))[0].click()
    print driver.alert(True, '输入汉字')
    time.sleep(7)

    #drag and drop
    driver.open('http://jqueryui.com/resources/demos/droppable/photo-manager.html')
    driver.find(attribute = Attribute('alt', 'The peaks of High Tatras'))[0].mousedown()
    driver.find(attribute = Attribute('id', 'trash'))[0].mouseup()
    driver.find(attribute = Attribute('alt', 'The chalet at the Green mountain lake'))[0].mousedown()
    driver.find(attribute = Attribute('id', 'trash'))[0].mouseup()
    driver.find(attribute = Attribute('alt', 'Planning the ascent'))[0].mousedown()
    driver.find(attribute = Attribute('id', 'trash'))[0].mouseup()
    driver.find(attribute = Attribute('alt', 'On top of Kozi kopka'))[0].mousedown()
    driver.find(attribute = Attribute('id', 'trash'))[0].mouseup()
    driver.find(attribute = Attribute('alt', 'The peaks of High Tatras'))[0].mousedown()
    driver.find(attribute = Attribute('id', 'trash'))[0].mouseup(-777, 17)
    driver.find(attribute = Attribute('alt', 'The chalet at the Green mountain lake'))[0].mousedown()
    driver.find(attribute = Attribute('id', 'trash'))[0].mouseup(-777, 17)
    driver.find(attribute = Attribute('alt', 'Planning the ascent'))[0].mousedown()
    driver.find(attribute = Attribute('id', 'trash'))[0].mouseup(-777, 17)
    driver.find(attribute = Attribute('alt', 'On top of Kozi kopka'))[0].mousedown()
    driver.find(attribute = Attribute('id', 'trash'))[0].mouseup(-777, 17)
    time.sleep(7)

    #select menu
    driver.open('https://contactform7.com/checkboxes-radio-buttons-and-menus/')
    driver.find(attribute = Attribute('class', 'wpcf7-form-control wpcf7-submit'))[0].hover() #scroll target elements in sight
    driver.find(attribute = Attribute('value', 'China'))[0].click()
    driver.find(attribute = Attribute('value', 'India'))[0].click()
    driver.find(attribute = Attribute('value', 'San Marino'))[0].click()
    print driver.find(attribute = Attribute('value', 'China'))[0].isselect()
    print driver.find(attribute = Attribute('value', 'India'))[0].isselect()
    print driver.find(attribute = Attribute('value', 'San Marino'))[0].isselect()
    driver.find(attribute = Attribute('value', 'China'))[0].click()
    driver.find(attribute = Attribute('value', 'India'))[0].click()
    driver.find(attribute = Attribute('value', 'San Marino'))[0].click()
    print driver.find(attribute = Attribute('value', 'China'))[0].isselect()
    print driver.find(attribute = Attribute('value', 'India'))[0].isselect()
    print driver.find(attribute = Attribute('value', 'San Marino'))[0].isselect()
    driver.find(attribute = Attribute('value', 'Football'))[0].click()
    driver.find(attribute = Attribute('value', 'Tennis'))[0].click()
    driver.find(attribute = Attribute('value', 'Pole-vault'))[0].click()
    print driver.find(attribute = Attribute('value', 'Football'))[0].isselect()
    print driver.find(attribute = Attribute('value', 'Tennis'))[0].isselect()
    print driver.find(attribute = Attribute('value', 'Pole-vault'))[0].isselect()
    driver.find(attribute = Attribute('class', 'wpcf7-form-control wpcf7-select wpcf7-validates-as-required'))[0].click()
    if driver.name == 'ff':
        driver.find(attribute = Attribute('class', 'wpcf7-form-control wpcf7-select wpcf7-validates-as-required'))[0].find(text = Text('Opera'))[0].click(1)
    else:
        driver.find(attribute = Attribute('class', 'wpcf7-form-control wpcf7-select wpcf7-validates-as-required'))[0].find(text = Text('Opera'))[0].click()
    driver.modifierdown(Key.CONTROL)
    driver.find(attribute = Attribute('class', 'wpcf7-form-control wpcf7-select'))[0].find(text = Text('fsdfs'))[0].click()
    driver.find(attribute = Attribute('class', 'wpcf7-form-control wpcf7-select'))[0].find(text = Text('klgjfk'))[0].click()
    driver.find(attribute = Attribute('class', 'wpcf7-form-control wpcf7-select'))[0].find(text = Text('vdrie'))[0].click()
    driver.modifierup(Key.CONTROL)
    time.sleep(7)

    #quit driver
    driver.quit()

if __name__ == '__main__':
    main()