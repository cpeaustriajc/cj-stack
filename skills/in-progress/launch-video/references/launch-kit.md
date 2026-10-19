# Launch kit: images, post templates, and publishing

## Images

Build covers and thumbnails from the video's own components (the same card, mark and type), in one HTML
page with a variant per size, and render them with `scripts/shoot_images.cjs`. Sizes that cover the
main platforms:

| Variant | Size | Use |
|---|---|---|
| YouTube thumbnail | 1280×720 | YouTube |
| Link preview | 1200×630 | X, LinkedIn, Facebook, the site's `og:image` |
| Square post | 1080×1080 | Instagram, Facebook, LinkedIn image posts |
| Vertical cover | 1080×1920 | Reels, TikTok, Shorts cover frame; keep the key text inside the middle 1080×1080 so the profile grid crop still reads |
| End card | 1920×1080 | YouTube end screen, website hero |

Look at every image at its real size before publishing; a card that fits at one scale runs off another.
Write one alt text that works for all of them.

## Post templates

One section per platform, each with a main version and a short one, written as the brand. Cover:

- **TikTok / Reels / Shorts:** cover text, caption, a short variant, pinned comment, a few hashtags.
- **YouTube:** title, a description with chapter timestamps taken from the film's frame times, which
  image is the thumbnail and which is the end screen.
- **X:** main post, short post, and a reply to the post carrying the second message.
- **Threads, Instagram/Facebook feed, LinkedIn:** a caption each, the register rising from casual to
  measured; a carousel option from the images.
- **Forums such as Reddit:** usually no trailer. Most finance and product communities punish promotion;
  give guidance on how to take part there instead.

End the page with the copy rules, each linked to the decision it comes from, so whoever writes the
next post checks against them. Derive the rules from the project (SKILL.md, "The rules come from the
project first"); do not carry rules from one project to another.

## Publishing

Put the kit where the person asked: a wiki, a drive, the repo. For a GitHub wiki, clone
`<repo>.wiki.git`, add the videos under `media/` and images under `images/`, write one page, link it
from the home page's index, commit and push. In a **private** repo, `raw.githubusercontent.com` links
404 even for the owner: link files with relative paths (`media/launch/x.mp4`), as the wiki's own
images do. Verify the push landed with `git status -sb` after a fetch, since an anonymous `curl` cannot
see a private wiki.
