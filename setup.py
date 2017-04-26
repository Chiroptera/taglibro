from setuptools import setup

setup(
    name='taglibro',
    version='0.02',
    description='simply journaling app',
    author='Diogo Silva',
    author_email='hi@diogoaos.eu',
    url='https://www.github.com/diogo-aos/taglibro',
    packages=['taglibro'],
    include_package_data=True,
    install_requires=[
        'flask', 'gevent', 'markdown2'
    ],
    scripts=['bin/taglibro_app', 'bin/taglibro']
)
