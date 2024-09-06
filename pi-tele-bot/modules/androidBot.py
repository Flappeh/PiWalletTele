from appium import webdriver
from typing import Dict, Any
from appium.options.common.base import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webelement import WebElement
from .environment import ANDROID_SERVER_URL
from .utils import get_logger, store_phrase
from time import sleep

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
            self.driver.find_element(by=AppiumBy.XPATH, value="//*[contains(@text,'Continue')]").click()
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
        Page_Source = self.driver.page_source
        if "Welcome to the Pi Browser" in Page_Source:
            return "home"
        if "Loading" in Page_Source:
            return "loading"
        if "Unlock Pi Wallet" in Page_Source:
            return "wallet_home"
        if "Turn on notifications!" in Page_Source:
            self.click_notif()
            return "notification"
        if "Update your app" in Page_Source:
            self.click_update()
            return "update"
        if "Others have to manually type in your wallet address" in Page_Source:
            self.verify_wallet()
            return "verification"
        if "Available Balance" in Page_Source:
            return "wallet_page"
        if "Translation loading ..." in Page_Source:
            self.click_update()
            return "update"
        return ""

    def check_current_wallet_balance(self):
        current_page = self.check_current_page()
        while current_page != "wallet_page":
            if current_page == "notification":
                self.click_notif()
            if current_page == "update":
                self.click_update()
            if current_page == "verification":
                self.verify_wallet()
            current_page = self.check_current_page()
        print("here")
        try:
            print("getting Balance")
            balance = self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text,"Available Bal")]/following-sibling::android.widget.TextView[2]')
            return balance.text
        except Exception as e:
            print("Erropr")
            logger.error(f"Error checking curent balance, error : {e}")
        print("Done")
        
    def reload_wallet_page(self):
        try:
            self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "Send / Receive")]').click()
        except:
            logger.error("Error clicking send receive button on reloading")
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
        try:
            self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "Wallet logo")]').click()
        except:
            logger.error("Error going to sub page")
        while self.check_current_page() != "wallet_home":
            self.click_notif()
            pass
            
    def navigate_to_wallet_home(self):
        current_page = self.check_current_page()
        while current_page != "wallet_home": 
            print(f"Current page before match: {current_page}")  # Debugging line
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
            current_page = self.check_current_page()
            print(f"Current page after match: {current_page}")  # Debugging line
                
    def login_to_wallet(self, pwd:str)-> str:
        try:
            login_box = self.driver.find_element(by=AppiumBy.CLASS_NAME, value="android.widget.EditText")
        except Exception as e:
            logger.error("Error inserting phrase to wallet box: %s", e)
        login_box.clear()
        login_box.send_keys(pwd)
        try:
            self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "Unlock With")]').click()
        except Exception as e:
            logger.error("Error finding login button")
        page = self.driver.page_source
        if "An error" in page:
            return "error"
        elif "Invalid" in page:
            return "invalid"
        elif ("Loading" in page) or ("Availabile" in page):
            return "ok"
        else:
            return "exception"
    def sign_out_user(self) -> bool:
        try:
            self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "code to share")]')
            return True
        except:
            print("Error finding user code to share")
        try:
            self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "Sign Out")]').click()
            sleep(0.4)
            self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "Sign Out")]').click()
            return True
        except:
            print("Error signing out in")
            return False
        
    def change_user(self) -> None:
        self.driver.activate_app('com.blockchainvault/com.pinetwork.MainActivity')
        self.sign_out_user()
        if "Core Team" not in self.driver.page_source:
            sleep(1)
            self.driver.tap([(30,50)])
            sleep(1)
        self.driver.flick(100,500,100,200)
        sleep(1)
        try:
            self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "Profile")]').click()
        except:
            logger.error("Error changing user")
            print("Error changing user")
        self.sign_out_user()
        
    def open_wallet_from_passphrase(self, pwd: str):
        self.driver.activate_app('pi.browser/com.pinetwork.MainActivity')
        logger.info(f"Received new request for phrase: {pwd}")
        if self.check_current_page() != "wallet_home":
            print("Not in wallet home")
            self.navigate_to_wallet_home()
        
        result = self.login_to_wallet(pwd)
        # while result != "ok":
        #     result = self.login_to_wallet(pwd)
            
        #     if result == "invalid":
        #         logger.error("Invalid passphrase given")
        #         result = "Invalid"
        #         break
        #     elif result == "error":
        #         logger.error("Error occured when unlocking with passphrase. Need to use other account")
        #         raise
        #     elif result == "ok":
        #         break
        if result == "exception":
            while result == "exception":
                result = self.login_to_wallet(pwd)
                print(result)
        if result == "error":
            self.change_user()
            return "Error butuh ganti ke user lain"
        if result == "invalid":
            return "Invalid passphrase given"
        value = self.check_current_wallet_balance()
        store_phrase(pwd, value)
        return value
    
    def __del__(self):
        logger.info("Finished running script")
        self.driver.quit()
    
    

