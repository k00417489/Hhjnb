from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import json
import os

API_TOKEN = "7975160732:AAE6FjtQbQglKpoQC5_KlasclbXlFOew67s"
ADMIN_USERNAME = "ADSRUNIGCC"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

BALANCE_FILE = "users.json"
ACCOUNT_FILE = "accounts.json"

def load_balances():
    if not os.path.exists(BALANCE_FILE):
        return {}
    with open(BALANCE_FILE, "r") as f:
        return json.load(f)

def save_balances(data):
    with open(BALANCE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_accounts():
    if not os.path.exists(ACCOUNT_FILE):
        return []
    with open(ACCOUNT_FILE, "r") as f:
        return json.load(f)

def save_accounts(data):
    with open(ACCOUNT_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_unused_account(ig_type):
    accounts = load_accounts()
    for acc in accounts:
        if not acc.get("used", False) and acc.get("type") == ig_type:
            acc["used"] = True
            save_accounts(accounts)
            return acc
    return None

def load_stock():
    accounts = load_accounts()
    stock = {"10+": 0, "15+": 0, "30+": 0}
    for acc in accounts:
        if not acc.get("used", False):
            acc_type = acc.get("type")
            if acc_type in stock:
                stock[acc_type] += 1
    return stock

user_ig_type = {}
prices = {"10+": 15, "15+": 20, "30+": 30}

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.add(KeyboardButton("ADD FUNDS"), KeyboardButton("BUY INDO IG"))
main_keyboard.add(KeyboardButton("MY BALANCE"), KeyboardButton("📦 STOCK"))
main_keyboard.add(KeyboardButton("🚪 Exit"))

exit_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("🚪 Exit"))

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    await msg.answer("WELCOME TO THE IG SELLER BOT!\nCONTACT: @ADSRUNIGCC", reply_markup=main_keyboard)

@dp.message_handler(lambda message: message.text == "ADD FUNDS")
async def add_funds(msg: types.Message):
    await msg.answer("PLEASE WAIT......... GENERATING QR")
    await msg.answer_photo(
        photo=open("qr.png", "rb"),
        caption="➤ PAY ON THIS QR AND CLICK CHECK ➤ TO ADD YOUR BALANCE ➤",
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True)
        .add(KeyboardButton("➤ CHECK"))
        .add(KeyboardButton("🚪 Exit")),
    )

@dp.message_handler(lambda message: message.text == "➤ CHECK")
async def check_payment(msg: types.Message):
    await msg.answer("➤ PAYMENT VERIFICATION\n\n➤ CONTACT: @ADSRUNIGCC", reply_markup=exit_keyboard)

@dp.message_handler(lambda message: message.text == "MY BALANCE")
async def my_balance(msg: types.Message):
    uid = str(msg.from_user.id)
    balances = load_balances()
    balance = balances.get(uid, 0)
    await msg.answer(f"➤ BALANCE FETCHED\n\n➤ YOUR BALANCE IS :- ₹{balance}\n\n➤ CONTACT @ADSRUNIGCC TO ADD FUNDS", reply_markup=exit_keyboard)

@dp.message_handler(lambda message: message.text == "📦 STOCK")
async def stock(msg: types.Message):
    stock = load_stock()
    await msg.answer(
        f"📦 STOCK\n\n📄 10+ DAYS OLD INDO ➤ {stock['10+']}\n📄 15+ DAYS OLD INDO ➤ {stock['15+']}\n📄 30+ DAYS OLD INDO ➤ {stock['30+']}",
        reply_markup=exit_keyboard
    )

@dp.message_handler(lambda message: message.text == "BUY INDO IG")
async def buy_indo(msg: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("10+ DAYS OLD INDO"), KeyboardButton("15+ DAYS OLD INDO"), KeyboardButton("30+ DAYS OLD INDO"))
    kb.add(KeyboardButton("🚪 Exit"))
    await msg.answer("📦 CHOOSE THE TYPE OF INDO IG YOU WANT TO BUY 👇", reply_markup=kb)

@dp.message_handler(lambda message: message.text in ["10+ DAYS OLD INDO", "15+ DAYS OLD INDO", "30+ DAYS OLD INDO"])
async def select_indo_type(msg: types.Message):
    uid = str(msg.from_user.id)
    if "10+" in msg.text:
        ig_type = "10+"
    elif "15+" in msg.text:
        ig_type = "15+"
    else:
        ig_type = "30+"

    user_ig_type[uid] = ig_type

    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=5)
    buttons = [KeyboardButton(f"OLD {i}") for i in range(1, 21)]
    kb.add(*buttons)
    kb.add(KeyboardButton("🚪 Exit"))

    await msg.answer(f"➤ {ig_type} DAYS OLD INDO\n➤ PRICE PER IG: ₹{prices[ig_type]}", reply_markup=kb)

@dp.message_handler(lambda message: message.text.startswith("OLD "))
async def handle_old(msg: types.Message):
    uid = str(msg.from_user.id)
    balances = load_balances()
    stock = load_stock()
    ig_type = user_ig_type.get(uid)

    if not ig_type:
        await msg.answer("❌ COULDN'T DETECT IG TYPE. PLEASE CHOOSE AGAIN.")
        return

    balance = balances.get(uid, 0)
    price = prices[ig_type]

    if balance < price:
        await msg.answer(
            f"⚠️ INSUFFICIENT BALANCE ⚠️\n\n➤ YOUR BALANCE IS :- ₹{balance}\n\n➤ EXIT AND CLICK ADD FUNDS",
            reply_markup=exit_keyboard
        )
        return

    if stock[ig_type] <= 0:
        await msg.answer(f"❌ OUT OF STOCK FOR {ig_type} DAYS OLD INDO", reply_markup=exit_keyboard)
        return

    account = get_unused_account(ig_type)
    if not account:
        await msg.answer("❌ All IG ACCOUNTS ARE SOLD OUT.", reply_markup=exit_keyboard)
        return

    balances[uid] = balance - price
    save_balances(balances)

    ig_user = account["username"]
    ig_pass = account["password"]
    await msg.answer(
        f"✅ PURCHASED SUCCESSFULLY!\n\n➤ IG Account:\n`{ig_user}:{ig_pass}`\n\n➤ DM @ADSRUNIGCC IF LOGIN FAILS.",
        parse_mode="Markdown",
        reply_markup=exit_keyboard
    )

@dp.message_handler(lambda message: message.text == "🚪 Exit")
async def exit_msg(msg: types.Message):
    await msg.answer("🚪 EXITED SUCCESSFULLY", reply_markup=main_keyboard)


@dp.message_handler(lambda message: message.text.startswith("/addstock"))
async def add_stock_command(msg: types.Message):
    if msg.from_user.username != ADMIN_USERNAME:
        await msg.answer("❌ You are not authorized to add stock.")
        return

    try:
        parts = msg.text.split()
        if len(parts) != 4:
            await msg.answer("❌ Usage: /addstock <username> <password> <type: 10+/15+/30+>")
            return

        _, username, password, acc_type = parts
        if acc_type not in ["10+", "15+", "30+"]:
            await msg.answer("❌ Invalid type. Use 10+, 15+ or 30+.")
            return

        accounts = load_accounts()
        accounts.append({
            "username": username,
            "password": password,
            "type": acc_type,
            "used": False
        })
        save_accounts(accounts)

        await msg.answer(f"✅ Stock added: {username}:{password} [{acc_type}]")

    except Exception as e:
        await msg.answer(f"❌ Error: {str(e)}")



@dp.message_handler(lambda message: message.text.startswith("/addbalance"))
async def add_balance_command(msg: types.Message):
    if msg.from_user.username != ADMIN_USERNAME:
        await msg.answer("❌ You are not authorized to add balance.")
        return

    try:
        parts = msg.text.split()
        if len(parts) != 3:
            await msg.answer("❌ Usage: /addbalance <user_id> <amount>")
            return

        _, user_id, amount = parts
        amount = int(amount)
        balances = load_balances()
        balances[user_id] = balances.get(user_id, 0) + amount
        save_balances(balances)

        await msg.answer(f"✅ ₹{amount} added to user {user_id}. New balance: ₹{balances[user_id]}")
    except Exception as e:
        await msg.answer(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)