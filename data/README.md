# About these files

`title-tag-study.csv` is the dataset behind
<https://tmlseo.freedev.app/research/title-tags/>: 78 homepages that answered with
HTML on 2026-11-21, one row each.

## One known inconsistency, stated plainly

The Slack row's meta description contains two zero-width non-joiner characters that
the page uses for line breaking. They are invisible and do not survive copy and paste,
so the text stored here does not contain them — but `description_len` keeps the
capture's **173**, which counted them, because that column mirrors the site's
published CSV. Calling `len()` on the stored text gives **171**.

No other cell differs from the site's capture, and neither figure changes any headline
number: both round to the same median.

## Five rows are not real measurements

`amazon.com` (one-character title), `khanacademy.org` (a page titled `Client
Challenge`) and `booking.com`, `imdb.com`, `espn.com` (HTTP 202, empty body) were
served bot challenges rather than their homepage markup. They are kept so the row
count matches the capture; exclude them for 73 clean rows. The README's conservative
table does exactly that.
