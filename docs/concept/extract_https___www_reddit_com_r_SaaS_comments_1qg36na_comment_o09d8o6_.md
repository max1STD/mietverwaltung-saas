Skip to main content Open menu Open navigation [](https://www.reddit.com/) Go to Reddit Home
r/SaaS
Expand user menu Open settings menu
[Go to SaaS](https://www.reddit.com/r/SaaS/) [r/SaaS](https://www.reddit.com/r/SaaS/) • 9mo ago
[u/blaze6414](https://www.reddit.com/user/blaze6414/)
How to design a non-generic saas ui (without vibe-coded slop)

# most saas products look the same. not because people want them to, but because the tools quietly push everyone toward the same outcomes.
same fonts. same spacing. same cards. same buttons. same “clean” layouts that feel obviously auto-generated.
this is a simple, practical guide for designing a saas ui that feels intentional and human instead of templated and forgettable.

# why most vibe coded ui feels bad
most modern ui fails for a few predictable reasons:
- everyone defaults to inter font
- spacing is too perfect and symmetrical
- components feel flat and disposable
- buttons, inputs, and cards look copied
- layouts optimize for “safe saas” instead of identity
start with constraints (this matters more than creativity)
before you design anything, lock these rules:

# fonts (avoid inter)
pick **one** font for body text and **one** for headlines. do not mix more.
good options that still feel modern but human:
* dm sans
* manrope
* space grotesk
* plus jakarta sans
* satoshi
* general sans

...

# define the product in one sentence
before opening google stitch, write this:
if you can’t write this clearly, the ui will feel confused no matter how good it looks.

# find visual references
use dribbble or similar sites, but be intentional.
search things like:
* editorial saas
* minimal dashboard
* luxury web app
* dark saas ui
save 3-5 screens MAX
good signs:
* strong hierarchy
* confident empty space
* great branding

...

# list every screen before designing
don’t design randomly. define the scope.
at minimum:

...

this prevents half-designed products.

# open with google stitch
prompt it it:
* what the product does
* who it’s for (your ICP)
* what to avoid (inter font, icons)
* what kind of feeling you want
* typography
* all of the screens
upload 3-5 inspiration dribbble designs
avoid prompts that say “modern, clean, saas” without context. that’s how you get generic results.
run it once. evaluate. don’t spam regenerate.
once you get your output, export the code and put it on your IDE of choice

# choosing components
using 21st dev, find components that match your brand profile
instead:
* pick one button style for primary actions
* one surface style for cards and panels
* one input style
* one navigation pattern

...

# quality check
ui fails if:
* it could be swapped with another saas and no one would notice
* looks like every other vibe coded slop website
* everything has identical spacing
it works if:
* a defined visual philosophy
* premium looking branding
* unique differentiation
[](https://preview.redd.it/how-to-design-a-non-generic-saas-ui-without-vibe-coded-slop-v0-6np1c2b6i2eg1.png?width=1077&format=png&auto=webp&s=55c15a75af118552a1d723abdcdbbb1f6595811b)