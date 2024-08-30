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
    "deviceName": "Android",
    "language": "en"
}

appium_server_url = "http://localhost:4724"
# appium_server_url = "http://192.168.18.211:4723"

driver = webdriver.Remote(appium_server_url, options=AppiumOptions().load_capabilities(capabilities))

# el = driver.find_element(by=AppiumBy.XPATH, value="//*[@text='Battery']")
# parent: WebElement = el.parent
# el.click()

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
    

def login_with_passphrase(pwd: str):
    current_page = check_current_page()
    match current_page:
        case "wallet_home":
            pass
        case "wallet_page":
            reload_wallet_page()
        case "loading":
            print("Loading")
        case _:
            print("Undefined")
            return
    if check_current_page() != "wallet_home":
        print("Not in wallet page")
        return
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
    
    
    
login_with_passphrase("coyote arctic million tattoo tenant onion retreat upon cat avoid correct suspect trick century hard mango song mimic space kingdom volume wealth scan attack")

driver.quit()