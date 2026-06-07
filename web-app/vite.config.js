import { defineConfig } from 'vite';
import { resolve } from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        leaderboard: resolve(__dirname, 'leaderboard.html'),
        myCity: resolve(__dirname, 'my-city.html'),
        quests: resolve(__dirname, 'quests.html'),
        shop: resolve(__dirname, 'shop.html'),
        socialFeed: resolve(__dirname, 'social-feed.html'),
      },
    },
  },
});
