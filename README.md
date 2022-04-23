# unicode-textwrapper
The official Python `textwrap` library only works for US-ASCII characters. This project will inherit from that class and add some additional support for unicode characters with different East Asian Width properties. 

This will particularly benefit languages like Chinese, Japanese and Korean which regularly use full-width or wide variants.


## About East Asian Width
Asian characters are typically twice as wide as western characters, for reasons of readability and aestheticness. For this reason, Unicode provides an East Asian Width property that specifies how wide a character should be displayed. Additional information about halfwidth and fullwidth forms can be found [here](https://en.wikipedia.org/wiki/Halfwidth_and_fullwidth_forms).

Code that assumes the width of a string is precisely equivalent to the number of characters it contains will not work properly for East Asian langauges.


## Sample Usage
The class inherits from the `TextWrapper` class from the Python Standard Library. Documentation for the `TextWrapper` class can be found on [docs.python.org](https://docs.python.org/3/library/textwrap.html). Here is one sample usage:

```python
from eawtextwrap import EAWTextWrapper
import os

# japanese text sourced from: https://www.aozora.gr.jp/cards/000879/files/60_15129.html
text = "堀川の大殿様おほとのさまのやうな方は、これまでは固もとより、後の世には恐らく二人とはいらつしやいますまい。噂に聞きますと、あの方の御誕生になる前には、大威徳明王だいゐとくみやうおうの御姿が御母君おんはゝぎみの夢枕にお立ちになつたとか申す事でございますが、兎とに角かく御生れつきから、並々の人間とは御違ひになつてゐたやうでございます。でございますから、あの方の為なさいました事には、一つとして私どもの意表に出てゐないものはございません。早い話が堀川のお邸の御規模を拝見致しましても、壮大と申しませうか、豪放と申しませうか、到底たうてい私どもの凡慮には及ばない、思ひ切つた所があるやうでございます。中にはまた、そこを色々とあげつらつて大殿様の御性行を始皇帝しくわうていや煬帝やうだいに比べるものもございますが、それは諺ことわざに云ふ群盲ぐんもうの象を撫なでるやうなものでもございませうか。"

terminal_width = os.get_terminal_size().columns
wrapper = eawtextwrap.EAWTextWrapper(width=terminal_width, subsequent_indent = '        ')
print('\n'.join(wrapper.wrap(text)))

```

## Disclaimer
This code was written in April 2022 and inherits from the Python `textwrap` library. Sections of code are adapted from the [original source code](https://github.com/python/cpython/blob/3.10/Lib/textwrap.py) for the purpose of writing appropriate overriding functions. Any substantial future updates to the parent class could cause breaking changes. 

This work is a personal project and comes with no guarantees. Under no circumstances is the author liable for any direct or indirect consequences from the usage of this code. 
