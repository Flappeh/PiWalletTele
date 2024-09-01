from appium import webdriver
from typing import Dict, Any
from appium.options.common.base import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webelement import WebElement
from .environment import ANDROID_SERVER_URL
from .utils import get_logger

logger = get_logger()

capabilities: Dict[str, Any] = {
    "platformName": "Android",
    "automationName": "uiautomator2",
    # "appPackage":"pi.browser", 
    # "appActivity": "com.pinetwork.MainActivity",
    "deviceName": "Android",
    "language": "en"
}

class AndroidBot():
    def __init__(self) -> None:
        self.driver: webdriver.Remote = webdriver.Remote(ANDROID_SERVER_URL, options=AppiumOptions().load_capabilities(capabilities))
        self.current_page = ""
    def click_update(self) -> None:
        try:
            updateParent = self.driver.find_element(by=AppiumBy.XPATH, value='//android.app.Dialog')
            children = updateParent.find_elements(by=AppiumBy.CLASS_NAME, value="android.widget.Button")
            children[0].click()
        except:
            pass
    def click_notif(self) -> None:
        try:
            notif = self.driver.find_element(by=AppiumBy.XPATH, value='//*[@text="Not Now"]')
            notif.click()
        except:
            pass
    def verify_wallet(self) -> None:
        try:
            self.driver.find_element(by=AppiumBy.XPATH, value='//*[@text="Not searchable"]').click()
            self.driver.find_element(by=AppiumBy.XPATH, value='//*[@text="Continue "]').click()
        except:
            pass
        
    def check_is_loading(self):
        loading_screen = self.driver.find_element(by=AppiumBy.XPATH, value='//*[@text="Loading..."]')
        if loading_screen:
            self.click_notif()
            self.click_update()
            return True
        return False

    def check_current_page(self):
        CURRENT_PAGE_SOURCE = self.driver.page_source
        if "Welcome to the Pi Browser" in CURRENT_PAGE_SOURCE:
            return "home"
        if "Loading" in CURRENT_PAGE_SOURCE:
            return "loading"
        if "Unlock Pi Wallet" in CURRENT_PAGE_SOURCE or "Unlock App Wallet" in CURRENT_PAGE_SOURCE:
            return "wallet_home"
        if "Turn on notifications!" in CURRENT_PAGE_SOURCE:
            self.click_notif()
            return "notification"
        if "Update your app" in CURRENT_PAGE_SOURCE:
            self.click_update()
            return "update"
        if "Others can search for your" in CURRENT_PAGE_SOURCE:
            self.verify_wallet()
            return "verification"
        if "History" in CURRENT_PAGE_SOURCE and "Migrations" in CURRENT_PAGE_SOURCE and "Wallet" in CURRENT_PAGE_SOURCE:
            return "wallet_page"
        if "Translation loading ..." in CURRENT_PAGE_SOURCE:
            self.click_update()
            return "update"
        print(CURRENT_PAGE_SOURCE)
        return ""

    def check_current_wallet_balance(self):
        current_page = self.check_current_page()
        while current_page != "wallet_page":
            pass
            # if current_page == "notification":
            #     self.click_notif()
            # if current_page == "update":
            #     self.click_update()
            # if current_page == "verification":
            #     self.verify_wallet()
            current_page = self.check_current_page()
        anchor = self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, " Pi")]')
        return anchor.text

    def reload_wallet_page(self):
        try:
            self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "Send / Receive")]').click()
        except:
            logger.error("Error clickig send receive button on reloading")
        try:
            self.driver.find_element(by=AppiumBy.XPATH, value='//*[@resource-id="address-bar-back-button"]').click()
        except:
            logger.error("Error clicking back button on reloading wallet page")
            raise
        while self.check_current_page() != "wallet_home":
            logger.info("Not in wallet home")
            self.click_notif()
            pass
        
    def open_wallet_sub_page(self):
        self.driver.find_element(by=AppiumBy.XPATH, value='//*[@text="Wallet logo "]').click()
        while self.check_current_page() != "wallet_home":
            self.click_notif()
            pass
            
    def navigate_to_wallet_home(self):
        current_page = self.check_current_page()
        while current_page != "wallet_home": 
            current_page = self.check_current_page()
            match current_page:
                case "wallet_home":
                    break
                case "wallet_page":
                    self.reload_wallet_page()
                case "home":
                    self.open_wallet_sub_page()
                case "loading":
                    print("Loading")
                case "notification":
                    print("Notification Found")
                case "update":
                    print("Update notification found")
                case _:
                    print("Undefined")
                
    def login_to_wallet(self, pwd:str)-> bool:
        try:
            login_box = self.driver.find_element(by=AppiumBy.CLASS_NAME, value="android.widget.EditText")
        except Exception as e:
            logger.error("Error inserting phrase to wallet box")
        
        login_box.clear()
        login_box.send_keys(pwd)
        try:
            self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "Unlock With")]').click()
        except Exception as e:
            logger.error("Error finding login button")
        try:
            self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "Unlock with")]').click()
        except Exception as e:
            logger.error("Error finding login button")
        
        
        

    def open_wallet_from_passphrase(self, pwd: str):
        logger.info(f"Received new request for phrase: {pwd}")
        if self.check_current_page() != "wallet_home":
            self.navigate_to_wallet_home()
            
        result = False
        while result != True:
            result = self.login_to_wallet(pwd)
            if "Invalid" in self.driver.page_source:
                logger.error("Invalid passphrase given")
                result = "Invalid"
                break
        if result == "Invalid":
            return "Invalid passphrase given"
        value = self.check_current_wallet_balance()
        return value
    
    def __del__(self):
        logger.info("Finished running script")
        self.driver.quit()
    
    


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