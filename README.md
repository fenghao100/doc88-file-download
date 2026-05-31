# 这是啥 WHAT IS THIS

## 简介 / Introduction

感谢开源者
一个可以完整提取道客巴巴预览文档（非截图）的工具。这个代码不是我写的，我从别的github中本地跑了一下，又上传到自己的github做保存的  
A tool to extract and convert doc88 documents (non-screenshot). \n
环境安装：
-     1、安装python
-     2、安装python依赖
-     3、安装java
-     4、cairosvg
-     5、安装gtk
-     6、安装ffdec(如果没有这个文件夹，自己创建一个)
-     7、下载合成的文档在doc文件夹下
- 注意：这个代码只是为了大家使用，所以发现里面有部分功能逻辑待补全，请正确使用。

## 特点 / Featuresdocd

- 利用 [JPEXS Free Flash Decompiler](https://github.com/jindrapetrik/jpexs-decompiler) (以下简称 ffdec) 工具，几乎完美转换文档，保留原始文本、形状与图片。  
    Powered by [JPEXS Free Flash Decompiler](https://github.com/jindrapetrik/jpexs-decompiler), this tool preserves original text, shapes, and images—almost identical to the source.
- 适用文档范围：几乎所有  
    It's available for almost all documents.
    
## 安装 / Installation

### Python

- 需要 Python 3.10 或更高版本。  
    Requires Python 3.10 or newer.

安装依赖：

```bash
pip3 install retrying pypdf requests
```

### Java

- 需要安装 Java 才能进行文档转换（推荐 Java 17）:
    <br>Requires Java (recommended: version 17):
    <br>[Microsoft Build of OpenJDK 17 for Windows x64](https://aka.ms/download-jdk/microsoft-jdk-17.0.14-windows-x64.msi)

### SVG 转换 / SVG Converting

- 若启用 swf2svg，需安装 cairosvg 以实现 SVG 到 PDF 的转换。  
    If swf2svg is enabled, install cairosvg:

```bash
pip3 install cairosvg
```

- Windows 用户还需安装 GTK Runtime：
    <br>For Windows, also install GTK Runtime:
    <br>[GTK Runtime](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases)


```bash
ffdec安装
```
- 如果ffdec文件夹下没有内容，需要下载并解压放到ffdec目录下
- <br>[ffdec](https://release-assets.githubusercontent.com/github-production-release-asset/19647328/f4b8bbf8-5efc-4fea-8261-059c43e17485?sp=r&sv=2018-11-09&sr=b&spr=https&se=2025-11-18T15%3A17%3A44Z&rscd=attachment%3B+filename%3Dffdec_24.1.1.zip&rsct=application%2Foctet-stream&skoid=96c2d410-5711-43a1-aedd-ab1947aa7ab0&sktid=398a6654-997b-47e9-b12b-9515b896b4de&skt=2025-11-18T14%3A17%3A10Z&ske=2025-11-18T15%3A17%3A44Z&sks=b&skv=2018-11-09&sig=js8mDzHkVtjDUZmjmy6%2FjXOJgI5tPgdc4fhH9MWUA7k%3D&jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmVsZWFzZS1hc3NldHMuZ2l0aHVidXNlcmNvbnRlbnQuY29tIiwia2V5Ijoia2V5MSIsImV4cCI6MTc2MzQ3NzQ0MSwibmJmIjoxNzYzNDc1NjQxLCJwYXRoIjoicmVsZWFzZWFzc2V0cHJvZHVjdGlvbi5ibG9iLmNvcmUud2luZG93cy5uZXQifQ.pRSLpUpMhNVqXLByeXydOXPzNO8rHWZs1AAHIk7nQxU&response-content-disposition=attachment%3B%20filename%3Dffdec_24.1.1.zip&response-content-type=application%2Foctet-stream)


## 如何使用 / How to Use

在程序目录下运行：

```bash
python3 main.py
```

- 控制台输入网址并回车。  
    Enter the URL in the console.
- 首次运行会生成配置文件，检测更新并下载 ffdec。  
    On first run, there will be a configuration file `config.json`, then check the updates and download the ffdec.


## 配置 / Configuration
### 说明 / Description
默认情况下配置在 `config.json` 文件中，主要说明如下：

| 键名 / Key         | 说明                                                              | Description                                                                   |
| ------------------ | ----------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `proxy_url`        | Github 代理服务的 URL                                             | The URL of Github's proxy service.                                            |
| `check_update`     | 是否在启动时检查更新                                              | Always check updates on startup.                                              |
| `swf2svg`          | 是否先转换到 SVG 再转到 PDF                                       | Convert swf files to svg first.                                               |
| `svgfontface`      | （仅 swf2pdf 为 false 时有效）在 SVG 转换中是否转换字体来呈现文本 | Only works when swf2pdf is false; using font to show texts in SVG converting. |
| `clean`            | 是否保留中间文件                                                  | Keep intermediate files.                                                      |
| `get_more`         | 是否始终通过扫描获取页面                                          | Always via scanning to get pages.                                             |
| `path_replace`     | 是否在 Windows 下替换过长路径                                     | Replace long paths on Windows.                                                |
| `download_workers` | 下载文件的线程数                                                  | Number of threads for downloading files.                                      |
| `convert_workers`  | 转换文件的线程数                                                  | Number of threads for converting files.                                       |

### 注意事项 / Attention
- 使用 `swf2svg` 选项，也许会解决部分文档的字体形状问题（不能解决字体不全的问题，原始文件为了压缩大小，减去了未使用的字）
- 若启用 `svgfontface` 选项，由于 `cairosvg` 的缺陷，会导致在 PDF 转换过程中出现大量问题，不推荐使用
