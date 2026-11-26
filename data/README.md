# About these files

`title-tag-study.csv` is the dataset behind
<https://tmlseo.freedev.app/research/title-tags/>: 78 homepages that answered with
HTML on 2026-11-21, one row each.

## The length columns match the text

`title_len` and `description_len` are the character counts measured from the live
page, and the stored text preserves the characters that were counted. That includes
two zero-width non-joiner characters in the Slack row's meta description, which the
page uses for line breaking and which are invisible in an editor. Calling `len()` on
any row's text reproduces the number in its length column.

## Five rows are not real measurements

`amazon.com` (one-character title), `khanacademy.org` (a page titled `Client
Challenge`) and `booking.com`, `imdb.com`, `espn.com` (HTTP 202, empty body) were
served bot challenges rather than their homepage markup. They are kept so the row
count matches the capture; exclude them for 73 clean rows. The README's conservative
table does exactly that.
