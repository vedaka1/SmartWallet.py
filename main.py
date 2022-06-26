import sys
from datetime import datetime
import pandas as pd
import json
from PyQt5 import uic, QtCore
import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.QtGui import QIcon
from pyrebase import pyrebase

firebaseconfig = {
    'apiKey': "AIzaSyCLWINn6PEYk8fjVwE-Q_PtT_8dxwT9UvI",
    'authDomain': "wallet-ce307.firebaseapp.com",
    "databaseURL": "https://wallet-ce307-default-rtdb.europe-west1.firebasedatabase.app",
    'storageBucket': "wallet-ce307.appspot.com"
}

firebase = pyrebase.initialize_app(firebaseconfig)
auth = firebase.auth()
db = firebase.database()
# Глобальные переменные
user_mail = ''
uid = ''
active_wallet = ''
balance = 0


class Login(QDialog):  # Класс окна авторизации
    def __init__(self):
        super(Login, self).__init__()
        uic.loadUi("login.ui", self)  # Загрузка интерфейса
        self.login_btn.clicked.connect(self.login_function)
        self.password_field.setEchoMode(QtWidgets.QLineEdit.Password)
        self.email_field.setPlaceholderText('Почта')
        self.password_field.setPlaceholderText('Пароль')
        self.go_to_register_btn.clicked.connect(self.go_to_regestration)
        self.go_to_resetpass_btn.clicked.connect(self.go_to_reset_pass)
        self.invalid.setVisible(False)
        self.success.setVisible(False)

    def login_function(self):  # Функция авторизации
        global user_mail, uid
        email = self.email_field.text()
        user_mail = self.email_field.text()
        password = self.password_field.text()
        try:
            uid = auth.sign_in_with_email_and_password(
                email, password).get("localId")  # Получает id пользователя из Firebase
            auth.sign_in_with_email_and_password(email, password)
            self.invalid.setVisible(False)
            self.success.setVisible(True)
            self.go_to_main()  # Переход в главное меню
        except:
            self.invalid.setVisible(True)

    def go_to_regestration(self):  # Функция регистрации
        createacc = CreateAcc()  # Открывает окно создания аккаунта
        widget.addWidget(createacc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def go_to_main(self):  # Функция перехода в главное меню
        main = Main()  # Открывает главное меню
        widget.addWidget(main)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def go_to_reset_pass(self):  # Функция восстановления пароля
        reset_pass = ResetPass()  # Открывает окно восстановления пароля
        widget.addWidget(reset_pass)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class CreateAcc(QDialog):  # Класс окна создания аккаунта
    def __init__(self):
        super(CreateAcc, self).__init__()
        uic.loadUi("registration.ui", self)  # Загрузка интерфейса
        self.registration_btn.clicked.connect(self.reg_function)
        self.password_field.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirm_password_field.setEchoMode(QtWidgets.QLineEdit.Password)
        self.email_field.setPlaceholderText('Почта')
        self.password_field.setPlaceholderText('Пароль')
        self.confirm_password_field.setPlaceholderText('Повторите пароль')
        self.go_to_login_btn.clicked.connect(self.go_to_login)
        self.invalid.setVisible(False)
        self.invalidpasswords.setVisible(False)

    def reg_function(self):  # Функция регистрации
        email = self.email_field.text()
        if self.password_field.text() == self.confirm_password_field.text():
            password = self.password_field.text()  # Сравнивает введенные пароли
            self.invalidpasswords.setVisible(False)
            try:
                auth.create_user_with_email_and_password(email, password)
                self.go_to_login()  # Если пароли совпадают, переносит пользователя к окну авторизации
            except:
                self.invalid.setVisible(True)
        else:
            self.invalidpasswords.setVisible(True)

    def go_to_login(self):  # Функция перехода к окну авторизации
        login = Login()  # Открывает окно авторизации
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class ResetPass(QDialog):  # Класс окна восстановления пароля
    def __init__(self):
        super(ResetPass, self).__init__()
        uic.loadUi("newpassword.ui", self)  # Загрузка интерфейса
        self.resetpass_btn.clicked.connect(self.reset_pass_function)
        self.go_to_login_btn.clicked.connect(self.go_to_login)
        self.email_field.setPlaceholderText('Email')
        self.invalid.setVisible(False)
        self.success.setVisible(False)

    def go_to_login(self):  # Функция перехода к авторизации
        login = Login()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def reset_pass_function(self):  # Функция восстановления пароля
        email = self.email_field.text()
        try:
            auth.send_password_reset_email(email)  # Отправляет на почту пользователя ссылку для смены пароля
            self.success.setVisible(True)
        except:
            self.invalid.setVisible(True)


class Main(QDialog):  # Класс окна главного меню
    def __init__(self):
        super(Main, self).__init__()
        uic.loadUi("main.ui", self)  # Загрузка интерфейса
        self.add_btn.clicked.connect(self.go_to_add_wallet)
        self.export_btn.clicked.connect(self.export_to_csv)
        self.wallets_list.itemClicked.connect(self.clicked)
        self.label_mail.setAlignment(QtCore.Qt.AlignCenter)
        self.label_mail.setText(f'{user_mail}')
        wallets_list = []  # Список кошельков в главном меню
        try:
            wallets = db.child("users").child(uid).get()  # Загружает информацию о кошельках пользователя из Firebase
            for wallet in wallets:
                wallets_list.append(wallet.key())
        except:
            pass
        else:
            self.wallets_list.addItems(wallets_list)

    def clicked(self):  # Отображает панели с кошельками пользователя, при нажатии открывает их
        global active_wallet
        active_wallet = self.wallets_list.currentItem().text()
        self.go_to_wallet()

    def go_to_add_wallet(self):  # Функция перехода к созданию кошелька
        new_wallet = NewWallet()  # Открывает окно создания кошелька
        widget.addWidget(new_wallet)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def go_to_wallet(self):  # Функция перехода к кошельку
        wallet = Wallet()
        widget.addWidget(wallet)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def export_to_csv(self):  # Функция экспорта данных
        data = db.child("users").child(uid).get()  # Считывает данные пользователя из Firebase
        data = json.dumps(data.val(), ensure_ascii=False, indent=4)  # Создает по ним json-файл
        pdObj = pd.read_json(data, orient='index')  # Считывает данные из json
        csvData = pdObj.to_csv('output.csv', encoding='utf-8-sig', header=True, index=True)  # Создает csv-файл

class NewWallet(QDialog):  # Класс создания нового кошелька
    def __init__(self):
        super(NewWallet, self).__init__()
        uic.loadUi("newwallet.ui", self)  # Загружает интерфейс
        self.invalid.setVisible(False)
        self.go_to_main_btn.clicked.connect(self.go_to_main)
        self.new_wallet_name_field.setPlaceholderText('Название кошелька')
        self.new_wallet_balance_field.setPlaceholderText('Баланс')
        self.create_new_wallet_btn.clicked.connect(self.push_new_wallet)

    def push_new_wallet(self):  # Функция создания нового кошелька
        global balance
        wallet_name = str(self.new_wallet_name_field.text())  # Его название
        balance = self.new_wallet_balance_field.text()  # Баланс
        try:
            balance = int(balance)
        except:
            self.invalid.setVisible(True)
        else:
            self.invalid.setVisible(False)
            data = {'balance': balance}
            # Загружает данные о новом кошельке в Firebase
            db.child("users").child(f'{uid}').child(wallet_name).set(data)
            self.go_to_main()

    def go_to_main(self):  # Функция перехода в главное меню
        main = Main()
        widget.addWidget(main)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class Wallet(QDialog):  # Класс окна кошелька
    def __init__(self):
        global balance
        super(Wallet, self).__init__()
        uic.loadUi("wallet.ui", self)  # Загружает интерфейс
        self.wallet_label.setText(f'{active_wallet}')  # Отображение названия
        self.go_to_main_btn.clicked.connect(self.go_to_main)
        self.add_income_btn.clicked.connect(self.go_to_income)
        self.add_spending_btn.clicked.connect(self.go_to_spending)
        self.go_to_transfer_btn.clicked.connect(self.go_to_transfer)
        self.report_btn.clicked.connect(self.go_to_report)
        self.delete_wallet_btn.clicked.connect(self.delete_wallet)
        balance_wrap = db.child("users").child(uid).child(active_wallet).get()
        balance = balance_wrap.val()['balance']
        self.balance_amount.setText(f'{balance}')  # Отображение баланса

    def go_to_main(self):  # Функция перехода в главное меню
        main = Main()
        widget.addWidget(main)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def go_to_transfer(self):  # Функция перехода к окну перевода средств между кошельками
        transfer = Transfer()
        widget.addWidget(transfer)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def go_to_income(self):  # Функция перехода к окну пополнения кошелька
        income = Income()
        widget.addWidget(income)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def go_to_spending(self):  # Функция перехода к окну траты средств с кошелька
        spending = Spending()
        widget.addWidget(spending)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def go_to_report(self):  # Функция перехода к окну формирования отчета
        report = Report()
        widget.addWidget(report)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def delete_wallet(self):  # Функция удаления кошелька
        db.child("users").child(uid).child(active_wallet).remove()
        self.go_to_main()


class Transfer(QDialog):  # Класс перевода средств между кошельками
    def __init__(self):
        super(Transfer, self).__init__()
        uic.loadUi("transfer.ui", self)  # Загрузка интерфейса
        self.go_to_wallet_btn.clicked.connect(self.go_to_wallet)
        self.transfer_amount_field.setPlaceholderText('Введите сумму')
        self.transfer_btn.clicked.connect(self.push_new_transfer)
        wallets_list = []  # Список кошельков
        try:
            wallets = db.child("users").child(uid).get()
            for wallet in wallets:
                wallets_list.append(wallet.key())
        except:
            pass
        else:
            self.transfer_to_dropdown.addItems(wallets_list)

    def push_new_transfer(self):  # Функция перевода средств
        transfer_from = active_wallet  # Откуда
        transfer_to = self.transfer_to_dropdown.currentText()  # Куда
        transfer_amount = self.transfer_amount_field.text()  # Сколько
        # Меняет значения балансов в Firebase
        sender_balance = db.child("users").child(f'{uid}').child(active_wallet).get()
        recipient_balance = db.child("users").child(f'{uid}').child(transfer_to).get()
        sender_balance = sender_balance.val()['balance']
        recipient_balance = recipient_balance.val()['balance']

        try:
            transfer_amount = int(transfer_amount)
        except:
            pass
        else:
            new_sender_balance = sender_balance - transfer_amount
            new_recipient_balance = recipient_balance + transfer_amount
            sender_data = {'balance': new_sender_balance}
            recipient_data = {'balance': new_recipient_balance}
            db.child("users").child(f'{uid}').child(transfer_from).update(sender_data)
            db.child("users").child(f'{uid}').child(transfer_to).update(recipient_data)
            self.go_to_wallet()


    def go_to_wallet(self):
        wallet = Wallet()
        widget.addWidget(wallet)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class Income(QDialog):  # Класс окна пополнения кошелька
    def __init__(self):
        super(Income, self).__init__()
        uic.loadUi("income.ui", self)  # Загрузка интерфейса
        self.go_to_wallet_btn.clicked.connect(self.go_to_wallet)
        self.income_amount_field.setPlaceholderText('Введите сумму')  # Сумма пополнения
        self.income_btn.clicked.connect(self.add_income)

    def add_income(self):  # Функция пополнения
        income_amount = self.income_amount_field.text()
        try:
            income_amount = int(income_amount)
        except:
            print('error')
        else:
            new_balance = balance + income_amount  # Изменение баланса
            data = {'balance': new_balance}
            db.child("users").child(uid).child(active_wallet).update(data)  # Изменяет баланс в Firebase
            self.go_to_wallet()  # Переход в меню кошелька

    def go_to_wallet(self):
        wallet = Wallet()
        widget.addWidget(wallet)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class Spending(QDialog):  # Класс окна траты средств
    def __init__(self):
        super(Spending, self).__init__()
        uic.loadUi("spending.ui", self)  # Загрузка интерфейса
        self.spending_amount_field.setPlaceholderText('Введите сумму')
        self.spending_btn.clicked.connect(self.add_spending)
        self.go_to_wallet_btn.clicked.connect(self.go_to_wallet)

    def add_spending(self):  # Функция добавления новой траты
        try:
            elements_amount = db.child("users").child(f'{uid}').child(active_wallet).child("spendings").get()
            elements_amount = len(elements_amount.val())
        except:
            elements_amount = 0
        old_balance = db.child("users").child(f'{uid}').child(active_wallet).get().val()['balance']
        spending_day = datetime.now().day  # День траты
        spending_month = datetime.now().month  # Месяц
        spending_year = datetime.now().year  # Год
        spending_category = self.spending_category_dropdown.currentText()  # Категория траты
        spending_sum = self.spending_amount_field.text()  # Сколько было потрачено
        new_balance = old_balance - int(spending_sum)
        spending_data = {'category': spending_category, 'sum': spending_sum, 'year': spending_year,
                         'month': spending_month, 'day': spending_day}  # Формат данных о трате
        db.child("users").child(f'{uid}').child(active_wallet).child('spendings').child(elements_amount)\
            .set(spending_data)  # Записывает трату в Firebase
        spending_balance_data = {'balance': new_balance}
        db.child("users").child(f'{uid}').child(active_wallet).update(spending_balance_data)
        self.go_to_wallet()


    def go_to_wallet(self):
        wallet = Wallet()
        widget.addWidget(wallet)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class Report(QDialog):  # Класс окна отчета
    def __init__(self):
        super(Report, self).__init__()
        uic.loadUi("report.ui", self)  # Загрузка интерфейса
        self.date_from_field.dateChanged.connect(self.load_date)
        self.date_to_field.dateChanged.connect(self.load_date)
        self.load_date()

    def load_date(self):  # Функция сортировки по времени и категориям
        self.go_to_wallet_btn.clicked.connect(self.go_to_wallet)
        # От какого дня, месяца, года
        year_from = self.date_from_field.date().year()
        month_from = self.date_from_field.date().month()
        day_from = self.date_from_field.date().day()
        # До какого
        year_to = self.date_to_field.date().year()
        month_to = self.date_to_field.date().month()
        day_to = self.date_to_field.date().day()
        # Загружает данные о тратах текущего пользователя
        spendings_dict = db.child("users").child(f'{uid}').child(active_wallet).child('spendings').get()
        # начальные значения
        transport_sum  = 0
        entertainment_sum = 0
        products_sum = 0
        beauty_sum = 0
        restaurant_sum = 0
        housing_sum = 0
        clothes_sum = 0
        services_sum = 0
        other_sum = 0
        try:
            for i in spendings_dict:
                if i.val()['category'] == 'Транспорт' and year_from <= i.val()['year'] <= year_to \
                        and month_from <= i.val()['month'] <= month_to and day_from <= i.val()['day'] <= day_to:
                    transport_sum += int(i.val()['sum'])  # Считывает траты пользователя в категории Транспорт
            for i in spendings_dict:
                if i.val()['category'] == 'Развлечения' and year_from <= i.val()['year'] <= year_to \
                        and month_from <= i.val()['month'] <= month_to and day_from <= i.val()['day'] <= day_to:
                    entertainment_sum += int(i.val()['sum'])  # Считывает траты пользователя в категории Развлечения
            for i in spendings_dict:
                if i.val()['category'] == 'Продукты и товары для дома' and year_from <= i.val()['year'] <= year_to \
                        and month_from <= i.val()['month'] <= month_to and day_from <= i.val()['day'] <= day_to:
                    products_sum += int(i.val()['sum'])  # Считывает траты пользователя в категории Продукты и товары для дома
            for i in spendings_dict:
                if i.val()['category'] == 'Красота и здоровье' and year_from <= i.val()['year'] <= year_to \
                        and month_from <= i.val()['month'] <= month_to and day_from <= i.val()['day'] <= day_to:
                    beauty_sum += int(i.val()['sum'])  # Считывает траты пользователя в категории Красота и здоровье
            for i in spendings_dict:
                if i.val()['category'] == 'Рестораны' and year_from <= i.val()['year'] <= year_to \
                        and month_from <= i.val()['month'] <= month_to and day_from <= i.val()['day'] <= day_to:
                    restaurant_sum += int(i.val()['sum'])  # Считывает траты пользователя в категории Рестораны
            for i in spendings_dict:
                if i.val()['category'] == 'Жилье' and year_from <= i.val()['year'] <= year_to \
                        and month_from <= i.val()['month'] <= month_to and day_from <= i.val()['day'] <= day_to:
                    housing_sum += int(i.val()['sum'])  # Считывает траты пользователя в категории Жилье
            for i in spendings_dict:
                if i.val()['category'] == 'Одежда' and year_from <= i.val()['year'] <= year_to \
                        and month_from <= i.val()['month'] <= month_to and day_from <= i.val()['day'] <= day_to:
                    clothes_sum += int(i.val()['sum'])  # Считывает траты пользователя в категории Одежда
            for i in spendings_dict:
                if i.val()['category'] == 'Услуги' and year_from <= i.val()['year'] <= year_to \
                        and month_from <= i.val()['month'] <= month_to and day_from <= i.val()['day'] <= day_to:
                    services_sum += int(i.val()['sum'])  # Считывает траты пользователя в категории Услуги
            for i in spendings_dict:
                if i.val()['category'] == 'Другое' and year_from <= i.val()['year'] <= year_to \
                        and month_from <= i.val()['month'] <= month_to and day_from <= i.val()['day'] <= day_to:
                    other_sum += int(i.val()['sum'])  # Считывает траты пользователя в категории Другое
        except:
            transport_sum = 0
            entertainment_sum = 0
            products_sum = 0
            beauty_sum = 0
            restaurant_sum = 0
            housing_sum = 0
            clothes_sum = 0
            services_sum = 0
            other_sum = 0

        # Отображает полученные данные в виде панелей с названием категории и суммой трат
        self.transport_sum_label.setText(f'{transport_sum}')
        self.entertainment_sum_label.setText(f'{entertainment_sum}')
        self.products_sum_label.setText(f'{products_sum}')
        self.beauty_sum_label.setText(f'{beauty_sum}')
        self.restaurant_sum_label.setText(f'{restaurant_sum}')
        self.housing_sum_label.setText(f'{housing_sum}')
        self.clothes_sum_label.setText(f'{clothes_sum}')
        self.services_sum_label.setText(f'{services_sum}')
        self.other_sum_label.setText(f'{other_sum}')


    def go_to_wallet(self):
        wallet = Wallet()
        widget.addWidget(wallet)
        widget.setCurrentIndex(widget.currentIndex() + 1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = Login()  # Загружает главное начальное окно авторизации
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(main_window)
    widget.setFixedWidth(360)  # Устанавливает ширину окна
    widget.setFixedHeight(650)  # Устанавливает высоту окна
    widget.setWindowTitle('SmartWallet')  # Название в верху диалогового окна
    widget.setWindowIcon(QIcon('money.png'))  # Загружает свою картинку в углу диалогового окна
    widget.show()
    app.exec()
