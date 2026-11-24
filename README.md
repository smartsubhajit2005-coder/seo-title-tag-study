# SEO title tag study: 99 high-traffic homepages

What the server actually sends in the HTML of 99 high-traffic homepages — the title
tag, the meta description and a handful of structural tags — measured in a single
pass on 2026-11-21, with one HTTPS GET per homepage and no JavaScript executed.

Every figure below is computed from [data/title-tag-study.csv](data/title-tag-study.csv).
Nothing here is estimated, sampled or rounded up for effect.

## Findings

99 homepages were requested across six categories; 78 answered with HTML.

| Measure | Value |
|---|---|
| Homepages requested / reachable | 99 / 78 |
| Median title length | 41 characters |
| Mean title length | 39.6 characters |
| Titles under 30 characters | 30 of 78 (38%) |
| Titles over 60 characters | 14 of 78 (18%) |
| Median meta description length | 140.5 characters |
| Homepages with no meta description | 14 of 78 (18%) |
| Meta descriptions over 160 characters | 13 of 78 |
| Homepages with no `h1` | 23 of 78 (29%) |
| Homepages with more than one `h1` | 8 of 78 |
| `rel=canonical` present | 64 of 78 (82%) |
| `application/ld+json` present | 41 of 78 (53%) |
| `og:title` present | 61 of 78 (78%) |
| `viewport` meta present | 75 of 78 (96%) |

The short version: on the homepages of very large sites, the most common title is
shorter than the 50–60 character band that most SEO checkers tell you to aim for.
38% of them are under 30 characters, and a third of those are a bare brand name —
`Apple` (5), `Google` (6), `YouTube` (7), `Wikipedia` (9). The long-title problem
most audits warn about is real but rarer: 18% are over 60.

### Median title length by category

| Category | Homepages | Median title |
|---|---|---|
| Social and media | 13 | 22 |
| Education, government, non-profit | 12 | 24 |
| E-commerce | 7 | 34 |
| Travel, local and services | 6 | 51 |
| Software | 25 | 53 |
| News | 10 | 53.5 |

The split is the interesting part. Social and media and institutional homepages
optimise for a brand token; news and software homepages optimise for a query.

### The conservative version of the same numbers

Five reachable rows are bot-challenge or empty responses rather than real homepage
markup (listed under [Limitations](#limitations)). Excluding them leaves 73 rows:

| Measure | All reachable (78) | Excluding challenge rows (73) |
|---|---|---|
| Median title | 41 | 43 |
| Titles under 30 characters | 38% | 34% |
| Titles over 60 characters | 17.9% | 19.2% |
| Homepages with no meta description | 14 | 9 |
| `rel=canonical` present | 82% | 88% |
| `application/ld+json` present | 53% | 56% |
| `og:title` present | 78% | 84% |

The direction of every finding holds either way. Quote whichever set you prefer, but
say which one you are quoting — that is the whole point of publishing the rows.

## Files

| Path | What it is |
|---|---|
| `data/title-tag-study.csv` | The 78 reachable homepages, one row each, with the measured values |
| `scripts/collect.py` | The collector. Reproduces the dataset; standard library only |
| `CITATION.cff` | Citation metadata |

The raw capture — all 99 rows including the 21 hosts that refused the request, with
their status codes — is published with the write-up at
<https://tmlseo.freedev.app/research/title-tags/>.

## Method

- One `GET https://<host>/` per homepage, redirects followed (max 5), 20 s timeout.
- Desktop Chrome user agent, `Accept: text/html,application/xhtml+xml`, gzip.
- No cookies, no JavaScript, no rendering. This is what the server sends to a
  logged-out visitor with a browser user agent.
- Title and description are HTML-decoded, tag-stripped and whitespace-collapsed
  before their length is counted, so a length is the length a person would read.
- `h1` count is a count of `<h1` occurrences in the source, not in the rendered DOM.
- Categories are assigned by hand, one per homepage.
- 60 characters for a title and 160 for a description are conventional guidelines,
  not limits enforced by Google. They are used here because audits use them.

## Limitations

- **No JavaScript.** A homepage that builds its title client-side will appear to have
  no title here. This affects rendered apps more than marketing pages.
- **Bot walls.** 21 of 99 hosts refused the request: 403 from Cloudflare-style edges,
  401, 429, and 400. Those rows are in the raw capture, not in this CSV.
- **Five rows are not real measurements.** Three returned HTTP 202 with an empty
  body (`booking.com`, `imdb.com`, `espn.com`), `amazon.com` returned a one-character
  title and `khanacademy.org` returned a page titled `Client Challenge`. They are
  kept in the CSV because removing data quietly is worse than flagging it, and they
  are excluded from the conservative figures above.
- **One snapshot.** Homepages change; this is 2026-11-21, not a trend.
- **No ranking data.** Nothing here claims a title length causes a ranking outcome.
  It measures what large sites do, not what works.

## Reproduce it

```bash
python3 scripts/collect.py --limit 5            # try five hosts
python3 scripts/collect.py --out titles.csv     # all 99
```

Expect today's numbers to differ: these pages are live. The point of the script is
that you do not have to trust this repository's CSV.

## Licence and citation

Data (`data/*.csv`) is licensed CC BY 4.0. The script is MIT. Cite it as:

> TML SEO Tools (2026). *SEO title tag study: 99 high-traffic homepages.*
> https://github.com/smartsubhajit2005-coder/seo-title-tag-study

The write-up with the full raw capture: <https://tmlseo.freedev.app/research/title-tags/>

Maintained by [TML SEO Tools](https://tmlseo.freedev.app), a free collection of SEO
utilities that compute results from your data instead of scoring them.
