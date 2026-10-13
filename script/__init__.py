"""兼容层：旧代码 ``from script.pyPengIm import pyPengIm`` 仍可使用。

代码已迁移到 ``pypengim`` 包，请改用 ``from pypengim import pyPengIm``。本兼容层将在后续版本删除。
"""
import sys
import warnings

import pypengim
from pypengim import accent, core, romanization, syllable, utils

warnings.warn('script 包已迁移到 pypengim，请改用 from pypengim import pyPengIm',
              DeprecationWarning, stacklevel=2)

# 让 script.xxx 与 pypengim.xxx 指向同一个模块对象
for _name, _module in {'pyPengIm': core, 'accent': accent, 'romanization': romanization,
                       'syllable': syllable, 'utils': utils}.items():
    sys.modules[__name__ + '.' + _name] = _module
    setattr(sys.modules[__name__], _name, _module)
