---
name: demo-page
description: Explains a system, a flow, a piece of work or a comparison as a short, visual, colour-pop one-page artifact to present in a 5-minute demo. One thesis, a few sections, each shown as well as told, and only claims backed by what was read. Use when the user runs /demo-page, or asks to explain, walk through or demo something visually, or for a page to present.
argument-hint: "<topic> [for <audience>] [<minutes> min]"
---

# demo-page

Make one page someone can scroll through while they talk for about five minutes. It should be short, precise, visual and good-looking: a colour-pop design, where saturated colour always means something. Arguments: $ARGUMENTS. With no topic, use the work in this conversation.

## 1. Gather

- Ground every claim. Read what the topic stands on: this conversation, the files, the commits, the docs it names. Write down each number with where it came from. A claim you can't back up stays off the page.
- Decide the audience, a team at a demo unless the arguments say otherwise. Write for them, not for whoever built the thing. If the audience or the question is unclear, ask once, in one message.
- Find the one question the page answers, such as "What happens between pressing Save and the row landing in the database?" Everything on the page serves it.
- For code, learn the real mechanism: read it, or use the explorer and explainer agents where the repository has them. Take order, timing and what runs in parallel from a real run or from the code, never from memory.
- Find why it's built this way. Review feedback, incidents and rejected options often explain the design better than the code does. Read the review threads and fix notes, and show each as the problem and the fix. Credit "review", never a person by name.
- Check every reference: a ticket or PR number is looked up in its tracker before it goes on the page.

## 2. Shape it for the time

- **One thesis.** It's the page's opening line: what this is and why it matters, in one or two sentences.
- **Five to seven sections, one idea each.** Go to nine only when the audience needs the depth, such as a design shaped by a security review. A fitting order: how it works, the key idea, what changed, what was left out and why, where it stands, how to try it. Drop any section the topic doesn't need.
- **Give it substance, not just headlines.** Each section opens with two or three sentences of context. Each visual carries the detail that explains it: what each step produces, who is involved, the rules that always hold, the numbers that make a comparison concrete. A section that only names things is too thin.
- **Explain a mechanism before naming it.** Say who acts, what the default would be and what was chosen instead, then give it its name. "A scoped deploy policy" means nothing until the reader knows a deploy runs as a role that would otherwise be an admin.
- **Explain every limit and trade-off in full.** Say when it applies and when it doesn't, how often to expect it, and the steps that keep it from hurting, in the right order. A one-line "the trade-off is X" raises the question it should answer.
- **No bare counts.** "Uploads 9 files" needs what each one is and why it's there, or leave the number out.
- **Say where it lives.** For a system built in code, say where each part is written, and which parts a library generates rather than the team. A file path goes after the plain description.
- **Show each section, don't only tell it.** Pick the visual that fits from the template:
  - a flow of numbered steps for a process;
  - two cards side by side for a contrast;
  - a ladder for a scale;
  - tiles with icon badges for what changed, and dashed "not now" tiles for what was left out;
  - big coloured figures for numbers, each with its source in its label;
  - a strip of small numbers for a comparison, and bars for one measured change;
  - fact cards for the detail under a visual;
  - a matrix for who can do what, with rows for before and now when a change closed a gap.

  Say plainly what a number doesn't show.
- **A diagram only when it's needed:** when the idea is a mechanism that boxes and cards can't show. Most pages need none.
- **Each tile holds a name and its substance.** When something changed, show it as before and now. No more than eight tiles in a group.
- **When people will use the thing, end with "commands to know"**, one row per command.
- **End on what's next,** in one line.

## 3. Write it plainly

- Name things the way the audience knows them, not the way the code does. IDs, file paths and branch names go last, or not at all.
- Use short sentences in the active voice. No em dashes, no lists of three, no filler.
- Count everything again before publishing. Every count and label must match the source.

## 4. Build

1. Make the `Artifact` tool's `quickstart` call with `intent: "other"`. A plain page is right here.
2. Copy [template.html](template.html) to the scratchpad and fill it in. Keep its layout and components. Set the `<title>` to the thing's own name, not a description of it.
3. Give each colour class (blue, coral, mint, violet, sun) one meaning for the whole page, and name it once, in a legend or the copy. Keep both themes, and keep every colour a token. Text on a filled colour must stay readable: the template gives sun dark ink and makes `code` inside the dark step cards inherit their colour, so keep those rules when adding components.
4. Nothing scrolls sideways, and nothing is drawn small. Build flows and comparisons from the template's boxes, which wrap on narrow screens. If a real diagram is needed:
   - put it in a `figure-svg` block, which scales to the page width;
   - make it inline SVG, coloured only through CSS classes, so it reads in light and dark;
   - every box is a real thing (a service, a file, a person, a queue), and every arrow a real call or handoff;
   - anything you couldn't confirm is drawn with the `unconfirmed` class, which dashes it, and said to be unconfirmed;
   - every box labelled;
   - arrows with the arrowhead marker;
   - a legend under it;
   - `role="img"` and an `aria-label` that says what the diagram shows.

   Keep it to about a dozen shapes.
5. Publish with a one-word `icon` and a one-sentence `description`.

## 5. Hand over

Reply with:
- a first line naming the audience, e.g. "Written for: the team, at a 5-minute demo";
- the link;
- one line per section, saying what it covers;
- that the page is private until they share it from its Share menu.
