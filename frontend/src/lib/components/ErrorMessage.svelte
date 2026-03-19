<script lang="ts">
  let { message, type = 'error', onDismiss }: {
    message: string;
    type?: 'error' | 'warning' | 'info';
    onDismiss?: () => void;
  } = $props();

  const colors: Record<string, string> = {
    error: 'bg-red-50 border-red-200 text-red-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800',
  };

  const icons: Record<string, string> = {
    error: '⚠',
    warning: '⚡',
    info: 'ℹ',
  };
</script>

<div class="flex items-center justify-between gap-3 px-4 py-3 rounded-lg border text-sm {colors[type]}" role="alert">
  <div class="flex items-center gap-2">
    <span class="text-base" aria-hidden="true">{icons[type]}</span>
    <span>{message}</span>
  </div>
  {#if onDismiss}
    <button
      onclick={onDismiss}
      class="shrink-0 opacity-60 hover:opacity-100 transition-opacity text-lg leading-none"
      aria-label="닫기"
    >&times;</button>
  {/if}
</div>
