from setuptools import setup

setup(
    name='go_to_bed',
    version='1.0',
    description='A useful module',
    author='Jerry Wu, Yingzhuo Yang',
    author_email='zw1711@nyu.edu, yy3826@nyu.edu',
    url='https://github.com/JerryWuZiJie/go_to_bed',
    install_requires=['pygame>=2.1.2', 'schedule>=1.1.0',
                      'luma>=2.1.4', 'luma.led_matrix>=1.6.1', 'pyttsx3>=2.90'],
    py_modules=['go_to_bed'],
)
