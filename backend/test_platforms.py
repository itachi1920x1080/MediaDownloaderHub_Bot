import yt_dlp

# បញ្ជី URL សម្រាប់តេស្ត
test_urls = [
    # "https://youtu.be/uspbIFxQ5Gw?si=CI5ApSW1HB_JpWtN", # YouTube
    "https://www.tiktok.com/@mr.chork1122/video/7648082804114214166?is_from_webapp=1&sender_device=pc", # TikTok
]

def test_extract_info(urls):
    ydl_opts = {'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for url in urls:
            try:
                print(f"Testing: {url}")
                info = ydl.extract_info(url, download=False)
                print(f"Success! Title: {info.get('title')}")
            except Exception as e:
                print(f"Failed: {url} | Error: {e}")

if __name__ == "__main__":
    test_extract_info(test_urls)