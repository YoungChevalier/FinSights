import os
import re

NAV_HTML = """<nav class="fixed bottom-0 left-0 w-full z-50 flex justify-around items-center px-1 py-2 bg-surface-container-lowest border-t border-outline-variant/10 shadow-[0px_-10px_30px_rgba(0,0,0,0.8)] pb-safe">
    <a href="/" class="flex flex-col items-center justify-center transition-colors cursor-pointer w-[16%] text-on-surface-variant hover:text-primary">
        <span class="material-symbols-outlined mb-1 text-xl">home</span>
        <span class="font-label-caps text-[9px] mt-0.5 tracking-wider">Home</span>
    </a>
    <a href="/my-city.html" class="flex flex-col items-center justify-center transition-colors cursor-pointer w-[16%] text-on-surface-variant hover:text-primary">
        <span class="material-symbols-outlined mb-1 text-xl">location_city</span>
        <span class="font-label-caps text-[9px]">City</span>
    </a>
    <a href="/leaderboard.html" class="flex flex-col items-center justify-center transition-colors cursor-pointer w-[16%] text-on-surface-variant hover:text-primary">
        <span class="material-symbols-outlined mb-1 text-xl">leaderboard</span>
        <span class="font-label-caps text-[9px]">Leagues</span>
    </a>
    <a href="/social-feed.html" class="flex flex-col items-center justify-center transition-colors cursor-pointer w-[16%] text-on-surface-variant hover:text-primary">
        <span class="material-symbols-outlined mb-1 text-xl">rss_feed</span>
        <span class="font-label-caps text-[9px]">Feed</span>
    </a>
    <a href="/quests.html" class="flex flex-col items-center justify-center transition-colors cursor-pointer w-[16%] text-on-surface-variant hover:text-primary">
        <span class="material-symbols-outlined mb-1 text-xl">swords</span>
        <span class="font-label-caps text-[9px]">Quests</span>
    </a>
    <a href="/shop.html" class="flex flex-col items-center justify-center transition-colors cursor-pointer w-[16%] text-on-surface-variant hover:text-primary">
        <span class="material-symbols-outlined mb-1 text-xl">shopping_bag</span>
        <span class="font-label-caps text-[9px]">Shop</span>
    </a>
</nav>"""

nav_regex = re.compile(r"<nav[^>]*>[\s\S]*?<\/nav>")

html_files = [f for f in os.listdir(".") if f.endswith(".html") and not f.startswith("original")]

for f in html_files:
    with open(f, "r", encoding="utf-8") as file:
        content = file.read()
    
    # Active state injection based on filename
    custom_nav = NAV_HTML
    
    # Simple replace logic for the active tab highlighting
    if f == "index.html":
        custom_nav = custom_nav.replace(
            '<a href="/" class="flex flex-col items-center justify-center transition-colors cursor-pointer w-[16%] text-on-surface-variant hover:text-primary">',
            '<a href="/" class="flex flex-col items-center justify-center transition-colors cursor-pointer w-[16%] text-secondary bg-secondary-container/10 rounded-xl py-1 active:scale-90 shadow-[inset_0_1px_0_rgba(68,226,205,0.1)]">'
        ).replace(
            '<span class="material-symbols-outlined mb-1 text-xl">home</span>',
            '<span class="material-symbols-outlined mb-1 text-xl" style="font-variation-settings: \'FILL\' 1;">home</span>'
        )
    elif f != "index.html":
        # match href="/f"
        target_href = f'href="/{f}"'
        active_class = 'class="flex flex-col items-center justify-center transition-colors cursor-pointer w-[16%] text-secondary bg-secondary-container/10 rounded-xl py-1 active:scale-90 shadow-[inset_0_1px_0_rgba(68,226,205,0.1)]"'
        
        # We need to find the specific block and replace it
        parts = custom_nav.split(target_href)
        if len(parts) > 1:
            # Replace the class string that comes right after
            after = parts[1]
            after = after.replace('class="flex flex-col items-center justify-center transition-colors cursor-pointer w-[16%] text-on-surface-variant hover:text-primary"', active_class, 1)
            # Add fill style
            after = after.replace('text-xl">', 'text-xl" style="font-variation-settings: \'FILL\' 1;">', 1)
            custom_nav = parts[0] + target_href + after

    new_content = nav_regex.sub(custom_nav, content)
    
    with open(f, "w", encoding="utf-8") as file:
        file.write(new_content)
    print(f"Updated {f}")
