# GitHub adapter

## Upload evidence

- `gh pr create`, `gh pr edit`, `gh pr comment`, `gh issue create`, `gh issue edit` and
  `gh issue comment` take `--attach ./file` (gh 2.99+, push access to the repo). Repeat the flag
  for each file, up to 50. Give an image alt text after `#`: `--attach './before.png#Login error'`.
- Reference the file in the body as `![alt](./before.png)`. gh uploads it and rewrites the path
  to a `user-attachments` URL. An attached file that the body does not reference goes at the end.
  Paths in a `--body-file` are relative to that file's folder, then to the working directory.
- Types: png, jpg, gif, webp, svg, mp4, mov, webm. Limits: image 10 MB, video 10 MB (Free) or
  100 MB (paid plans). For a paid repo, pass the limit to `scripts/check-video.sh <file> 100`.
- If one upload fails, gh still creates or updates the PR or issue with the others and exits
  non-zero. Check the exit code and the rendered body, then attach the missing file with
  `gh pr edit --attach`.
- For other file types, or a repo you cannot push to, `gh image` (drogers0/gh-image) can upload,
  but it may read the browser's session cookie. Ask CJ before you use it.
