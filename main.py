from flask import Flask, render_template, request, redirect, jsonify
import pymysql

app = Flask(__name__, template_folder="./")


# Головна сторінка
@app.route('/')
def index():
    # Отримання списку студентів з бази даних

    return render_template('index.html')

@app.route('/students')
def students():
    # устанавливаем соединение с базой данных
    conn = pymysql.connect(host='localhost', user='root', password='', db='university')
    # Запрос к базе данных на получение данных о студентах, группах и оценках
    query = '''
       SELECT `groups`.name as group_name, students.name as student_name, subjects.name as subject_name, grades.grade, students.id as student_id
       FROM grades
       JOIN students ON grades.student_id = students.id
       JOIN `groups` ON students.group_id = groups.id
       JOIN subjects ON grades.subject_id = subjects.id
       ORDER BY group_name, student_name, subject_name
       '''
    cursor = conn.cursor()
    cursor.execute(query)
    # Получение всех строк из результата запроса
    rows = cursor.fetchall()

    # Обработка результатов запроса и создание словаря групп
    groups = {}
    current_group = None
    for row in rows:
        group_name = row[0]
        student_name = row[1]
        subject_name = row[2]
        grade = row[3]
        student_id = row[4]

        if current_group != group_name:
            current_group = group_name
            groups[group_name] = {'students': []}

        if not any(student['name'] == student_name for student in groups[group_name]['students']):
            groups[group_name]['students'].append({'id': student_id, 'name': student_name, 'grades': {}})

        for student in groups[group_name]['students']:
            if student['name'] == student_name:
                student['grades'][subject_name] = grade
                break

    return render_template('students.html', groups=groups)


@app.route('/delete_student', methods=['GET', 'POST'])
def delete_student():
    if request.method == 'POST':
        # Отримуємо ідентифікатор студента, який видаляється
        student_id = request.form.get('student_id')

        # Устанавливаем соединение з базою даних
        conn = pymysql.connect(host='localhost', user='root', password='', db='university')
        cursor = conn.cursor()

        # Удаляем связанные записи в таблице grades
        delete_grades_query = f"DELETE FROM grades WHERE student_id = {student_id}"
        cursor.execute(delete_grades_query)

        # Удаляем запись студента
        delete_student_query = f"DELETE FROM students WHERE id = {student_id}"
        cursor.execute(delete_student_query)
        conn.commit()

        cursor.close()
        conn.close()

        return redirect('/students')
    else:
        return redirect('/students')


@app.route('/update_student', methods=['POST'])
def update_student():
    if request.method == 'POST':
        data = request.get_json()
        student_id = data['student_id']
        grades = data['grades']

        # Устанавливаем соединение с базой данных
        conn = pymysql.connect(host='localhost', user='root', password='', db='university')
        cursor = conn.cursor()

        print(student_id, grades)

        # Обновляем оценки студента в базе данных
        try:
            for subject, grade in grades.items():
                # Получаем идентификатор предмета
                select_subject_query = f"SELECT id FROM subjects WHERE name = '{subject}'"
                cursor.execute(select_subject_query)
                subject_id = cursor.fetchone()[0]

                # Обновляем оценку
                update_query = f"UPDATE grades SET grade = '{grade}' WHERE student_id = '{student_id}' AND subject_id = '{subject_id}'"
                cursor.execute(update_query)

            conn.commit()
            cursor.close()
            conn.close()

            return "Success"

        except Exception as e:
            return jsonify({"error": str(e)})


@app.route('/teachers')
def teachers():
    # устанавливаем соединение с базой данных
    conn = pymysql.connect(host='localhost', user='root', password='', db='university')
    # Запрос к базе данных на получение данных о учителях и их предметах
    query = '''
       SELECT teachers.name as teacher_name, subjects.name as subject_name
       FROM `teachers` 
       INNER JOIN `subjects` ON `teachers`.subject_id = subjects.id 
       ORDER BY teacher_name, subject_name
       '''
    cursor = conn.cursor()
    cursor.execute(query)
    # Получение всех строк из результата запроса
    rows = cursor.fetchall()

    # Обработка результатов запроса и создание словаря учителей
    teachers_subjects = {}
    current_teacher = None
    for row in rows:
        teacher_name = row[0]
        subject_name = row[1]

        if current_teacher != teacher_name:
            current_teacher = teacher_name
            teachers_subjects[teacher_name] = []

        teachers_subjects[teacher_name].append(subject_name)

    return render_template('teachers.html', teachers_subjects=teachers_subjects)

@app.route('/delete_teacher', methods=['GET', 'POST'])
def delete_teacher():
    if request.method == 'POST':
        # Отримуємо ідентифікатор студента, який видаляється
        teacher_name = request.form.get('teacher_name_input')
        print(teacher_name)

        # Устанавливаем соединение з базою даних
        conn = pymysql.connect(host='localhost', user='root', password='', db='university')
        cursor = conn.cursor()

        # Удаляем запись студента
        delete_teacher_query = f"DELETE FROM teachers WHERE name = '{teacher_name}'"
        cursor.execute(delete_teacher_query)
        conn.commit()

        cursor.close()
        conn.close()

        return redirect('/teachers')
    else:
        return redirect('/teachers')

@app.route('/add_teacher', methods=['POST'])
def add_teacher():
    if request.method == 'POST':
        teacher_name = request.form['teacher_name']
        subject_name = request.form['subject_name']

        conn = pymysql.connect(host='localhost', user='root', password='', db='university')
        cursor = conn.cursor()

        select_subject_query = f"SELECT id FROM subjects WHERE name = '{subject_name}'"
        cursor.execute(select_subject_query)
        subject_id = cursor.fetchone()[0]

        # Додавання вчителя
        cursor.execute('INSERT INTO teachers (name, subject_id) VALUES (%s,%s)', (teacher_name,subject_id,))

        conn.commit()
        cursor.close()
        conn.close()

    return redirect('/teachers')

@app.route('/ranking_for_group')
def ranking_for_group():
    # устанавливаем соединение с базой данных
    conn = pymysql.connect(host='localhost', user='root', password='', db='university')
    # Запрос к базе данных на получение данных о студентах, группах и оценках
    query = '''
        SELECT `groups`.name as group_name, students.id as student_id, students.name as student_name, 
               subjects.name as subject_name, grades.grade
        FROM grades
        JOIN students ON grades.student_id = students.id
        JOIN `groups` ON students.group_id = groups.id
        JOIN subjects ON grades.subject_id = subjects.id
        ORDER BY group_name, student_name, subject_name
    '''
    cursor = conn.cursor()
    cursor.execute(query)

    # Получение всех строк из результата запроса
    rows = cursor.fetchall()

    # Обработка результатов запроса и создание словаря групп
    groups = {}
    current_group = None
    for row in rows:
        group_name = row[0]
        student_id = row[1]
        student_name = row[2]
        subject_name = row[3]
        grade = row[4]

        if current_group != group_name:
            current_group = group_name
            groups[group_name] = {'students': []}

        if not any(student['id'] == student_id for student in groups[group_name]['students']):
            groups[group_name]['students'].append({'id': student_id, 'name': student_name, 'grades': {}})

        for student in groups[group_name]['students']:
            if student['id'] == student_id:
                student['grades'][subject_name] = grade
                break

    # Добавление рейтингового балла для каждого студента
    for group in groups.values():
        for student in group['students']:
            grades_sum = sum(student['grades'].values())
            num_subjects = len(student['grades'])
            student['rating'] = round(grades_sum / num_subjects, 2)


    # Запись рейтинговых баллов в таблицу rankings
    with conn.cursor() as cursor:
        for group in groups.values():
            for student in group['students']:
                cursor.execute("SELECT student_id FROM rankings")
                identif_students = cursor.fetchall()
                if student['id'] in [row[0] for row in identif_students]:
                    # Вычисление рейтинга студента
                    grades_sum = sum(student['grades'].values())
                    num_subjects = len(student['grades'])
                    student['rating'] = round(grades_sum / num_subjects, 2)
                    query = f"UPDATE rankings SET `rank` = {student['rating']} WHERE student_id = {student['id']}"
                    cursor.execute(query)
                    conn.commit()
                elif student['id'] not in [row[0] for row in identif_students]:
                    # Вычисление рейтинга студента
                    grades_sum = sum(student['grades'].values())
                    num_subjects = len(student['grades'])
                    student['rating'] = round(grades_sum / num_subjects, 2)
                    query = f"INSERT INTO rankings (student_id, `rank`) VALUES ({student['id']}, {student['rating']})"
                    cursor.execute(query)
                    conn.commit()
            cursor.execute(query)
        conn.commit()

    # Сортировка студентов в каждой группе по рейтингу
    for group in groups.values():
        group['students'] = sorted(group['students'], key=lambda x: x['rating'], reverse=True)

    return render_template('ranking_for_group.html', groups=groups)

@app.route('/ranking')
def ranking():
    # устанавливаем соединение с базой данных
    conn = pymysql.connect(host='localhost', user='root', password='', db='university')
    # Запрос к базе данных на получение данных о студентах, группах и оценках
    query = '''
        SELECT `groups`.name as group_name, students.id as student_id, students.name as student_name, 
               subjects.name as subject_name, grades.grade
        FROM grades
        JOIN students ON grades.student_id = students.id
        JOIN `groups` ON students.group_id = groups.id
        JOIN subjects ON grades.subject_id = subjects.id
        ORDER BY student_name, subject_name
    '''
    cursor = conn.cursor()
    cursor.execute(query)

    # Получение всех строк из результата запроса
    rows = cursor.fetchall()

    # Создание словаря студентов
    students = {}
    for row in rows:
        student_id = row[1]
        student_name = row[2]
        subject_name = row[3]
        grade = row[4]

        if student_id not in students:
            students[student_id] = {'name': student_name, 'group': row[0], 'grades': {}}

        students[student_id]['grades'][subject_name] = grade

    # Запись рейтинговых баллов в таблицу rankings
    with conn.cursor() as cursor:
        cursor.execute("SELECT student_id FROM rankings")
        identif_students = cursor.fetchall()
        for student_id, student in students.items():
            if student_id in [row[0] for row in identif_students]:
                # Вычисление рейтинга студента
                grades_sum = sum(student['grades'].values())
                num_subjects = len(student['grades'])
                student['rating'] = round(grades_sum / num_subjects, 2)
                query = f"UPDATE rankings SET `rank` = {student['rating']} WHERE student_id = {student_id}"
                cursor.execute(query)
                conn.commit()
            elif student_id not in [row[0] for row in identif_students]:
                # Вычисление рейтинга студента
                grades_sum = sum(student['grades'].values())
                num_subjects = len(student['grades'])
                student['rating'] = round(grades_sum / num_subjects, 2)
                query = f"INSERT INTO rankings (student_id, `rank`) VALUES ({student_id}, {student['rating']})"
                cursor.execute(query)
                conn.commit()

    # Сортировка студентов по рейтингу
    students_sorted = sorted(students.values(), key=lambda x: x['rating'], reverse=True)

    return render_template('ranking.html', students_sorted=students_sorted)



@app.route('/students/add')
def add_student():
    conn = pymysql.connect(host='localhost', user='root', password='', db='university')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM `groups`')
    groups = cursor.fetchall()
    print(groups) # добавьте эту строку для отладки
    cursor.execute('SELECT id, name FROM subjects')
    subjects = cursor.fetchall()
    print(subjects) # добавьте эту строку для отладки
    cursor.close()

    return render_template('add_student.html', groups=groups, subjects=subjects)



@app.route('/students/add_form', methods=['GET', 'POST'])
def add_student_form():
    if request.method == 'POST':
        name = request.form['name']
        group_id = request.form['group']
        grades = request.form.getlist('grades[]')
        subject_ids = request.form.getlist('subject_ids[]')

        conn = pymysql.connect(host='localhost', user='root', password='', db='university')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO students (name, group_id) VALUES (%s, %s)', (name, group_id))
        student_id = cursor.lastrowid

        for grade, subject_id in zip(grades, subject_ids):
            cursor.execute('INSERT INTO grades (student_id, subject_id, grade) VALUES (%s, %s, %s)', (student_id, subject_id, grade))

        conn.commit()
        cursor.close()

    return redirect('/students')

if __name__ == '__main__':
    app.run(debug=True)
