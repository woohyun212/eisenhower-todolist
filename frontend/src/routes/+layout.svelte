<script lang="ts">
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { isAuth, logout, getUser } from '$lib/stores/auth.svelte';
  import '../app.css';

  $effect(() => {
    const isAuthenticated = isAuth();
    const currentPath = $page.url.pathname;
    const isPublicRoute = currentPath === '/login' || currentPath === '/register';

    if (!isAuthenticated && !isPublicRoute) {
      goto('/login');
      return;
    }

    if (isAuthenticated && isPublicRoute) {
      goto('/');
    }
  });

  async function handleLogout() {
    await logout();
    goto('/login');
  }
</script>

<svelte:head>
  <title>아이젠하워 매트릭스 - 할일 관리</title>
</svelte:head>

{#if isAuth()}
  <header class="border-b border-gray-200 bg-white">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-4 py-4">
      <h1 class="text-xl font-bold">아이젠하워 매트릭스</h1>
      <div class="flex items-center gap-4">
        <span class="text-sm text-gray-600">{getUser()?.email}</span>
        <button
          on:click={handleLogout}
          class="rounded bg-red-500 px-4 py-2 text-white hover:bg-red-600"
        >
          로그아웃
        </button>
      </div>
    </div>
  </header>
{/if}
<slot />
