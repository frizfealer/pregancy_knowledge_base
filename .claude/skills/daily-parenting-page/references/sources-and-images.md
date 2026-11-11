# Sources and images

## Source tiers

**Tier 1, required for any medical or safety claim**
CDC (cdc.gov), NIH and its institutes (medlineplus.gov, nichd.nih.gov, niddk.nih.gov,
ods.od.nih.gov), womenshealth.gov, FDA, WHO, AAP (healthychildren.org, aap.org), NHS (nhs.uk),
peer-reviewed papers on PubMed/PMC.

ACOG (acog.org) is authoritative but blocks automated fetching. Don't try to get around
that. Use a tier-1 page that states the same guidance, or link ACOG as further reading
without citing it for a claim you couldn't read.

**Tier 2, fine for practical and non-medical claims**
March of Dimes, Mayo Clinic, Cleveland Clinic, Johns Hopkins Medicine, Zero to Three,
Consumer Reports, Wirecutter (product testing), healthcare.gov and insurers (coverage),
New York State and NYC government sites (childcare licensing, paid family leave, worker
rules), manufacturers' own pages (product specs only, never their health claims).

**Not sources**: forums, content farms, AI-written sites, affiliate listicles, news
articles about a study (find the study or the agency page instead).

## Rules

- Search first, then fetch. In an unattended run, the fetch tool only lets through URLs
  that appeared in a search result or in the task prompt; any other URL waits for an
  approval nobody answers and stays blocked for the rest of the run. So run WebSearch
  for each source, then fetch the URL exactly as the result shows it (same trailing
  slash, same `www.`). Never type a URL from memory or adjust one, and never retry a URL
  that was blocked. If a site's page doesn't show up in search, use another tier-1 page
  that does.
- Fetch and read every page you cite. Don't cite from memory or from a search snippet.
- Record title, publisher and the page's own reviewed or updated date in the sources list.
- When sources disagree, say so on the page with both citations.
- Prefer the most recently reviewed tier-1 page; note when the best source is old.
- Numbers keep their units and what they count; convert units only as an aside
  (3 英吋（7.6 公分）).
- Paraphrase. At most one quote per source, under 15 words, in quotation marks.
- After writing, verify every citation against its page (SKILL.md step 6).

## Practical and local resources

- NYC childcare and nannies: point to agencies, licensing lookups (NYC Health
  Department child care, NYS OCFS), and worker-rights and tax rules (NY Domestic Workers'
  Bill of Rights, IRS household employer rules). Never name or profile a private
  individual.
- Products (breast pumps, car seats, cribs): what to look for, safety standards and
  recalls (CPSC, NHTSA, FDA), insurance coverage, and tested reviews. List prices only
  with the date you saw them. Never invent specs.

## Images

Allowed, best first:

1. Your own inline SVG diagram.
2. Wikimedia Commons files under public domain, CC0, CC BY or CC BY-SA:
   `python3 <skill>/scripts/fetch_image.py commons "File:Name.jpg" --out daily/img/YYYY-MM-DD-name.jpg`.
   The script reads the license and author from Commons, refuses other licenses and
   files whose author adds conditions, resizes, strips metadata and prints the credit.
   Find candidates with the Commons API (`action=query&generator=search&gsrnamespace=6`,
   sending a User-Agent).
3. U.S. federal government images that the hosting page marks as public domain (many
   CDC PHIL images are; stock photos on .gov sites often are not):
   `fetch_image.py url <image url> --page <page> --author "CDC" --license "Public domain (U.S. government work)"`.

Not allowed: hotlinking, images from news sites, stock sites, brands' marketing, social
media, or anything without a clear reuse license. Never use photos of identifiable
private people or of children's faces. Look at every image before using it.
