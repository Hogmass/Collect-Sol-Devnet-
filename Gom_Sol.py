import asyncio
import random
from base58 import b58decode
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import ID as SYSTEM_PROGRAM_ID, transfer, TransferParams
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction
from colorama import init, Fore

init(autoreset=True)

# Load ví nhận
with open("wallet.txt", "r") as f:
    receiver_address = f.readline().strip()
receiver_pubkey = Pubkey.from_string(receiver_address)

# Load private keys dạng base58
with open("private.txt", "r") as f:
    private_keys = [line.strip() for line in f if line.strip()]

# Kết nối đến Devnet
client = AsyncClient("https://api.devnet.solana.com")

async def send_sol(base58_key, thread_id):
    try:
        secret = b58decode(base58_key)
        sender = Keypair.from_bytes(secret)
        sender_pubkey = sender.pubkey()

        # Lấy balance
        resp = await client.get_balance(sender_pubkey)
        lamports = resp.value
        sol_balance = lamports / 1e9

        if lamports < 5000:
            print(Fore.YELLOW + f"[⚠️] Thread {thread_id}: Số dư thấp ({sol_balance:.5f} SOL)")
            return

        amount = lamports - 5000  # trừ phí

        ix = transfer(
            TransferParams(
                from_pubkey=sender_pubkey,
                to_pubkey=receiver_pubkey,
                lamports=amount,
            )
        )
        tx = Transaction().add(ix)
        sig = await client.send_transaction(tx, sender)

        if sig.value:
            print(Fore.GREEN + f"[✅] Thread {thread_id}: Gửi thành công! Hash: {sig.value}")
        else:
            print(Fore.RED + f"[❌] Thread {thread_id}: Lỗi khi gửi: {sig}")
    except Exception as e:
        print(Fore.RED + f"[❌] Thread {thread_id}: Lỗi - {e}")
    finally:
        delay = round(random.uniform(1.5, 3.5), 2)
        print(Fore.CYAN + f"[⏳] Đợi {delay} giây...")
        await asyncio.sleep(delay)

async def main():
    num_threads = random.randint(10, 20)
    print(Fore.MAGENTA + f"[🚀] Bắt đầu gom SOL với {num_threads} luồng!")

    tasks = []
    for i in range(min(num_threads, len(private_keys))):
        tasks.append(send_sol(private_keys[i], i + 1))

    await asyncio.gather(*tasks)
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
