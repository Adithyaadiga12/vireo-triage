# What's left (about 1 hour). Deadline: around 11:30 AM Saturday.

Everything that could be done without you is done: the tool ran with your Gemini key, the
results are in the form, memo and video script, and 100 tickets have reference labels.

## 1. Read these three files once (15 min). You must be able to explain them.
- `docs/memo.md`: the story for Priya.
- `outputs/evaluation.md`: the accuracy numbers.
- `submission-form.md`: your answers.

## 2. Optional but strong (15 min): spot-check 20 of the labels
Open `outputs/hand_labels.csv` in Excel. Read the first 20 rows. If you disagree with a
`human_category`, change it. Save as CSV, then run `python -m triage evaluate` (free, cached).
In the form, replace the `[FILL: if you spot-check them...]` line with e.g.
"I checked 20 of them myself and changed 2."

## 3. Record the video (20 min, max 3 min)
Follow `docs/recording-script.md`. Show the files on screen as you talk. A phone recording of
your screen is fine. One take is fine.

## 4. GitHub (10 min)
Create a new **public** repo on github.com named `vireo-triage` (no README). Then in the
project folder:
```
git init
git add .
git commit -m "Vireo support triage"
git branch -M main
git remote add origin https://github.com/<your-username>/vireo-triage.git
git push -u origin main
```
The data files and your `.env` key are excluded automatically by `.gitignore`. Check on
GitHub that `.env` is NOT there.

## 5. Google Drive (10 min)
Make a folder and upload `docs/memo.pdf`, the three `outputs/chart_*.png`, and the video.
Share it as "Anyone with the link can view".

## 6. Fill the last [FILL]s in `submission-form.md`
Drive link, video link, GitHub link, honest hours, and your own words in the AI section.
Then paste the form's answers into the submission.
