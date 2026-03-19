<script lang="ts">
  import type { Task } from '$lib/types';
  import { dndzone } from 'svelte-dnd-action';
  import EmptyQuadrant from './EmptyQuadrant.svelte';
  import TaskCard from './TaskCard.svelte';

  let { quadrant, tasks = [], ondelete, ontoggle, onupdate, onDrop }: {
    quadrant: string;
    tasks: Task[];
    ondelete?: (id: string) => void;
    ontoggle?: (id: string) => void;
    onupdate?: (id: string, data: Partial<Task>) => void;
    onDrop?: (task: Task, newQuadrant: string) => void;
  } = $props();

  let items = $state<Task[]>([]);

  $effect(() => {
    items = [...tasks];
  });

  const config: Record<string, { bg: string; border: string; dot: string; titleColor: string; hintColor: string; label: string; hint: string }> = {
    DO: { bg: 'bg-[#fee2e2]', border: 'border-red-100', dot: 'bg-[#ef4444]', titleColor: 'text-red-900', hintColor: 'text-red-700', label: '지금 하기 (DO)', hint: '긴급하고 중요한 일' },
    PLAN: { bg: 'bg-[#dbeafe]', border: 'border-blue-100', dot: 'bg-[#3b82f6]', titleColor: 'text-blue-900', hintColor: 'text-blue-700', label: '계획하기 (PLAN)', hint: '중요하지만 급하지 않은 일' },
    DELEGATE: { bg: 'bg-[#fef3c7]', border: 'border-amber-100', dot: 'bg-[#f59e0b]', titleColor: 'text-amber-900', hintColor: 'text-amber-700', label: '위임하기 (DELEGATE)', hint: '급하지만 중요하지 않은 일' },
    ELIMINATE: { bg: 'bg-[#f3f4f6]', border: 'border-gray-200', dot: 'bg-[#6b7280]', titleColor: 'text-gray-900', hintColor: 'text-gray-700', label: '제거 (ELIMINATE)', hint: '급하지도 중요하지도 않은 일' },
  };

  let c = $derived(config[quadrant]);

  function handleConsider(e: CustomEvent) {
    items = e.detail.items;
  }

  function handleFinalize(e: CustomEvent) {
    items = e.detail.items;
    const droppedId = e.detail.info?.id;
    if (droppedId && onDrop) {
      const movedTask = items.find(t => t.id === droppedId);
      if (movedTask) {
        onDrop(movedTask, quadrant);
      }
    }
  }
</script>

<article
  class="{c.bg} rounded-2xl p-6 flex flex-col shadow-sm border {c.border}"
  data-quadrant={quadrant}
>
  <header class="mb-4">
    <div class="flex items-center gap-2 mb-1">
      <span class="w-2.5 h-2.5 rounded-full {c.dot}"></span>
      <h2 class="text-lg font-bold {c.titleColor}">{c.label}</h2>
      <span class="text-sm text-gray-500">({tasks.length})</span>
    </div>
    <p class="text-sm {c.hintColor} opacity-80">{c.hint}</p>
  </header>
  <div
    class="space-y-3 flex-1 overflow-auto min-h-[60px]"
    use:dndzone={{ items, flipDurationMs: 200, type: 'task' }}
    on:consider={handleConsider}
    on:finalize={handleFinalize}
  >
    {#if items.length === 0}
      <EmptyQuadrant />
    {:else}
      {#each items as task (task.id)}
        <TaskCard
          {task}
          ondelete={() => ondelete?.(task.id)}
          ontoggle={() => ontoggle?.(task.id)}
          onupdate={(data) => onupdate?.(task.id, data)}
        />
      {/each}
    {/if}
  </div>
</article>
