# -*- coding: utf-8 -*-
"""解析 Word (.docx) 简历文本 —— 纯标准库实现（zipfile + XML 解析，无需第三方依赖）

用法：
    .venv\\Scripts\\python.exe parse_resume.py "C:\\Users\\jiang\\Desktop\\Word\\杨恒-桌面运维-三年.docx"
"""
import sys
import xml.etree.ElementTree as ET
import zipfile

W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def docx_text(path):
    """提取 .docx 全部段落文本（含表格单元格里的段落）"""
    with zipfile.ZipFile(path) as z:
        xml_bytes = z.read("word/document.xml")
    root = ET.fromstring(xml_bytes)
    lines = []
    for p in root.iter(f"{W_NS}p"):
        text = "".join(t.text or "" for t in p.iter(f"{W_NS}t"))
        text = text.strip()
        if text:
            lines.append(text)
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: parse_resume.py <简历.docx>")
        sys.exit(1)
    print(docx_text(sys.argv[1]))
