import { api } from '$lib/api/client';
import type { Task } from '$lib/types';
import { Quadrant } from '$lib/types';

function sortByTime(a: Task, b: Task): number {
  // Completed tasks always last
  if (a.completed !== b.completed) return a.completed ? 1 : -1;

  // Sort by parsed_datetime if both have it (earliest deadline first)
  if (a.parsed_datetime && b.parsed_datetime) {
    return new Date(a.parsed_datetime).getTime() - new Date(b.parsed_datetime).getTime();
  }

  // Tasks with datetime come before tasks without
  if (a.parsed_datetime) return -1;
  if (b.parsed_datetime) return 1;

  // Both have no datetime: sort by created_at ascending
  return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
}

function createTaskStore() {
  let tasks = $state<Task[]>([]);
  let loading = $state(false);
  let error = $state<string | null>(null);

  let doTasks = $derived(
    tasks.filter(t => t.quadrant === Quadrant.DO).sort(sortByTime)
  );
  let planTasks = $derived(
    tasks.filter(t => t.quadrant === Quadrant.PLAN).sort(sortByTime)
  );
  let delegateTasks = $derived(
    tasks.filter(t => t.quadrant === Quadrant.DELEGATE).sort(sortByTime)
  );
  let eliminateTasks = $derived(
    tasks.filter(t => t.quadrant === Quadrant.ELIMINATE).sort(sortByTime)
  );
  let uncategorized = $derived(
    tasks.filter(t => !t.quadrant)
  );

  async function fetchTasks() {
    loading = true;
    error = null;
    try {
      tasks = await api.tasks.list();
    } catch {
      error = '할 일을 불러올 수 없습니다';
    } finally {
      loading = false;
    }
  }

  async function addTask(title: string) {
    const tempId = `temp-${Date.now()}`;
    const tempTask: Task = {
      id: tempId,
      user_id: '',
      title,
      quadrant: null,
      completed: false,
      confidence: 0,
      parsed_datetime: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    // Optimistic add (quadrant=null shows AnalyzingBadge)
    tasks = [...tasks, tempTask];

    try {
      const newTask = await api.tasks.create(title);
      // Replace temp with real task (may have AI classification)
      tasks = tasks.map(t => t.id === tempId ? newTask : t);
    } catch {
      // Rollback
      tasks = tasks.filter(t => t.id !== tempId);
      error = '할 일을 추가할 수 없습니다';
    }
  }

  async function updateTask(id: string, data: Partial<Task>) {
    const oldTasks = [...tasks];
    // Optimistic update
    tasks = tasks.map(t => t.id === id ? { ...t, ...data } : t);

    try {
      const updated = await api.tasks.update(id, data);
      tasks = tasks.map(t => t.id === id ? updated : t);
    } catch {
      // Rollback
      tasks = oldTasks;
      error = '할 일을 수정할 수 없습니다';
    }
  }

  async function deleteTask(id: string) {
    const oldTasks = [...tasks];
    // Optimistic remove
    tasks = tasks.filter(t => t.id !== id);

    try {
      await api.tasks.delete(id);
    } catch {
      // Rollback
      tasks = oldTasks;
      error = '할 일을 삭제할 수 없습니다';
    }
  }

  return {
    get tasks() { return tasks; },
    get loading() { return loading; },
    get error() { return error; },
    set error(v: string | null) { error = v; },
    get doTasks() { return doTasks; },
    get planTasks() { return planTasks; },
    get delegateTasks() { return delegateTasks; },
    get eliminateTasks() { return eliminateTasks; },
    get uncategorized() { return uncategorized; },
    fetchTasks,
    addTask,
    updateTask,
    deleteTask,
  };
}

export const taskStore = createTaskStore();
