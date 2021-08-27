import time, pickle
from socket import AF_INET, SOCK_STREAM, socket
import config
import argparse
from logs.config_log.log_config import init_log

log = init_log('client_log')


def create_presence_meassage(account_name='Guest'):
    log.info('Формирования сообщения')
    if len(account_name) > 25:
        log.error('Имя пользователя более 25 символов')
        raise ValueError
    if not isinstance(account_name, str):
        log.error("Имя пользователя не является строкой символов")
        raise TypeError

    message = {
        config.ACTION: config.PRESENCE,
        config.TIME: time.time(),
        config.USER: {
            config.ACCOUNT_NAME: account_name
        }
    }
    return message


def start_client(serv_addr=config.server_address, serv_port=config.server_port, action=config.PRESENCE):
    log.info('Старт клиенского проложения')
    s = socket(AF_INET, SOCK_STREAM)

    if not isinstance(serv_addr, str) or not isinstance(serv_port, int):
        log.error('Полученный адрес сервера или порт не является строкой или числом!')
        s.close()
        raise ValueError
    try:
        if config.server_address != '0.0.0.0':
            s.connect((config.server_address, config.server_port))
        else:
            s.connect(('localhost', config.server_port))
    except Exception as e:
        log.error(f'Ошибка подключения:{e}')
        s.close()
        raise Exception

    message = create_presence_meassage()
    if isinstance(message, dict):
        message = pickle.dumps(message)
    log.info(f"Отравляю сообщение {message} на сервер")
    s.send(message)
    log.info("Ожидаем ответ")
    server_response = pickle.loads(s.recv(1024))
    log.info(f"Ответ с сервера: {server_response}")
    if server_response.get('response') == 200:
        log.info("Соеденение с сервером установленно")
    else:
        log.error("Не известная ошибка")
    s.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='JSON instant messaging'
    )

    parser_group = parser.add_argument_group(title='Parameters')
    parser_group.add_argument('-a', '--addr', default=config.server_address, help='IP address')
    parser_group.add_argument('-p', '--port', type=int, default=config.server_port, help='TCP port')
    start_client('132.0.0.0', 21)
