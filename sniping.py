
import requests
import pickle
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
from ocr import load_model, get_number_from_image, save_image
from urllib.request import urlretrieve
import gif2numpy
from selenium.webdriver.common.action_chains import ActionChains
from personal import user_info, card_info, loc_zip

TIMEOUT = 5
AWAIT = 0.5
TRY = 5

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# iphone 14 model code
# https://shinsegaemall.ssg.com/item/dealItemView.ssg?itemId=1000517934018&siteNo=6004&salestrNo=6005
model_code = {
    "pro-gold-128gb": "MQ083KH/A",
    "pro-gold-256gb": "MQ183KH/A",
    "pro-gold-512gb": "MQ233KH/A",
    "pro-gold-1tb": "MQ2V3KH/A",
    "pro-deeppurple-128gb": "MQ0G3KH/A",
    "pro-deeppurple-256gb": "MQ1F3KH/A",
    "pro-deeppurple-512gb": "MQ293KH/A",
    "pro-deeppurple-1tb": "MQ323KH/A",
    "pro-spaceblack-128gb": "MPXV3KH/A",
    "pro-spaceblack-256gb": "MQ0T3KH/A",
    "pro-spaceblack-512gb": "MQ1M3KH/A",
    "pro-spaceblack-1tb": "MQ2G3KH/A",
    "pro-silver-128gb": "MQ023KH/A",
    "pro-silver-256gb": "MQ103KH/A",
    "pro-silver-512gb": "MQ1W3KH/A",
    "pro-silver-1tb": "MQ2N3KH/A",
    "max-deeppurple-256gb": "MQ9X3KH/A",
    "magsafe-duo": "MHXF3KH/A"
}

color_code = {
    "deeppurple": "딥-퍼플",
    "gold": "골드",
    "silver": "실버",
    "spaceblack": "스페이스-블랙"
}

def is_pickup_possible(model, loc_zip):
    is_available = False
    notes = []
    avail_list = []
    code = model_code[model]
    url = f"https://www.apple.com/kr/shop/fulfillment-messages?parts.0={code}&searchNearby=true&location={loc_zip}"
    r = requests.get(url)
    if r.status_code == 200:
        try:
            d = r.json()
            stores = d["body"]["content"]["pickupMessage"]["stores"]
            for store in stores:
                storeName = store["storeName"]
                message = store["partsAvailability"][code]["pickupSearchQuote"]
                modelname = store["partsAvailability"][code]["messageTypes"]["regular"]["storePickupProductTitle"]
                storeName = "Apple " + storeName
                note = f"{storeName}의 {modelname}: {message}"
                col = bcolors.FAIL
                if "가능" in message:
                    is_available = True
                    notes.append(note)
                    avail_list.append({"storeName": storeName, "model": model})
                    col = bcolors.OKGREEN
                print(col + note + bcolors.ENDC)
        except Exception as e:
            print(e)
    time.sleep(0.2)
    return is_available, notes, avail_list

def save_cookie(driver, path):
    with open(path, 'wb') as filehandler:
        pickle.dump(driver.get_cookies(), filehandler)

def load_cookie(driver, path):
     with open(path, 'rb') as cookiesfile:
         cookies = pickle.load(cookiesfile)
         for cookie in cookies:
             driver.add_cookie(cookie)

def wait_and_click(driver, xpath, enter=False, timeout=TIMEOUT):
    element = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, xpath)
	))
    element = driver.find_element(By.XPATH, xpath)
    if enter:
        element.send_keys(Keys.ENTER)
    else:
        element.click()
    return element

def make_click_dict(driver, ocr_model=None):
    click_dict = {}
    # element = WebDriverWait(driver, 10).until(
    #     EC.presence_of_element_located((By.XPATH, "//input[@type='image' and contains(@onclick, ok)]")
	# ))
    try:
        for keyvalue in range(10):
            xpath = f"//td[@class='dd']//input[@type='image' and contains(@onclick, {keyvalue})]"
            element = driver.find_element(By.XPATH, xpath)
            img_src = element.get_attribute("src")
            img_path = f"./tmp/{keyvalue}.gif"
            urlretrieve(img_src, img_path)
            np_img, extensions, image_specifications = gif2numpy.convert(img_path)
            num = get_number_from_image(np_img[0], ocr_model)[0]
            click_dict[str(num)] = xpath
    except:
        pass
    return click_dict

def purchase(model, loc_zip="08826", store="Apple 명동", user_info={}, card_info={}, ocr_model=None, is_acc=False, test=False):
    # driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver = webdriver.Chrome(executable_path="./chromedriver")
    # suffix, color, capacity = model.split("-")
    # model_version = 13 if test else 14
    # if "pro" in suffix:
    #     durl = f"https://www.apple.com/kr/shop/buy-iphone/iphone-{model_version}-pro"
    #     url = durl + "/6.1형-디스플레이-"
    #     if "max" in suffix:
    #         url = durl + "/6.7형-디스플레이-"
    # else:
    #     url = f"https://www.apple.com/kr/shop/buy-iphone/iphone-{model_version}"
    
    if model == "magsafe-duo":
        is_acc = True

    code = model_code[model]
    url = f"https://www.apple.com/kr/shop/product/{code}"

    try:
        driver.get(url)
        if not is_acc:
            wait_and_click(driver, f"//input[@name='tradeupinline' and @value='noTradeIn']/following-sibling::label")
            time.sleep(AWAIT)
            driver.find_element(By.XPATH, f"//input[contains(@name, 'applecareplus') and contains(@data-autom, 'noapplecare')]/following-sibling::label").click()
            time.sleep(AWAIT)
            wait_and_click(driver, f"//button[@data-autom='productLocatorTriggerLink_{code}']")
            wait_and_click(driver, f"//input[@data-autom='zipCode']")
            element = driver.find_element(By.XPATH, f"//input[@data-autom='zipCode']")
            element.send_keys(loc_zip)
            element.submit()
            wait_and_click(driver, f"//span[text()='{store}']")
            wait_and_click(driver, f"//button[@data-autom='continuePickUp']")
        else:
            wait_and_click(driver, f"//span[text()='재고 확인']")
            time.sleep(AWAIT)
            wait_and_click(driver, "//input[@data-autom='zipCode']")
            element = driver.find_element(By.XPATH, "//input[@data-autom='zipCode']")
            element.send_keys(loc_zip)
            element.submit()
            wait_and_click(driver, f"//span[text()='{store}']")
            wait_and_click(driver, "//span[text()='매장 선택']")
        time.sleep(AWAIT)

        element = False
        for i in range(TRY):
            try:
                element = driver.find_element(By.XPATH, "//h1[@class='rs-bag-header']")
            except:
                try:
                    element = driver.find_element(By.XPATH, "//button[@name='proceed']")
                    element.click()
                except:
                    time.sleep(AWAIT)
                    driver.find_element(By.XPATH, "//button[@name='add-to-cart']").click()
            if element:
                break
        if not element:
            raise NotImplementedError    

        # url = f"https://www.apple.com/kr/shop/buy-iphone/iphone-14-pro?product={code}&step=attach"
        # driver.get(url)

        wait_and_click(driver, f"//button[@id='shoppingCart.actions.checkout']")
        wait_and_click(driver, f"//button[@id='signIn.guestLogin.guestLogin']")
        
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//select[@id='checkout.fulfillment.pickupTab.pickup.timeSlot.dateTimeSlots.timeSlotValue']")
        ))
        select = Select(driver.find_element(By.XPATH, "//select[@id='checkout.fulfillment.pickupTab.pickup.timeSlot.dateTimeSlots.timeSlotValue']"))
        select.select_by_index(1)
        time.sleep(1)
        wait_and_click(driver, "//button[@data-autom='fulfillment-continue-button']")
        wait_and_click(driver, "//label[@for='pickupOptionButtonGroup0']")

        driver.find_element(By.XPATH, "//input[@id='checkout.pickupContact.selfPickupContact.selfContact.address.firstName']").send_keys(user_info['first_name'])
        driver.find_element(By.XPATH, "//input[@id='checkout.pickupContact.selfPickupContact.selfContact.address.lastName']").send_keys(user_info['last_name'])
        driver.find_element(By.XPATH, "//input[@id='checkout.pickupContact.selfPickupContact.selfContact.address.emailAddress']").send_keys(user_info['mail'])
        driver.find_element(By.XPATH, "//input[@id='checkout.pickupContact.selfPickupContact.selfContact.address.mobilePhone']").send_keys(user_info['phone'])
        wait_and_click(driver, "//button[@id='rs-checkout-continue-button-bottom']")

        wait_and_click(driver, "//input[@id='checkout.billing.billingOptions.selectedBillingOptions.inicis.billingAddress.address.lastName']")
        driver.find_element(By.XPATH, "//input[@id='checkout.billing.billingOptions.selectedBillingOptions.inicis.billingAddress.address.lastName']").send_keys(card_info["last_name"])
        driver.find_element(By.XPATH, "//input[@id='checkout.billing.billingOptions.selectedBillingOptions.inicis.billingAddress.address.firstName']").send_keys(card_info["first_name"])
        select = Select(driver.find_element(By.XPATH, "//select[@id='checkout.billing.billingOptions.selectedBillingOptions.inicis.billingAddress.address.state']"))
        select.select_by_value(card_info["state"])

        driver.find_element(By.XPATH, "//input[@id='checkout.billing.billingOptions.selectedBillingOptions.inicis.billingAddress.address.city']").send_keys(card_info["city"])
        driver.find_element(By.XPATH, "//input[@id='checkout.billing.billingOptions.selectedBillingOptions.inicis.billingAddress.address.postalCode']").send_keys(card_info["postalCode"])
        driver.find_element(By.XPATH, "//input[@id='checkout.billing.billingOptions.selectedBillingOptions.inicis.billingAddress.address.street']").send_keys(card_info["street"])
        driver.find_element(By.XPATH, "//input[@id='checkout.billing.billingOptions.selectedBillingOptions.inicis.billingAddress.address.street2']").send_keys(card_info["street2"])
        
        wait_and_click(driver, "//button[@data-autom='continue-button-label']")
        wait_and_click(driver, "//input[@id='checkout.review.placeOrder.termsAndConditions.segmentSpecificRetailTerms.termsCheckbox']")
        wait_and_click(driver, "//button[@data-autom='continue-button-label']")
        
        wait_and_click(driver, "//input[@id='ncardnum1']")

        driver.find_element(By.XPATH, "//input[@id='ncardnum1']").send_keys(card_info["card_num"][0])
        driver.find_element(By.XPATH, "//input[@id='ncardnum2']").send_keys(card_info["card_num"][1])
        driver.find_element(By.XPATH, "//input[@id='ncardnum3']").send_keys(card_info["card_num"][2])

        click_dict = {}
        while not click_dict:
            element = driver.find_element(By.XPATH, "//input[@id='ncardnum3']")
            ActionChains(driver).move_to_element(element).send_keys(Keys.TAB).perform()
            time.sleep(AWAIT)
            click_dict = make_click_dict(driver, ocr_model)
        for num in card_info["card_num"][3]:
            driver.find_element(By.XPATH, click_dict[str(num)]).click()
        driver.find_element(By.XPATH, "//input[@type='image' and contains(@onclick, ok)]").send_keys(Keys.ESCAPE)
        time.sleep(1)

        select = Select(driver.find_element(By.XPATH, "//select[@name='cardexpm']"))
        select.select_by_value(card_info["cardexpm"])
        select = Select(driver.find_element(By.XPATH, "//select[@name='cardexpy']"))
        select.select_by_value(card_info["cardexpy"])
        

        click_dict = {}
        while not click_dict:
            element = driver.find_element(By.XPATH, "//div[contains(text(), '비밀번호')]")
            ActionChains(driver).move_to_element(element).send_keys(Keys.TAB).perform()
            time.sleep(AWAIT)
            click_dict = make_click_dict(driver, ocr_model)

        for num in card_info["cardpasswd2"]:
            driver.find_element(By.XPATH, click_dict[str(num)]).click()
        driver.find_element(By.XPATH, "//input[@type='image' and contains(@onclick, ok)]").send_keys(Keys.ESCAPE) 
        time.sleep(1)

        driver.find_element(By.XPATH, "//input[@name='authField1']").send_keys(card_info["card_birth"])

        select = Select(driver.find_element(By.XPATH, "//select[@name='cardquota']"))
        select.select_by_index(int(card_info["cardquota"] - 1))

        try:
            wait_and_click(driver, "//input[@name='chk_agree1']",
                timeout=0.5)
        except:
            pass
        wait_and_click(driver, "//input[@name='chk_agree2']")
        wait_and_click(driver, "//input[@name='chk_agree3']")
        wait_and_click(driver, "//input[@name='chk_agree4']")

        if not test:
            wait_and_click(driver, "//span[text()='결제']")
        col = bcolors.OKGREEN
        print(col + "성공" + bcolors.ENDC)
        time.sleep(120)
        return True
    except Exception as e:
        print(e)
        return False
    # finally:
    #     time.sleep(30)

if __name__ == "__main__":
    ocr_model = load_model(model_path="./static/mnist_inicis.mlpackage")
    purchase("magsafe-duo", store="Apple 가로수길", user_info=user_info, card_info=card_info, ocr_model=ocr_model, test=True)

    