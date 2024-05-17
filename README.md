# Stopwrdz

## Description

**Stopwrdz**

Stopwrdz is a command-line tool designed to replace prohibited stop words in video titles and captions, specifically tailored for compliance with TikTok's guidelines.


## Key Features

- Stop-word replacement in video titles
- Configurable through command line arguments
- Easily deployable

## Dependencies

To run this project, ensure you have the following Python libraries installed:

```bash
pip install langdetect chardet
```

### langdetect
https://pypi.org/project/langdetect/

langdetect supports 55 languages out of the box (ISO 639-1 codes):
```bash
af, ar, bg, bn, ca, cs, cy, da, de, el, en, es, et, fa, fi, fr, gu, he,
hi, hr, hu, id, it, ja, kn, ko, lt, lv, mk, ml, mr, ne, nl, no, pa, pl,
pt, ro, ru, sk, sl, so, sq, sv, sw, ta, te, th, tl, tr, uk, ur, vi, zh-cn, zh-tw
```

### chardet
https://pypi.org/project/chardet/

Chardet: The Universal Character Encoding Detector

Detects:
```bash
ASCII, UTF-8, UTF-16 (2 variants), UTF-32 (4 variants)
Big5, GB2312, EUC-TW, HZ-GB-2312, ISO-2022-CN (Traditional and Simplified Chinese)
EUC-JP, SHIFT_JIS, CP932, ISO-2022-JP (Japanese)
EUC-KR, ISO-2022-KR, Johab (Korean)
KOI8-R, MacCyrillic, IBM855, IBM866, ISO-8859-5, windows-1251 (Cyrillic)
ISO-8859-5, windows-1251 (Bulgarian)
ISO-8859-1, windows-1252, MacRoman (Western European languages)
ISO-8859-7, windows-1253 (Greek)
ISO-8859-8, windows-1255 (Visual and Logical Hebrew)
TIS-620 (Thai)
```


## Usage

### Windows, Linux

```bash
python stopwrdz.py "C:\Users\user\Downloads\title.srt"
python3 stopwrdz.py C:\Users\user\Downloads\title.srt
```

## Examples

(TO-DO: Add examples demonstrating the tool's features)

## License

This project is licensed under the MIT License.

## Support

For more information or questions, please feel free to reach out:

- **Contact Person**: Osvald
- **Email**: [trustvlking@gmail.com](mailto: trustvlking@gmail.com)