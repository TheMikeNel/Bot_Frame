from configparser import ConfigParser

def get_conf(sec, opt) -> str:
    conf = ConfigParser()
    conf.read('config.ini')
    return conf.get(section=sec, option=opt)

class Server:
    host = get_conf('Server', 'host') 
    psql_url = get_conf('Server', 'psql_url')
    redis_url = get_conf('Server', 'redis_url')

class Telebot:
    token = get_conf('Telebot', 'bot_token')
    test_token = get_conf('Telebot', 'test_bot_token')

class Commands:
    menu = get_conf('Commands', 'menu')
    clear = get_conf('Commands', 'clear')
    exit = get_conf('Commands', 'exit')
    admin = get_conf('Commands', 'admin')

class Stickers:
    jobs = get_conf('Stickers', 'jobs')
    admin = get_conf('Stickers', 'admin')