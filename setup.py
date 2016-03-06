from setuptools import setup

extra = {}

try:
    from trac.util.dist  import  get_l10n_cmdclass
    cmdclass = get_l10n_cmdclass()
    if cmdclass:
        extra['cmdclass'] = cmdclass
        extractors = [
#            ('**.py',                'python', None),
            ('**/templates/**.html', 'genshi', None),
        ]
        extra['message_extractors'] = {
            'customdbtable': extractors,
        }
except:
    pass

setup(
    name='TracCustomDBTablePlugin',
    #description='',
    #keywords='',
    #url='',
    version='0.1',
    #license='',
    #author='',
    #author_email='',
    #long_description="",
    packages=['customdbtable'],
    package_data={
        'customdbtable': [
            'templates/*.html',
#            'locale/*/LC_MESSAGES/*.mo',
        ]
    },
    entry_points={
        'trac.plugins': [
            'customdbtable.api = customdbtable.api',
            'customdbtable.web_ui = customdbtable.web_ui',
        ]
    },
#    **extra
)
