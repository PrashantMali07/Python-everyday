import sqlite3

## Connect to the database
connection=sqlite3.connect("students.db")

## create a cursor object read/write/delete operations
cursor=connection.cursor()

## table info
table_info="""CREATE TABLE IF NOT EXISTS students(st_name VARCHAR(50),st_class VARCHAR(25), st_section VARCHAR(25), st_marks INT)"""

print("Dropping the students table, if exists...")
cursor.execute("DROP TABLE IF EXISTS students") ## dropping the table if it already exists

cursor.execute(table_info)

## creating and inserting some student data
student_data=[("John Doe","10th","A",85),("Jane Smith","10th","B",90),("Emily Davis","9th","A",78),("Michael Brown","9th","B",92),("Sarah Jenkins","9th","B",92),("Michael Chang","11th","A",78),("Emily Rodriguez","10th","C",88),("David Smith","12th","B",95),("Jessica Taylor","9th","A",81),("Robert Wilson","10th","B",74),("Amanda Lee","11th","C",89),("Kevin Martinez","12th","A",91),
("Rachel Thomas","9th","C",83),("Christopher Brown","10th","A",76),("Melissa Garcia","11th","B",94),("Brian Anderson","12th","C",87),("Lauren Miller","9th","B",79),("Jason Davis","10th","C",96),("Stephanie Moore","11th","A",84),("Matthew Jackson","12th","B",72),("Nicole White","9th","A",88),("Daniel Harris","10th","B",93),("Elizabeth Clark","11th","C",85),("James Lewis","12th","A",90)]

print("Inserting student data into the database...")
for data in student_data:
    cursor.execute("INSERT INTO students VALUES (?,?,?,?)", data)

print("Data inserted successfully!")
print("Checking the inserted data...")
# cursor.execute("SELECT * FROM students")
rows=cursor.execute("SELECT * FROM students")

for row in rows:
    print(row)

## commit the changes and close the connection
connection.commit()
connection.close()