<script lang="ts">
  import { getError, register } from '$lib/stores/auth.svelte';

  let email = $state('');
  let password = $state('');
  let confirmPassword = $state('');
  let isLoading = $state(false);
  let error = $state<string | null>(null);

  async function handleRegister(event: SubmitEvent) {
    event.preventDefault();
    if (password !== confirmPassword) {
      error = '비밀번호가 일치하지 않습니다';
      return;
    }

    isLoading = true;
    error = null;
    const success = await register(email, password);
    isLoading = false;
    if (success) {
      window.location.href = '/';
    } else {
      error = getError() || '회원가입에 실패했습니다. 다시 시도해주세요';
    }
  }
</script>

<div class="min-h-screen bg-white flex items-center justify-center">
  <div class="w-full max-w-[420px] py-12 px-6">
    <!-- Logo -->
    <div class="flex justify-center mb-6">
      <div class="w-12 h-12 bg-[#3b82f6] rounded flex items-center justify-center">
        <span class="text-white font-bold text-2xl">E</span>
      </div>
    </div>

    <!-- Title -->
    <h1 class="text-2xl font-bold text-gray-900 text-center mb-2">아이젠하워 매트릭스</h1>
    <p class="text-sm text-gray-500 text-center mb-8">생산성을 높이는 가장 스마트한 방법</p>

    <!-- Form -->
    <form onsubmit={handleRegister} class="space-y-4">
      <!-- Email Input -->
      <div>
        <label for="email" class="block text-sm font-medium text-gray-700 mb-2">이메일</label>
        <input
          id="email"
          type="email"
          bind:value={email}
          placeholder="example@email.com"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
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
          class="w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
        />
      </div>

      <!-- Confirm Password Input -->
      <div>
        <label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-2">비밀번호 확인</label>
        <input
          id="confirmPassword"
          type="password"
          bind:value={confirmPassword}
          placeholder="••••••••"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
        />
      </div>

      <!-- Error Message -->
      {#if error}
        <div class="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
          {error}
        </div>
      {/if}

      <!-- Register Button -->
      <button
        type="submit"
        disabled={isLoading}
        class="w-full py-3 bg-[#3b82f6] hover:bg-blue-600 disabled:bg-blue-400 text-white font-semibold rounded-lg transition-colors"
      >
        {isLoading ? '회원가입 중...' : '회원가입'}
      </button>
    </form>

    <!-- Divider -->
    <div class="flex items-center gap-3 my-6">
      <div class="flex-1 h-px bg-gray-200"></div>
      <span class="text-sm text-gray-500">또는</span>
      <div class="flex-1 h-px bg-gray-200"></div>
    </div>

    <!-- Login Link -->
    <div class="text-center text-sm text-gray-600">
      이미 계정이 있으신가요?{' '}
      <a href="/login" class="text-blue-500 hover:text-blue-600 font-medium">로그인</a>
    </div>
  </div>
</div>
