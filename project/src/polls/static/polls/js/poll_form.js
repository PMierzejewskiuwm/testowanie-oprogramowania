document.addEventListener('DOMContentLoaded', () => {
  // References to elements needed for dynamic form handling
  const container = document.getElementById('choices-container');
  const list = document.getElementById('choices-list');
  const addBtn = document.getElementById('add-choice');
  const remBtn = document.getElementById('remove-choice');

  // Get min and max number of forms allowed
  const minForms = parseInt(container.dataset.minForms, 10);
  const maxForms = parseInt(container.dataset.maxForms, 10);
  
  // Input that Django uses to track total number of forms in formset
  const totalFormsInp = container.querySelector('input[name$="-TOTAL_FORMS"]');

  // Updates the TOTAL_FORMS input by given delta
  function updateTotal(delta) {
    totalFormsInp.value = parseInt(totalFormsInp.value,10) + delta;
  }

  // Adds a new choice form by cloning the first one and adjusting index
  function addForm() {
    const count = list.children.length;
    if (count >= maxForms) return;
    const newForm = list.children[0].cloneNode(true);
    newForm.innerHTML = newForm.innerHTML.replace(/-(\d+)-/g, `-${count}-`);
    list.appendChild(newForm);
    updateTotal(+1);
  }

  // Removes the last choice form if the minimum number hasn't been reached
  function removeForm() {
    const count = list.children.length;
    if (count <= minForms) return;
    list.removeChild(list.lastElementChild);
    updateTotal(-1);
  }

  // Listens to when the buttons are pressed
  addBtn.addEventListener('click', addForm);
  remBtn.addEventListener('click', removeForm);
});
