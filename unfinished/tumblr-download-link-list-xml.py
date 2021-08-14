from bs4 import BeautifulSoup
import json
import sys
import time

if sys.version_info[0] != 3:
    print('This script requires Python 3.x.')
    sys.exit(1)

from urllib.request import urlopen  # noqa: E402


def get_posts(url, t):
    s = urlopen(url).read()
    if t == 'json':
        # Loads JSONP, so initial "var something = " and trailing ";" should be cut
        # before decoding.
        return json.loads(s[s.index(b'=')+1:s.rindex(b';')])
    else:
        return BeautifulSoup(s, 'xml')


def process_json_response(p):
    if 'posts' not in p:
        return
    for post in p['posts']:
        if 'photo-url-1280' in post:
            print(post['photo-url-1280'])

        if 'photos' in post:
            for photo in post['photos']:
                if 'photo-url-1280' in photo:
                    print(photo['photo-url-1280'])

        if 'video-player' in post:
            try:
                soup = BeautifulSoup(post['video-player'],
                                     'html.parser')
                print(soup.video.source['src'])
            except Exception:
                pass


def process_xml_response(p):
    for post in p.tumblr.posts:
        has_photo_url = False
        has_photo_url_1280 = False
        for child in post.children:
            if child.name == 'photo-url':
                has_photo_url = True
            if child.name == 'photo-url' and child['max-width'] == '1280':
                has_photo_url_1280 = True
                print(child.contents[0])

            if child.name == 'photos':
                photos = child
                exit(1)
        if has_photo_url and not has_photo_url_1280:
            raise "why"

def main(tumblr_name, t):
    # API v1
    url = 'https://' + tumblr_name + '.tumblr.com/api/read' + \
        ('/json' if t == 'json' else '') + '?'

    p = get_posts(url + 'num=0', t)
    if t == 'json':
        total_posts = int(p['posts-total'])
    else:
        total_posts = int(p.tumblr.posts['total'])
    print(total_posts)

    # Main loop.
    for start in range(0, total_posts, 50):
        p = get_posts(url + 'num=50&start={}'.format(start), t)

        if t == 'json':
            process_json_response(p)
        else:
            process_xml_response(p)

        time.sleep(1)


if __name__ == '__main__':
    tumblr_name = sys.argv[1]
    main(tumblr_name, 'xml')
