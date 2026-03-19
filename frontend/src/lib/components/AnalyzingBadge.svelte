<style>
  .spinner {
    border: 2px solid rgba(0, 0, 0, 0.1);
    border-left-color: #3b82f6;
    border-radius: 50%;
    width: 12px;
    height: 12px;
    animation: spin 1s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
</style>

<span class="text-[11px] bg-blue-50 text-blue-600 px-2 py-0.5 rounded border border-blue-100 inline-flex items-center gap-1.5">
  <span class="spinner"></span>분석 중...
</span>
