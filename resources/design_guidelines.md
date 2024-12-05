# Design Guidelines
This document collects general guidelines regarding the (visual, partly functional) design of the GerPS Tool.
Feel free to suggest changes.
### Sources
- public domain "icons" https://undraw.co/search
- bootstrap examples https://getbootstrap.com/docs/5.3/examples/
- public domain icons https://github.com/apancik/public-domain-icons
- color selection: https://colorbrewer2.org/#type=sequential&scheme=BuGn&n=3
- color contrast checker https://webaim.org/resources/contrastchecker/

### Basic Guidelines
This overlaps with the "8 golden rules"

0. **Keep it as simple as possible**
1. Design should look good / work for different screen sizes (mobile not necessary)
2. Use as little additional libraries / dependencies as possible
3. Center elements horizontally and vertically (most of the time)
5. Do not use too bright colors that distract the user / grab all attention
7. Max 3 different fonts
8. Max 4 colors (primary, secondary, and shades of these, shades of white / grey)
9. Contrast between "neighboring" elements (+ text) should be sufficient if required -> https://webaim.org/resources/contrastchecker/
10. Provide useful tooltips when hovering over buttons
13. Display load-indicator for interactions with delay > 1 second
15. Reduce visual clutter (non-useful elements)
16. Give structure to the page (e.g. borders around groups of elements that belong together)
17. *If in doubt: quickly send a screenshot to one of your coworkers and ask for their opinion :)*

### Navigation:
- Standardization of workflows
- Clear description of the target for embedded links
- Clear and descriptive headings

### Target user
- Beginners → intensive help dialogues
- occasional users → consistent processes

### 8 Golden Rules of Design
[Source: Shneiderman](https://www.interaction-design.org/literature/article/shneiderman-s-eight-golden-rules-will-help-you-design-better-interfaces)

1. **consistency** wherever possible (paddings, processes, colors, layout, fonts, menus, etc.) 
2. usability as universal as possible 
	- (beginners to experts, age groups, disabilities, technical preferences)
3. informative feedback for every user action
4. design of dialogs that lead a group of actions to completion
5. **prevention of errors**
6. easy undoing of actions / going back
7. support a sense of control over every aspect of the user interface
8. reduce the memory load 
	- (Rule of thumb: 7±2 chunks of information can be held in working memory simultaneously)

### Practical Guidelines
- use Bootstrap and bootstrap examples
- create CSS classes for everything, no inline styling 
- reuse classes across different pages (but style in parent)
- use multiple classes that you can combine as desired, instead of many single-use classes
- do not use JS animations, prefer CSS animations (uses SVG)
- disable buttons when not usable
- add validation, where possible (for inputs)
- use svg as source format whereever possible (icons, animations, etc)


### Colormaps, Font-Family, Font-Size, etc
- Roboto Font
- Accent Color: #9999ff

