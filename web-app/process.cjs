const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const urls = {
    'index.html': 'https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sX2FhYWUxOWM2MmRjNzRmODY5MjM1ZmJkZjEyNmI4OGUzEgsSBxC_qa6t7BkYAZIBJAoKcHJvamVjdF9pZBIWQhQxNDAyODUzMzU3ODIyMDI4MTU2NQ&filename=&opi=89354086',
    'my-city.html': 'https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sX2E5NDE0ZjU1NDZjNTQxMDE5YmEyM2EyZWVkOTM5NDQyEgsSBxC_qa6t7BkYAZIBJAoKcHJvamVjdF9pZBIWQhQxNDAyODUzMzU3ODIyMDI4MTU2NQ&filename=&opi=89354086',
    'leaderboard.html': 'https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sXzFlNjNiZDc0ZTZjMDQwOWViMTA1MWJkOGY5OTJjYjIzEgsSBxC_qa6t7BkYAZIBJAoKcHJvamVjdF9pZBIWQhQxNDAyODUzMzU3ODIyMDI4MTU2NQ&filename=&opi=89354086',
    'social-feed.html': 'https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sX2M2NDBkMDUxNDNjZDQxMjc5ZGI1MGIxYzFmYTQ2NDA5EgsSBxC_qa6t7BkYAZIBJAoKcHJvamVjdF9pZBIWQhQxNDAyODUzMzU3ODIyMDI4MTU2NQ&filename=&opi=89354086'
};

for (const [filename, url] of Object.entries(urls)) {
    // Download
    execSync(`curl -s "${url}" -o "${filename}"`);

    let content = fs.readFileSync(filename, 'utf8');

    // Remove Tailwind CDN script
    content = content.replace(/<script src="https:\/\/cdn\.tailwindcss\.com\?plugins=forms,container-queries"><\/script>/g, '');
    
    // Remove tailwind config block completely
    content = content.replace(/<script id="tailwind-config">[\s\S]*?<\/script>/g, '');
    
    // We KEEP the <style> blocks. But we need to insert the main.js
    if (!content.includes('<script type="module" src="/src/main.js"></script>')) {
        content = content.replace('</head>', '  <script type="module" src="/src/main.js"></script>\n</head>');
    }

    // Now let's just write the bottom nav bar manually to be fully functional, replacing the existing one.
    // We can replace the entire <nav> block with a working one.
    const navRegex = /<nav[^>]*>[\s\S]*?<\/nav>/;
    
    const workingNav = `
<nav class="fixed bottom-0 left-0 w-full z-50 flex justify-around items-center px-4 py-3 bg-surface-container-lowest border-t border-outline-variant/10 shadow-[0px_-10px_30px_rgba(0,0,0,0.8)] pb-safe">
<a href="/" class="flex flex-col items-center justify-center transition-colors cursor-pointer w-16 ${filename === 'index.html' ? 'text-secondary bg-secondary-container/10 rounded-xl px-4 py-1.5 active:scale-90 shadow-[inset_0_1px_0_rgba(68,226,205,0.1)]' : 'text-on-surface-variant hover:text-primary'}">
<span class="material-symbols-outlined mb-1" ${filename === 'index.html' ? 'style="font-variation-settings: \'FILL\' 1;"' : ''}>home</span>
<span class="font-label-caps text-[10px] ${filename === 'index.html' ? 'mt-0.5 tracking-wider' : ''}">Home</span>
</a>
<a href="/my-city.html" class="flex flex-col items-center justify-center transition-colors cursor-pointer w-16 ${filename === 'my-city.html' ? 'text-secondary bg-secondary-container/10 rounded-xl px-4 py-1.5 active:scale-90 shadow-[inset_0_1px_0_rgba(68,226,205,0.1)]' : 'text-on-surface-variant hover:text-primary'}">
<span class="material-symbols-outlined mb-1" ${filename === 'my-city.html' ? 'style="font-variation-settings: \'FILL\' 1;"' : ''}>location_city</span>
<span class="font-label-caps text-[10px] ${filename === 'my-city.html' ? 'mt-0.5 tracking-wider' : ''}">City</span>
</a>
<a href="/leaderboard.html" class="flex flex-col items-center justify-center transition-colors cursor-pointer w-16 ${filename === 'leaderboard.html' ? 'text-secondary bg-secondary-container/10 rounded-xl px-4 py-1.5 active:scale-90 shadow-[inset_0_1px_0_rgba(68,226,205,0.1)]' : 'text-on-surface-variant hover:text-primary'}">
<span class="material-symbols-outlined mb-1" ${filename === 'leaderboard.html' ? 'style="font-variation-settings: \'FILL\' 1;"' : ''}>leaderboard</span>
<span class="font-label-caps text-[10px] ${filename === 'leaderboard.html' ? 'mt-0.5 tracking-wider' : ''}">Leagues</span>
</a>
<a href="/social-feed.html" class="flex flex-col items-center justify-center transition-colors cursor-pointer w-16 ${filename === 'social-feed.html' ? 'text-secondary bg-secondary-container/10 rounded-xl px-4 py-1.5 active:scale-90 shadow-[inset_0_1px_0_rgba(68,226,205,0.1)]' : 'text-on-surface-variant hover:text-primary'}">
<span class="material-symbols-outlined mb-1" ${filename === 'social-feed.html' ? 'style="font-variation-settings: \'FILL\' 1;"' : ''}>rss_feed</span>
<span class="font-label-caps text-[10px] ${filename === 'social-feed.html' ? 'mt-0.5 tracking-wider' : ''}">Feed</span>
</a>
</nav>
`;
    content = content.replace(navRegex, workingNav);

    fs.writeFileSync(filename, content, 'utf8');
    console.log(`Processed ${filename}`);
}
