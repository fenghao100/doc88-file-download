import time
import os
import requests
import zipfile
from retrying import retry
from pathlib import Path

# 延迟导入 config，避免循环导入
cfg2 = None

__all__ = [
    "ospath", "special_path", "choose", "logw", "r",
    "get_request", "write_file", "writes_file", "read_file",
    "load_file", "download", "download_validated", "extractzip", "github_release",
    "get_cfg2",
]

def get_cfg2():
    """获取 cfg2 实例（延迟初始化）"""
    global cfg2
    if cfg2 is None:
        from config import get_config
        cfg2 = get_config()
    return cfg2


def ospath(path):
    config = get_cfg2()
    if os.name == "nt" and config.path_replace:
        fullpath = Path(path)
        if len(str(fullpath.absolute())) >= 260:
            return "\\\\?\\" + str(fullpath.absolute())
        else:
            return str(fullpath)
    else:
        return path

def special_path(path):
    char_list = ['*', '|', ':', '?', '/', '<', '>', '"', '\\']
    new_char_list = ['＊', '｜', '：', '？', '／', '＜', '＞', '＂', '＼']
    for i in range(len(char_list)):
        path = path.replace(char_list[i], new_char_list[i])
    return path

def choose(text=""):
    if text == "exists":
        text = "The directory already exists!\nContinue? (Y/n): "
    elif text == "down":
        text = "是否下载，否则继续提取预览文档？ (Y/n): "
    elif text == "":
        text = "Continue? (Y/n): "
    try:
        user_input = input(text)
    except KeyboardInterrupt:
        exit()
    if user_input == "Y" or user_input == "y":
        return True
    else:
        return False


def logw(t: str):
    log = "[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "]: " + t + "\n"
    log_dir = "logs/"
    dirc = log_dir + time.strftime("%Y-%m-%d", time.localtime()) + ".log"
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)
    with open(ospath(dirc), "a") as file:
        file.write(log)


def r(str):
    return '"' + str + '"'


def get_request(url: str, timeout: int = 10):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.39",
        "Content-Type": "text/html; charset=utf-8",
        "Referer": "https://www.doc88.com/",
    }
    return requests.get(url, headers=headers, timeout=timeout)


def write_file(data, path):
    with open(ospath(path), "wb") as f:
        f.write(data)
        f.close()


def writes_file(data, path):
    with open(ospath(path), "w") as f:
        f.write(data)
        f.close()


def read_file(path):
    with open(ospath(path), "r") as file:
        read = file.read()
        return read


def load_file(path):
    with open(ospath(path), "rb") as file:
        read = file.read()
        return read


@retry(stop_max_attempt_number=3, wait_fixed=500)
def download(url: str, filepath: str):
    """下载文件到本地，失败自动重试 3 次。"""
    resp = get_request(url, timeout=60)
    resp.raise_for_status()
    write_file(resp.content, filepath)


def download_validated(url: str, filepath: str, min_size: int = 1024):
    """下载文件并校验返回内容确实是文件（而非 HTML 错误页/登录页）。"""
    resp = get_request(url, timeout=60)
    resp.raise_for_status()
    data = resp.content
    ct = (resp.headers.get("Content-Type") or "").lower()
    is_pdf = data[:5] == b"%PDF-"
    if len(data) < min_size or ("text/html" in ct and not is_pdf):
        raise ValueError(
            "返回内容不是有效文件（可能需登录或链接已失效），"
            "大小 %d 字节，类型 %s" % (len(data), ct or "未知")
        )
    write_file(data, filepath)


def extractzip(file_path: str, topath: str):
    with zipfile.ZipFile(file_path, "r") as f:
        f.extractall(topath)
        f.close

class github_release:
    def __init__(self, repo: str, n: int = 0) -> None:
        self.repo = repo
        self.latest_version = ""
        self.download_url = ""
        self.name = ""
        self.fetch_release_info(n)

    def fetch_release_info(self, n: int = 0):
        version_info = get_request(f"https://api.github.com/repos/{self.repo}/releases/latest").json()
        self.latest_version = version_info["tag_name"]
        self.download_url = version_info['assets'][n]['browser_download_url']
        self.name = version_info['assets'][n]['name']