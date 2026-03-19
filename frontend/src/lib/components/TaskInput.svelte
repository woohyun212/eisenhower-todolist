<script lang="ts">
  let { onsubmit }: { onsubmit: (title: string) => void } = $props();
  let inputValue = $state('');
  let inputEl: HTMLInputElement;

  function handleKeydown(e: KeyboardEvent) {
    if (e.isComposing) return;
    if (e.key === 'Enter' && inputValue.trim()) {
      onsubmit(inputValue.trim());
      inputValue = '';
    }
  }
</script>

<section class="mb-8">
  <div class="relative">
    <input
      bind:this={inputEl}
      bind:value={inputValue}
      onkeydown={handleKeydown}
      class="w-full h-14 px-6 rounded-xl border border-gray-200 shadow-sm focus:ring-blue-500 focus:border-blue-500 text-lg transition-all outline-none"
      placeholder="할 일을 입력하세요... (Enter로 추가)"
      type="text"
    />
    <div class="absolute right-6 top-1/2 -translate-y-1/2 text-gray-400 text-sm">Enter ↵</div>
  </div>
</section>
