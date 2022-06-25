import sys
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
# Глобальные переменные для хранения базовых данных текущего пользователя
user_mail = ''
uid = ''
active_wallet = ''
balance = 0


# Класс входа в приложение
class Login(QDialog):
    def __init__(self):
        super(Login, self).__init__()
        uic.loadUi("login.ui", self)
        self.login_btn.clicked.connect(self.login_function)
        self.password_field.setEchoMode(QtWidgets.QLineEdit.Password)
        self.email_field.setPlaceholderText('Почта')
        self.password_field.setPlaceholderText('Пароль')
        self.go_to_register_btn.clicked.connect(self.go_to_regestration)
        self.go_to_resetpass_btn.clicked.connect(self.go_to_reset_pass)
        self.invalid.setVisible(False)
        self.success.setVisible(False)

    def login_function(self):  # Метод отвечающий за сбор введенных данных
        global user_mail, uid
        email = self.email_field.text()
        user_mail = self.email_field.text()
        password = self.password_field.text()
        try:  # Если данные введены правильно, открывает главное диалоговое окно Main
            uid = auth.sign_in_with_email_and_password(
                email, password).get("localId")  # Принимает id пользователя из Firebase
            auth.sign_in_with_email_and_password(email, password)
            self.invalid.setVisible(False)
            self.success.setVisible(True)
            self.go_to_main()
        except:
            self.invalid.setVisible(True)

    def go_to_regestration(self):  # Отвечает за кнопку перехода на окно регистрации
        createacc = CreateAcc()
        widget.addWidget(createacc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def go_to_main(self):  # Отвечает за кнопку перехода на главное окно
        main = Main()
        widget.addWidget(main)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def go_to_reset_pass(self):  # Отвечает за кнопку перехода на окно восстановления пароля
        reset_pass = ResetPass()
        widget.addWidget(reset_pass)
        widget.setCurrentIndex(widget.currentIndex() + 1)


# Класс для создания аккаунта
class CreateAcc(QDialog):
    def __init__(self):
        super(CreateAcc, self).__init__()
        uic.loadUi("registration.ui", self)
        self.registration_btn.clicked.connect(self.reg_function)
        self.password_field.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirm_password_field.setEchoMode(QtWidgets.QLineEdit.Password)
        self.email_field.setPlaceholderText('Почта')
        self.password_field.setPlaceholderText('Пароль')
        self.confirm_password_field.setPlaceholderText('Повторите пароль')
        self.go_to_login_btn.clicked.connect(self.go_to_login)
        self.invalid.setVisible(False)
        self.invalidpasswords.setVisible(False)

    def reg_function(self):
        email = self.email_field.text()
        if self.password_field.text() == self.confirm_password_field.text():
            password = self.password_field.text()
            self.invalidpasswords.setVisible(False)
            try:
                auth.create_user_with_email_and_password(email, password)
                self.go_to_login()
            except:
                self.invalid.setVisible(True)
        else:
            self.invalidpasswords.setVisible(True)

    def go_to_login(self):
        login = Login()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex() + 1)

# Класс чтоб сбросить пароль
class ResetPass(QDialog):
    def __init__(self):
        super(ResetPass, self).__init__()
        uic.loadUi("newpassword.ui", self)
        self.resetpass_btn.clicked.connect(self.reset_pass_function)
        self.go_to_login_btn.clicked.connect(self.go_to_login)
        self.email_field.setPlaceholderText('Email')
        self.invalid.setVisible(False)
        self.success.setVisible(False)

    def go_to_login(self):
        login = Login()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def reset_pass_function(self):
        email = self.email_field.text()
        try:
            auth.send_password_reset_email(email)
            self.success.setVisible(True)
        except:
            self.invalid.setVisible(True)

# Класс главной вкладки
class Main(QDialog):
    def __init__(self):
        super(Main, self).__init__()
        uic.loadUi("main.ui", self)
        self.add_btn.clicked.connect(self.go_to_add_wallet)
        self.wallets_list.itemClicked.connect(self.clicked)
        self.label_mail.setAlignment(QtCore.Qt.AlignCenter)
        self.label_mail.setText(f'{user_mail}')
        wallets_list = []
        try:
            wallets = db.child("users").child(uid).get()
            for wallet in wallets:
                wallets_list.append(wallet.key())
        except:
            pass
        else:
            self.wallets_list.addItems(wallets_list)

    def clicked(self):
        global active_wallet
        active_wallet = self.wallets_list.currentItem().text()
        self.go_to_wallet()

    def go_to_add_wallet(self):
        new_wallet = NewWallet()
        widget.addWidget(new_wallet)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def go_to_wallet(self):
        wallet = Wallet()
        widget.addWidget(wallet)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class NewWallet(QDialog):
    def __init__(self):
        super(NewWallet, self).__init__()
        uic.loadUi("newwallet.ui", self)
        self.invalid.setVisible(False)
        self.go_to_main_btn.clicked.connect(self.go_to_main)
        self.new_wallet_name_field.setPlaceholderText('Название кошелька')
        self.new_wallet_balance_field.setPlaceholderText('Баланс')
        self.create_new_wallet_btn.clicked.connect(self.push_new_wallet)

    def push_new_wallet(self):
        global balance
        wallet_name = str(self.new_wallet_name_field.text())
        balance = self.new_wallet_balance_field.text()
        try:
            balance = int(balance)
        except:
            self.invalid.setVisible(True)
        else:
            self.invalid.setVisible(False)
            data = {'balance': balance}
            db.child("users").child(f'{uid}').child(wallet_name).set(data)
            self.go_to_main()

    def go_to_main(self):
        main = Main()
        widget.addWidget(main)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class Wallet(QDialog):
    def __init__(self):
        global balance
        super(Wallet, self).__init__()
        uic.loadUi("wallet.ui", self)
        self.wallet_label.setText(f'{active_wallet}')
        self.go_to_main_btn.clicked.connect(self.go_to_main)
        self.add_income_btn.clicked.connect(self.go_to_income)
        self.go_to_transfer_btn.clicked.connect(self.go_to_transfer)
        self.delete_wallet_btn.clicked.connect(self.delete_wallet)
        balance_wrap = db.child("users").child(uid).child(active_wallet).get()
        for item in balance_wrap:
            balance = item.val()
        self.balance_amount.setText(f'{balance}')

    def go_to_main(self):
        main = Main()
        widget.addWidget(main)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def go_to_transfer(self):
        transfer = Transfer()
        widget.addWidget(transfer)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def go_to_income(self):
        income = Income()
        widget.addWidget(income)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def delete_wallet(self):
        db.child("users").child(uid).child(active_wallet).remove()
        self.go_to_main()


class Transfer(QDialog):
    def __init__(self):
        super(Transfer, self).__init__()
        uic.loadUi("transfer.ui", self)
        self.go_to_wallet_btn.clicked.connect(self.go_to_wallet)
        self.transfer_amount_field.setPlaceholderText('Сумма перевода')
        # self.create_new_wallet_btn.clicked.connect(self.push_new_wallet)
        wallets_list = []
        try:
            wallets = db.child("users").child(uid).get()
            for wallet in wallets:
                wallets_list.append(wallet.key())
        except:
            pass
        else:
            self.transfer_from_dropdown.addItems(wallets_list)
            self.transfer_to_dropdown.addItems(wallets_list)

    def go_to_wallet(self):
        main = Wallet()
        widget.addWidget(main)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class Income(QDialog):
    def __init__(self):
        super(Income, self).__init__()
        uic.loadUi("income.ui", self)
        self.go_to_wallet_btn.clicked.connect(self.go_to_wallet)
        self.income_amount_field.setPlaceholderText('Введите сумму')
        self.income_btn.clicked.connect(self.add_income)

    def add_income(self):
        income_amount = self.income_amount_field.text()
        try:
            income_amount = int(income_amount)
        except:
            print('error')
        else:
            new_balance = balance + income_amount
            data = {'balance': new_balance}
            db.child("users").child(uid).child(active_wallet).update(data)
            self.go_to_wallet()

    def go_to_wallet(self):
        wallet = Wallet()
        widget.addWidget(wallet)
        widget.setCurrentIndex(widget.currentIndex() + 1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = Login()
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(main_window)
    widget.setFixedWidth(360)
    widget.setFixedHeight(650)
    widget.setWindowTitle('SmartWallet')
    widget.setWindowIcon(QIcon('money.png'))
    widget.show()
    app.exec()
