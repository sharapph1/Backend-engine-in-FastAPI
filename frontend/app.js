/**
 * WebX Frontend Application Core Architecture
 * Senior Integration & QA Client Engine
 */

const API_BASE_URL = 'http://10.170.204.130:8000/api/v1';
const API_HOST = "http://10.170.204.130:8000";

// Client State
const state = {
  accessToken: localStorage.getItem('webx_access_token') || null,
  refreshToken: localStorage.getItem('webx_refresh_token') || null,
  currentUser: null,
  isRefreshing: false,
};

// UI Elements Cache
const elements = {};

document.addEventListener('DOMContentLoaded', () => {
  initElementsCache();
  setupTabNavigation();
  setupEventListeners();
  checkApiHealth();

  if (state.accessToken) {
    fetchProfileData();
  } else {
    updateHeaderUserStatus();
  }
});

// Cache DOM Elements
function initElementsCache() {
  elements.apiStatusBadge = document.getElementById('apiStatusBadge');
  elements.apiStatusText = document.getElementById('apiStatusText');
  elements.userProfileBadge = document.getElementById('userProfileBadge');
  elements.headerUsername = document.getElementById('headerUsername');
  elements.headerUserTag = document.getElementById('headerUserTag');
  elements.headerLogoutBtn = document.getElementById('headerLogoutBtn');
  elements.globalAlert = document.getElementById('globalAlert');
  elements.apiLogConsole = document.getElementById('apiLogConsole');
  elements.clearApiLogsBtn = document.getElementById('clearApiLogsBtn');
  
  // Forms & Interactive Displays
  elements.registerForm = document.getElementById('registerForm');
  elements.verifyOtpForm = document.getElementById('verifyOtpForm');
  elements.resendOtpBtn = document.getElementById('resendOtpBtn');
  elements.loginForm = document.getElementById('loginForm');
  elements.fetchProfileBtn = document.getElementById('fetchProfileBtn');
  elements.profileDetails = document.getElementById('profileDetails');
  elements.tokenDisplayAccess = document.getElementById('tokenDisplayAccess');
  elements.tokenDisplayRefresh = document.getElementById('tokenDisplayRefresh');
  elements.refreshTokenBtn = document.getElementById('refreshTokenBtn');
  elements.logoutBtn = document.getElementById('logoutBtn');
  
  // Streaks & Referrals
  elements.currentStreakNum = document.getElementById('currentStreakNum');
  elements.highestStreakNum = document.getElementById('highestStreakNum');
  elements.lastClaimDate = document.getElementById('lastClaimDate');
  elements.claimStreakBtn = document.getElementById('claimStreakBtn');
  elements.kycBadge = document.getElementById('kycBadge');
  elements.myReferralCode = document.getElementById('myReferralCode');
  elements.totalReferralsCount = document.getElementById('totalReferralsCount');
  elements.referredUsersList = document.getElementById('referredUsersList');
  elements.claimReferralForm = document.getElementById('claimReferralForm');
  elements.copyReferralBtn = document.getElementById('copyReferralBtn');
  
  // Games & Analytics
  elements.createGameForm = document.getElementById('createGameForm');
  elements.refreshGamesBtn = document.getElementById('refreshGamesBtn');
  elements.gamesGrid = document.getElementById('gamesGrid');
  elements.logAdForm = document.getElementById('logAdForm');
  elements.adBannerCount = document.getElementById('adBannerCount');
  elements.adInterstitialCount = document.getElementById('adInterstitialCount');
  elements.adRewardedCount = document.getElementById('adRewardedCount');
  elements.adNativeCount = document.getElementById('adNativeCount');
  
  // Modal
  elements.webviewModal = document.getElementById('webviewModal');
  elements.modalGameTitle = document.getElementById('modalGameTitle');
  elements.gameIframe = document.getElementById('gameIframe');
  elements.closeModalBtn = document.getElementById('closeModalBtn');
}

// --- API HTTP Client with Token Refresh & Logging ---
async function apiFetch(endpoint, options = {}, isRetry = false) {
  const url = `${API_BASE_URL}${endpoint}`;
  options.headers = options.headers || {};
  options.headers['Content-Type'] = options.headers['Content-Type'] || 'application/json';

  if (state.accessToken && !options.headers['Authorization']) {
    options.headers['Authorization'] = `Bearer ${state.accessToken}`;
  }

  logApiRequest(options.method || 'GET', endpoint, options.body);

  try {
    const response = await fetch(url, options);
    let data = null;
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    logApiResponse(options.method || 'GET', endpoint, response.status, data);

    // 401 Unauthorized -> Handle Automatic Token Refresh Flow
    if (response.status === 401 && state.refreshToken && !isRetry && !endpoint.includes('/auth/login')) {
      logApiConsole(`⚠️ 401 Unauthorized on ${endpoint}. Attempting automatic JWT refresh...`, 'info');
      const refreshed = await autoRefreshToken();
      if (refreshed) {
        options.headers['Authorization'] = `Bearer ${state.accessToken}`;
        return await apiFetch(endpoint, options, true);
      }
    }

    if (!response.ok) {
      const errorMsg = data?.detail || data?.message || `HTTP ${response.status} Error`;
      throw new Error(errorMsg);
    }

    return data;
  } catch (err) {
    if (err.name === 'TypeError' && err.message.includes('Failed to fetch')) {
      const corsMessage = `🚨 CORS / Network Error: Request to ${url} failed. Check if FastAPI server is running at ${API_BASE_URL} and CORS headers are allowed.`;
      logApiConsole(corsMessage, 'cors');
      showGlobalAlert(corsMessage, 'danger');
    }
    throw err;
  }
}

// Automatic JWT Refresh Flow
async function autoRefreshToken() {
  if (state.isRefreshing || !state.refreshToken) return false;
  state.isRefreshing = true;

  try {
    const url = `${API_BASE_URL}/auth/refresh`;
    logApiRequest('POST', '/auth/refresh', JSON.stringify({ refresh_token: state.refreshToken }));
    
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: state.refreshToken }),
    });

    const data = await response.json();
    logApiResponse('POST', '/auth/refresh', response.status, data);

    if (response.ok && data.access_token) {
      setAuthSession(data.access_token, data.refresh_token || state.refreshToken);
      logApiConsole('✅ Automatic JWT refresh successful!', 'success');
      state.isRefreshing = false;
      return true;
    }
  } catch (e) {
    logApiConsole(`❌ Refresh token failed: ${e.message}`, 'error');
  }

  state.isRefreshing = false;
  clearAuthSession();
  showGlobalAlert('Session expired. Please login again.', 'danger');
  return false;
}

// Check Backend API Health
async function checkApiHealth() {
  try {
    const res = await fetch('http://10.170.204.130:8000');
    if (res.ok) {
      elements.apiStatusBadge.querySelector('.status-dot').className = 'status-dot green';
      elements.apiStatusText.textContent = 'API Connected (Online)';
    } else {
      throw new Error('API returned status ' + res.status);
    }
  } catch (e) {
    elements.apiStatusBadge.querySelector('.status-dot').className = 'status-dot red';
    elements.apiStatusText.textContent = 'API Offline / Unreachable';
  }
}

// --- Auth Session Management ---
function setAuthSession(accessToken, refreshToken, user = null) {
  state.accessToken = accessToken;
  state.refreshToken = refreshToken;
  if (user) state.currentUser = user;

  localStorage.setItem('webx_access_token', accessToken);
  localStorage.setItem('webx_refresh_token', refreshToken);

  updateHeaderUserStatus();
  updateTokenDisplay();
}

function clearAuthSession() {
  state.accessToken = null;
  state.refreshToken = null;
  state.currentUser = null;

  localStorage.removeItem('webx_access_token');
  localStorage.removeItem('webx_refresh_token');

  updateHeaderUserStatus();
  updateTokenDisplay();
}

function updateHeaderUserStatus() {
  if (state.currentUser) {
    elements.userProfileBadge.classList.remove('hidden');
    elements.headerUsername.textContent = `@${state.currentUser.username}`;
    elements.headerUserTag.textContent = state.currentUser.is_verified ? 'Verified ✓' : 'Unverified ⚠️';
    elements.headerUserTag.className = state.currentUser.is_verified ? 'user-tag text-emerald' : 'user-tag text-amber';
  } else {
    elements.userProfileBadge.classList.add('hidden');
  }
}

function updateTokenDisplay() {
  if (elements.tokenDisplayAccess) elements.tokenDisplayAccess.value = state.accessToken || 'No Active Access Token';
  if (elements.tokenDisplayRefresh) elements.tokenDisplayRefresh.value = state.refreshToken || 'No Active Refresh Token';
}

// --- Event Handlers & Features ---
function setupEventListeners() {
  // Navigation
  elements.headerLogoutBtn.addEventListener('click', handleLogout);
  elements.logoutBtn.addEventListener('click', handleLogout);
  elements.clearApiLogsBtn.addEventListener('click', () => { elements.apiLogConsole.innerHTML = ''; });
  
  // 1. Register Form
  elements.registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('regUsername').value.trim();
    const email = document.getElementById('regEmail').value.trim();
    const password = document.getElementById('regPassword').value.trim();

    try {
      showGlobalAlert('Sending registration request...', 'info');
      const user = await apiFetch('/auth/register', {
        method: 'POST',
        body: JSON.stringify({ username, email, password }),
      });

      showGlobalAlert(`Registration successful for @${user.username}! OTP sent to email.`, 'success');
      document.getElementById('otpEmail').value = email;
      switchTab('auth-tab');
    } catch (err) {
      showGlobalAlert(`Registration Failed: ${err.message}`, 'danger');
    }
  });

  // 2. Verify OTP Form
  elements.verifyOtpForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('otpEmail').value.trim();
    const otp = document.getElementById('otpCode').value.trim();

    try {
      showGlobalAlert('Verifying OTP...', 'info');
      const res = await apiFetch('/auth/verify-otp', {
        method: 'POST',
        body: JSON.stringify({ email, otp }),
      });

      showGlobalAlert(`✅ ${res.message}`, 'success');
    } catch (err) {
      showGlobalAlert(`OTP Verification Failed: ${err.message}`, 'danger');
    }
  });

  // 3. Resend OTP Button
  elements.resendOtpBtn.addEventListener('click', async () => {
    const email = document.getElementById('otpEmail').value.trim();
    if (!email) {
      showGlobalAlert('Please enter your email to resend OTP.', 'danger');
      return;
    }

    try {
      showGlobalAlert('Requesting new OTP...', 'info');
      const res = await apiFetch('/auth/resend-otp', {
        method: 'POST',
        body: JSON.stringify({ email }),
      });

      showGlobalAlert(`📩 ${res.message}`, 'success');
    } catch (err) {
      showGlobalAlert(`Resend OTP Failed: ${err.message}`, 'danger');
    }
  });

  // 4. Login Form
  elements.loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email_or_username = document.getElementById('loginIdentifier').value.trim();
    const password = document.getElementById('loginPassword').value.trim();

    try {
      showGlobalAlert('Authenticating credentials...', 'info');
      const tokens = await apiFetch('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email_or_username, password }),
      });

      setAuthSession(tokens.access_token, tokens.refresh_token);
      await fetchProfileData();
      showGlobalAlert('Login successful! Welcome to WebX Universe.', 'success');
      loadAllAuthenticatedData();
    } catch (err) {
      showGlobalAlert(`Login Failed: ${err.message}`, 'danger');
    }
  });

  // 5. Fetch Profile & Refresh Token Manual Buttons
  elements.fetchProfileBtn.addEventListener('click', fetchProfileData);
  elements.refreshTokenBtn.addEventListener('click', async () => {
    if (!state.refreshToken) {
      showGlobalAlert('No refresh token available.', 'danger');
      return;
    }
    const success = await autoRefreshToken();
    if (success) showGlobalAlert('Tokens refreshed manually!', 'success');
  });

  // 6. Streak Claim Button
  elements.claimStreakBtn.addEventListener('click', async () => {
    try {
      showGlobalAlert('Claiming daily streak...', 'info');
      const res = await apiFetch('/streaks/claim', { method: 'POST' });
      showGlobalAlert(`🔥 ${res.message}`, 'success');
      loadStreakData();
    } catch (err) {
      showGlobalAlert(`Streak Claim Failed: ${err.message}`, 'danger');
    }
  });

  // 7. Referral Claim Form
  elements.claimReferralForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const referral_code = document.getElementById('referralInputCode').value.trim();

    try {
      showGlobalAlert('Claiming referral reward...', 'info');
      const res = await apiFetch('/referrals/claim', {
        method: 'POST',
        body: JSON.stringify({ referral_code }),
      });

      showGlobalAlert('🎉 Referral claimed successfully!', 'success');
      loadReferralData();
    } catch (err) {
      showGlobalAlert(`Referral Claim Failed: ${err.message}`, 'danger');
    }
  });

  elements.copyReferralBtn.addEventListener('click', () => {
    const code = elements.myReferralCode.textContent;
    if (code && code !== '--------') {
      navigator.clipboard.writeText(code);
      showGlobalAlert(`Copied referral code: ${code}`, 'success');
    }
  });

  // 8. Create Game Form
  elements.createGameForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('gameTitleInput').value.trim();
    const url = document.getElementById('gameUrlInput').value.trim();

    try {
      showGlobalAlert('Publishing game metadata...', 'info');
      await apiFetch('/games', {
        method: 'POST',
        body: JSON.stringify({ title, url }),
      });

      showGlobalAlert(`Game "${title}" published successfully!`, 'success');
      document.getElementById('gameTitleInput').value = '';
      document.getElementById('gameUrlInput').value = '';
      loadGamesData();
    } catch (err) {
      showGlobalAlert(`Game Publish Failed: ${err.message}`, 'danger');
    }
  });

  elements.refreshGamesBtn.addEventListener('click', loadGamesData);

  // 9. Ad Impression Log Form
  elements.logAdForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const ad_type = document.getElementById('adTypeSelect').value;
    const count = parseInt(document.getElementById('adCountInput').value, 10);

    try {
      showGlobalAlert(`Logging ${count} ${ad_type} ad impression(s)...`, 'info');
      await apiFetch('/analytics/ads', {
        method: 'POST',
        body: JSON.stringify({ ad_type, count }),
      });

      showGlobalAlert('Ad impression recorded successfully!', 'success');
      loadAnalyticsData();
    } catch (err) {
      showGlobalAlert(`Ad Logging Failed: ${err.message}`, 'danger');
    }
  });

  // Modal Close
  elements.closeModalBtn.addEventListener('click', () => {
    elements.webviewModal.classList.add('hidden');
    elements.gameIframe.src = 'about:blank';
  });
}

// --- Data Fetchers ---
async function fetchProfileData() {
  try {
    const user = await apiFetch('/auth/me');
    state.currentUser = user;
    updateHeaderUserStatus();

    elements.profileDetails.innerHTML = `
      <div class="profile-card">
        <p><strong>User ID:</strong> <code>${user.id}</code></p>
        <p><strong>Username:</strong> @${user.username}</p>
        <p><strong>Email:</strong> ${user.email}</p>
        <p><strong>Account Verified:</strong> ${user.is_verified ? '✅ Yes' : '❌ No (Verification Pending)'}</p>
        <p><strong>Active Status:</strong> ${user.is_active ? '✅ Active' : '❌ Disabled'}</p>
        <p><strong>Member Since:</strong> ${new Date(user.created_at).toLocaleString()}</p>
      </div>
    `;

    loadAllAuthenticatedData();
  } catch (err) {
    elements.profileDetails.innerHTML = `<p class="text-muted">Error loading profile: ${err.message}</p>`;
  }
}

function loadAllAuthenticatedData() {
  loadStreakData();
  loadReferralData();
  loadGamesData();
  loadAnalyticsData();
}

async function loadStreakData() {
  try {
    const streak = await apiFetch('/streaks/me');
    elements.currentStreakNum.textContent = streak.current_streak;
    elements.highestStreakNum.textContent = streak.highest_streak;
    elements.lastClaimDate.textContent = streak.last_claim_date || 'Never';

    elements.kycBadge.textContent = streak.kyc_eligible ? 'Eligible ✓' : 'Ineligible';
    elements.kycBadge.className = streak.kyc_eligible ? 'badge badge-green' : 'badge badge-red';

    // Highlight Tier
    document.querySelectorAll('.tier-item').forEach(item => item.style.border = 'none');
    if (streak.star_coupon_tier) {
      const activeTier = document.getElementById(`tier${streak.star_coupon_tier}`);
      if (activeTier) activeTier.style.border = '1px solid var(--amber)';
    }
  } catch (e) {}
}

async function loadReferralData() {
  try {
    const data = await apiFetch('/referrals/me');
    elements.myReferralCode.textContent = data.referral_code || '--------';
    elements.totalReferralsCount.textContent = data.total_referrals || 0;

    if (data.referred_users && data.referred_users.length > 0) {
      elements.referredUsersList.innerHTML = data.referred_users.map(u => `
        <li class="user-item">
          <span><strong>@${u.username}</strong></span>
          <span class="text-sm text-muted">${new Date(u.created_at).toLocaleDateString()}</span>
        </li>
      `).join('');
    } else {
      elements.referredUsersList.innerHTML = '<li class="empty-list">No referred users yet. Share your code!</li>';
    }
  } catch (e) {}
}

async function loadGamesData() {
  try {
    const games = await apiFetch('/games');
    if (!games || games.length === 0) {
      elements.gamesGrid.innerHTML = '<p class="text-muted">No games published yet in directory.</p>';
      return;
    }

    elements.gamesGrid.innerHTML = games.map(g => `
      <div class="game-card">
        <div>
          <div class="game-title">${escapeHtml(g.title)}</div>
          <div class="game-url">🔗 ${escapeHtml(g.url)}</div>
        </div>
        <div class="stats-row">
          <span>❤️ ${g.likes_count}</span>
          <span>📌 ${g.pins_count}</span>
          <span>▶️ ${g.plays_count}</span>
        </div>
        <div class="game-actions">
          <button class="btn btn-sm ${g.is_liked ? 'btn-danger' : 'btn-outline'}" onclick="toggleGameAction('${g.id}', 'like')">
            ${g.is_liked ? 'Unlike' : 'Like'}
          </button>
          <button class="btn btn-sm ${g.is_pinned ? 'btn-warning' : 'btn-outline'}" onclick="toggleGameAction('${g.id}', 'pin')">
            ${g.is_pinned ? 'Unpin' : 'Pin'}
          </button>
          <button class="btn btn-sm btn-primary" onclick="launchGameWebView('${g.id}', '${escapeHtml(g.title)}', '${escapeHtml(g.url)}')">
            Play Game
          </button>
        </div>
      </div>
    `).join('');
  } catch (e) {
    elements.gamesGrid.innerHTML = `<p class="text-muted">Error loading games: ${e.message}</p>`;
  }
}

async function toggleGameAction(gameId, action) {
  try {
    await apiFetch(`/games/${gameId}/${action}`, { method: 'POST' });
    loadGamesData();
  } catch (err) {
    showGlobalAlert(`Action failed: ${err.message}`, 'danger');
  }
}

async function launchGameWebView(gameId, title, url) {
  try {
    // Record gameplay API call
    await apiFetch(`/games/${gameId}/play`, { method: 'POST' });
    loadGamesData();

    elements.modalGameTitle.textContent = title;
    elements.gameIframe.src = url;
    elements.webviewModal.classList.remove('hidden');
  } catch (err) {
    showGlobalAlert(`Failed to launch webview: ${err.message}`, 'danger');
  }
}

async function loadAnalyticsData() {
  try {
    const data = await apiFetch('/analytics/me');
    elements.adBannerCount.textContent = data.banner_ads || 0;
    elements.adInterstitialCount.textContent = data.interstitial_ads || 0;
    elements.adRewardedCount.textContent = data.rewarded_ads || 0;
    elements.adNativeCount.textContent = data.native_ads || 0;
  } catch (e) {}
}

async function handleLogout() {
  if (state.refreshToken) {
    try {
      await apiFetch('/auth/logout', {
        method: 'POST',
        body: JSON.stringify({ refresh_token: state.refreshToken }),
      });
    } catch (e) {}
  }
  clearAuthSession();
  showGlobalAlert('Logged out successfully.', 'info');
}

// --- Navigation Tabs ---
function setupTabNavigation() {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const tabId = btn.getAttribute('data-tab');
      switchTab(tabId);
    });
  });
}

function switchTab(tabId) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

  const activeBtn = document.querySelector(`.tab-btn[data-tab="${tabId}"]`);
  const activeContent = document.getElementById(tabId);

  if (activeBtn) activeBtn.classList.add('active');
  if (activeContent) activeContent.classList.add('active');
}

// --- Helpers & UI Feedback ---
function showGlobalAlert(message, type = 'info') {
  elements.globalAlert.className = `alert alert-${type}`;
  elements.globalAlert.innerHTML = message;
  elements.globalAlert.classList.remove('hidden');

  setTimeout(() => {
    elements.globalAlert.classList.add('hidden');
  }, 6000);
}

function logApiRequest(method, endpoint, body) {
  const time = new Date().toLocaleTimeString();
  const entry = document.createElement('div');
  entry.className = 'log-entry info';
  entry.innerHTML = `[${time}] 📤 <strong>${method}</strong> ${endpoint} ${body ? `| Body: ${body}` : ''}`;
  elements.apiLogConsole.prepend(entry);
}

function logApiResponse(method, endpoint, status, data) {
  const time = new Date().toLocaleTimeString();
  const entry = document.createElement('div');
  const isSuccess = status >= 200 && status < 300;
  entry.className = `log-entry ${isSuccess ? 'success' : 'error'}`;
  entry.innerHTML = `[${time}] 📥 <strong>${method}</strong> ${endpoint} -> Status <strong>${status}</strong> | Response: ${JSON.stringify(data)}`;
  elements.apiLogConsole.prepend(entry);
}

function logApiConsole(msg, type = 'info') {
  const time = new Date().toLocaleTimeString();
  const entry = document.createElement('div');
  entry.className = `log-entry ${type}`;
  entry.innerHTML = `[${time}] ${msg}`;
  elements.apiLogConsole.prepend(entry);
}

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
