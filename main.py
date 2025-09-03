from web3 import Web3
import json

# RPC-URL для сети Linea
RPC_URL = 'https://rpc.linea.build'

# Адрес контракта
CONTRACT_ADDRESS = "0x87bAa1694381aE3eCaE2660d97fe60404080Eb64"

# ABI контракта, сокращённый до нужной функции
# Используем json.loads, чтобы Python распознал строку как список
ABI = json.loads('''
[
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_account",
        "type": "address"
      }
    ],
    "name": "calculateAllocation",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "tokenAllocation",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  }
]
''')

def main():
    try:
        # Подключение к провайдеру
        w3 = Web3(Web3.HTTPProvider(RPC_URL))

        # Проверка подключения
        if not w3.is_connected():
            print("Ошибка: Не удалось подключиться к Ethereum-сети. Проверьте ваш RPC-URL.")
            return

        # Создание экземпляра контракта
        contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

        # Открытие и чтение адресов из файла
        wallets_file = 'addresses.txt'
        try:
            with open(wallets_file, 'r') as f:
                wallets = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Ошибка: Файл '{wallets_file}' не найден. Пожалуйста, создайте его и добавьте адреса кошельков.")
            return

        # Проверка, что файл не пуст
        if not wallets:
            print(f"Предупреждение: Файл '{wallets_file}' пуст. Пожалуйста, добавьте адреса кошельков в файл.")
            return

        print(f"Начинаем проверку аллокаций для {len(wallets)} адресов...")
        print("-" * 30)
        
        # Переменная для хранения общей суммы аллокаций в Wei
        total_allocation_wei = 0

        # Перебор каждого адреса в списке
        for wallet_address in wallets:
            try:
                # Преобразование адреса в формат контрольной суммы
                checksum_address = Web3.to_checksum_address(wallet_address)
                
                # Вызов функции calculateAllocation
                allocation_wei = contract.functions.calculateAllocation(checksum_address).call()

                # Добавление аллокации к общей сумме
                total_allocation_wei += allocation_wei

                # Преобразование значения из Wei в токены
                allocation = w3.from_wei(allocation_wei, 'ether')
                
                print(f"Адрес: {wallet_address}\nАллокация токенов: {allocation}\n")

            except Exception as e:
                print(f"Ошибка при обработке адреса {wallet_address}: {e}\n")

        # Вывод общей суммы аллокаций
        print("-" * 30)
        total_allocation = w3.from_wei(total_allocation_wei, 'ether')
        print(f"Общая аллокация для всех кошельков: {total_allocation}\n")
        print("Проверка завершена.")

    except Exception as e:
        print(f"Произошла глобальная ошибка: {e}")

if __name__ == "__main__":
    main()
