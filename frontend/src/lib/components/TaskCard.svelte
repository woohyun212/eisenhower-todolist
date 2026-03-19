<script lang="ts">
  import type { Task } from '$lib/types';
  import AnalyzingBadge from './AnalyzingBadge.svelte';

  let { task, quadrantColor = 'gray', ondelete, ontoggle, onupdate }: {
    task: Task;
    quadrantColor?: string;
    ondelete?: () => void;
    ontoggle?: () => void;
    onupdate?: (data: Partial<Task>) => void;
  } = $props();

  let isUncertain = $derived((task.confidence ?? 1) < 0.6);
  let isAnalyzing = $derived(task.quadrant === null);
  
  let editing = $state(false);
  let editValue = $state(task.title);

  function formatDate(dt: string | null): string {
    if (!dt) return '';
    const d = new Date(dt);
    const month = d.getMonth() + 1;
    const day = d.getDate();
    const hours = d.getHours().toString().padStart(2, '0');
    const minutes = d.getMinutes().toString().padStart(2, '0');
    return `${month}/${day} ${hours}:${minutes}`;
  }

  function startEdit() {
    editing = true;
    editValue = task.title;
  }

  function saveEdit() {
    if (editValue.trim() && editValue !== task.title) {
      onupdate?.({ title: editValue.trim() });
    }
    editing = false;
  }

  function cancelEdit() {
    editing = false;
    editValue = task.title;
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.isComposing) return;
    if (e.key === 'Enter') saveEdit();
    if (e.key === 'Escape') cancelEdit();
  }
</script>

<style>
  .task-card:hover .delete-btn { opacity: 1; }
  .task-card.completed {
    opacity: 0.6;
  }
</style>

<div class="task-card {task.completed ? 'completed' : ''} {isUncertain ? 'bg-white/80 border-2 border-dotted border-blue-300' : 'bg-white border border-transparent'} p-4 rounded-xl shadow-sm flex items-center group">
  <input
    class="rounded w-5 h-5 cursor-pointer"
    type="checkbox"
    checked={task.completed}
    onchange={ontoggle}
  />
  <div class="ml-4 flex-1">
    {#if editing}
      <input
        class="w-full px-2 py-1 border border-gray-300 rounded text-gray-800 font-medium"
        type="text"
        bind:value={editValue}
        onblur={saveEdit}
        onkeydown={handleKeydown}
        autofocus
      />
    {:else}
      <h3
        class="text-gray-800 font-medium cursor-pointer hover:bg-gray-100 px-2 py-1 rounded transition-colors"
        class:line-through={task.completed}
        onclick={startEdit}
      >
        {task.title}
      </h3>
    {/if}
    <div class="flex items-center gap-2 mt-1">
      {#if isAnalyzing}
        <AnalyzingBadge />
      {:else if task.quadrant === null}
        <span class="text-[11px] bg-yellow-50 text-yellow-700 px-2 py-0.5 rounded border border-yellow-200">
          미분류 (수동 분류 필요)
        </span>
      {/if}
      {#if task.parsed_datetime}
        <span class="text-[11px] bg-gray-50 text-gray-500 px-2 py-0.5 rounded border border-gray-200">
          {formatDate(task.parsed_datetime)}
        </span>
      {:else if !isAnalyzing && task.quadrant !== null}
        <span class="text-[11px] text-gray-400">일정 미정</span>
      {/if}
    </div>
  </div>
  <button
    class="delete-btn opacity-0 transition-opacity p-2 text-gray-400 hover:text-red-500"
    onclick={ondelete}
    aria-label="삭제"
  >
    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path d="M6 18L18 6M6 6l12 12" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path>
    </svg>
  </button>
</div>
