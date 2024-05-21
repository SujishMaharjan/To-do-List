import sys,sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QVBoxLayout, QLineEdit, QWidget
from datetime import datetime
from UI.login_ui import Ui_LoginMainWindow
from UI.main_window_ui import Ui_MainWindow


class ShowDialogue():
    def show_dialog(self,message):
        msg = QMessageBox()
        msg.setWindowTitle("Message ")
        msg.setText(message)
        x = msg.exec_() 

global_user_id = 0

class Login(QMainWindow,ShowDialogue):
    def __init__(self):
        super(Login, self).__init__()
        self.login_ui = Ui_LoginMainWindow()
        self.login_ui.setupUi(self)
        self.login_ui.login.clicked.connect(self.login)
        self.login_ui.add_users.clicked.connect(self.create_user)
        self.login_ui.delete_user.clicked.connect(self.delete_user)
        self.login_ui.show_users.clicked.connect(self.show_users)     

    def login(self):
        con = create_connection()
        cur = con.cursor()

        if self.login_ui.username.text()=="" or self.login_ui.password.text()=="":
            self.show_dialog("Please Enter Username and Password")
        else:
            cur.execute("select user_id from users where username = ? and password = ?;",(self.login_ui.username.text(),self.login_ui.password.text()))
            user_id = cur.fetchone()

            if user_id == None:
                message = "Please Enter valid username or password"
                self.show_dialog(message)
            else:
                global global_user_id
                global_user_id = user_id[0]
                message = "Login Successful"
                self.show_dialog(message)

                
                username = self.login_ui.username.text()

                #initializing input date placeholders to empty
                self.login_ui.username.setText("")
                self.login_ui.password.setText("")
                item_zero =()
                self.load_user_to_table(item_zero)

                
                
                self.close()
                self.main_window = MainWindow(username)
                self.main_window.show()

    def create_user(self):
        con = create_connection()
        #user_add_query = """INSERT INTO users (username, password) values (?, ?);"""
        cur = con.cursor()
        cur.execute("select username from users;")
        result_tuple= cur.fetchall()
        
        all_users = []
        for item in result_tuple:
            for i in item:
                all_users.append(i)

        if self.login_ui.password.text()=="" or self.login_ui.username.text()=="":
            self.show_dialog("Please Enter Username and Password")
        elif self.login_ui.username.text() in all_users:
            self.show_dialog(f"Username {self.login_ui.username.text()} has been taken.\nPlease use another username.")
        else:
            cur.execute("INSERT INTO users (username, password) values (?, ?);",(self.login_ui.username.text(),self.login_ui.password.text()))
            con.commit()
            self.show_dialog(f"User {self.login_ui.username.text()}  Successfully created")
            self.show_users()
            self.login_ui.username.setText("")
            self.login_ui.password.setText("")

    def show_users(self):
        con = create_connection()
        cur = con.cursor()
        cur.execute("select username from users;")
        rows = cur.fetchall()
        self.load_user_to_table(rows)

    def load_user_to_table(self,users):
        self.login_ui.tableWidgetUsers.setRowCount(len(users))
        self.login_ui.tableWidgetUsers.setColumnCount(1)
        self.login_ui.tableWidgetUsers.setHorizontalHeaderLabels(('Users',''))
        
        
        self.login_ui.tableWidgetUsers.setColumnWidth(0,100)
        self.login_ui.tableWidgetUsers.setColumnWidth(1,1)
    
    
        
    
        row_index = 0
        for item in users:
            self.login_ui.tableWidgetUsers.setItem(row_index,0,QTableWidgetItem(item[0]))
            row_index +=1
       
    def delete_user(self):
        con = create_connection()
        cur = con.cursor()
        cur.execute("select username from users;")
        result_tuple= cur.fetchall()
        
        all_users = []
        for item in result_tuple:
            for i in item:
                all_users.append(i)

        if self.login_ui.password.text() == "" or self.login_ui.username.text()=="":
                self.show_dialog("Please Enter Username and Password")
    
        elif self.login_ui.username.text() not in all_users:
            self.show_dialog(f"There is no such Username {self.login_ui.username.text()}")
        
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Close")
            msg.setText("Are you sure")
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel | QMessageBox.Ignore)
            msg.setDefaultButton(QMessageBox.Cancel)
            msg.setDetailedText("Details...")
            msg.buttonClicked.connect(self.popup_button)
            x = msg.exec_()

    def popup_button(self,i):
        con = create_connection()
        cur = con.cursor()
        if i.text() == "OK":
            cur.execute("select user_id from users where username = ? and password= ?;",(self.login_ui.username.text(),self.login_ui.password.text()))
            user_id = cur.fetchone()
            cur.execute("DELETE FROM users where username = ? and password = ?;",(self.login_ui.username.text(),self.login_ui.password.text()))
            cur.execute("DELETE FROM tasks where user_id= ?;",user_id)
            con.commit()
        
        self.login_ui.username.setText("")
        self.login_ui.password.setText("")
        self.show_users()



class MainWindow(QMainWindow,ShowDialogue):
    def __init__(self, username):
        super(MainWindow,self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.view_uncompleted_task.clicked.connect(self.view_uncompleted_task)
        self.ui.add_task_to_user.clicked.connect(self.add_task_to_users)
        self.ui.delete_task_by_task_id.clicked.connect(self.delete_task_by_task_id)
        self.ui.update_completed_date_for_finished_task.clicked.connect(self.update_task_by_task_id)
        self.ui.view_all_list.clicked.connect(self.view_all_tasks)
        self.ui.view_completed_task.clicked.connect(self.view_completed_task)
        self.ui.go_back.clicked.connect(self.go_back)
        self.ui.login_success_txt.setText(f"Welcome {username}")           

    def load_items_to_table(self,items):
        self.ui.tableWidget.setRowCount(len(items))
        self.ui.tableWidget.setColumnCount(3)
        
        self.ui.tableWidget.setHorizontalHeaderLabels(('Task ID','Task Title','Task Description'))
        
        self.ui.tableWidget.setColumnWidth(0,70)
        self.ui.tableWidget.setColumnWidth(1,150)
        self.ui.tableWidget.setColumnWidth(2,350)
        
        row_index = 0
        for item in items:
            self.ui.tableWidget.setItem(row_index,0,QTableWidgetItem(str(item[0])))
            self.ui.tableWidget.setItem(row_index,1,QTableWidgetItem(item[1]))
            self.ui.tableWidget.setItem(row_index,2,QTableWidgetItem(item[2]))
            row_index +=1

    def view_uncompleted_task(self):
        self.ui.lbl_result.setText("UNCOMPLETED TASKS")
        con = create_connection()
        cur = con.cursor()
        cur.execute("select task_id ,task_title, task_description from tasks where user_id = ? AND completed_date IS NULL OR completed_date = '';",(global_user_id,))
        rows = cur.fetchall()
        self.load_items_to_table(rows)
           
    def add_task_to_users(self):
        con = create_connection()
        cur = con.cursor()
        task_add_query = """
            INSERT INTO tasks (user_id, task_title, task_description, created_date)
            values(?, ?, ?, ?);
        """

        current_datetime = datetime.now()
        tasks =(global_user_id,self.ui.task_title.text(),self.ui.task_description.toPlainText(),current_datetime)
        cur.execute(task_add_query,tasks)
        con.commit()
        self.show_dialog("Added")
        self.ui.task_title.setText("")
        self.ui.task_description.setText("")
        self.view_uncompleted_task()

    def delete_task_by_task_id(self):
        con = create_connection()
        cur = con.cursor()

        cur.execute("SELECT task_id from tasks where user_id = ?;",(global_user_id,))
        result = cur.fetchall()

        user_ids=[]
        for item in result:
            user_ids.append(item[0])


        if self.ui.task_id_to_del.text()=="":
            self.show_dialog("Please Enter Task ID to Delete")
        elif not self.ui.task_id_to_del.text().isdigit():
            self.show_dialog("Please Enter Valid Task ID to Delete")
        elif int(self.ui.task_id_to_del.text()) not in user_ids:
            self.show_dialog(f"No such id {self.ui.task_id_to_del.text()} to delete")
        else:
            cur.execute("delete from tasks where task_id = ?;",(self.ui.task_id_to_del.text(),))
            con.commit()
            self.show_dialog("Deleted")
            self.ui.task_id_to_del.setText("")
        
            self.view_all_tasks()
        
    def update_task_by_task_id(self):
        con = create_connection()
        cur = con.cursor()
        cur.execute("SELECT task_id from tasks where user_id = ?;",(global_user_id,))
        result = cur.fetchall()
        
        user_ids=[]
        for item in result:
            user_ids.append(item[0])

        if self.ui.task_id_to_update.text()=="":
            self.show_dialog("Please Enter Task ID")
        elif not self.ui.task_id_to_update.text().isdigit():
            self.show_dialog("Please Enter Valid Task ID to Finish")
        elif int(self.ui.task_id_to_update.text()) not in user_ids:
            self.show_dialog(f"No such ID {self.ui.task_id_to_update.text()} to finish")
        else:
            completed_date = datetime.now()
            cur.execute("update tasks set completed_date = ? where task_id = ?;",(completed_date,self.ui.task_id_to_update.text()))
            con.commit()
            cur.execute("Select task_title from tasks where task_id = ?;",(self.ui.task_id_to_update.text(),))
            task_title = cur.fetchone()
            self.show_dialog(f"Task Id {self.ui.task_id_to_update.text()} Task Title {task_title}\n is updated to \nCompleted Task")
            self.ui.task_id_to_update.setText("")
            self.view_completed_task()

    def view_all_tasks(self):
        self.ui.lbl_result.setText("ALL TASKS")
        con = create_connection()
        cur = con.cursor()
        cur.execute("select task_id ,task_title, task_description from tasks WHERE user_id = ?;",(global_user_id,))
        rows = cur.fetchall()
        self.load_items_to_table(rows)
        
    def view_completed_task(self):
        self.ui.lbl_result.setText("COMPLETED TASK")
        con = create_connection()
        cur = con.cursor()
        global global_user_id
        cur.execute("select task_id, task_title, task_description from tasks where user_id = ? AND completed_date IS NOT NULL AND completed_date != '';",(global_user_id,))
        rows = cur.fetchall()
        self.load_items_to_table(rows)
        
    def go_back(self):
        item_zero = ()
        self.load_items_to_table(item_zero)
        self.ui.lbl_result.setText("RESULT")
        self.ui.task_title.setText("")
        self.ui.task_description.setText("")
        self.ui.task_id_to_del.setText("")
        self.ui.task_id_to_update.setText("")
        self.close()
        login_window.show()  

        

DB_NAME = "user.sqlite3"
def create_connection():
    try:
        con = sqlite3.connect(DB_NAME)
        return con
    except Exception as e:
        print(str(e))

def create_task_table(con):
    CREATE_TASKS_TABLE_QUERY = """
    CREATE TABLE IF NOT EXISTS tasks (
        task_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        task_title CHAR(255) NOT NULL,
        task_description TEXT,
        created_date DATETIME,
        scheduled_date DATETIME,
        completed_date DATETIME,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    );
    """
    cur = con.cursor()
    cur.execute(CREATE_TASKS_TABLE_QUERY)

def create_table_user(con):
    CREATE_USERS_TABLE_QUERY = """
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username CHAR(255) NOT NULL,
        password CHAR(255) NOT NULL,
        CONSTRAINT username_unique UNIQUE (username)
    );
    """
    cur = con.cursor()
    cur.execute(CREATE_USERS_TABLE_QUERY)

def adapt_datetime(dt):#Function to adapt datetime objects to a string
    return dt.strftime("%Y-%m-%d %H:%M:%S")
sqlite3.register_adapter(datetime, adapt_datetime)#reister the adapter


if __name__ == "__main__":
    con = create_connection()
    create_table_user(con)
    create_task_table(con)
    app = QApplication(sys.argv)
    login_window = Login()
    login_window.show()
    

    

    sys.exit(app.exec_())
