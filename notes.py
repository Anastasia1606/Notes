import sqlite3 as sl
import easygui as gui
import os
import datetime

conn = sl.connect("Notes.db", detect_types=sl.PARSE_DECLTYPES|sl.PARSE_COLNAMES)
cur = conn.cursor()
#cur.execute('Drop table notes')
cur.execute("""
            CREATE TABLE IF NOT EXISTS notes
            (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            headline TEXT,
            message TEXT,
            date date
            );""")

#Функция для отображения заметок
def display_notes():
  
  #Создание списка заметок
  cur.execute('SELECT * FROM notes ORDER BY date DESC')
  results = cur.fetchall()

  notes_list = []
  for row in results:
    id, headline, message, date = row 
    date = datetime.datetime.now()  
    notes_list.append("{}: {}, date {}".format(headline, message, date))
  gui.textbox("Заметки","Заметки", "\n".join(notes_list))

#Функция для сохранения заметок в файл
def save_notes():
  cur.execute ("SELECT * FROM notes ORDER BY date DESC")
  rows = cur.fetchall ()
  filedir = gui.diropenbox(msg="Выберите заметку", title="Заметки")
  if filedir != None:
    filename = os.path.join(filedir,"notes.csv")
    file = open(filename, 'w')
    file.write("id;headline;message;date\n")
    for row in rows:
      file.write(";".join(map(str,row))+'\n')
    file.close()
    gui.msgbox ("Записи сохранены в файл notes.csv.", "Экспорт", ok_button="Close")

#Функция для импорта заметок из файла
def import_notes():
  filename = gui.fileopenbox('Выберете csv-файл для импорта данных')
  if filename != None:
    if filename[-4:] != '.csv':
      gui.msgbox ("Неверный формат файла.", "Импорт", ok_button="Close")
    else:
      file = open(filename, 'r')
      i = 0
      for line in file:
        if i == 0:
          i += 1
          continue
        id, headline, message, date = line.strip().split(";")
        cur.execute("INSERT INTO notes (headline, message, date) VALUES (?, ?, ?);", (headline, message, date))
        i += 1
      if i != 0: i -=1  
      conn.commit()
      gui.msgbox (f"Добавлено {i} заметок", "Импорт", ok_button="Close")

#Функция для добавления заметки
def add_notes():
  msg = "Введите заметку"
  title = "Добавление заметки" 
  fieldNames = ["Заголовок","Текст"]
  box = gui.multenterbox(msg,title, fieldNames)
  date = datetime.datetime.now()
  if box != None:
    headline, message = box
    cur.execute("INSERT INTO notes (headline, message, date) VALUES (?, ?, ?);", (headline, message, date))
    conn.commit()
    gui.msgbox ("Заметка сохранена", "Сохранение", ok_button="Close")

#Функция для выборки по дате
def display_date_notes():
  msg = "Введите дату заметки"
  title = "Выборка заметок по дате" 
  fieldNames = ["Дата создания"]
  box = gui.multenterbox(msg,title, fieldNames)
  if box != None:
    datestr = box[0]
    date1= datetime.datetime.strptime(datestr, '%d.%m.%Y')
    date2 = date1 + datetime.timedelta(days=1)
    cur.execute("SELECT * FROM notes WHERE date >= ? and date < ? ;", (date1,date2)) 
                #and date < ? ;' (date1, date2))
    results = cur.fetchall()

    notes_list = []
    for row in results:
      id, headline, message, date = row 
      date = datetime.datetime.now()  
      notes_list.append("{}: {}, date {}".format(headline, message, date))
    gui.textbox("Заметки","Заметки", "\n".join(notes_list))

#Функция для удаления заметки
def delete_notes():
  msg = "Введите заголовок заметки"
  title = "Удаление заметки" 
  fieldNames = ["Заголовок"]
  box = gui.multenterbox(msg,title, fieldNames)
  if box != None:
    headline = box
    cur.execute("SELECT id FROM notes WHERE headline = ? ;", (headline))
    results = cur.fetchall()
    if len(results) > 0:
      cur.execute("Delete FROM notes WHERE headline = ? ;", (headline))
      conn.commit()  
      gui.msgbox("Заметка удалена")
    else:
      gui.msgbox("Заметка не найдена")  

#Функция для редактирования заметки
def modify_note():
  msg = "Введите заголовок заметки"
  title = "Редактирование заметки" 
  fieldNames = ["Заголовок"]
  box = gui.multenterbox(msg,title, fieldNames)
  if box != None:
    headline = box
    cur.execute("SELECT * FROM notes WHERE headline = ? ;", (headline))
    results = cur.fetchall()
    if len(results) > 0:
      id, headline, message, date  = results[0]
      default_list = [headline, message, date]
      fieldNames = ["Заголовок","Текст","Дата создания"]
      msg = "Редактирование заметки"
      box = gui.multenterbox(msg,title, fieldNames, default_list)
      if box != None:
        headline, message, date = box
        date = datetime.datetime.now()  
        cur.execute("Update notes set headline = ? , message = ? , date = ? where id = ? ;", (headline, message, date, id))
        conn.commit()
        gui.msgbox ("Заметка изменена", "Изменение", ok_button="Close")
    else:
      gui.msgbox("Заметка не найдена")

#Функция для просмотра заметки
def display_one_note():
  msg = "Введите заголовок заметки"
  title = "Выбор заметки" 
  fieldNames = ["Заголовок"]
  box = gui.multenterbox(msg,title, fieldNames)
  if box != None:
    headline = box
    cur.execute("SELECT * FROM notes WHERE headline = ? ;", (headline))
    results = cur.fetchall()
    if len(results) > 0:
      id, headline, message, date  = results[0]
      default_list = [headline, message, date]
      msg = "Просмотр заметки"
      fieldNames = ["Заголовок","Текст","Дата создания"]
      box = gui.multenterbox(msg,title, fieldNames, default_list)
    else:
      gui.msgbox("Заметка не найдена")

#Основной код

while True:
  #Отображение главного меню
  choices = ["Сохранение в файл", "Импорт из файла", "Поиск по дате", "Вывести на экран заметку", "Вывести на экран весь список заметок", "Добавление", "Редактирование", "Удаление", "Выход"]
  choice = gui.buttonbox("Заметки", choices = choices)

  #Обработка выбранного действия
  if choice == "Вывести на экран весь список заметок":
    display_notes()
  elif choice == "Поиск по дате":
    display_date_notes()
  elif choice == "Вывести на экран заметку":
    display_one_note() 
  elif choice == "Сохранение в файл":
    save_notes()
  elif choice == "Импорт из файла":
    notes = import_notes()
  elif choice == "Поиск по дате":
    search_notes()
  elif choice == "Добавление":
    add_notes()
  elif choice == "Удаление":
    delete_notes()
  elif choice == "Редактирование":
    modify_note()
  else:
    break 

conn.close()