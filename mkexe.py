from distutils.core import setup
import py2exe,os,sys
os.system('rm -rf build dist')
sys.argv.append('py2exe')
setup(
    console = ["decoder.py"],
    options={"py2exe":{'bundle_files': 1, 'compressed': True}},
    zipfile=None
)
os.system('mv dist/* ./')
os.system('rm -rf build dist')
os.system('cp C:/MathPlot/gnuplot/bin/*.exe gnuplot/')
os.system('cp C:/MathPlot/gnuplot/bin/*.dll gnuplot/')
os.system('cp C:/MathPlot/gnuplot/bin/*.chm gnuplot/')
os.system('cp C:/MathPlot/gnuplot/docs/*.pdf gnuplot/')
