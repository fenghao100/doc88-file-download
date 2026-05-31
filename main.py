# -*- coding: utf-8 -*-

from config import *
# 延迟初始化配置
cfg2 = get_config()
print(f"DOC88 （预览）文档提取工具 V{cfg2.default_config['version']}")
print("by: Cuite_Piglin")
print(
    "\n免责声明： 仅供学习或交流用，请在 24 小时内删除本程序，严禁用于任何商业或非法用途，使用该工具而产生的任何法律后果，用户需自行承担全部责任\n"
)
import os

if cfg2.swf2svg:
    print(
        "使用 SVG 转换功能建议同时关闭 font-face 功能，否则将会导致大量转换失败，若只需要 SVG 文件可关闭清理功能，文件将会生成到文档目录下的 svg 目录"
    )
    if os.name == "nt":
        print(
            "警告：你正在使用 Windows 系统并使用 SVG 转换功能，虽然我们有意使其在多平台下工作，但需要使用 Cairo 库才能进行 SVG 的转换，建议你安装 GTK 运行库（需要 200MB 左右的安装空间）：\nhttps://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases\n如果安装后仍然无效，请尝试将安装目录下的 bin 目录添加到系统环境的 PATH 中然后重启终端或 Vscode\n"
        )
        list = os.environ["Path"].split(";")
        import re

        pattern = re.compile(r"GTK.?-Runtime")
        matches = [item for item in list if pattern.search(item)]
        if matches:
            try:
                os.add_dll_directory(matches[0])
            except:
                print("Error when setting environment.")
        else:
            print("GTK runtime not found, maybe not install?")
    import cairosvg
import sys
import json
import re
import time
import shutil
from compressor import *
from concurrent.futures import ThreadPoolExecutor
from pypdf import PdfWriter
from gen_cfg import *
from get_more import *
from utils import *
from updater import *

class get_cfg:
    def __init__(self, url: str) -> None:
        if url.find("doc88.com/p-") == -1 and url.find("doc88.piglin.eu.org/p-") == -1:
            raise Exception("Invalid URL!")
        self.url = url
        self.content = ""
        self.data = ""
        self.sta = 0
        if not self.get_main():
            if choose("Do you want to use CDN?(Y/n): "):
                self.__init__(
                    "https://doc88.piglin.eu.org" + url[url.find("doc88.com/") + 9 :]
                )
                return None
        return None

    def req(self):
        request = get_request(self.url)
        if request.status_code == 404:
            self.sta = 1
            raise Exception("404 Not found!")
        self.content = request.text

    def get_main(self):
        self.req()
        data = re.search(r"m_main.init\(\".*\"\);", self.content)
        if data == None:
            if re.search("网络环境安全验证", self.content):
                print("WAF detected!")
                return False
            raise Exception("Config data not found! May be deleted?")
        c = data.span()
        self.data = self.content[c[0] + 13 : c[1] - 3]
        return True


def append_pdf(pdf: PdfWriter, file: str):
    pdf.append(ospath(file))
    return pdf


class init:
    def __init__(self, config: dict) -> None:
        cfg2.dir_path = cfg2.o_dir_path + config["p_code"] + "/"
        cfg2.swf_path = cfg2.dir_path + cfg2.o_swf_path
        cfg2.svg_path = cfg2.dir_path + cfg2.o_svg_path
        cfg2.pdf_path = cfg2.dir_path + cfg2.o_pdf_path
        try:
            os.makedirs(ospath(cfg2.dir_path))
        except FileExistsError:
            if choose("exists"):
                pass
            else:
                exit()
        if not os.path.exists(ospath(f"{cfg2.dir_path}index.json")):
            write_file(
                bytes(json.dumps(config), encoding="utf-8"),
                cfg2.dir_path + "index.json",
            )
        try:
            os.makedirs(ospath(cfg2.swf_path))
            os.makedirs(ospath(cfg2.svg_path))
            os.makedirs(ospath(cfg2.pdf_path))
        except:
            print("")


def main(encoded_str, more=False):
    try:
        config = json.loads(decode(encoded_str))
    except json.decoder.JSONDecodeError:
        print("Can't read!")
        return False
    except (ValueError, UnicodeDecodeError):
        print("Can't read! Maybe keys were changed?")
        return False
    init(config)
    cfg = gen_cfg(config)
    if os.path.exists(ospath(f"{cfg2.dir_path}index.json")):
        cfg = gen_cfg(json.loads(read_file(f"{cfg2.dir_path}index.json")))
    print(f"文档名：{cfg.p_name}")
    print(f"文档 ID：{cfg.p_code}")
    print(f"上传日期：{cfg.p_date}")
    print(f"页数：{cfg.p_pagecount}")
    if int(cfg.p_pagecount) != cfg.p_count:
        more = True
        print(f"可预览页数：{cfg.p_countinfo}")
        print(f"可直接获取页数：{cfg.p_count}")
        print(f"可能有额外页面（需扫描）！")
    if not choose("开始提取？ (Y/n): "):
        return False
    if cfg.p_download == "1":
        print("该文档为免费文档，可直接下载！")
        if choose("down"):
            try:
                if config["if_zip"] == 0:
                    doc_format = str.lower(cfg.p_doc_format)
                else:
                    doc_format = "zip"
                file_path = "docs/" + cfg.p_name + "." + doc_format
                download(
                    get_request(
                        "https://www.doc88.com/doc.php?act=download&pcode=" + cfg.p_code
                    ).text,
                    file_path,
                )
                print("Saved file to " + file_path)
                return True
            except Exception as err:
                print("Downlaod error: " + str(err))
                logw("Downlaod error: " + str(err))
        else:
            print("Continuing...")
    if more:
        if choose("即将通过扫描获取页面，是否继续（否则正常下载）？ (Y/n): "):
            print("尝试通过扫描获取页面...")
            newpageids = []
            cfg.p_count = 0
            for i in range(1, cfg.ph_nums() + 1):
                get = get_more(cfg, i, cfg2.dir_path, cfg.p_count)
                get.start()
                newpageids += get.newpageids
                cfg.p_count += len(get.newpageids)
                del get
            cfg.pageids = newpageids
            config["pageInfo"] = encode(",".join(newpageids))
            config["p_count"] = cfg.p_count
            write_file(
                bytes(json.dumps(config), encoding="utf-8"),
                cfg2.dir_path + "index.json",
            )
            print(f"成功扫描页数：{cfg.p_count}")
            del newpageids
            time.sleep(2)
        else:
            print("普通下载模式...")
            more = False
    try:
        if not more:
            get_swf(cfg)
        convert(cfg)
        del cfg
        return True
    except Exception as err:
        print(err)
        return False


class downloader:
    def __init__(self, cfg: gen_cfg) -> None:
        self.cfg = cfg
        self.downloaded = True
        self.progressfile = cfg2.dir_path + "progress.json"
        if os.path.isfile(ospath(self.progressfile)):
            self.read_progress()
        else:
            self.progress = {"pk": [], "ph": []}

    def read_progress(self):
        try:
            self.progress = json.loads(read_file(self.progressfile))
        except json.decoder.JSONDecodeError:
            self.progress = {}

    def save_progress(self, type: str, page: int):
        self.progress[type].append(page)
        writes_file(json.dumps(self.progress), self.progressfile)

    def ph(self, i: int):
        url = self.cfg.ph(i)
        print(f"Downloading PH {i}: \n{url.url}")
        file_path = cfg2.dir_path + url.name
        if i in self.progress["ph"]:
            print("Using Cache...")
            return None
        try:
            download(url.url, file_path)
            self.save_progress("ph", i)
        except Exception as e:
            logw(f"Download PH {i} error: {e}")
            self.downloaded = False

    def pk(self, i: int):
        url = self.cfg.pk(i)
        print(f"Downloading page {i}: \n{url.url}")
        file_path = cfg2.dir_path + url.name
        if i in self.progress["pk"]:
            print("Using Cache...")
            return None
        try:
            download(url.url, file_path)
            self.save_progress("pk", i)
        except Exception as e:
            logw(f"Download page {i} error: {e}")
            self.downloaded = False

    def makeswf(self, i: int):
        try:
            level_num = self.cfg.ph_num(i)
            make_swf(
                cfg2.dir_path + self.cfg.ph(level_num).name,
                cfg2.dir_path + self.cfg.pk(i).name,
                cfg2.swf_path + str(i) + ".swf",
            )
        except Exception as e:
            print(f"Can't decompress page {i}! Skipping...")
            logw(str(e))
            self.cfg.p_count -= 1


def get_swf(cfg: gen_cfg):
    max_workers = cfg2.download_workers
    down = downloader(cfg)
    print("Downloading PH...")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for i in range(1, cfg.ph_nums() + 1):
            executor.submit(down.ph, i)
    print("Downloading PK...")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for i in range(1, cfg.p_count + 1):
            executor.submit(down.pk, i)
    if not down.downloaded:
        raise Exception("Downlaod error")
    print("Making pages...")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for i in range(1, cfg.p_count + 1):
            executor.submit(down.makeswf, i)
    print("Donload done. (total page: " + str(cfg.p_count) + ")")


class converter:
    def __init__(self) -> None:
        self.pdf = PdfWriter()
        self.pdflist = set()
        try:
            if cfg2.svgfontface:
                log = os.popen(
                    "java -jar ffdec/ffdec.jar -config textExportExportFontFace=true"
                ).read()
            else:
                log = os.popen(
                    "java -jar ffdec/ffdec.jar -config textExportExportFontFace=flase"
                ).read()
        except Exception as err:
            logw(str(err))

    def set_swf(self, i: int):
        return os.popen(
            "java -jar ffdec/ffdec.jar -header -set frameCount 1 "
            + r(cfg2.swf_path + str(i) + ".swf")
            + " "
            + r(cfg2.swf_path + str(i) + ".swf")
        ).read()

    def swf2svg(self, i: int):
        def execute(num: int):
            dirpath = cfg2.svg_path + str(num) + "/"
            log = os.popen(
                "java -jar ffdec/ffdec.jar -format frame:svg -select 1 -export frame "
                + r(dirpath)
                + " "
                + r(cfg2.swf_path + str(num) + ".swf")
            ).read()
            shutil.move(
                ospath(dirpath + "1.svg"), ospath(cfg2.svg_path + str(i) + "_.svg")
            )
            shutil.rmtree(ospath(dirpath))

        print("Converting page " + str(i) + " to svg...")
        try:
            execute(i)
        except FileNotFoundError:
            log = self.set_swf(i)
            try:
                execute(i)
            except FileNotFoundError:
                print("Can't convert this page! Skipping...")
                logw("SVG converting error: " + log)

    def swf2pdf(self, i: int):
        def execute(num: int):
            dirpath = cfg2.pdf_path + str(num) + "/"
            log = os.popen(
                "java -jar ffdec/ffdec.jar -format frame:pdf -select 1 -export frame "
                + r(dirpath)
                + " "
                + r(cfg2.swf_path + str(num) + ".swf")
            ).read()
            shutil.move(
                ospath(dirpath + "frames.pdf"), ospath(cfg2.pdf_path + str(i) + "_.pdf")
            )
            shutil.rmtree(dirpath)
            shutil.move(
                ospath(cfg2.pdf_path + str(i) + "_.pdf"),
                ospath(cfg2.pdf_path + str(i) + ".pdf"),
            )
            self.pdflist.add(i)

        print("Converting page " + str(i) + " to pdf...")
        try:
            execute(i)
        except FileNotFoundError:
            log = self.set_swf(i)
            try:
                execute(i)
            except FileNotFoundError:
                print("Can't convert this page! Skipping...")
                logw("PDF converting error: " + log)

    def svg2pdf(self, i: int):
        try:
            print(f"Converting page {i} to pdf...")
            cairosvg.svg2pdf(
                url=cfg2.svg_path + str(i) + "_.svg",
                write_to=str(ospath(cfg2.pdf_path + str(i) + ".pdf")),
            )
            self.pdflist.add(i)
        except FileNotFoundError:
            print("Can't convert this page! Skipping...")

    def makepdf(self):
        for i in self.pdflist:
            self.pdf = append_pdf(
                self.pdf, str(ospath(cfg2.pdf_path + str(i) + ".pdf"))
            )


def convert(cfg: gen_cfg):
    print("开始转换...")
    if cfg2.swf2svg:
        print(
            "!! 警告: 此过程可能会在 SVG 转换到 PDF 时使用较多的内存(100MB-10GB)，较高的 CPU 使用率，以及较长的时间。您可以在配置文件中修改线程数以平衡性能 !!"
        )
    else:
        print("!! 警告: 此过程可能会使用较高的 CPU 使用率，以及较长的时间。您可以在配置文件中修改线程数以平衡性能 !!")
    max_workers = cfg2.convert_workers
    doc = converter()
    if not cfg2.swf2svg:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for i in range(1, cfg.p_count + 1):
                executor.submit(doc.swf2pdf, i)
    else:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for i in range(1, cfg.p_count + 1):
                executor.submit(doc.swf2svg, i)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for i in range(1, cfg.p_count + 1):
                executor.submit(doc.svg2pdf, i)
    print("Now start making pdf, please wait...")
    doc.makepdf()
    pdf_name = cfg2.o_dir_path + special_path(cfg.p_name) + ".pdf"
    doc.pdf.write(str(ospath(pdf_name)))
    print("转换完成！")
    print("已将文件保存至 " + pdf_name)
    print(
        "Tip: 在 Edge 中查看文档可能会无法正常显示文本，但您也可以使用其他阅读器，例如 Chrome。"
    )


def clean(cfg2):
    print("正在清理缓存...")
    shutil.rmtree(ospath(cfg2.swf_path))
    shutil.rmtree(ospath(cfg2.pdf_path))
    shutil.rmtree(ospath(cfg2.svg_path))
    for i in os.listdir(ospath(cfg2.dir_path)):
        if i.endswith(".ebt"):
            os.remove(ospath(cfg2.dir_path + i))
        elif i == "progress.json":
            os.remove(ospath(cfg2.dir_path + i))


class mode:
    def __init__(self) -> None:
        self.encode = ""

    def url(self):
        try:
            url = input("请输入网址：")
        except KeyboardInterrupt:
            exit()
        try:
            return main(get_cfg(url).data, cfg2.get_more)
        except Exception as Err:
            print(Err)
            return False

    def pcode(self):
        try:
            p_code = input("请输入id：")
        except KeyboardInterrupt:
            exit()
        try:
            return main(
                get_cfg(f"https://www.doc88.com/p-{p_code}.html").data, cfg2.get_more
            )
        except Exception as Err:
            print(Err)
            return False

    def data(self):
        try:
            data = input("请输入init_data：")
        except KeyboardInterrupt:
            exit()
        try:
            return main(data, cfg2.get_more)
        except Exception as Err:
            print(Err)
            return False


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    print("\033[36m" + r"""
    ╔══════════════════════════════════════════╗
    ║       DOC88 文档提取工具 V1.8           ║
    ║            by: Cuite_Piglin              ║
    ╚══════════════════════════════════════════╝
    """ + "\033[0m")


def print_menu():
    print("\033[33m" + "  ── 主菜单 ──" + "\033[0m")
    print("  1. 通过网址下载文档")
    print("  2. 通过文档 ID 下载")
    print("  3. 通过 init_data 下载")
    print("  4. 查看当前配置")
    print("  5. 修改配置")
    print("  6. 检查更新")
    print("  7. 清理文档缓存")
    print("  0. 退出")
    print()


def show_config():
    print("\033[33m" + "  ── 当前配置 ──" + "\033[0m")
    items = [
        ("输出目录", cfg2.o_dir_path),
        ("代理地址", cfg2.proxy_url),
        ("SWF 目录", cfg2.o_swf_path),
        ("PDF 目录", cfg2.o_pdf_path),
        ("SVG 目录", cfg2.o_svg_path),
        ("自动检查更新", "是" if cfg2.check_update else "否"),
        ("SWF 转 SVG", "是" if cfg2.swf2svg else "否"),
        ("SVG Font-Face", "是" if cfg2.svgfontface else "否"),
        ("完成后清理", "是" if cfg2.clean else "否"),
        ("扫描额外页面", "是" if cfg2.get_more else "否"),
        ("路径替换", "是" if cfg2.path_replace else "否"),
        ("下载线程数", str(cfg2.download_workers)),
        ("转换线程数", str(cfg2.convert_workers)),
    ]
    for label, value in items:
        print(f"  \033[90m{label:<14}\033[0m {value}")
    print()


def modify_config():
    print("\033[33m" + "  ── 修改配置 (直接回车保持原值) ──" + "\033[0m")

    def ask(key, current, hint=""):
        h = f" ({hint})" if hint else ""
        val = input(f"  {key}{h} [{current}]: ").strip()
        if isinstance(current, bool):
            if val.lower() in ("true", "1", "y", "yes"):
                return True
            elif val.lower() in ("false", "0", "n", "no"):
                return False
            return current
        if isinstance(current, int):
            try:
                return int(val)
            except ValueError:
                return current
        return val if val else current

    cfg2.o_dir_path = ask("输出目录", cfg2.o_dir_path)
    cfg2.proxy_url = ask("代理地址", cfg2.proxy_url)
    cfg2.o_swf_path = ask("SWF 目录", cfg2.o_swf_path)
    cfg2.o_pdf_path = ask("PDF 目录", cfg2.o_pdf_path)
    cfg2.o_svg_path = ask("SVG 目录", cfg2.o_svg_path)
    cfg2.check_update = ask("自动检查更新", cfg2.check_update, "y/n")
    cfg2.swf2svg = ask("SWF 转 SVG", cfg2.swf2svg, "y/n")
    cfg2.svgfontface = ask("SVG Font-Face", cfg2.svgfontface, "y/n")
    cfg2.clean = ask("完成后清理", cfg2.clean, "y/n")
    cfg2.get_more = ask("扫描额外页面", cfg2.get_more, "y/n")
    cfg2.path_replace = ask("路径替换", cfg2.path_replace, "y/n")
    cfg2.download_workers = ask("下载线程数", cfg2.download_workers)
    cfg2.convert_workers = ask("转换线程数", cfg2.convert_workers)
    cfg2.save()
    print("\033[32m  配置已保存！\033[0m\n")


def clean_cache():
    docs_dir = cfg2.o_dir_path[0:-1] if cfg2.o_dir_path.endswith("/") else cfg2.o_dir_path
    if not os.path.isdir(docs_dir):
        print("\033[33m  文档目录不存在，无需清理。\033[0m\n")
        return
    subdirs = os.listdir(docs_dir)
    if not subdirs:
        print("\033[33m  文档目录为空，无需清理。\033[0m\n")
        return
    print(f"\033[33m  ── 文档列表 ──\033[0m")
    for i, name in enumerate(subdirs):
        print(f"  {i + 1}. {name}")
    print(f"  0. 全部清理")
    choice = input("\n  输入编号清理 (0=全部, 回车取消): ").strip()
    if not choice:
        return
    if choice == "0":
        if input("  确定清理所有文档？(y/N): ").strip().lower() == "y":
            shutil.rmtree(ospath(docs_dir))
            os.makedirs(docs_dir)
            print("\033[32m  已清理全部文档。\033[0m\n")
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(subdirs):
                target = os.path.join(docs_dir, subdirs[idx])
                shutil.rmtree(ospath(target))
                print(f"\033[32m  已清理: {subdirs[idx]}\033[0m\n")
            else:
                print("\033[31m  编号无效。\033[0m\n")
        except ValueError:
            print("\033[31m  无效输入。\033[0m\n")


def interactive_menu():
    user = mode()
    options = {
        "1": lambda: user.url(),
        "2": lambda: user.pcode(),
        "3": lambda: user.data(),
        "4": lambda: (show_config(), None)[1],
        "5": lambda: (modify_config(), None)[1],
        "6": lambda: (update.check_update(), None)[1],
        "7": lambda: (clean_cache(), None)[1],
    }
    while True:
        clear_screen()
        print_banner()
        print_menu()
        choice = input("\033[36m  请选择 [0-7]: \033[0m").strip()
        if choice == "0":
            print("\033[33m  再见！\033[0m")
            break
        action = options.get(choice)
        if action:
            print()
            result = action()
            if choice in ("1", "2", "3"):
                if result:
                    update.gen_indexs()
                    if cfg2.clean:
                        try:
                            clean(cfg2)
                        except NameError:
                            pass
            input("\033[90m  按回车键继续...\033[0m")
        else:
            input("\033[31m  无效选择，按回车键继续...\033[0m")


if __name__ == "__main__":
    print("正在初始化...", flush=True)
    update=Update(cfg2)
    java_ok = update.check_java()
    if not java_ok:
        print("\033[33m警告: Java 未安装或配置异常，SWF 转换功能将不可用。\033[0m", flush=True)
        print("请安装 Java 后再进行文档转换。\n", flush=True)
    update.upgrade()
    print("初始化完成！\n", flush=True)
    a = sys.argv
    if len(a) > 1 and "-p" in a:
        user = mode()
        while True:
            if user.pcode():
                update.gen_indexs()
                if cfg2.clean:
                    try:
                        clean(cfg2)
                    except NameError:
                        pass
                if choose():
                    pass
                else:
                    exit()
            else:
                pass
    elif len(a) > 1 and "-d" in a:
        user = mode()
        while True:
            if user.data():
                update.gen_indexs()
                if cfg2.clean:
                    try:
                        clean(cfg2)
                    except NameError:
                        pass
                if choose():
                    pass
                else:
                    exit()
            else:
                pass
    else:
        interactive_menu()


# https://www.doc88.com/p-74787813372750.html