let filters = { status: 'all', priority: 'all' };

async function loadTodos() {
  const res = await fetch(`/api/todos?status=${filters.status}&priority=${filters.priority}`);
  const todos = await res.json();
  renderTodos(todos);
  loadStats();
}

async function loadStats() {
  const res = await fetch('/api/stats');
  const stats = await res.json();
  document.getElementById('totalCount').textContent = stats.total;
  document.getElementById('activeCount').textContent = stats.active;
  document.getElementById('doneCount').textContent = stats.completed;
  document.getElementById('highCount').textContent = stats.high_priority;
}

function renderTodos(todos) {
  const list = document.getElementById('todosList');
  if (todos.length === 0) {
    list.innerHTML = '<div class="empty-state">No todos found! Add one above. ✨</div>';
    return;
  }

  list.innerHTML = todos.map(t => {
    const isOverdue = t.due_date && !t.completed && new Date(t.due_date) < new Date();
    const dueDateHtml = t.due_date
      ? `<span class="due-date ${isOverdue ? 'overdue' : ''}">
           📅 ${isOverdue ? '⚠️ Overdue: ' : ''}${t.due_date}
         </span>`
      : '';

    return `
      <div class="todo-item ${t.completed ? 'completed' : ''} ${t.priority}"
           id="todo-${t.id}">
        <div class="todo-check ${t.completed ? 'checked' : ''}"
             onclick="toggleTodo(${t.id}, ${t.completed})">
          ${t.completed ? '✓' : ''}
        </div>
        <div class="todo-content">
          <div class="todo-title">${t.title}</div>
          ${t.description ? `<div class="todo-desc">${t.description}</div>` : ''}
          <div class="todo-meta">
            <span class="priority-badge ${t.priority}">
              ${t.priority === 'high' ? '🔴' : t.priority === 'medium' ? '🟡' : '🟢'}
              ${t.priority}
            </span>
            ${dueDateHtml}
          </div>
        </div>
        <button class="todo-delete" onclick="deleteTodo(${t.id})">✕</button>
      </div>`;
  }).join('');
}

async function addTodo() {
  const title = document.getElementById('titleInput').value.trim();
  if (!title) { alert('Please enter a title!'); return; }

  await fetch('/api/todos', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      title,
      description: document.getElementById('descInput').value.trim(),
      priority: document.getElementById('priorityInput').value,
      due_date: document.getElementById('dueDateInput').value
    })
  });

  document.getElementById('titleInput').value = '';
  document.getElementById('descInput').value = '';
  document.getElementById('dueDateInput').value = '';
  loadTodos();
}

async function toggleTodo(id, completed) {
  await fetch(`/api/todos/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ completed: !completed })
  });
  loadTodos();
}

async function deleteTodo(id) {
  await fetch(`/api/todos/${id}`, { method: 'DELETE' });
  loadTodos();
}

function setFilter(type, value, btn) {
  filters[type] = value;
  const group = btn.parentElement;
  group.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  loadTodos();
}

document.getElementById('titleInput').addEventListener('keydown', e => {
  if (e.key === 'Enter') addTodo();
});

window.onload = () => loadTodos();