"""pyPengIm：潮州话（潮汕话）文本处理工具。

    from pypengim import pyPengIm
    tool = pyPengIm()
    tool.pinyin('潮汕人食糜')

数据文件放在包内的 ``pypengim/data/``，与当前工作目录无关。
主类依赖 jieba、cn2an，按需加载：只用 ``pypengim.accent`` / ``pypengim.romanization`` 时不需要安装它们。
"""
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

__all__ = ['pyPengIm', 'PyPengIm', 'AccentConverter', 'romanization', 'utils', 'DATA_DIR']
__version__ = '0.2.0'


def __getattr__(name):
    if name in ('pyPengIm', 'PyPengIm'):
        from .core import pyPengIm
        return pyPengIm          # PyPengIm 是符合 PEP 8 的别名
    if name == 'AccentConverter':
        from .accent import AccentConverter
        return AccentConverter
    if name in ('romanization', 'utils', 'accent', 'core', 'syllable'):
        import importlib
        return importlib.import_module('.' + name, __name__)
    raise AttributeError("module 'pypengim' has no attribute '{}'".format(name))
