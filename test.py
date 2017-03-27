import requests
s = requests.Session()

s.headers = {'user-agent': 'Chrome/56.0.2924.87'}
print s.get("http://anhsangsoiduong.vn/files/game_assd/html5/index.php?game_token=jWP8qSE5hJG9DXTHEP-mXL0LowMCENeS").content
