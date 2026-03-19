<script lang="ts">
  import { getError, login } from '$lib/stores/auth.svelte';

  let email = $state('');
  let password = $state('');
  let isLoading = $state(false);
  let error = $state<string | null>(null);

  async function handleLogin(event: SubmitEvent) {
    event.preventDefault();
    isLoading = true;
    error = null;
    const success = await login(email, password);
    isLoading = false;
    if (success) {
      window.location.href = '/';
    } else {
      error = getError() || '로그인에 실패했습니다';
    }
  }
</script>

<div class="min-h-screen bg-white">
  <!-- Header -->
  <header class="h-16 bg-white border-b border-gray-100 flex items-center px-6">
    <div class="flex items-center gap-3">
      <div class="w-8 h-8 bg-blue-500 rounded flex items-center justify-center">
        <svg class="w-5 h-5 text-white" viewBox="0 0 24 24" fill="currentColor">
          <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-size="14" font-weight="bold" fill="white">E</text>
        </svg>
      </div>
      <h1 class="text-lg font-semibold text-gray-900">아이젠하워 매트릭스</h1>
    </div>
  </header>

  <!-- Center Card -->
  <div class="flex items-center justify-center pt-20">
    <div class="w-[400px] p-10 bg-white border border-gray-200 rounded-xl shadow-sm">
      <h2 class="text-2xl font-semibold text-gray-900 mb-2">로그인</h2>
      <p class="text-sm text-gray-500 mb-6">오늘의 우선순위를 관리하세요</p>

      <form onsubmit={handleLogin} class="space-y-6">
        <!-- Email Input -->
        <div>
          <label for="email" class="block text-sm font-medium text-gray-700 mb-2">이메일</label>
          <input
            id="email"
            type="email"
            bind:value={email}
            placeholder="example@email.com"
            class="w-full px-4 py-2 bg-[#f9fafb] border border-gray-200 rounded-lg text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <!-- Password Input -->
        <div>
          <label for="password" class="block text-sm font-medium text-gray-700 mb-2">비밀번호</label>
          <input
            id="password"
            type="password"
            bind:value={password}
            placeholder="••••••••"
            class="w-full px-4 py-2 bg-[#f9fafb] border border-gray-200 rounded-lg text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <!-- Error Message -->
        {#if error}
          <div class="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
            {error}
          </div>
        {/if}

        <!-- Login Button -->
        <button
          type="submit"
          disabled={isLoading}
          class="w-full py-3 bg-[#3b82f6] hover:bg-blue-600 disabled:bg-blue-400 text-white font-semibold rounded-lg transition-colors"
        >
          {isLoading ? '로그인 중...' : '로그인'}
        </button>
      </form>

      <!-- Register Link -->
      <div class="mt-6 text-center text-sm text-gray-600">
        계정이 없으신가요?{' '}
        <a href="/register" class="text-blue-500 hover:text-blue-600 font-medium">회원가입</a>
      </div>
    </div>
  </div>
</div>
