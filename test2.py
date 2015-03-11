__author__ = 'faianca'
import ConfigParser

config = ConfigParser.RawConfigParser()

config.add_section('themes')
config.add_section('config')
config.set('themes', 'green', 'styles/green')
config.set('themes', 'black', 'styles/black')

config.set('config', 'default_theme', 'green')

# Writing our configuration file to 'example.cfg'
with open('config/config.cfg', 'wb') as configfile:
    config.write(configfile)