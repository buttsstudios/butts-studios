const firebaseConfig = {
  apiKey: "AIzaSyCF7CrquYmLxZ6nOushPFyVmC_zHCL_ZBY",
  authDomain: "butts-studios.firebaseapp.com",
  projectId: "butts-studios",
  storageBucket: "butts-studios.firebasestorage.app",
  messagingSenderId: "956486562117",
  appId: "1:956486562117:web:6026c09e69202d6f340e2c"
};

class GameFirebase {
  constructor() {
    this.db = null;
    this.initialized = false;
  }

  async init() {
    if (this.initialized) return;
    
    if (typeof window === 'undefined' || !window.firebase) {
      console.log('Firebase not loaded, skipping init');
      return;
    }
    
    try {
      const app = window.firebase.getApps().length === 0 
        ? window.firebase.initializeApp(firebaseConfig)
        : window.firebase.getApps()[0];
      this.db = window.firebase.firestore(app);
      this.initialized = true;
    } catch (e) {
      console.log('Firebase init failed:', e);
    }
  }

  async saveScore(game, playerName, score, gridSize = null) {
    await this.init();
    if (!this.db) return false;
    
    try {
      await this.db.collection(`${game}_scores`).add({
        playerName,
        score,
        gridSize,
        timestamp: new Date().toISOString()
      });
      return true;
    } catch (e) {
      console.error('Error saving score:', e);
      return false;
    }
  }

  async getLeaderboard(game, gridSize = null, limitCount = 10) {
    await this.init();
    if (!this.db) return [];
    
    try {
      let query = this.db.collection(`${game}_scores`)
        .orderBy('score', gridSize ? 'asc' : 'desc')
        .limit(limitCount);
      
      if (gridSize) {
        query = query.where('gridSize', '==', gridSize);
      }
      
      const snapshot = await query.get();
      return snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
    } catch (e) {
      console.error('Error getting leaderboard:', e);
      return [];
    }
  }

  async saveAnalytics(events) {
    await this.init();
    if (!this.db || !events.length) return;
    
    try {
      for (const event of events) {
        await this.db.collection('analytics').add(event);
      }
    } catch (e) {
      console.error('Error saving analytics:', e);
    }
  }
}

window.GameFirebase = GameFirebase;
