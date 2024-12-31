from appium import webdriver
from typing import Dict, Any
from appium.options.common.base import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webelement import WebElement
from .environment import ANDROID_SERVER_URL, TIMEOUT_LIMIT, WALLET_DEST, TRY_SEND_DURATION
from math import floor
from .utils import get_logger, store_phrase, get_wallet_account, PiAccount, delete_wallet_account
from .exceptions import PiAccountError
from time import sleep,time
from multiprocessing import Process, Queue
from datetime import datetime

TIMEOUT = TIMEOUT_LIMIT
logger = get_logger(__name__)
running_bot = []

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
        self.driver.update_settings({"waitForIdleTimeout": 0})
        self.current_page = ""
        self.age = time()
        self.width = self.driver.get_window_size()["width"]
        self.height = self.driver.get_window_size()["height"]
        
    def click_update(self) -> None:
        try:
            logger.debug("Clicking Update")
            updateParent = self.driver.find_element(by=AppiumBy.XPATH, value='//android.app.Dialog')
            children = updateParent.find_elements(by=AppiumBy.CLASS_NAME, value="android.widget.Button")
            children[0].click()
        except:
            logger.error("Unable to click Update")
            pass
    def click_notif(self) -> None:
        try:
            logger.debug("Clicking notification")
            notif = self.driver.find_element(by=AppiumBy.XPATH, value='//*[@text="Not Now"]')
            notif.click()
        except:
            pass
    def click_phone_notif(self) -> None:
        try:
            logger.debug("Clicking phone notification")
            notif = self.driver.find_element(by=AppiumBy.XPATH, value='//android.widget.Button[@resource-id="com.android.permissioncontroller:id/permission_deny_button"]')
            notif.click()
        except:
            pass
    def verify_wallet(self) -> bool:
        try:
            logger.debug("Verifying wallet ownership")
            self.driver.find_element(by=AppiumBy.XPATH, value="//android.widget.Button[contains(@text,'Continue')]").click()
            sleep(1)
            return True
        except:
            logger.warning("Unable to verify")
            return False
    def check_is_loading(self):
        loading_screen = self.driver.find_element(by=AppiumBy.XPATH, value='//*[@text="Loading..."]')
        if loading_screen:
            self.click_notif()
            self.click_update()
            return True
        return False

    def click_back_button(self):
        try:
            logger.debug("Clicking back button")
            self.driver.find_element(by=AppiumBy.XPATH, value='//*[@resource-id="address-bar-back-button"]').click()
        except:
            logger.error("Error clicking back button")

    def click_back_button_login(self):
        try:
            logger.debug("Clicking back button")
            self.driver.find_element(by=AppiumBy.XPATH, value='//android.widget.Button[@text="Open drawer"]').click()
        except:
            logger.error("Error clicking back button")
    
    def click_remind_button(self):
        try:
            logger.debug("Clicking remind later")
            self.driver.tap([(260,60)])
        except:
            logger.error("Error clicking remind later")
    def click_try_mining(self):
        try:
            logger.debug("Found start mining popup")
            self.driver.tap()
        except:
            logger.error("Unable to click try mining")
            
    def check_current_page(self):
        Page_Source = self.driver.page_source
        if "Welcome to the Pi Browser" in Page_Source:
            self.current_page = "home"
            return "home"
        if "Loading" in Page_Source:
            self.current_page = "loading"
            return "loading"
        if "Unlock Pi Wallet" in Page_Source:
            self.current_page = "wallet_home"
            return "wallet_home"
        if "Turn on notifications!" in Page_Source:
            self.click_notif()
            self.current_page = "notification"
            return "notification"
        if "This is your identity on the Pi" in Page_Source:
            self.verify_wallet()
            self.current_page = "verification"
            return "verification"
        if "Available Balance" in Page_Source:
            self.current_page = "wallet_page"
            return "wallet_page"
        if "Transaction Details" in Page_Source:
            self.current_page = "transaction"
            return "transaction"
        if "Allow Pi Browser to send" in Page_Source:
            self.click_phone_notif()
            self.current_page = "phone_notif"
            return "phone_notif"
        if "Update your app" in Page_Source or "Translation loading ..." in Page_Source:
            self.click_update()
            self.current_page = "update"
            return "update"
        if "blockexplorer" in Page_Source:
            self.current_page = "blockexplorer"
            return "blockexplorer"
        if "You are about to send" in Page_Source or "Memo (optional)" in Page_Source or "Manually Add Wallet Address" in Page_Source or "sum of amount and transaction" in Page_Source:
            self.current_page = "transfer_page"
            return "transfer_page"
        if "Start Mining Pi Effort" in Page_Source or "try mining now" in self.driver.page_source.lower():
            self.current_page = "try_mining"
            return "try_mining"
        if "System UI isn't" in Page_Source:
            self.current_page = "systemerr"
            return "systemerr"
        
        return ""

    def check_current_wallet_balance(self):
        logger.debug("Checking current wallet balance")
        current_page = self.check_current_page()
        while current_page != "wallet_page":
            if current_page == "notification":
                self.click_notif()
            if current_page == "update":
                self.click_update()
            if current_page == "verification":
                self.verify_wallet()
            if current_page == "try_mining":
                self.click_try_mining()
            current_page = self.check_current_page()
        try:
            logger.debug("Trying to get available balance")
            balance = self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text," Pi")][1]')
            return balance.text
        except Exception as e:
            logger.error(f"Error checking curent balance, error : {e}")
        
    def reload_wallet_page(self):
        try:
            logger.debug("Finding send/receive element")
            self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "Send / Receive")]').click()
        except:
            logger.error("Error clicking send receive button on reloading")
        try:
            logger.debug("Finding back button element")
            self.driver.find_element(by=AppiumBy.XPATH, value='//*[@resource-id="address-bar-back-button"]').click()
        except:
            logger.error("Error clicking back button on reloading wallet page")
            raise
        while self.check_current_page() != "wallet_home":
            logger.info("Not in wallet home")
            self.click_notif()
            if self.check_current_page() == "home":
                break
            pass
    
    # From home page open "Wallet" Page
    def open_wallet_sub_page(self):
        while self.check_current_page() != "wallet_home":
            if self.check_current_page() == "home":
                try:
                    logger.debug("Opening wallet sub page")
                    self.driver.find_element(by=AppiumBy.ANDROID_UIAUTOMATOR, value='new UiSelector().text("Wallet logo")').click()
                except:
                    logger.error("Error going to sub page")
            self.click_notif()
            pass
    def reset_system_app(self):
        try:
            self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "Close app")]').click()
            sleep(3)
            self.driver.activate_app('pi.browser/com.pinetwork.MainActivity')
        except:
            logger.error("Error resetting system UI after error")
    def navigate_to_wallet_home(self):
        current_page = self.check_current_page()
        tries = 0
        while current_page != "wallet_home": 
            logger.debug(f"Current page before match: {current_page}")  # Debugging line
            match current_page:
                case "wallet_home":
                    break
                case "wallet_page":
                    self.reload_wallet_page()
                case "home":
                    self.open_wallet_sub_page()
                case "transaction":
                    self.tap_menu_burger()
                case "loading":
                    logger.debug("Still loading")
                case "notification":
                    logger.debug("Notification Found")
                case "update":
                    logger.debug("Update notification found")
                    if tries > 50:
                        self.tap_menu_burger()
                case "verification":
                    self.verify_wallet()
                case "blockexplorer":
                    self.tap_menu_burger()
                case "transfer_page":
                    self.tap_menu_burger()
                case "systemerr":
                    self.reset_system_app()
                case _:
                    logger.warning("Got undefined while navigating to wallet home")
                    sleep(1)
            tries += 1
            current_page = self.check_current_page()
            logger.debug(f"Current page after match: {current_page}")  # Debugging line
    
    def try_enter_wallet(self, pwd:str):
        try:
            logger.debug("Trying to enter wallet phrase")
            login_box = self.driver.find_element(by=AppiumBy.XPATH, value='//android.widget.EditText')
            sleep(0.4)
            login_box.clear()
            sleep(0.4)
            login_box.send_keys(pwd)
            self.driver.hide_keyboard()
            self.driver.find_element(by=AppiumBy.XPATH, value='//android.widget.Button[contains(@text, "Unlock With")]').click()
            return True
        except Exception as e:
            logger.error("Error entering wallet phrase")
            return False
    
    
    def enter_wallet_phrase(self, pwd:str)-> str:
        
        logger.debug("Received enter wallet phrase command")
        page = ""
        tries = 0
        check_page = 0
        while tries < 9:
            while self.check_current_page() != "wallet_home":
                if check_page == 20:
                    app = self.driver.current_package
                    self.driver.terminate_app(app)
                    sleep(1)
                    self.driver.activate_app(app)
                    sleep(1)
                    self.open_wallet_sub_page()
                sleep(1)
                if self.check_current_page() == "wallet_page":
                    break
                check_page += 1
            self.try_enter_wallet(pwd)
            page = self.driver.page_source
            if "Loading" in page:
                pass
            if "An error occurred" in page:
                return "error"
            if "Available Balance" in page:
                break
            if "This is your identity on the Pi Blockchain" in self.driver.page_source:
                if self.verify_wallet():
                    break
            if "Welcome to the Pi Browser" in self.driver.page_source:
                self.open_wallet_sub_page()
            if "Continue with phone number" in self.driver.page_source:
                break
            if "Register with phone number" in self.driver.page_source:
                break
            if "Enter your password" in self.driver.page_source:
                break
            tries +=1
        
        # if tries == 6:
        #     self.capture_screen()
        page = self.driver.page_source
        if "An error" in page:
            return "error"
        elif "Invalid" in page:
            return "invalid"
        elif "Available Balance" in page:
            return "ok"
        else:
            return "exception"
        
    def sign_out_user(self):
        logger.debug("Received sign out user command")
        result = False
        while result == False:
            if "Continue with phone number" in self.driver.page_source:
                result = True
                break
            if "Register with phone number" in self.driver.page_source:
                result = True
                break
            if "Enter your password" in self.driver.page_source:
                result = True
                break
            try:
                self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "Sign Out")]').click()
                sleep(0.4)
                self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "Sign Out")]').click()
                result = True
            except:
                logger.error("Unable to sign out")
                print(self.driver.current_activity)
                if "blockchainvault" not in self.driver.current_package:
                    self.driver.activate_app('com.blockchainvault/com.pinetwork.MainActivity')
                    sleep(3)
                result = False
                break
            sleep(0.3)
        return result
    
    
    def tap_menu_burger(self) -> None:
        try:
            menu_burger = (floor(self.width*0.09), floor(self.height*0.065))
            sleep(0.3)
            self.driver.tap([(menu_burger)])
        except:
            logger.error("Error tapping menu burger")
    
    def open_profile_page(self) -> None:
        try:
            if "Referral Team" not in self.driver.page_source and "Node" not in self.driver.page_source:
                self.tap_menu_burger()
                sleep(1)
            self.driver.flick(100,self.height*0.5,100,self.height*0.2)
            sleep(1)
            try:
                self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "Profile")]').click()
            except:
                logger.error("Error clicking profile button")
                self.driver.tap([(self.width*0.23,self.height*0.79)])
            sleep(1)
        except:
            logger.error("Error opening profile page")
            raise
    
    def start_logout_user(self) -> None:
        logger.debug("Opening profile page")
        self.open_profile_page()
        while self.sign_out_user() == False:
            self.open_profile_page()
            self.sign_out_user()
            
    def enter_keyboard_indonesia(self):
        self.driver.press_keycode(37)
        self.driver.press_keycode(42)
        self.driver.press_keycode(32)
        self.driver.press_keycode(43)
        self.driver.press_keycode(42)
    
    def insert_phone_number(self, account: PiAccount)-> bool:
        try:
            logger.debug("Inserting phone number")
            if "Continue with phone number" in self.driver.page_source:
                self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "with phone number")]').click()
                sleep(1)
            # while "Register with phone number" not in self.driver.page_source:
            #     print("Clicking register with phone number")
            #     self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "with phone number")]').click()
            #     sleep(0.2)
            input_boxes = self.driver.find_elements(by=AppiumBy.CLASS_NAME, value='android.widget.EditText')
            # country_box = self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "United States")]')
            country_box = input_boxes[0]
            # country_box.click()
            sleep(0.2)
            country_box.send_keys("indonesia")
            sleep(0.2)
            self.driver.find_element(by=AppiumBy.XPATH, value='//android.widget.TextView[@text="Phone number:"]').click()
            # self.enter_keyboard_indonesia()
            # self.driver.hide_keyboard()
            # self.driver.find_element(by=AppiumBy.XPATH, value='//android.widget.TextView[contains(@text, "Phone number")]').click()
            # phone_box = self.driver.find_element(by=AppiumBy.XPATH, value='//android.view.View[@resource-id="root"]/android.view.View/android.view.View/android.view.View/android.view.View[3]/android.widget.EditText')
            phone_box = input_boxes[1]
            phone_box.send_keys(account.phone)
            logger.debug("Clicking submit button")
            self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "Submit")]').click()
            sleep(0.5)
            return True
        except:
            logger.error("Error inserting phone number")
            return False
    
    def enter_phone_password(self, account: PiAccount) -> bool:
        try:
            while "Enter your password" in self.driver.page_source:
                logger.debug("Trying to insert phone number")
                sleep(1)
                password_box = self.driver.find_element(by=AppiumBy.XPATH, value='//android.widget.EditText')
                password_box.send_keys(account.password)
                sleep(1)
                self.driver.hide_keyboard()
                self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "Submit")]').click()
                sleep(0.5)
            return True
        except:
            logger.error("Error inserting phone number")
        
    def login_with_phone_number(self) -> bool:
        try:
            logger.debug("Getting new wallet account")
            account = get_wallet_account()
        except:
            logger.error("Error getting new wallet account")
            return False
        try:
            logger.debug("Logging in with new phone number")
            while "Register with phone number" not in self.driver.page_source:
                self.insert_phone_number(account)
                if "Enter your password" in self.driver.page_source:
                    break
            sleep(1)
            self.enter_phone_password(account)
            while "Enter your password" in self.driver.page_source:
                logger.warning("Still in password form")
                self.enter_phone_password(account)
                # self.driver.hide_keyboard()
                try:
                    if "Invalid phone number" in self.driver.page_source:
                        self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "Return to login")]').click()
                        delete_wallet_account(account)
                        return False
                except:
                    pass
            return True
        except Exception as e:
            logger.error(f"Error occured while logging in with phone number, {e}")
    
    def dismiss_contributor(self):
        try:
            self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "Dismiss")]').click()
        except:
            logger.error("Error clicking dismiss contributor")
    
    def navigate_to_pi_network(self) -> None:
        try:
            logger.debug("Navigation to pi network, clicking keep on mining")
            width = floor(self.width * 0.97)
            min_height = floor(self.height * 0.35)
            max_height = floor(self.height * 0.76)
            while "Keep on mining" not in self.driver.page_source:
                if "Mining Session Ends" in self.driver.page_source:
                    self.click_back_button_login()
                    break
                if "Continue with phone number" in self.driver.page_source:
                    break
                if "Register with phone number" in self.driver.page_source:
                    break
                if "Enter your password" in self.driver.page_source:
                    break
                if "You just unlocked" in self.driver.page_source:
                    self.dismiss_contributor()
                if "Referral" in self.driver.page_source or "Sharing text" in self.driver.page_source:
                    self.tap_menu_burger()
                    break
                if "Mine by confirming" in self.driver.page_source:
                    try:
                        sleep(1)
                        self.driver.find_element(by=AppiumBy.XPATH, value='//android.widget.Button[@text="Mine"]').click()
                        self.driver.tap([(self.width*0.46,self.height*0.89)])
                        sleep(0.3)
                        self.tap_menu_burger()
                        break
                    except:
                        logger.error("Error clicking mine by confirming")
                for i in range(min_height,max_height,60):
                    if "Mine by confirming" in self.driver.page_source:
                        break
                    if "Referral" in self.driver.page_source:
                        break
                    if "Mining Session Ends" in self.driver.page_source:
                        break
                    if "Sharing" in self.driver.page_source:
                        break
                    sleep(0.1)
                    self.driver.tap([(width, i)])
            self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text,"Not Now")]').click()
            self.driver.tap([(50,350)])
        except:
            logger.error(f"Error navigating to pi network")
    
    def login_to_browser(self) -> bool:
        try:
            logger.debug("Logging in to pi browser after signing in")
            if "Referral Team" not in self.driver.page_source and "Node" not in self.driver.page_source:
                sleep(0.3)
                self.tap_menu_burger()
            sleep(0.35)
            self.driver.flick(100,self.height*0.2,100,self.height*0.5)
            sleep(0.5)
            self.driver.find_element(by=AppiumBy.XPATH, value='//android.widget.Button[@text="Pi Browser"]').click()
            # sleep(0.5)
            # self.driver.flick(100,400,100,100)
            sleep(1)
            try:
                self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text,"Alternative Sign In")]').click()
            except:
                pass
            current_tries = 0
            result = False
            while current_tries < 5:
                if "pi.browser" in self.driver.current_package:
                    result = True
                    break
                if "Welcome to the Pi Browser" in self.driver.page_source:
                    logger.debug("Successfully logged into browser")
                    result = True
                    break
                if "Unlock Pi Wallet" in self.driver.page_source:
                    logger.debug("Successfully logged into browser")
                    result = True
                    break
                if "If above button doesn't" in self.driver.page_source:
                    try:
                        self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text,"Alternative Sign")]').click()
                    except:
                        pass
                else:
                    sleep(1)
                    current_tries += 1
            return result
        except:
            logger.error("Error logging in to pi browser")
            return False
         
    def start_login_user(self) -> None:
        try:
            logger.debug("Start logging in new user")
            while "Continue with phone" not in self.driver.page_source:
                pass
            login_result = self.login_with_phone_number()
            if login_result == False:
                while login_result == False:
                    login_result = self.login_with_phone_number()
            self.navigate_to_pi_network()
            if self.login_to_browser() == False:
                self.change_user()
        except:
            logger.error("Error logging in user")
    
    def check_if_user_verif_needed(self) -> bool:
        try:
            logger.debug("Handling user verification")
            if "Sign out" in self.driver.page_source or  "Sign Out" in self.driver.page_source:
                return True
            if "Total mining" in self.driver.page_source:
                self.tap_menu_burger()
                return True
            elif "Continue with phone" in self.driver.page_source or "Please verify your identity" in self.driver.page_source:
                return True
            self.tap_menu_burger()
            if "Chat" in self.driver.page_source and "Roles" in self.driver.page_source and "Referral" in self.driver.page_source:
                return True
            self.tap_menu_burger()
            if "Chat" in self.driver.page_source and "Roles" in self.driver.page_source and "Referral" in self.driver.page_source:
                return True
            elif "Continue with phone" in self.driver.page_source or "Please verify your identity" in self.driver.page_source:
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"Error in handling user verification, {e}")
    
    def change_user(self) -> None:
        logger.debug("Received command to change user")
        self.driver.activate_app('com.blockchainvault/com.pinetwork.MainActivity')
        sleep(1)
        if self.check_if_user_verif_needed() == False:
            logger.debug("Need user Verification")
            self.navigate_to_pi_network()
        page = self.driver.page_source
        if "code to share" in page or "Settings" in page or "Hide real name" in page:
            logger.debug("Already on profile page")
            self.sign_out_user()
            self.start_login_user()
        elif "Continue with phone" in self.driver.page_source:
            self.start_login_user()
        else:
            logger.debug("Not in profile page")
            self.start_logout_user()
            self.start_login_user()
    
    def start_send_coin(self):
        try:
            self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "Send")]').click()
            sleep(0.06)
        except:
            pass
        try:
            self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "Confirm")]').click()
            sleep(0.06)
        except:
            pass
        try:
            self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "Close")]').click()
            sleep(0.06)
        except:
            pass
            
    
    def scroll_to_bottom(self):
        sleep(0.5)
        self.driver.flick(100,1900,100,200)
        sleep(0.5)
    
    def enter_wallet_address(self):
        try:
            logger.debug("Entering wallet address")
            element = self.driver.find_elements(by=AppiumBy.CLASS_NAME, value='android.widget.EditText')
            sleep(1)
            element[2].send_keys(WALLET_DEST)
            self.driver.hide_keyboard()
        except:
            logger.error("Unable to enter receiver wallet address")
            
    def enter_send_amount(self, amount:float):
        try:
            logger.debug("Entering send amount")
            amount_box = self.driver.find_element(by=AppiumBy.ANDROID_UIAUTOMATOR, value='new UiSelector().className("android.widget.EditText").instance(0)')
            amount_box.send_keys(amount)
            sleep(1)
            self.driver.hide_keyboard()
        except:
            logger.error("Error entering send amount")
            
    def open_pay_page(self):
        try:
            logger.debug("Opening Pay/Request Page")
            self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "Pay / Request")]').click()
            while "Manually Add Wallet Address" not in self.driver.page_source:
                if "Fee" in self.driver.page_source or "Memo" in self.driver.page_source or "Dismiss" in self.driver.page_source:
                    logger.debug("Opened transaction details ")
                    sleep(1)
                    self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "Dismiss")]').click()
                    sleep(1)
                    self.driver.tap([(250,800)])
                    sleep(1)
                logger.debug("Waiting for entering wallet address manually")
                sleep(0.2)
            self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "Manually Add Wallet Address")]').click()
        except:
            logger.error("Error opening pay/request page!")
    
        
    def open_wallet_from_passphrase(self, pwd: str):
        self.driver.activate_app('pi.browser/com.pinetwork.MainActivity')
        logger.info(f"Received new request for phrase: {pwd}")
        current_page = self.check_current_page()
        if current_page == "wallet_home":
            self.click_back_button()
        elif current_page == "transaction":
            self.click_back_button()
        else:
            self.navigate_to_wallet_home()
        
        result = self.enter_wallet_phrase(pwd)
        if result == "exception":
            result = self.enter_wallet_phrase(pwd)
        if result == "error":
            return "Error butuh ganti ke user lain"
        if result == "invalid":
            result = self.enter_wallet_phrase(pwd)
            if result == "ok":
                self.check_current_page()
            elif result == "error":
                return "Error butuh ganti ke user lain"
            else:
                return "Invalid passphrase given"
        else:
            self.check_current_page()
        logger.debug(f"Current value = {result}")
        if result == "exception":
            return "Error butuh ganti ke user lain"
        value = self.check_current_wallet_balance()
        store_phrase(pwd, value)
        
        # Get data of held coins
        return value
    
    def open_wallet_after_error(self, pwd: str):
        self.change_user()
        data = self.open_wallet_from_passphrase(pwd)
        while data == "Error butuh ganti ke user lain":
            self.change_user()
            data = self.open_wallet_from_passphrase(pwd)
        return self.open_wallet_from_passphrase(pwd)
    
    
    def start_transaction(self, pwd:str, amount:float):
        open_phrase = self.open_wallet_from_passphrase(pwd)
        if "error" in open_phrase.lower():
            self.open_wallet_after_error(pwd)
        self.open_pay_page()
        sleep(2)
        self.enter_send_amount(amount)
        sleep(2)
        self.enter_wallet_address()
        sleep(2)
        self.scroll_to_bottom()
        current_time = time()
        logger.debug("Start sending coin")
        result = False
        while (time() < current_time + TRY_SEND_DURATION) and result == False:
            self.start_send_coin()
                
    def print_current_page(self):
        return self.driver.page_source
    
    def change_user_command(self) -> str:
        self.change_user()
    
    def kill_all_apps(self) -> None:
        self.driver.terminate_app('pi.browser')
        self.driver.terminate_app('com.blockchainvault')
       
    def __del__(self):
        logger.info("Finished running script")
        self.driver.quit()

def get_running_bot():
    # if len(running_bot) != 0:
    #     logger.debug("Found running bot")
    #     bot: AndroidBot = running_bot[0]
    #     if time() - bot.age > 4800:
    #         logger.debug("Bot exceeds maximum time, creating a new one")
    #         del bot
    #     else:
    #         return bot
    logger.debug("Creating a new bot.")
    bot = AndroidBot()
    # running_bot.append(bot)
    logger.info(f"Running bot count : {len(running_bot)}")
    return bot

def process_phrase(phrase:str, result_queue : Queue):
    try:
        logger.debug("Starting new request for processing phrase")
        bot = get_running_bot()
        data = bot.open_wallet_from_passphrase(phrase)
        result_queue.put(data)
    except:
        logger.error("Error processing phrase")

def process_phrase_after_error(phrase:str, result_queue : Queue):
    try:
        logger.debug("Starting new request for processing phrase")
        bot = get_running_bot()
        data = bot.open_wallet_after_error(phrase)
        result_queue.put(data)
    except:
        logger.error("Error processing phrase")

def process_transaction(data):
    try:
        phrase = data[0]
        amount = data[1]
        logger.debug("Starting a new transaction")
        bot = get_running_bot()
        bot.start_transaction(phrase,amount)
    except:
        logger.error("Error processing transaction")
        
def process_change_user():
    try:
        logger.debug("Starting new request for processing phrase")
        bot = get_running_bot()
        data = bot.change_user_command()
        return data
    except:
        logger.error("Error processing phrase")

def kill_all_apps():
    bot = get_running_bot()
    bot.kill_all_apps()
    del bot

def start_background_process(target: Any, phrase: str = None, amount: float = None):
    START_TIME = time()
    current_process = None
    if phrase and amount == None:
        result = Queue()
        current_process = Process(target=target, args=(phrase,result))
    elif phrase and amount:
        current_process = Process(target=target,args=((phrase,amount),))
    else:
        current_process = Process(target=target)
    current_process.start()
    while time() - START_TIME <= TIMEOUT:
        if not current_process.is_alive():
            break
        sleep(1)
    else:
        current_process.terminate()
        kill_all_apps()
        current_process.join()
        return "timeout"
    return result.get()

def start_background_process_void(target: Any, phrase: str = None, amount: float = None):
    START_TIME = time()
    current_process = Process(target=target,args=((phrase,amount),))
    current_process.start()
    while time() - START_TIME <= TIMEOUT:
        if not current_process.is_alive():
            break
        sleep(1)
    else:
        current_process.terminate()
        kill_all_apps()
        current_process.join()

def start_transaction_process(phrase:str, amount: float):
    start_background_process_void(process_transaction,phrase,amount)

def start_bot_phrase_process(phrase:str):
    return start_background_process(process_phrase, phrase)

def start_change_user_process():
    return start_background_process(process_change_user)

def start_phrase_process_after_error(phrase:str):
    return start_background_process(process_phrase_after_error,phrase)