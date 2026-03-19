<script lang="ts">
  import { onMount } from 'svelte';
  import Matrix from '$lib/components/Matrix.svelte';
  import TaskInput from '$lib/components/TaskInput.svelte';
  import TaskCard from '$lib/components/TaskCard.svelte';
  import ErrorMessage from '$lib/components/ErrorMessage.svelte';
  import { taskStore } from '$lib/stores/tasks.svelte';

  onMount(() => {
    taskStore.fetchTasks();
  });

  function handleToggle(id: string) {
    const task = taskStore.tasks.find(t => t.id === id);
    if (task) {
      taskStore.updateTask(id, { completed: !task.completed });
    }
  }
</script>

<div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
  <header class="text-center mb-8">
    <h1 class="text-4xl font-bold text-gray-900">아이젠하워 매트릭스</h1>
    <p class="text-gray-600 mt-2">우선순위 기반 할일 관리 시스템</p>
  </header>

  <div class="max-w-6xl mx-auto">
    <TaskInput onsubmit={(title) => taskStore.addTask(title)} />

    {#if taskStore.error}
      <div class="mb-4">
        <ErrorMessage
          message={taskStore.error}
          type="error"
          onDismiss={() => taskStore.error = null}
        />
      </div>
    {/if}

    {#if taskStore.uncategorized.length > 0}
      <div class="mb-6 space-y-2">
        {#each taskStore.uncategorized as task (task.id)}
          <TaskCard
            {task}
            ondelete={() => taskStore.deleteTask(task.id)}
            ontoggle={() => taskStore.updateTask(task.id, { completed: !task.completed })}
            onupdate={(data) => taskStore.updateTask(task.id, data)}
          />
        {/each}
      </div>
    {/if}

    {#if taskStore.loading}
      <section class="grid grid-cols-2 gap-6" style="grid-template-rows: 1fr 1fr; min-height: calc(100vh - 180px);">
        {#each Array(4) as _}
          <div class="rounded-2xl p-6 bg-gray-100 border border-gray-200 animate-pulse">
            <div class="flex items-center gap-2 mb-4">
              <div class="w-2.5 h-2.5 rounded-full bg-gray-300"></div>
              <div class="h-5 w-32 bg-gray-300 rounded"></div>
            </div>
            <div class="space-y-3">
              <div class="h-10 bg-gray-200 rounded-lg"></div>
              <div class="h-10 bg-gray-200 rounded-lg"></div>
              <div class="h-10 bg-gray-200 rounded-lg w-3/4"></div>
            </div>
          </div>
        {/each}
      </section>
    {:else}
      <Matrix
        doTasks={taskStore.doTasks}
        planTasks={taskStore.planTasks}
        delegateTasks={taskStore.delegateTasks}
        eliminateTasks={taskStore.eliminateTasks}
        ondelete={(id) => taskStore.deleteTask(id)}
        ontoggle={handleToggle}
        onupdate={(id, data) => taskStore.updateTask(id, data)}
      />
    {/if}
  </div>
</div>
