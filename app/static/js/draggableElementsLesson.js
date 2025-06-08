document.addEventListener('DOMContentLoaded', () => {
  function placeCaretAtEnd(el) {
    el.focus();
    const range = document.createRange();
    range.selectNodeContents(el);
    range.collapse(false);
    const sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);
  }

  // Обработка всех редакторов
  document.querySelectorAll('.lesson').forEach(lessonDiv => {
    const editor = lessonDiv.querySelector('.editor-area');
    const form = lessonDiv.querySelector('.lesson-form');
    let savedRange = null;

    if (!editor || !form) return;

    function saveSelection() {
      const sel = window.getSelection();
      if (sel.rangeCount > 0) {
        savedRange = sel.getRangeAt(0);
      }
    }

    editor.addEventListener('keyup', saveSelection);
    editor.addEventListener('mouseup', saveSelection);
    editor.addEventListener('mouseout', saveSelection);

    editor.addEventListener('dragover', e => {
      e.preventDefault();
      e.dataTransfer.dropEffect = 'copy';
    });

    editor.addEventListener('drop', e => {
      e.preventDefault();
      const html = e.dataTransfer.getData('text/html');
      if (!html) return;

      if (savedRange) {
        const sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(savedRange);
        const frag = savedRange.createContextualFragment(html);
        savedRange.deleteContents();
        savedRange.insertNode(frag);
        savedRange = sel.getRangeAt(0);
      } else {
        editor.insertAdjacentHTML('beforeend', html);
      }

      requestAnimationFrame(() => placeCaretAtEnd(editor));
    });

    form.addEventListener('submit', () => {
      let hiddenInput = form.querySelector('input[name="lesson_content"]');
      if (!hiddenInput) {
        hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.name = 'lesson_content';
        form.appendChild(hiddenInput);
      }
      hiddenInput.value = editor.innerHTML;
    });
  });

  // Drag-источники
  document.querySelectorAll('.draggable').forEach(elem => {
    elem.addEventListener('dragstart', e => {
      e.dataTransfer.setData('text/html', elem.dataset.html);
      e.dataTransfer.effectAllowed = 'copy';
    });
  });

  // Кнопка редактирования модуля
  document.querySelectorAll('.btn-edit-module').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.dataset.moduleId;
      const moduleBlock = document.querySelector(`.module-block[data-module-id="${id}"]`);
      moduleBlock.querySelector('h3').style.display = 'none';
      moduleBlock.querySelector('.btn-group').style.display = 'none';
      moduleBlock.querySelector(`.edit-module-form[data-module-id="${id}"]`).style.display = 'block';
    });
  });

  // Отмена редактирования модуля
  document.querySelectorAll('.btn-cancel-edit').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.dataset.moduleId;
      const moduleBlock = document.querySelector(`.module-block[data-module-id="${id}"]`);
      moduleBlock.querySelector('h3').style.display = 'block';
      moduleBlock.querySelector('.btn-group').style.display = 'flex';
      moduleBlock.querySelector(`.edit-module-form[data-module-id="${id}"]`).style.display = 'none';
    });
  });

  // Кнопка редактирования урока
  document.querySelectorAll('.btn-edit-lesson').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.dataset.lessonId;
      const lessonDiv = document.querySelector(`.lesson[data-lesson-id="${id}"]`);
      lessonDiv.querySelector('strong').style.display = 'none';
      lessonDiv.querySelector('.lesson-header .btn-group').style.display = 'none';
      const form = lessonDiv.querySelector('form.edit-lesson-form');
      form.style.display = 'block';

      const editor = form.querySelector('.editor-area');
      if (editor) {
        requestAnimationFrame(() => placeCaretAtEnd(editor));
      }
    });
  });

  // Отмена редактирования урока
  document.querySelectorAll('.btn-cancel-edit-lesson').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.dataset.lessonId;
      const lessonDiv = document.querySelector(`.lesson[data-lesson-id="${id}"]`);
      lessonDiv.querySelector('strong').style.display = 'block';
      lessonDiv.querySelector('.lesson-header .btn-group').style.display = 'flex';
      lessonDiv.querySelector('form.edit-lesson-form').style.display = 'none';
    });
  });
});
