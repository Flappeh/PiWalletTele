from appium import webdriver
from typing import Dict, Any
from appium.options.common.base import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webelement import WebElement
from .environment import ANDROID_SERVER_URL
CURRENT_24_PHRASE=""
CURRENT_PAGE_SOURCE=""

capabilities: Dict[str, Any] = {
    "platformName": "Android",
    "automationName": "uiautomator2",
    # "appPackage":"pi.browser", 
    # "appActivity": "com.pinetwork.MainActivity",
    "deviceName": "Android",
    "language": "en"
}

# appium_server_url = "http://localhost:4724"
appium_server_url = ANDROID_SERVER_URL

driver = webdriver.Remote(appium_server_url, options=AppiumOptions().load_capabilities(capabilities))


def click_update():
    try:
        updateParent = driver.find_element(by=AppiumBy.XPATH, value='//android.app.Dialog')
        children = updateParent.find_elements(by=AppiumBy.CLASS_NAME, value="android.widget.Button")
        print(children)
        children[0].click()
    except:
        print("error")
        pass

def click_notif():
    try:
        notif = driver.find_element(by=AppiumBy.XPATH, value='//*[@text="Not Now"]')
        notif.click()
    except:
        pass
    

def check_is_loading():
    loading_screen = driver.find_element(by=AppiumBy.XPATH, value='//*[@text="Loading..."]')
    if loading_screen:
        click_notif()
        return True
    return False

def check_current_page():
    CURRENT_PAGE_SOURCE = driver.page_source
    if "Welcome to the Pi Browser" in CURRENT_PAGE_SOURCE:
        return "home"
    if "Loading" in CURRENT_PAGE_SOURCE:
        return "loading"
    if "Unlock Pi Wallet" in CURRENT_PAGE_SOURCE:
        return "wallet_home"
    if "Turn on notifications!" in CURRENT_PAGE_SOURCE:
        return "notification"
    if "Update your app" in CURRENT_PAGE_SOURCE:
        return "update"
    if "History" in CURRENT_PAGE_SOURCE and "Migrations" in CURRENT_PAGE_SOURCE and "Wallet" in CURRENT_PAGE_SOURCE:
        return "wallet_page"
    if "Translation loading ..." in CURRENT_PAGE_SOURCE:
        return "update"
    return ""

def check_current_wallet_balance():
    while check_current_page() != "wallet_page":
        click_notif()
        pass
    anchor = driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, " Pi")]')
    print(anchor.text)
    return anchor.text

def reload_wallet_page():
    back = driver.find_element(by=AppiumBy.XPATH, value='//*[@resource-id="address-bar-back-button"]')
    back.click()
    while check_current_page() != "wallet_home":
        print("not wallet home")
        click_notif()
        pass
    
def open_wallet_sub_page():
        wallet = driver.find_element(by=AppiumBy.XPATH, value='//*[@text="Wallet logo "]')
        wallet.click()
        while check_current_page() != "wallet_home":
            print("not wallet home")
            click_notif()
            pass
        
def navigate_to_wallet_home():
    current_page = check_current_page()
    while current_page != "wallet_home": 
        current_page = check_current_page()
        print(current_page)
        match current_page:
            case "wallet_home":
                break
            case "wallet_page":
                reload_wallet_page()
            case "home":
                open_wallet_sub_page()
            case "loading":
                print("Loading")
            case "notification":
                print("Notification Found")
                click_notif()
            case "update":
                print("Update notification found")
                click_update()
            case _:
                print("Undefined")
            
    

def open_wallet_from_passphrase(pwd: str):
    print(check_current_page())
    if check_current_page() != "wallet_home":
        print("Not in wallet page")
        navigate_to_wallet_home()
    try:
        login_box = driver.find_element(by=AppiumBy.CLASS_NAME, value="android.widget.EditText")
    except Exception as e:
        print("text")
        print(e)
    try:
        button_login = driver.find_element(by=AppiumBy.XPATH, value='//*[@text="Unlock With Passphrase "]')
    except Exception as e:
        print("login")
        print(e)
    login_box.clear()
    login_box.send_keys(pwd)
    button_login.click()
    if "Invalid Passphrase" in driver.page_source:
        print("Invalid passphase")
        return "Invalid Pass"
    check_current_wallet_balance()
    driver.quit()
    
    
    


# class AndroidRunner():
#     def __init__(self) -> None:
#         print("Initializing driver")
#         try:
#             self.driver =  webdriver.Remote(appium_server_url, options=AppiumOptions().load_capabilities(capabilities))
#         except Exception as e:
#             print(e)
#     def click_update(self):
#         try:
#             update = self.driver.find_element(by=AppiumBy.XPATH, value='//*[@resource-id="mui-3"]')
#             update.click()
#         except:
#             print("error")
#             pass

#     def click_notif(self):
#         try:
#             notif = self.driver.find_element(by=AppiumBy.XPATH, value='//*[@text="Not Now"]')
#             notif.click()
#         except:
#             pass
        

#     def check_is_loading(self):
#         loading_screen = self.driver.find_element(by=AppiumBy.XPATH, value='//*[@text="Loading..."]')
#         if loading_screen:
#             self.click_notif()
#             return True
#         return False

#     def check_current_page(self):
#         CURRENT_PAGE_SOURCE = self.driver.page_source
#         if "Welcome to the Pi Browser" in CURRENT_PAGE_SOURCE:
#             return "home"
#         if "Loading" in CURRENT_PAGE_SOURCE:
#             return "loading"
#         if "Unlock Pi Wallet" in CURRENT_PAGE_SOURCE:
#             return "wallet_home"
#         if "Turn on notifications!" in CURRENT_PAGE_SOURCE:
#             return "notification"
#         if "Update your app" in CURRENT_PAGE_SOURCE:
#             return "update"
#         if "History" in CURRENT_PAGE_SOURCE and "Migrations" in CURRENT_PAGE_SOURCE and "Wallet" in CURRENT_PAGE_SOURCE:
#             return "wallet_page"

#     def check_current_wallet_balance(self):
#         while self.check_current_page() != "wallet_page":
#             self.click_notif()
#             pass
#         anchor = self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, " Pi")]')
#         print(anchor.text)
#         return anchor.text

#     def reload_wallet_page(self):
#         back = self.driver.find_element(by=AppiumBy.XPATH, value='//*[@resource-id="address-bar-back-button"]')
#         back.click()
#         while self.check_current_page() != "wallet_home":
#             print("not wallet home")
#             self.click_notif()
#             pass

#     def open_wallet_sub_page(self):
#         wallet = self.driver.find_element(by=AppiumBy.XPATH, value='//*[@text="Wallet logo "]')
#         wallet.click()
#         while self.check_current_page() != "wallet_home":
#             print("not wallet home")
#             self.click_notif()
#             pass
        

#     def navigate_to_wallet_home(self):
#         while self.check_current_page() != "wallet_home":    
#             match self.check_current_page():
#                 case "wallet_home":
#                     break
#                 case "wallet_page":
#                     self.reload_wallet_page()
#                 case "home":
#                     self.open_wallet_sub_page()
#                 case "loading":
#                     print("Loading")
#                 case "notification":
#                     print("Notification Found")
#                     self.click_notif()
#                 case "update":
#                     print("Update notification found")
#                     self.click_update()
#                 case _:
#                     print("Undefined")
#                     return
                
        

#     def open_wallet_from_passphrase(self, pwd: str):
#         if self.check_current_page() != "wallet_home":
#             print("Not in wallet page")
#             self.navigate_to_wallet_home()
#         try:
#             login_box = self.driver.find_element(by=AppiumBy.XPATH, value="//android.widget.EditText")
#             button_login = self.driver.find_element(by=AppiumBy.XPATH, value='//*[@text="Unlock With Passphrase"]')
#         except:
#             print("Not in wallet page")
#         login_box.clear()
#         login_box.send_keys(pwd)
#         button_login.click()
#         if "Invalid Passphrase" in self.driver.page_source:
#             print("Invalid passphase")
#             return "Invalid Pass"
#         self.check_current_wallet_balance()
#         self.driver.quit()    