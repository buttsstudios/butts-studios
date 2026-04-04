const STORAGE_KEYS = {
  PLAYER_NAME: 'buttsstudios_player',
  IS_PREMIUM: 'buttsstudios_premium',
  DAILY_TRIES_PUZZLE: 'buttsstudios_puzzle_tries',
  DAILY_TRIES_CARDS: 'buttsstudios_cards_tries',
  LAST_PLAYED_DATE: 'buttsstudios_last_played',
  ANALYTICS_QUEUE: 'buttsstudios_analytics_queue',
};

const FREE_DAILY_TRIES = 5;
const MAX_UNDO_HISTORY = 10;

function getTodayDate() {
  return new Date().toISOString().split('T')[0];
}

export function login(playerName) {
  if (typeof window === 'undefined') return;
  localStorage.setItem(STORAGE_KEYS.PLAYER_NAME, playerName);
}

export function getPlayerName() {
  if (typeof window === 'undefined') return '';
  return localStorage.getItem(STORAGE_KEYS.PLAYER_NAME) || '';
}

export function isPremium() {
  if (typeof window === 'undefined') return false;
  return localStorage.getItem(STORAGE_KEYS.IS_PREMIUM) === 'true';
}

export function setPremium(value) {
  if (typeof window === 'undefined') return;
  localStorage.setItem(STORAGE_KEYS.IS_PREMIUM, String(value));
}

export function getDailyTries(game) {
  if (typeof window === 'undefined') return FREE_DAILY_TRIES;
  
  const key = game === 'puzzle' ? STORAGE_KEYS.DAILY_TRIES_PUZZLE : STORAGE_KEYS.DAILY_TRIES_CARDS;
  const lastPlayedDate = localStorage.getItem(STORAGE_KEYS.LAST_PLAYED_DATE);
  const today = getTodayDate();
  
  if (lastPlayedDate !== today) {
    localStorage.setItem(key, String(FREE_DAILY_TRIES));
    localStorage.setItem(STORAGE_KEYS.LAST_PLAYED_DATE, today);
    return FREE_DAILY_TRIES;
  }
  
  return parseInt(localStorage.getItem(key) || String(FREE_DAILY_TRIES), 10);
}

export function decrementTries(game) {
  if (typeof window === 'undefined') return 0;
  
  const key = game === 'puzzle' ? STORAGE_KEYS.DAILY_TRIES_PUZZLE : STORAGE_KEYS.DAILY_TRIES_CARDS;
  const currentTries = getDailyTries(game);
  const newTries = Math.max(0, currentTries - 1);
  localStorage.setItem(key, String(newTries));
  localStorage.setItem(STORAGE_KEYS.LAST_PLAYED_DATE, getTodayDate());
  
  return newTries;
}

export function canPlay(game) {
  return getDailyTries(game) > 0;
}

export function isLoggedIn() {
  return !!getPlayerName();
}

export function logout() {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(STORAGE_KEYS.PLAYER_NAME);
}

export function canUndo() {
  if (typeof window === 'undefined') return false;
  const history = JSON.parse(localStorage.getItem('buttsstudios_move_history') || '[]');
  return history.length > 0;
}

export function pushMove(move) {
  if (typeof window === 'undefined') return;
  const history = JSON.parse(localStorage.getItem('buttsstudios_move_history') || '[]');
  history.push(move);
  if (history.length > MAX_UNDO_HISTORY) {
    history.shift();
  }
  localStorage.setItem('buttsstudios_move_history', JSON.stringify(history));
}

export function popMove() {
  if (typeof window === 'undefined') return null;
  const history = JSON.parse(localStorage.getItem('buttsstudios_move_history') || '[]');
  const move = history.pop();
  localStorage.setItem('buttsstudios_move_history', JSON.stringify(history));
  return move;
}

export function clearMoveHistory() {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('buttsstudios_move_history');
}

export function queueAnalytics(event, data = {}) {
  if (typeof window === 'undefined') return;
  const queue = JSON.parse(localStorage.getItem(STORAGE_KEYS.ANALYTICS_QUEUE) || '[]');
  queue.push({
    event,
    data,
    timestamp: new Date().toISOString(),
  });
  localStorage.setItem(STORAGE_KEYS.ANALYTICS_QUEUE, JSON.stringify(queue));
}

export function getAnalyticsQueue() {
  if (typeof window === 'undefined') return [];
  return JSON.parse(localStorage.getItem(STORAGE_KEYS.ANALYTICS_QUEUE) || '[]');
}

export function clearAnalyticsQueue() {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(STORAGE_KEYS.ANALYTICS_QUEUE);
}

export default {
  login,
  getPlayerName,
  isPremium,
  setPremium,
  getDailyTries,
  decrementTries,
  canPlay,
  isLoggedIn,
  logout,
  canUndo,
  pushMove,
  popMove,
  clearMoveHistory,
  queueAnalytics,
  getAnalyticsQueue,
  clearAnalyticsQueue,
};
