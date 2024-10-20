import asyncio
import os

from loguru import logger

from functions.create_files import create_files
from functions.Import import Import
from data.models import Settings
from utils.db_api.wallet_api import get_wallets
from utils.db_api.models import Wallet
from withdrawal.main import okx_withdraw
from functions.initial import initial
from functions.activity import activity
from libs.eth_async.client import Client
from libs.eth_async.data.models import Networks


async def create_wallets():
    file_path = 'new_wallets.csv'
    if os.path.exists(file_path):
        answer = print('The wallet file is already exists\n'
                       'New wallets will be added to the end of the file')
    number = int(input('How many wallets do you want to create? (1 - 10000): '))
    try:
        if number < 1:
            number = 1
        elif number > 10000:
            number = 10000
        for _ in range(number):
            client = Client(network=Networks.Ethereum)
            with open(file_path, 'a') as f:
                f.write(f'{client.account.address}, {client.account.key.hex()}\n')
    except KeyboardInterrupt:
        print()

    except ValueError as err:
        logger.error(f'Value error: {err}')

    except BaseException as e:
        logger.error(f'Something went wrong: {e}')
    await choose_action()


async def start_script():
    settings = Settings()

    if not settings.oklink_api_key:
        logger.error('Specify the API key for oklink explorer!')
        return

    await asyncio.wait([asyncio.create_task(initial()), asyncio.create_task(activity())])


async def start_okx_withdraw():
    settings = Settings()
    if not settings.okx.credentials.completely_filled():
        logger.error('OKX credentials not filled')
        return
    wallets: list[Wallet] = get_wallets()
    await okx_withdraw(wallets=wallets)


async def choose_action():
    print('''  Select the action:
    1) Create new wallets to file
    2) Import wallets from the spreadsheet to the DB;
    3) Start the script;
    4) Start withdraw ETH from OKX
    5) Exit.''')
    try:
        action = int(input('> '))
        if action == 1:
            await create_wallets()

        if action == 2:
            await Import.wallets()

        elif action == 3:
            await start_script()

        elif action == 4:
            await start_okx_withdraw()

        elif action == 5:
            raise SystemExit(0)

        else:
            raise SystemExit(1)

    except KeyboardInterrupt:
        print()

    except SystemExit as err:
        logger.info(f'SystemExit. Code: {err}')
        raise SystemExit(err)

    except ValueError as err:
        logger.error(f'Value error: {err}')
        raise SystemExit(1)

    except BaseException as e:
        logger.error(f'Something went wrong: {e}')
        raise SystemExit(1)

async def main():
    await choose_action()

if __name__ == '__main__':
    create_files()
    asyncio.run(main())
