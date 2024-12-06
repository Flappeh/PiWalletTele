from appium import webdriver
from typing import Dict, Any
from appium.options.common.base import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webelement import WebElement
import time

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
appium_server_url = "http://192.168.18.221:4723"

driver = webdriver.Remote(appium_server_url, options=AppiumOptions().load_capabilities(capabilities))

# el = driver.find_element(by=AppiumBy.XPATH, value="//*[@text='Battery']")
# parent: WebElement = el.parent
# el.click()

def click_update():
    try:
        update = driver.find_element(by=AppiumBy.XPATH, value='//*[@resource-id="mui-3"]')
        update.click()
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
    

def navigate_to_wallet_home():
    while check_current_page() != "wallet_home":    
        match check_current_page():
            case "wallet_home":
                break
            case "wallet_page":
                reload_wallet_page()
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
                return
            
    

def open_wallet_from_passphrase(pwd: str):
    current_page = check_current_page()
    if check_current_page() != "wallet_home":
        print("Not in wallet page")
        navigate_to_wallet_home()
    try:
        login_box = driver.find_element(by=AppiumBy.XPATH, value="//android.widget.EditText")
        button_login = driver.find_element(by=AppiumBy.XPATH, value='//*[@text="Unlock With Passphrase"]')
    except:
        print("Not in wallet page")
    login_box.clear()
    login_box.send_keys(pwd)
    button_login.click()
    if "Invalid Passphrase" in driver.page_source:
        print("Invalid passphase")
        return "Invalid Pass"
    check_current_wallet_balance()
    
    
    
open_wallet_from_passphrase("coyote arctic million tattoo tenant onion retreat upon cat avoid correct suspect trick century hard mango song mimic space kingdom volume wealth scan attack")

driver.quit()