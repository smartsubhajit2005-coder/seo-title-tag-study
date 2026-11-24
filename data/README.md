# About these files

`title-tag-study.csv` is the dataset behind
<https://tmlseo.freedev.app/research/title-tags/>: 78 homepages that answered with
HTML on 2026-11-21, one row each.

## One deliberate difference from the site's capture

The Slack row's meta description contains two zero-width non-joiner characters that
the page uses for line breaking. They are invisible, they do not survive copy and
paste, and counting them makes the length column impossible to reproduce by hand.
They are stripped here, and `description_len` for `slack.com` is **171**, the length
of the text as stored in this file. The site's own capture counts them and prints
**173**. No other cell differs. Both figures round to the same median, so no headline
number moves.

If you regenerate the data with `scripts/collect.py`, your Slack row will contain the
zero-width characters (the script preserves the source text) and will report 173.
That is expected, not a bug.

## Five rows are not real measurements

`amazon.com` (one-character title), `khanacademy.org` (a page titled `Client
Challenge`) and `booking.com`, `imdb.com`, `espn.com` (HTTP 202, empty body) were
served bot challenges rather than their homepage markup. They are kept so the row
count matches the capture; exclude them for 73 clean rows. The README's conservative
table does exactly that.
