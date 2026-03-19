<script lang="ts">
  import type { Quadrant, Task } from '$lib/types';
  import { taskStore } from '$lib/stores/tasks.svelte';
  import QuadrantComponent from './Quadrant.svelte';

  let { doTasks = [], planTasks = [], delegateTasks = [], eliminateTasks = [], ondelete, ontoggle, onupdate }: {
    doTasks: Task[];
    planTasks: Task[];
    delegateTasks: Task[];
    eliminateTasks: Task[];
    ondelete?: (id: string) => void;
    ontoggle?: (id: string) => void;
    onupdate?: (id: string, data: Partial<Task>) => void;
  } = $props();

  const quadrantMap: Record<string, Quadrant> = {
    DO: 'DO' as Quadrant,
    PLAN: 'PLAN' as Quadrant,
    DELEGATE: 'DELEGATE' as Quadrant,
    ELIMINATE: 'ELIMINATE' as Quadrant,
  };

  async function handleDrop(task: Task, displayQuadrant: string) {
    const newQuadrant = quadrantMap[displayQuadrant];
    if (task.quadrant === newQuadrant) return;
    await taskStore.updateTask(task.id, { quadrant: newQuadrant as any, user_override: true });
  }
</script>

<section class="grid grid-cols-2 gap-6" style="grid-template-rows: 1fr 1fr; min-height: calc(100vh - 180px);">
  <QuadrantComponent quadrant="DO" tasks={doTasks} onDrop={handleDrop} {ondelete} {ontoggle} {onupdate} />
  <QuadrantComponent quadrant="PLAN" tasks={planTasks} onDrop={handleDrop} {ondelete} {ontoggle} {onupdate} />
  <QuadrantComponent quadrant="DELEGATE" tasks={delegateTasks} onDrop={handleDrop} {ondelete} {ontoggle} {onupdate} />
  <QuadrantComponent quadrant="ELIMINATE" tasks={eliminateTasks} onDrop={handleDrop} {ondelete} {ontoggle} {onupdate} />
</section>
