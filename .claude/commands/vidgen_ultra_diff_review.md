# ultra DF review

> Execute each task in the order given to conduct a pharaoh code review

## Task one: create diff.txt

Create a New file called diff.md.
At the top of the file, add the following markdown:

```md
# Code Review'
- Review the diff, report on issues, bugs, and improvements
- And with a concise markdown table of any issues, found their solutions and a risk assessment for each issue if applicable
- Use emojis to convey the severity of each issue

## Diff

```

## Task two: git diff and append

Then run git diff and append, the output to the file.

## Task three: vidgen multi-LLM tool call

Then use the file as the input to the just-prompt to call

prompts_from_file_to_file(
    from_file = diff.md,
    models = "openai:o3-mini, anthropic:claude-3-7-sonnet-20250219:4k, gemini:gemini-2.0-flash-thinking-exp"
    output_dir = ultra_diff_review/
)

## Task four: Read the output files and synthesize

Then read the Output files and **think hard** to synthesize the results into a new single file called `ultra_diff_review/fusion_ultra_diff_review.md` following the original instructions plus any additional instructions or callouts you think are needed to create the best possible review.

## Task five: Present the results

Then let me know which issue you think are worth resolving and will proceed from there.
want to come in and say, let me know what you think Creative