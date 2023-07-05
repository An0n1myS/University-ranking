// Отримуємо всі елементи з класом "edit-grade-button"
const editButtons = document.querySelectorAll('.edit-grade-button');
const deleteButtons = document.querySelectorAll('.delete-student-button');
const saveButtons = document.querySelectorAll('.save-grade-button');
const cancelButtons = document.querySelectorAll('.cancel-grade-button');

// Додаємо обробник події для кожної кнопки редагування
editButtons.forEach(button => {
button.addEventListener('click', () => {
  const row = button.parentNode.parentNode;
  const gradeSpans = row.querySelectorAll('.grade');
  const gradeInputs = row.querySelectorAll('.edit-grade-input');

  gradeSpans.forEach(span => {
    span.style.display = 'none';
  });

  gradeInputs.forEach(input => {
    input.style.display = 'inline-block';
  });

  button.classList.add('clicked');
  button.style.display = 'none';
  row.querySelector('.delete-student-button').style.display = 'none';
  row.querySelector('.save-grade-button').style.display = 'inline-block';
  row.querySelector('.cancel-grade-button').style.display = 'inline-block';
});
});


// Додаємо обробник події для кожної кнопки скасування
cancelButtons.forEach(button => {
button.addEventListener('click', () => {
  const row = button.parentNode.parentNode;
  const gradeSpans = row.querySelectorAll('.grade');
  const gradeInputs = row.querySelectorAll('.edit-grade-input');

  gradeSpans.forEach(span => {
    span.style.display = 'inline-block';
  });

  gradeInputs.forEach(input => {
    input.style.display = 'none';
  });

  button.style.display = 'none';
  row.querySelector('.edit-grade-button').classList.remove('clicked');
  row.querySelector('.delete-student-button').classList.remove('clicked');
  row.querySelector('.edit-grade-button').style.display = 'inline-block';
  row.querySelector('.delete-student-button').style.display = 'inline-block';
  row.querySelector('.save-grade-button').style.display = 'none';
});
});
 // JavaScript-код для обработки нажатия кнопки "Зберегти"
document.addEventListener("DOMContentLoaded", function() {
  var saveButtons = document.querySelectorAll(".save-grade-button");

  saveButtons.forEach(function(button) {
    button.addEventListener("click", function(event) {
      var group = button.getAttribute("data-group");
      var student = button.getAttribute("data-student");

      // Собираем все оценки для данного студента
      var inputs = document.querySelectorAll("[data-group='" + group + "'][data-student='" + student + "'][data-subject]");

      var grades = {};
      inputs.forEach(function(input) {
        var subject = input.getAttribute("data-subject");
        var value = input.value;
        grades[subject] = value;
      });

      // Отправляем данные на сервер для обновления оценок студента
      var xhr = new XMLHttpRequest();
      xhr.open("POST", "/update_student", true);
      xhr.setRequestHeader("Content-Type", "application/json");

      xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
          // Обработка успешного ответа от сервера
          location.reload(); // Перезагрузка страницы после обновления оценок
        }
      };

      var data = JSON.stringify({ student_id: student, grades: grades });
      xhr.send(data);
    });
  });
});
