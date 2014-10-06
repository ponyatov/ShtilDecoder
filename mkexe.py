from distutils.core import setup
import py2exe
setup(
      console = ["decoder.py"],
      options={"py2exe":{}}
# #     windows=[{"script":"main.py"}],
#     options={"py2exe": {"includes":["sip"]}}
)
