import time
import applescript
import datetime
import random
from sniping import is_pickup_possible, model_code, purchase
from ocr import load_model
from multiprocessing import Pool
from personal import user_info, card_info, loc_zip

ocr_model = load_model(model_path="./static/mnist_inicis.mlpackage")

def notify(notes):
    # notify using Apple Reminder app
    now = datetime.datetime.now() - datetime.timedelta(minutes=1)
    now = now.strftime('%m/%d/%Y %I:%M %p')
    for note in notes:
        applescript.tell.app("Reminders", f"make new reminder with properties {{name:\"{note}\", due date:date \"{now}\"}}")

def timing(interval):
    # sample from (interval * 0.7, interval * 1.2)
    scaler = 0.7 + 0.5 * random.random()
    return interval * scaler

def try_purchase(find, notes, avail_list, test=False):
    done = False
    if find:
        try:
            print("구매 시도")
            print(avail_list)
            done = purchase(
                model=avail_list[0]["model"],
                loc_zip=loc_zip,
                store=avail_list[0]["storeName"],
                user_info=user_info,
                card_info=card_info,
                ocr_model=ocr_model,
                test=test
            )
        except Exception as e:
            print(e)
            pass
    return done

def main(models, loc_zip, interval, test=False):
    num_cores = 4
    pool = Pool(num_cores)
    trial = 1
    done = False
    loc_zips = [loc_zip for _ in range(len(models))]
    note = ""
    find = False
    while not done:
        pool = Pool(num_cores)
        print(f"{trial}번째 시도:")
        results = []
        def collect_result(result):
            results.append(result)
        output = pool.starmap(is_pickup_possible, zip(models, loc_zips))
        # find = any([out[0] for out in output])
        # avail_list = []
        # for out in output:
        #     avail_list += out[2]
        # find, notes, avail_list = is_pickup_possible(models, loc_zip)
        for out in output:
            # async_done = pool.apply_async(try_purchase, args=out,
            # kwds={"test": test}, callback=collect_result)
            results.append(try_purchase(*out, test=test))
        pool.close()
        pool.join()
        done = any(results)
        if done:
            break
        print("-" * 50)
        time.sleep(timing(interval))
        trial += 1
    notify(["아이폰 구매 성공 확인하기"])

if __name__ == "__main__":
    print(f"available options: {list(model_code.keys())}")
    test = False
    models = ["max-deeppurple-256gb"]
    # models = ["pro-silver-256gb"]
    # models = ["pro-deeppurple-256gb"]
    # models = ["magsafe-duo"]
    interval = 10
    loc_zip = "08826"
    main(models, loc_zip, interval, test=test)