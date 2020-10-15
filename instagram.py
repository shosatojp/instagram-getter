#!/bin/python3
import functools
import html
from selenium.webdriver import FirefoxOptions, Firefox, FirefoxProfile
from selenium.webdriver.firefox.webelement import FirefoxWebElement
import time
import os
import re
from ffcache import FirefoxCache


def get_picture(ff: Firefox, thumb_element: FirefoxWebElement, outdir='.') -> bool:
    thumb_link_element: FirefoxWebElement = thumb_element.find_element_by_css_selector('a')
    thumb_url = thumb_link_element.get_attribute("href")
    print('thumb: ', thumb_url)

    match = re.match('.*/p/(.*)/', thumb_url)
    outpath = os.path.join(outdir, f'{match[1]}.jpg')

    if not os.path.exists(outpath):
        try:
            thumb_element.click()
            time.sleep(0.5)

            top_comments = ff.find_element_by_css_selector('._2dDPU ul.XQXOT').text  # .get_attribute('innerHTML')
            print(top_comments[:100])
            likes = ff.find_element_by_css_selector('._2dDPU .Nm9Fw button span').text
            print('likes: ', likes)
            srcset = ff.find_element_by_css_selector('._2dDPU img.FFVAD').get_attribute('srcset').split(',')

            # save from cache
            print('waiting for cache...')
            time.sleep(1)
            cache = FirefoxCache(ff.capabilities['moz:profile'] + '/cache2')

            # save loaded image in srcset
            for src in srcset:
                try:
                    image_url, _ = src.split(' ')
                    entry = cache.find(image_url)
                    entry.save(outpath)
                except:
                    pass
        except Exception as e:
            print(e)
        finally:
            try:
                ff.find_element_by_css_selector('[aria-label="閉じる"]').click()
                print('waiting for ui...')
                time.sleep(0.5)
                return True
            except Exception as e:
                print(e)
                return False
    else:
        return False


def get_user_page(url: str, profile_dir: str, outdir='.') -> None:
    opt = FirefoxOptions()
    # opt.add_argument('-headless')

    p = FirefoxProfile(profile_dir)
    p.set_preference('extensions.lastAppBuildId', '-1')
    p.set_preference('network.proxy.socks', '')
    p.set_preference('network.proxy.socks', '')


    with Firefox(p, options=opt) as ff:
        ff.get(url)

        heights = []

        while True:
            count = 0

            for elem in ff.find_elements_by_css_selector('.v1Nh3'):
                try:
                    get_picture(ff, elem, outdir)
                except Exception as e:
                    print(e)

            heights.append(ff.execute_script('return document.body.scrollHeight;'))
            if len(heights) >= 3 and functools.reduce(lambda a, b: a == b and a, heights[-3:]):
                break

            ff.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(2)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('url')
    parser.add_argument('--profile', default=os.environ['FIREFOX_PROFILE'])
    parser.add_argument('--out', '-o', default='.')
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)

    get_user_page(args.url, args.profile, args.out)
