""" Use Apple's Vision Framework via PyObjC to detect text in images """

import pathlib

import Quartz
import Vision
from Cocoa import NSURL
from Foundation import NSDictionary
# needed to capture system-level stderr
from wurlitzer import pipes


def image_to_text(img_path=None, img=None, lang="eng", input_url=None):
    if input_url is None:
        input_url = NSURL.fileURLWithPath_(img_path)

    with pipes() as (out, err):
    # capture stdout and stderr from system calls
    # otherwise, Quartz.CIImage.imageWithContentsOfURL_
    # prints to stderr something like:
    # 2020-09-20 20:55:25.538 python[73042:5650492] Creating client/daemon connection: B8FE995E-3F27-47F4-9FA8-559C615FD774
    # 2020-09-20 20:55:25.652 python[73042:5650492] Got the query meta data reply for: com.apple.MobileAsset.RawCamera.Camera, response: 0
        input_image = Quartz.CIImage.imageWithContentsOfURL_(input_url)

    vision_options = NSDictionary.dictionaryWithDictionary_({})
    vision_handler = Vision.VNImageRequestHandler.alloc().initWithCIImage_options_(
        input_image, vision_options
    )
    results = []
    handler = make_request_handler(results)
    vision_request = Vision.VNRecognizeTextRequest.alloc().initWithCompletionHandler_(handler)
    # print(vision_request.recognitionLanguages())
    error = vision_handler.performRequests_error_([vision_request], None)
    vision_request.dealloc()
    vision_handler.dealloc()
    return results

def make_request_handler(results):
    """ results: list to store results """
    if not isinstance(results, list):
        raise ValueError("results must be a list")

    def handler(request, error):
        if error:
            print(f"Error! {error}")
        else:
            observations = request.results()
            for text_observation in observations:
                recognized_text = text_observation.topCandidates_(1)[0]
                results.append([recognized_text.string(), recognized_text.confidence()])
    return handler


def main():
    import sys
    import pathlib

    img_path = pathlib.Path(sys.argv[1])
    if not img_path.is_file():
        sys.exit("Invalid image path")
    img_path = str(img_path.resolve())
    results = image_to_text(img_path)
    print(results)


if __name__ == "__main__":
    main()