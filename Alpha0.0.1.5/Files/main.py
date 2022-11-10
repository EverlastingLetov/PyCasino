
import sys
import csv
import random
import sqlite3
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QFileDialog, QInputDialog
from PyQt5.QtWidgets import QWidget, QMessageBox, QLineEdit, QTableWidgetItem
from PyQt5.QtGui import QImage, QPalette, QBrush
from PyQt5 import QtCore, QtMultimedia
from PyQt5.QtGui import QPixmap
con = sqlite3.connect('users.sqlite')
cur = con.cursor()


class LoginWindow(QWidget): #ОКНО ВХОДА
    def __init__(self):
        super().__init__()
        uic.loadUi('login.ui', self)
        self.setWindowTitle("Войти в КАЗИНО")
        self.login_button.clicked.connect(self.loginw)
        self.signup_button.clicked.connect(self.signup)

    def loginw(self): #САМ ЛОГИН
        self.login = self.log.text()
        self.password = self.pwd.text()
        if not self.login:
            QMessageBox.critical(
                self, 'ОШИБКА!', 'Введите логин!',
                QMessageBox.Ok)
            return
        if not self.password:
            QMessageBox.critical(
                self, 'ОШИБКА!', 'Введите пароль!',
                QMessageBox.Ok)
            return
        self.userd = cur.execute(f"SELECT id FROM users WHERE username = ?"
                                  f" and password = ?", (self.login, self.password)).fetchone()
        self.admin = cur.execute("""SELECT id FROM users WHERE prava = 'yes'""").fetchone()
        if self.userd:
            if self.userd != self.admin:
                self.userprofile = Profile(self.login)
                self.userprofile.show()
            elif self.userd == self.admin:
                 self.adminapnel = Admin(self.login)
                 self.adminapnel.show()
                 print('admin = true')
            self.close()
        else:
            QMessageBox.critical(
                self, 'Ошибка входа', "Неправильный логин или пароль",
                QMessageBox.Ok)
            return

    def signup(self): #РЕГИСТРАЦИЯ
        slogin = self.log.text()
        spassword = self.pwd.text()
        if not slogin:
            QMessageBox.critical(
                self, 'Ошибка входа!', 'Введите логин!',
                QMessageBox.Ok)
            return
        if not spassword:
            QMessageBox.critical(
                self, 'Ошибка входа!', 'Введите пароль!',
                QMessageBox.Ok)
            return
        cur.execute("""INSERT INTO users (username, password, prava, balance) VALUES (?, ?, ?, ?)""",
                    (slogin, spassword, 'no', 0))
        con.commit()
        QMessageBox.critical(
            self, 'Готово', 'А теперь войдите.',
            QMessageBox.Close)


class Profile(QMainWindow): #ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.setWindowTitle('Профиль')
        oImage = QImage("fnv.png")
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(oImage))
        self.setPalette(palette)
        self.name = args[0]
        self.toexitlogin = args[0]
        self.label.setStyleSheet("color: white")
        self.pushButton.clicked.connect(self.run1)
        self.pushButton_2.clicked.connect(self.profmenu)
        self.pushButton_2.setStyleSheet("background-color: green; color: white")
        self.pushButton_3.clicked.connect(self.run3)
        self.logout.setStyleSheet("background-color: red; color: white;")
        self.logout.clicked.connect(self.toexit)
        self.balance = cur.execute(f"SELECT balance FROM users WHERE username = ?", args).fetchone()
        self.label_3.setText("Баланс: " f'{self.balance[0]}' "р.")
        self.label_3.setStyleSheet("color: white")
        self.label_4.setText(*args)
        self.label_4.setStyleSheet("color: white")

    def run1(self):
        fname = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '')[0]
        self.pixmap = QPixmap(fname)
        self.label_2.setPixmap(self.pixmap)

    def run3(self):
        name, ok_pressed = QInputDialog.getText(self, "Введите имя.",
                                                "Ваше новое имя: ")
        if ok_pressed:
            self.label.setText(name)

    def profmenu(self):
        self.lobby = Lobby(self.balance, self.name)
        self.lobby.show()
        self.close()

    def toexit(self):
        self.toex = Logout(self.toexitlogin)
        self.toex.show()
        self.close()


class Logout(QWidget): #ВЫХОД
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('exitmenu.ui', self)
        self.setWindowTitle('Выйти?')
        self.loginl = args[0]
        self.pushButton.clicked.connect(self.logoutfunc)
        self.pushButton_2.clicked.connect(self.dontexit)

    def logoutfunc(self):
        self.close()
        self.loginw = LoginWindow()
        self.loginw.show()

    def dontexit(self):
        self.close()
        self.prof = Profile(self.loginl)
        self.prof.show()


class Admin(QMainWindow): #АДМИНКА
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('admin.ui', self)
        self.setWindowTitle('Админ-панель')
        self.name = args[0]
        self.toexitlogin = args[0]
        self.pushButton.clicked.connect(self.run1)
        self.pushButton_2.clicked.connect(self.run2)
        self.pushButton_2.setStyleSheet("background-color: green; color: white")
        self.pushButton_3.clicked.connect(self.run3)
        self.pushButton_4.clicked.connect(self.run4)
        self.pushButton_5.clicked.connect(self.run5)
        self.logout.clicked.connect(self.toexit)
        self.logout.setStyleSheet("background-color: red; color: white;")
        self.balance = cur.execute(f"SELECT balance FROM users WHERE username = ?", args).fetchone()
        self.label_3.setText("Баланс: " f'{self.balance[0]}' "р.")
        self.label.setText(*args)

    def run1(self):
        fname = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '')[0]
        self.pixmap = QPixmap(fname)
        self.label_2.setPixmap(self.pixmap)

    def run2(self):
        self.lobby = Lobby(self.balance, self.name)
        self.lobby.show()
        self.close()

    def run3(self):
        dump_users = cur.execute("""SELECT * FROM users WHERE id > 0""").fetchall()
        print(*dump_users)
        with open('dump.csv', 'w') as f:
            writer = csv.writer(f)
            for num, item in enumerate(dump_users):
                writer.writerow(dump_users[num])

    def run4(self):
        self.admbc = AdmBalance()
        self.admbc.show()
        self.close()

    def run5(self):
        self.ban = BanHammer()
        self.ban.show()

    def toexit(self):
        self.toex = AdminLogout(self.toexitlogin)
        self.toex.show()
        self.close()


class AdminLogout(QWidget): #ВЫХОД
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('exitmenu.ui', self)
        self.setWindowTitle('Выйти?')
        self.loginl = args[0]
        self.pushButton.clicked.connect(self.logoutfunc)
        self.pushButton_2.clicked.connect(self.dontexit)

    def logoutfunc(self):
        self.close()
        self.loginw = LoginWindow()
        self.loginw.show()

    def dontexit(self):
        self.close()
        self.prof = Admin(self.loginl)
        self.prof.show()


class AdmBalance(QMainWindow): #ИЗМЕНЕНИЕ БАЛАНСА
    def __init__(self):
        super().__init__()
        uic.loadUi('balanceadm.ui', self)
        self.setWindowTitle('Изменить баланс')
        self.pushButton.clicked.connect(self.update_result)
        self.tableWidget.itemChanged.connect(self.item_changed)
        self.pushButton_2.clicked.connect(self.save_results)
        self.modified = {}
        self.titles = None

    def update_result(self):
        result = cur.execute("SELECT * FROM users WHERE id = ?",
                            (item_id := self.spinBox.text(), )).fetchall()
        self.tableWidget.setRowCount(len(result))
        if not result:
            self.statusBar().showMessage('ERROR 404')
            return
        else:
            self.statusBar().showMessage(f"Найдено с id = {item_id}")
        self.tableWidget.setColumnCount(len(result[0]))
        self.titles = [description[0] for description in cur.description]
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
        self.modified = {}

    def item_changed(self, item):
        self.modified[self.titles[item.column()]] = item.text()

    def save_results(self):
        if self.modified:
            que = "UPDATE users SET\n"
            que += ", ".join([f"{key}='{self.modified.get(key)}'"
                                for key in self.modified.keys()])
            que += "WHERE id = ?"
            cur.execute(que, (self.spinBox.text(),))
            con.commit()
            self.modified.clear()
            self.nebag = LoginWindow()
            self.nebag.show()
            self.close()


class BanHammer(QMainWindow): #БАНХАММЕР
    def __init__(self):
        super().__init__()
        uic.loadUi('banhammer.ui', self)
        self.setWindowTitle('Заблокировать пользователя')
        self.pushButton.clicked.connect(self.delete_results)
        self.pushButton_2.clicked.connect(self.update_result)
        self.pushButton_4.clicked.connect(self.unban_user)
        self.titles = None

    def update_result(self):
        result = cur.execute("SELECT * FROM users WHERE id = ?",
                            (item_id := self.spinBox.text(),)).fetchall()
        self.item_id = int(item_id)
        self.tableWidget.setRowCount(len(result))
        if not result:
            self.statusBar().showMessage('ERROR 404')
            return
        else:
            self.statusBar().showMessage(f"Найдено с id = {item_id}")
        self.tableWidget.setColumnCount(len(result[0]))
        self.titles = [description[0] for description in cur.description]
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
        self.result = result

    def delete_results(self):
        if self.result:
            valid = QMessageBox.question(
                self, '', "Действительно заблокировать пользователя?",
                QMessageBox.Yes, QMessageBox.No)
            if valid == QMessageBox.Yes:
                cur.execute("INSERT INTO banned(id, username, password, prava, balance) VALUES(?, ?, ?, ?, ?)", *self.result)
                cur.execute("DELETE FROM users WHERE id = ?", (self.item_id, ))
                con.commit()
                QMessageBox.critical(
                    self, 'Успех!', "Пользователь заблокирован.",
                    QMessageBox.Ok)
            else:
                QMessageBox.critical(
                    self, 'Ошибка!', "Пользователь не найден!",
                    QMessageBox.Ok)
        else:
            QMessageBox.critical(
                self, 'Ошибка!', "Проверьте пользователя!",
                QMessageBox.Ok)

    def unban_user(self): #РАЗБАН
        if self.result:
            valid = QMessageBox.question(
                self, '', "Действительно разблокировать пользователя?",
                QMessageBox.Yes, QMessageBox.No)
            if valid == QMessageBox.Yes:
                cur.execute("INSERT INTO users(id, username, password, prava, balance) VALUES(?, ?, ?, ?, ?)", *self.result)
                cur.execute("DELETE FROM banned WHERE id = ?", (self.item_id, ))
                con.commit()
                QMessageBox.critical(
                    self, 'Успех!', "Пользователь разблокирован.",
                    QMessageBox.Ok)
            else:
                QMessageBox.critical(
                    self, 'Ошибка!', "Пользователь не найден!",
                    QMessageBox.Ok)
        else:
            QMessageBox.critical(
                self, 'Ошибка!', "Проверьте пользователя!",
                QMessageBox.Ok)


class Lobby(QMainWindow): #МЕНЮ С ИГРАМИ
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('lobby.ui', self)
        self.setWindowTitle('Лобби')
        self.pixmap = QPixmap('nvgame.jpg')
        self.label_2.setPixmap(self.pixmap)
        self.pixmap2 = QPixmap('bones.webp')
        self.label_3.setPixmap(self.pixmap2)
        self.pixmap3 = QPixmap('777.png')
        self.label_4.setPixmap(self.pixmap3)
        self.pixmap4 = QPixmap('0to100.jpg')
        self.label_5.setPixmap(self.pixmap4)
        self.balance = args[0][0]
        self.name = args[1]
        self.pushButton.clicked.connect(self.run1)
        self.pushButton_2.clicked.connect(self.run2)
        self.pushButton_3.clicked.connect(self.run3)
        self.pushButton_4.clicked.connect(self.run4)
        self.profileButton.clicked.connect(self.run5)
        self.profileButton.setStyleSheet("background-color: green; color: white")
        self.radioButtonCas.clicked.connect(self.run6)
        self.radioButtonCas.setStyleSheet("background-color: green; color: white")

    def run1(self):
        self.nvutigame = NvutiGame(self.balance, self.name)
        self.nvutigame.show()

    def run2(self):
        self.bonesgame = BonesGame(self.balance, self.name)
        self.bonesgame.show()

    def run3(self):
        self.slotsgame = SlotsGame(self.balance, self.name)
        self.slotsgame.show()

    def run4(self):
        self.zerohund = Zerohundred(self.balance, self.name)
        self.zerohund.show()

    def run5(self):
        if self.name == "admin":
            self.profbutton = Admin(self.name)
            self.profbutton.show()
            self.close()
        else:
            self.profbutton = Profile(self.name)
            self.profbutton.show()
            self.close()

    def run6(self):
        self.radio = Player()
        self.radio.show()


class Player(QMainWindow): #РАДИО "МОХАВЕ"
    def __init__(self):
        super().__init__()
        uic.loadUi('music.ui', self)
        self.setWindowTitle('Радио')
        filename = QFileDialog.getOpenFileName(self, 'Выбрать музыку', '')[0]
        self.load_mp3(filename)
        self.pushButton.clicked.connect(self.player.play)
        self.pushButton_3.clicked.connect(self.player.pause)
        self.pushButton_2.clicked.connect(self.player.stop)

    def load_mp3(self, filename):
        media = QtCore.QUrl.fromLocalFile(filename)
        content = QtMultimedia.QMediaContent(media)
        self.player = QtMultimedia.QMediaPlayer()
        self.player.setMedia(content)


class NvutiGame(QMainWindow): #СЛЕДУЮЩИЕ 4 КЛАССА - ИГРЫ
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('nvuti.ui', self)
        self.balance = args[0]
        self.name = args[1]
        self.setWindowTitle('NVUTI')
        self.bigger.clicked.connect(self.bolshe)
        self.lower.clicked.connect(self.menshe)
        self.label_3.setText("Баланс: " f'{self.balance}' "р.")

    def bolshe(self):
        if self.balance > 0:
            self.betz = self.lineEdit.text()
            if not self.betz:
                QMessageBox.critical(
                    self, 'ОШИБКА', 'Введите ставку!',
                    QMessageBox.Ok)
            else:
                self.bet = int(self.betz)
                self.label_7.setText(f"{int(self.betz)}")
                self.result = random.uniform(-9999, 9999)
                self.label_4.setText(f"{int(self.result)}")
                if self.result > 0:
                    self.balance = self.balance + self.bet
                    win = 'Вы выиграли!'
                    self.label_6.setText(win)
                    cur.execute(f"UPDATE users SET balance = balance + ?" f"WHERE username = ?", (self.bet, self.name))
                    con.commit()
                    self.label_3.setText("Баланс: " f'{self.balance}' "р.")
                elif self.result < 0:
                    self.balance = self.balance - self.bet
                    lose = 'Вы проиграли!'
                    self.label_6.setText(lose)
                    cur.execute(f"UPDATE users SET balance = balance - ?" f"WHERE username = ?", (self.bet, self.name))
                    con.commit()
                    self.label_3.setText("Баланс: " f'{self.balance}' "р.")
        else:
            QMessageBox.critical(
                self, 'Денег нету', 'Будешь играть в кредит.',
                QMessageBox.Ok)

    def menshe(self):
        if self.balance > 0:
            self.betz = self.lineEdit.text()
            if not self.betz:
                QMessageBox.critical(
                    self, 'ОШИБКА', 'Введите ставку!',
                    QMessageBox.Ok)
            else:
                self.bet = int(self.betz)
                self.label_7.setText(f"{int(self.betz)}")
                self.result = random.uniform(-9999, 9999)
                self.label_4.setText(f"{int(self.result)}")
                if self.result > 0:
                    self.balance = self.balance - self.bet
                    lose = 'Вы проиграли!'
                    self.label_6.setText(lose)
                    cur.execute(f"UPDATE users SET balance = balance - ?" f"WHERE username = ?", (self.bet, self.name))
                    con.commit()
                    self.label_3.setText("Баланс: " f'{self.balance}' "р.")
                elif self.result < 0:
                    self.balance = self.balance + self.bet
                    win = 'Вы выиграли!'
                    self.label_6.setText(win)
                    cur.execute(f"UPDATE users SET balance = balance + ?" f"WHERE username = ?", (self.bet, self.name))
                    con.commit()
                    self.label_3.setText("Баланс: " f'{self.balance}' "р.")
        else:
            QMessageBox.critical(
                self, 'Денег нету', 'Будешь играть в кредит.',
                QMessageBox.Ok)

    def hohol(self):
        sdf = Lobby()
        sdf.show()


class BonesGame(QMainWindow):
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('bones.ui', self)
        self.balance = args[0]
        self.name = args[1]
        self.setWindowTitle('Кости')
        self.play.clicked.connect(self.start)
        self.label_3.setText("Баланс: " f'{self.balance}' "р.")

    def start(self):
        if self.balance > 0:
            self.betz = self.lineEdit.text()
            if not self.betz:
                QMessageBox.critical(
                    self, 'ОШИБКА', 'Введите ставку!',
                    QMessageBox.Ok)
            else:
                self.bet = int(self.betz)
                self.stavka = int(self.lineEdit_2.text())
                self.label_7.setText(f"{int(self.betz)}")
                self.result = random.randint(1, 6)
                self.label_4.setText(f"{int(self.result)}")
                if self.result == self.stavka:
                    self.balance = self.balance + self.bet
                    win = 'Вы выиграли!'
                    self.label_6.setText(win)
                    cur.execute(f"UPDATE users SET balance = balance + ?" f"WHERE username = ?", (self.bet, self.name))
                    con.commit()
                    self.label_3.setText("Баланс: " f'{self.balance}' "р.")
                elif self.result != self.stavka:
                    self.balance = self.balance - self.bet
                    win = 'Вы проиграли!'
                    self.label_6.setText(win)
                    cur.execute(f"UPDATE users SET balance = balance - ?" f"WHERE username = ?", (self.bet, self.name))
                    con.commit()
                    self.label_3.setText("Баланс: " f'{self.balance}' "р.")
        else:
            QMessageBox.critical(
                self, 'Денег нету', 'Будешь играть в кредит.',
                QMessageBox.Ok)


class SlotsGame(QMainWindow):
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('slots.ui', self)
        self.balance = args[0]
        self.name = args[1]
        self.setWindowTitle('Слоты')
        self.play.clicked.connect(self.start)
        self.label_3.setText("Баланс: " f'{self.balance}' "р.")


    def start(self):
        if self.balance > 0:
            self.betz = self.lineEdit.text()
            if not self.betz:
                QMessageBox.critical(
                    self, 'ОШИБКА', 'Введите ставку!',
                    QMessageBox.Ok)
            else:
                self.bet = int(self.betz)
                self.label_7.setText(f"{int(self.betz)}")
                self.slot1 = random.randint(0, 7)
                self.slot2 = random.randint(0, 7)
                self.slot3 = random.randint(0, 7)
                self.label_4.setText(f"{int(self.slot1)}")
                self.label_5.setText(f"{int(self.slot2)}")
                self.label_9.setText(f"{int(self.slot3)}")

                if (self.slot1 == self.slot2 == self.slot3) and (self.slot1 == 7) and (self.slot2 == 7) and (self.slot3 == 7):
                    self.balance = self.balance + (self.bet * 100)
                    win = 'Вы выиграли!'
                    self.label_6.setText(win)
                    cur.execute(f"UPDATE users SET balance = balance + (? * 10)" f"WHERE username = ?", (self.bet, self.name))
                    con.commit()
                    self.label_3.setText("Баланс: " f'{self.balance}' "р.")

                elif (self.slot1 == self.slot3 == self.slot3) and (self.slot1 != 7):
                    self.balance = self.balance + self.bet
                    win = 'Вы выиграли!'
                    self.label_6.setText(win)
                    cur.execute(f"UPDATE users SET balance = balance + ?" f"WHERE username = ?", (self.bet, self.name))
                    con.commit()
                    self.label_3.setText("Баланс: " f'{self.balance}' "р.")

                elif (self.slot1 == self.slot3 == self.slot3) and (self.slot1 == 6) and (self.slot2 == 6) and (self.slot3 == 6):
                    self.balance = self.balance + (self.bet * 2)
                    win = 'Вы выиграли!'
                    self.label_6.setText(win)
                    cur.execute(f"UPDATE users SET balance = balance + (? * 2)" f"WHERE username = ?", (self.bet, self.name))
                    con.commit()
                    self.label_3.setText("Баланс: " f'{self.balance}' "р.")

                elif (self.slot1 == self.slot3 == self.slot3) and (self.slot1 == 0) and (self.slot2 == 0) and (self.slot3 == 0):
                    self.balance = self.balance + (self.bet * 10)
                    win = 'Вы выиграли!'
                    self.label_6.setText(win)
                    cur.execute(f"UPDATE users SET balance = balance + (? * 10)" f"WHERE username = ?", (self.bet, self.name))
                    con.commit()
                    self.label_3.setText("Баланс: " f'{self.balance}' "р.")

                else:
                    self.balance = self.balance - self.bet
                    win = 'Вы проиграли!'
                    self.label_6.setText(win)
                    cur.execute(f"UPDATE users SET balance = balance - ?" f"WHERE username = ?", (self.bet, self.name))
                    con.commit()
                    self.label_3.setText("Баланс: " f'{self.balance}' "р.")
        else:
            QMessageBox.critical(
                self, 'Денег нету', 'Будешь играть в кредит.',
                QMessageBox.Ok)


class Zerohundred(QMainWindow):
    def __init__(self, *args):
        super().__init__()
        uic.loadUi('0to100.ui', self)
        self.balance = args[0]
        self.name = args[1]
        self.setWindowTitle('Ноль - сто')
        self.play.clicked.connect(self.start)
        self.label_3.setText("Баланс: " f'{self.balance}' "р.")

    def start(self):
        if self.balance > 0:
            self.betz = self.lineEdit.text()
            if not self.betz:
                QMessageBox.critical(
                    self, 'ОШИБКА', 'Введите ставку!',
                    QMessageBox.Ok)
            else:
                self.bet = int(self.betz)
                self.label_7.setText(f"{int(self.betz)}")
                self.slot = random.randint(0, 100)
                self.label_5.setText(f"{int(self.slot)}")

                if self.slot == 0:
                    self.balance = self.balance + (self.bet * 100)
                    win = 'Вы выиграли!'
                    self.label_6.setText(win)
                    cur.execute(f"UPDATE users SET balance = balance + (? * 100)" f"WHERE username = ?", (self.bet, self.name))
                    con.commit()
                    self.label_3.setText("Баланс: " f'{self.balance}' "р.")

                elif (self.slot > 0) and (self.slot <= 10):
                    self.balance = self.balance + (self.bet * 2)
                    win = 'Вы выиграли!'
                    self.label_6.setText(win)
                    cur.execute(f"UPDATE users SET balance = balance + (? * 2)" f"WHERE username = ?", (self.bet, self.name))
                    con.commit()
                    self.label_3.setText("Баланс: " f'{self.balance}' "р.")

                elif (self.slot > 10) and (self.slot <= 50):
                    self.balance = self.balance - self.bet
                    win = 'Вы проиграли!'
                    self.label_6.setText(win)
                    cur.execute(f"UPDATE users SET balance = balance - ?" f"WHERE username = ?", (self.bet, self.name))
                    con.commit()
                    self.label_3.setText("Баланс: " f'{self.balance}' "р.")

                elif (self.slot > 50) and (self.slot <= 55):
                    self.balance = self.balance + (self.bet * 10)
                    win = 'Вы выиграли!'
                    self.label_6.setText(win)
                    cur.execute(f"UPDATE users SET balance = balance + (? * 10)" f"WHERE username = ?", (self.bet, self.name))
                    con.commit()
                    self.label_3.setText("Баланс: " f'{self.balance}' "р.")

                elif (self.slot > 55) and (self.slot <= 99):
                    self.balance = self.balance - self.bet
                    win = 'Вы проиграли!'
                    self.label_6.setText(win)
                    cur.execute(f"UPDATE users SET balance = balance - ?" f"WHERE username = ?", (self.bet, self.name))
                    con.commit()
                    self.label_3.setText("Баланс: " f'{self.balance}' "р.")

                elif self.slot == 100:
                    self.balance = self.balance + (self.bet * 100)
                    win = 'Вы выиграли!'
                    self.label_6.setText(win)
                    cur.execute(f"UPDATE users SET balance = balance + (? * 100)" f"WHERE username = ?", (self.bet, self.name))
                    con.commit()
                    self.label_3.setText("Баланс: " f'{self.balance}' "р.")
        else:
            QMessageBox.critical(
                self, 'Денег нету', 'Будешь играть в кредит.',
                QMessageBox.Ok)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    sys.excepthook = except_hook
    ex = LoginWindow()
    ex.show()
    sys.exit(app.exec_())