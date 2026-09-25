# -*- coding: utf-8 -*-
"""
Java 运行时定位模块

doc88 提取工具依赖 ffdec（JPEXS Flash Decompiler），而 ffdec 需要 Java 才能运行。
很多“不好使”的情况其实是系统里的 java 不可用（比如 PATH 中被其它软件注入了无效的
java 启动器、JAVA_HOME 指向了不存在的目录等），导致每一次转换都直接失败。

本模块按以下顺序寻找一个“真正能跑起来”的 java.exe：
  1. 程序目录下的便携 JRE（jre/bin/java.exe，可用 download_jre 自动获取）
  2. JAVA_HOME/bin/java.exe
  3. 常见安装目录（Program Files 下的 Java / Eclipse Adoptium / Microsoft 等）
  4. PATH 中的 java.exe
找到后会用 `java -version` 实际验证，能正常输出版本才采用，
从而自动跳过那些“看似存在、实际一启动就崩溃”的无效 java。
"""
import os
import subprocess

_BASE = os.path.dirname(os.path.abspath(__file__))
_java_path = None

# JRE 下载地址：Adoptium Temurin JRE 17（与 README 推荐的 Java 17 一致）
JRE_DOWNLOAD_URL = (
    "https://api.adoptium.net/v3/binary/latest/17/ga/windows/x64/"
    "jre/hotspot/normal/eclipse"
)


def portable_java():
    """程序目录下的便携 JRE 路径（jre/bin/java.exe）。"""
    return os.path.join(_BASE, "jre", "bin", "java.exe")


def ffdec_jar():
    """程序目录下的 ffdec.jar 绝对路径。"""
    return os.path.join(_BASE, "ffdec", "ffdec.jar")


def _java_version_ok(java_path):
    """启动一次 java -version，只有能正常返回 0 才认为可用。"""
    try:
        p = subprocess.run(
            [java_path, "-version"],
            capture_output=True,
            timeout=25,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        return p.returncode == 0
    except Exception:
        return False


def _candidates():
    cands = []
    cands.append(portable_java())
    jh = os.environ.get("JAVA_HOME", "").strip().strip('"')
    if jh:
        cands.append(os.path.join(jh, "bin", "java.exe"))
    roots = [
        r"C:\Program Files\Java",
        r"C:\Program Files\Eclipse Adoptium",
        r"C:\Program Files\Microsoft",
        r"C:\Program Files\Zulu",
        r"C:\Program Files\Amazon Corretto",
        r"C:\Program Files\BellSoft",
        r"C:\Program Files\Red Hat",
        r"C:\Program Files (x86)\Java",
        r"C:\Program Files (x86)\Eclipse Adoptium",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs"),
        os.path.expandvars(r"%USERPROFILE%\.jdks"),
    ]
    for root in roots:
        if not os.path.isdir(root):
            continue
        try:
            names = sorted(os.listdir(root), key=str.lower, reverse=True)
        except OSError:
            continue
        for name in names:
            j = os.path.join(root, name, "bin", "java.exe")
            if os.path.isfile(j):
                cands.append(j)
    for p in os.environ.get("PATH", "").split(os.pathsep):
        p = p.strip().strip('"')
        if p:
            cands.append(os.path.join(p, "java.exe"))
    return cands


def find_java():
    """返回一个可用的 java.exe 绝对路径；找不到返回 None（成功结果会被缓存）。"""
    global _java_path
    if _java_path and os.path.isfile(_java_path):
        return _java_path
    seen = set()
    for j in _candidates():
        try:
            j = os.path.normpath(os.path.abspath(j))
        except Exception:
            continue
        if j in seen:
            continue
        seen.add(j)
        if os.path.isfile(j) and _java_version_ok(j):
            _java_path = j
            return j
    return None
